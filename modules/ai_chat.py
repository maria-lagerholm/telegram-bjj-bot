import json
import os
import re
import asyncio
import logging
from datetime import datetime

from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ContextTypes

from .database import load_database, save_database, data_directory
from .ai_tools import action_tools, tool_executors
from .ai_tools import exec_get_notes, exec_get_goals, exec_get_schedule, exec_get_focus, exec_get_stats
from .ai_guards import is_off_topic, clean_response

logger = logging.getLogger(__name__)

daily_message_limit = 200
max_history_messages = 40

user_sessions = {}
session_timeout_minutes = 30

monthly_global_limit = int(os.getenv("MONTHLY_AI_LIMIT", "10000"))

model_candidates = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite-001",
]

base_system_instruction = (
    "You are a casual BJJ training buddy inside a Telegram bot.\n"
    "\n"
    "IMPORTANT: The user's current training data is provided below in YOUR_DATA section.\n"
    "Use that data directly when answering. Do NOT make up data that is not there.\n"
    "If the user asks about their notes, goals, schedule, focus, or stats, use the data below.\n"
    "\n"
    "TOOL RULES (follow strictly):\n"
    "1. When the user mentions a technique name, call search_technique to find it.\n"
    "2. When the user asks what techniques are available, call list_techniques.\n"
    "3. When the user describes training and says YES to saving, call save_training_note ONCE.\n"
    "   After the tool returns success, just confirm to the user. Do NOT call it again.\n"
    "4. When the user wants to focus on or drill a technique, first call search_technique,\n"
    "   then call set_focus_technique with the technique_key from the result.\n"
    "5. When the user wants to set a goal, call add_goal with the goal text (1 to 7 words).\n"
    "6. When the user says they train on a day/time, call add_schedule_entry.\n"
    "7. When the user says they know a technique, call add_to_toolbox.\n"
    "\n"
    "CRITICAL: After a tool returns a success result, do NOT call the same tool again.\n"
    "Just confirm the action to the user in one short sentence.\n"
    "\n"
    "ONLY discuss BJJ, martial arts, fitness, and this user's training.\n"
    "If the user asks about unrelated topics, politely say you can only help with training.\n"
    "Reply in the SAME language the user writes in.\n"
    "Keep every reply to one or two short sentences. Never write long paragraphs.\n"
    "Use casual, friendly tone like a training partner.\n"
    "When greeting, use a short BJJ phrase like 'oss!', 'let's roll!', 'ready to train?'.\n"
    "Never use dashes as punctuation. Use commas or periods instead.\n"
    "Never use markdown headers. Keep it simple chat text.\n"
    "Never use emojis in your text. Zero emojis.\n"
    "Do NOT write any URLs in your reply. The system will automatically attach the correct video links.\n"
    "\n"
    "ALWAYS end your reply with the most relevant command the user can type next.\n"
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


def build_user_context(chat_id):
    """Pre-fetch all user data and return it as a text block for the system prompt."""
    sections = []

    notes_data = exec_get_notes(chat_id, {"count": 5})
    sections.append(f"NOTES:\n{notes_data}")

    goals_data = exec_get_goals(chat_id, {})
    sections.append(f"GOALS:\n{goals_data}")

    schedule_data = exec_get_schedule(chat_id, {})
    sections.append(f"SCHEDULE:\n{schedule_data}")

    focus_data = exec_get_focus(chat_id, {})
    sections.append(f"FOCUS AND TOOLBOX:\n{focus_data}")

    stats_data = exec_get_stats(chat_id, {})
    sections.append(f"STATS:\n{stats_data}")

    return "\n\n".join(sections)


def build_system_instruction(chat_id):
    """Build a full system instruction with the user's live data embedded."""
    context = build_user_context(chat_id)
    return base_system_instruction + f"\n\n--- YOUR_DATA ---\n{context}\n--- END YOUR_DATA ---\n"


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
                types.Content(
                    role=role,
                    parts=[types.Part(text=text)],
                )
            )
    return contents


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def build_gemini_tools():
    gemini_tools = []
    for t in action_tools:
        properties = {}
        for k, v in t["parameters"].get("properties", {}).items():
            if v.get("type") == "string":
                prop_type = types.Type.STRING
            else:
                prop_type = types.Type.INTEGER
            properties[k] = types.Schema(
                type=prop_type,
                description=v.get("description", ""),
            )
        gemini_tools.append(types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name=t["name"],
                    description=t["description"],
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
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


async def run_tool_loop(chat, chat_id, response, max_rounds=5):
    collected_urls = []
    completed_calls = set()

    for _ in range(max_rounds):
        parts = response.candidates[0].content.parts if response.candidates else []
        function_parts = [p for p in parts if p.function_call and p.function_call.name]
        if not function_parts:
            break

        new_calls = []
        for fp in function_parts:
            call_key = fp.function_call.name
            args_str = str(dict(fp.function_call.args)) if fp.function_call.args else ""
            dedup_key = f"{call_key}:{args_str}"
            if dedup_key not in completed_calls:
                new_calls.append(fp)
                completed_calls.add(dedup_key)

        if not new_calls:
            break

        response_parts = []
        for fp in new_calls:
            fn_name, result = execute_tool_call(chat_id, fp)

            result_urls = []
            for line in str(result).splitlines():
                stripped = line.strip()
                if stripped.startswith("EXACT_VIDEO_URL:"):
                    url = stripped.split("EXACT_VIDEO_URL:", 1)[1].strip()
                    if url:
                        result_urls.append(url)
            if len(result_urls) <= 3:
                collected_urls.extend(result_urls)

            response_parts.append(
                types.Part.from_function_response(
                    name=fn_name,
                    response={"result": str(result)},
                )
            )

        try:
            response = chat.send_message(response_parts)
        except Exception as err:
            logger.warning(f"tool loop send failed: {err}")
            break
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

    client = get_gemini_client()
    if not client:
        await update.message.reply_text(
            "ai chat is not available right now. use /help to see what i can do!"
        )
        return

    gemini_tools = build_gemini_tools()
    full_system_instruction = build_system_instruction(chat_id)

    chat_config = types.GenerateContentConfig(
        system_instruction=full_system_instruction,
        tools=gemini_tools,
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode="AUTO",
            )
        ),
    )

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

    message_parts = []
    if voice_bytes:
        message_parts.append(
            types.Part.from_bytes(data=voice_bytes, mime_type=voice_mime)
        )
        message_parts.append(
            types.Part(text=(
                "(voice message from user. transcribe it and respond in the same language. "
                "if they describe training, ask to save as note. "
                "if they mention a technique, search for it. "
                "if they want to set a goal, focus, or schedule, use the right tool. "
                "respond to what they said.)"
            ))
        )
    if user_text:
        message_parts.append(types.Part(text=user_text))

    last_error = None
    retry_delay = 1.0

    for model_name in model_candidates:
        for attempt in range(3):
            try:
                if chat_session and used_model == model_name and attempt == 0:
                    chat = chat_session
                else:
                    past = load_history(chat_id)
                    chat = client.chats.create(
                        model=model_name,
                        config=chat_config,
                        history=past,
                    )

                response = chat.send_message(message_parts)
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
                is_rate_limit = "429" in err_str or "quota" in err_str or "rate" in err_str
                is_not_found = "404" in err_str or "not found" in err_str or "no longer available" in err_str or "not supported" in err_str

                if is_rate_limit and attempt < 2:
                    logger.warning(f"{model_name} rate limited (attempt {attempt + 1}), waiting {retry_delay}s")
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 10.0)
                    chat_session = None
                    used_model = None
                    continue

                if is_not_found:
                    logger.warning(f"{model_name} not found, trying next model")
                    break

                if is_rate_limit:
                    logger.warning(f"{model_name} rate limited after retries, trying next model")
                    break

                logger.error(f"Gemini error ({model_name}) for chat {chat_id}: {err}")
                break

    user_sessions.pop(chat_id, None)
    err_str = str(last_error).lower() if last_error else ""
    is_rate_limit = "429" in err_str or "quota" in err_str or "rate" in err_str
    logger.error(f"Gemini API error for chat {chat_id}: {last_error}")

    if is_rate_limit:
        await update.message.reply_text(
            "too many messages too fast. wait a minute and try again! "
            "meanwhile you can use all commands from /help."
        )
    else:
        await update.message.reply_text(
            "something went wrong with the ai. try again or use /help for all bot features!"
        )
