import io
import json
import os
import re
import asyncio
import logging
from datetime import datetime
from pathlib import Path

import google.generativeai as genai
from telegram import Update
from telegram.ext import ContextTypes

from .database import load_database, save_database, data_directory
from .ai_tools import all_tools, tool_executors
from .ai_guards import is_off_topic, clean_response

logger = logging.getLogger(__name__)

daily_message_limit = 100
max_history_messages = 20

user_sessions = {}
session_timeout_minutes = 30

monthly_global_limit = int(os.getenv("MONTHLY_AI_LIMIT", "10000"))

model_candidates = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite-001",
]

system_instruction = (
    "You are a casual BJJ training buddy inside a Telegram bot.\n"
    "Use the provided tools to look up the user's notes, goals, schedule, and stats.\n"
    "ONLY discuss BJJ, martial arts, fitness, and this user's training.\n"
    "If the user asks about unrelated topics, politely say you can only help with training.\n"
    "Reply in the SAME language the user writes in.\n"
    "Keep every reply to one or two short sentences. Never write long paragraphs.\n"
    "Use casual, friendly tone like a training partner.\n"
    "When greeting, use a short BJJ phrase like 'oss!', 'let's roll!', 'ready to train?'.\n"
    "Never use dashes as punctuation. Use commas or periods instead.\n"
    "Never use markdown headers. Keep it simple chat text.\n"
    "Never use emojis in your text. Zero emojis.\n"
    "IMPORTANT: when a technique is mentioned (by you or the user), ALWAYS call search_technique first.\n"
    "When the user asks what techniques are available, what to practice, or asks to see a list, "
    "ALWAYS call list_techniques with the relevant category. Present ALL results from the tool, not just some.\n"
    "For category questions like 'what escapes are there', call list_techniques with category='escapes'.\n"
    "If the user says a general topic like 'escapes' or 'sweeps', call list_techniques for that category.\n"
    "Do NOT write any URLs in your reply. The system will automatically attach the correct video links.\n"
    "When the user describes what they practiced or learned today, ask if they want to save it as a note.\n"
    "If they confirm, call save_training_note with a short summary (max 20 words) of what they said.\n"
    "Never save a note without the user confirming first.\n"
    "\n"
    "CRITICAL RULE: ALWAYS end your reply with the most relevant command the user can type next.\n"
    "Every tool result includes a COMMAND hint. Always include that command in your reply.\n"
    "Available commands:\n"
    "  /note  log a training note\n"
    "  /notes  view saved notes\n"
    "  /goal  set a new goal\n"
    "  /goals  view current goals\n"
    "  /focus  set or view focus technique\n"
    "  /technique  browse all techniques\n"
    "  /toolbox  view known techniques\n"
    "  /stats  view training stats\n"
    "  /schedule  set training schedule\n"
    "  /reminders  customize reminder times\n"
    "  /export  export your data\n"
    "  /map  see the full bot feature map\n"
    "  /help  open the main menu\n"
)


def get_remaining_messages(db):
    today = datetime.now().strftime("%Y-%m-%d")
    ai_usage = db.get("ai_usage", {})
    if ai_usage.get("date") != today:
        return daily_message_limit
    return max(0, daily_message_limit - ai_usage.get("count", 0))


def increment_usage(chat_id, db):
    today = datetime.now().strftime("%Y-%m-%d")
    ai_usage = db.get("ai_usage", {})
    if ai_usage.get("date") != today:
        ai_usage = {"date": today, "count": 0}
    ai_usage["count"] = ai_usage.get("count", 0) + 1
    db["ai_usage"] = ai_usage
    save_database(chat_id, db)


global_usage_file = data_directory / "global_ai_usage.json"


def load_global_usage():
    current_month = datetime.now().strftime("%Y-%m")
    if global_usage_file.exists():
        with open(global_usage_file, "r") as f:
            data = json.load(f)
        if data.get("month") == current_month:
            return data
    return {"month": current_month, "count": 0}


def save_global_usage(data):
    with open(global_usage_file, "w") as f:
        json.dump(data, f)


def is_budget_exceeded():
    usage = load_global_usage()
    return usage["count"] >= monthly_global_limit


def increment_global_usage():
    usage = load_global_usage()
    usage["count"] = usage.get("count", 0) + 1
    save_global_usage(usage)
    return usage["count"]


def save_history(chat_id, user_text, model_text):
    db = load_database(chat_id)
    history = db.get("ai_history", [])
    history.append({"role": "user", "text": user_text})
    history.append({"role": "model", "text": model_text})
    db["ai_history"] = history[-(max_history_messages * 2):]
    save_database(chat_id, db)


def load_history(chat_id):
    db = load_database(chat_id)
    history = db.get("ai_history", [])
    if not history:
        return []
    contents = []
    for entry in history:
        role = entry.get("role", "user")
        text = entry.get("text", "")
        if text:
            contents.append(
                genai.protos.Content(
                    role=role,
                    parts=[genai.protos.Part(text=text)],
                )
            )
    return contents


def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return False
    genai.configure(api_key=api_key)
    return True


def build_gemini_tools():
    gemini_tools = []
    for t in all_tools:
        properties = {}
        for k, v in t["parameters"].get("properties", {}).items():
            if v.get("type") == "string":
                prop_type = genai.protos.Type.STRING
            else:
                prop_type = genai.protos.Type.INTEGER
            properties[k] = genai.protos.Schema(
                type=prop_type,
                description=v.get("description", ""),
            )
        gemini_tools.append(genai.protos.Tool(
            function_declarations=[
                genai.protos.FunctionDeclaration(
                    name=t["name"],
                    description=t["description"],
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties=properties,
                    ),
                )
            ]
        ))
    return gemini_tools


def execute_tool_call(chat_id, part):
    fn_name = part.function_call.name
    fn_args = {}
    if part.function_call.args:
        for key, val in part.function_call.args.items():
            fn_args[key] = val

    executor = tool_executors.get(fn_name)
    if executor:
        result = executor(chat_id, fn_args)
    else:
        result = "Tool not available."

    return fn_name, result


async def run_tool_loop(chat, chat_id, response, max_rounds=3):
    collected_urls = []
    for _ in range(max_rounds):
        part = response.candidates[0].content.parts[0]
        if not hasattr(part, "function_call") or not part.function_call.name:
            break

        fn_name, result = execute_tool_call(chat_id, part)

        result_urls = []
        for line in str(result).splitlines():
            stripped = line.strip()
            if stripped.startswith("EXACT_VIDEO_URL:"):
                url = stripped.split("EXACT_VIDEO_URL:", 1)[1].strip()
                if url:
                    result_urls.append(url)
        if len(result_urls) <= 3:
            collected_urls.extend(result_urls)

        response = chat.send_message(
            genai.protos.Content(
                parts=[
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=fn_name,
                            response={"result": result},
                        )
                    )
                ]
            )
        )
    return response, collected_urls


async def download_voice(update, context):
    voice = update.message.voice
    voice_file = await voice.get_file()
    raw = await voice_file.download_as_bytearray()
    return bytes(raw), voice.mime_type or "audio/ogg"


async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    is_voice = update.message.voice is not None
    is_text = bool(update.message.text and update.message.text.strip())

    if not is_voice and not is_text:
        return

    chat_id = update.effective_chat.id
    user_text = update.message.text.strip() if is_text else ""
    voice_bytes = None
    voice_mime = None

    if is_voice:
        try:
            voice_bytes, voice_mime = await download_voice(update, context)
        except Exception as err:
            logger.error(f"Failed to download voice for {chat_id}: {err}")
            await update.message.reply_text(
                "could not process that voice message. try again or type instead."
            )
            return

    if is_text and is_off_topic(user_text):
        await update.message.reply_text(
            "i can only help with BJJ and training related topics. try /help!"
        )
        return

    if is_budget_exceeded():
        await update.message.reply_text(
            "the ai assistant is temporarily overloaded. you can still use all the commands from the menu!"
        )
        return

    db = load_database(chat_id)
    remaining = get_remaining_messages(db)
    if remaining <= 0:
        await update.message.reply_text(
            f"you've used all {daily_message_limit} ai messages for today.\n"
            "they reset at midnight. use /help for all bot features!"
        )
        return

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    configure_gemini()
    gemini_tools = build_gemini_tools()

    session = user_sessions.get(chat_id)
    now = datetime.now()

    if session:
        age = (now - session["last_used"]).total_seconds() / 60
        if age > session_timeout_minutes:
            session = None

    if len(user_sessions) > 200:
        stale_ids = []
        for uid, s in user_sessions.items():
            age_minutes = (now - s["last_used"]).total_seconds() / 60
            if age_minutes > session_timeout_minutes:
                stale_ids.append(uid)
        for uid in stale_ids:
            del user_sessions[uid]

    chat_session = session["chat"] if session else None
    used_model = session["model_name"] if session else None

    last_error = None
    for model_name in model_candidates:
        try:
            if chat_session and used_model == model_name:
                chat = chat_session
            else:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_instruction,
                    tools=gemini_tools,
                )
                past = load_history(chat_id)
                chat = model.start_chat(history=past)

            message_parts = []
            if voice_bytes:
                message_parts.append(
                    genai.protos.Part(
                        inline_data=genai.protos.Blob(
                            mime_type=voice_mime,
                            data=voice_bytes,
                        )
                    )
                )
                message_parts.append(
                    genai.protos.Part(
                        text="(the user sent a voice message, respond to what they said)"
                    )
                )
            if user_text:
                message_parts.append(genai.protos.Part(text=user_text))

            response = chat.send_message(
                genai.protos.Content(role="user", parts=message_parts)
            )

            response, collected_urls = await run_tool_loop(chat, chat_id, response)

            reply_text = ""
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text") and part.text:
                    reply_text += part.text

            if not reply_text:
                reply_text = "i can help with your BJJ training. try asking about your notes, goals, or schedule!"

            reply_text = clean_response(reply_text)

            if collected_urls:
                reply_text = re.sub(r'https?://\S+', '', reply_text).strip()
                reply_text = re.sub(r'\s{2,}', ' ', reply_text).strip()
                reply_text = reply_text.rstrip(':').strip()
                for url in collected_urls:
                    reply_text += f"\n{url}"

            user_sessions[chat_id] = {
                "chat": chat,
                "model_name": model_name,
                "last_used": now,
            }

            history_user_text = user_text if user_text else "(voice message)"
            save_history(chat_id, history_user_text, reply_text)

            increment_usage(chat_id, db)
            increment_global_usage()
            remaining = remaining - 1

            if remaining <= 3:
                reply_text += f"\n\n({remaining} ai messages left today)"

            await update.message.reply_text(reply_text)
            return

        except Exception as err:
            last_error = err
            err_str = str(err).lower()
            if chat_session and used_model == model_name:
                chat_session = None
                used_model = None
                logger.warning(f"session expired for {chat_id}, retrying fresh")
                continue
            retryable = (
                "429" in err_str
                or "quota" in err_str
                or "404" in err_str
                or "not found" in err_str
                or "no longer available" in err_str
                or "not supported" in err_str
            )
            if retryable and model_name != model_candidates[-1]:
                logger.warning(f"{model_name} unavailable, trying next: {err}")
                await asyncio.sleep(0.5)
                continue
            logger.error(f"Gemini error ({model_name}) for chat {chat_id}: {err}")
            break

    user_sessions.pop(chat_id, None)
    err_str = str(last_error) if last_error else ""
    logger.error(f"Gemini API error for chat {chat_id}: {last_error}")
    await update.message.reply_text(
        "the ai assistant is temporarily overloaded. you can still use all the commands from the menu!"
    )
