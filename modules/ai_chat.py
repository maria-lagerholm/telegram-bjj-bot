import json
import os
import re
import asyncio
import logging

from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ContextTypes

from .database import load_database, save_database, data_directory
from .ai_tools import action_tools, tool_executors
from .ai_tools import exec_get_notes, exec_get_goals, exec_get_schedule, exec_get_focus, exec_get_stats
from .ai_guards import is_off_topic, clean_response
from .helpers import now_se

logger = logging.getLogger(__name__)

DAILY_LIMIT = 200
MAX_HISTORY = 40
SESSION_TIMEOUT = 30
MONTHLY_LIMIT = int(os.getenv("MONTHLY_AI_LIMIT", "10000"))

user_sessions = {}

MODEL_CANDIDATES = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite-001",
]

base_system_instruction = (
    "You are a casual BJJ training buddy inside a Telegram bot.\n"
    "\n"
    "The user's data is in YOUR_DATA section below. Use it directly. Never invent data.\n"
    "\n"
    "TOOL RULES:\n"
    "1. You CANNOT save notes. If the user wants to save a note, tell them to use /note command.\n"
    "   They can type /note or send a voice message after typing /note.\n"
    "2. ALWAYS call search_technique when ANY technique or move is mentioned. Even if you know it.\n"
    "3. When the user asks what techniques exist, call list_techniques.\n"
    "4. To focus/drill a technique: search_technique first, then set_focus_technique.\n"
    "5. To add a goal: call add_goal (1 to 7 words).\n"
    "6. To add schedule: call add_schedule_entry.\n"
    "7. To mark technique as known: call add_to_toolbox.\n"
    "8. After any tool returns success, confirm in one short sentence. Never call the same tool twice.\n"
    "\n"
    "STYLE:\n"
    "Only discuss BJJ, martial arts, fitness, and this user's training.\n"
    "Reply in the same language the user writes in.\n"
    "One or two short sentences max. Casual, friendly, like a training partner.\n"
    "Greet with a short BJJ phrase like 'oss!' or 'let's roll!'.\n"
    "No dashes as punctuation. No markdown headers. No emojis. No caps lock.\n"
    "Never invent URLs. Only share URLs returned by tools.\n"
    "Always suggest the most relevant command from this list:\n"
    "  /note /notes /goal /goals /focus /technique /toolbox /stats /schedule /reminders /export /map /help\n"
)

def build_user_context(chat_id):
    return "\n\n".join([
        f"NOTES:\n{exec_get_notes(chat_id, {'count': 5})}",
        f"GOALS:\n{exec_get_goals(chat_id, {})}",
        f"SCHEDULE:\n{exec_get_schedule(chat_id, {})}",
        f"FOCUS AND TOOLBOX:\n{exec_get_focus(chat_id, {})}",
        f"STATS:\n{exec_get_stats(chat_id, {})}",
    ])


def build_system_instruction(chat_id):
    ctx = build_user_context(chat_id)
    return base_system_instruction + f"\n\n--- YOUR_DATA ---\n{ctx}\n--- END YOUR_DATA ---\n"


def get_remaining(db):
    today = now_se().strftime("%Y-%m-%d")
    usage = db.get("ai_usage", {})
    if usage.get("date") != today:
        return DAILY_LIMIT
    return max(0, DAILY_LIMIT - usage.get("count", 0))


def increment_usage(chat_id, db):
    today = now_se().strftime("%Y-%m-%d")
    usage = db.get("ai_usage", {})
    if usage.get("date") != today:
        usage = {"date": today, "count": 0}
    usage["count"] = usage.get("count", 0) + 1
    db["ai_usage"] = usage
    save_database(chat_id, db)


global_usage_file = data_directory / "global_ai_usage.json"


def load_global_usage():
    month = now_se().strftime("%Y-%m")
    if global_usage_file.exists():
        with open(global_usage_file, "r") as f:
            data = json.load(f)
        if data.get("month") == month:
            return data
    return {"month": month, "count": 0}


def save_global_usage(data):
    with open(global_usage_file, "w") as f:
        json.dump(data, f)


def is_budget_exceeded():
    return load_global_usage()["count"] >= MONTHLY_LIMIT


def increment_global():
    usage = load_global_usage()
    usage["count"] = usage.get("count", 0) + 1
    save_global_usage(usage)
    return usage["count"]


def save_history(chat_id, user_text, model_text):
    db = load_database(chat_id)
    h = db.get("ai_history", [])
    h.append({"role": "user", "text": user_text})
    h.append({"role": "model", "text": model_text})
    db["ai_history"] = h[-(MAX_HISTORY * 2):]
    save_database(chat_id, db)


def load_history(chat_id):
    db = load_database(chat_id)
    result = []
    for e in db.get("ai_history", []):
        if e.get("text"):
            result.append(types.Content(role=e["role"], parts=[types.Part(text=e["text"])]))
    return result


def get_client():
    key = os.getenv("GEMINI_API_KEY", "")
    return genai.Client(api_key=key) if key else None


def build_tools():
    tools = []
    for t in action_tools:
        props = {}
        for k, v in t["parameters"].get("properties", {}).items():
            pt = types.Type.STRING if v.get("type") == "string" else types.Type.INTEGER
            props[k] = types.Schema(type=pt, description=v.get("description", ""))
        tools.append(types.Tool(function_declarations=[
            types.FunctionDeclaration(
                name=t["name"],
                description=t["description"],
                parameters=types.Schema(type=types.Type.OBJECT, properties=props),
            )
        ]))
    return tools


def execute_tool(chat_id, part):
    name = part.function_call.name
    args = dict(part.function_call.args) if part.function_call.args else {}
    executor = tool_executors.get(name)
    return name, executor(chat_id, args) if executor else "Tool not available."


async def run_tool_loop(chat, chat_id, response, max_rounds=5):
    urls = []
    done = set()
    called = set()

    for _ in range(max_rounds):
        parts = response.candidates[0].content.parts if response.candidates else []
        fn_parts = [p for p in parts if p.function_call and p.function_call.name]
        if not fn_parts:
            break

        new_parts = []
        for fp in fn_parts:
            key = f"{fp.function_call.name}:{dict(fp.function_call.args) if fp.function_call.args else ''}"
            if key not in done:
                new_parts.append(fp)
                done.add(key)
        if not new_parts:
            break

        resp_parts = []
        for fp in new_parts:
            name, result = execute_tool(chat_id, fp)
            called.add(name)
            for line in str(result).splitlines():
                s = line.strip()
                if s.startswith("EXACT_VIDEO_URL:"):
                    url = s.split("EXACT_VIDEO_URL:", 1)[1].strip()
                    if url and len(urls) < 3:
                        urls.append(url)
            resp_parts.append(types.Part.from_function_response(name=name, response={"result": str(result)}))

        try:
            response = chat.send_message(resp_parts)
        except Exception as err:
            logger.warning(f"tool loop send failed: {err}")
            break

    return response, urls, called


async def download_voice(update, context):
    voice = update.message.voice
    f = await voice.get_file()
    raw = await f.download_as_bytearray()
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
    voice_bytes = voice_mime = None

    if is_voice:
        try:
            voice_bytes, voice_mime = await download_voice(update, context)
        except Exception as err:
            logger.error(f"voice download failed {chat_id}: {err}")
            await update.message.reply_text("could not process that voice message. try again or type instead.")
            return

    if is_text and is_off_topic(user_text):
        await update.message.reply_text("i can only help with BJJ and training related topics. try /help!")
        return

    if is_budget_exceeded():
        await update.message.reply_text("the ai assistant is temporarily overloaded. you can still use all the commands from the menu!")
        return

    db = load_database(chat_id)
    remaining = get_remaining(db)
    if remaining <= 0:
        await update.message.reply_text(f"you've used all {DAILY_LIMIT} ai messages for today.\nthey reset at midnight. use /help for all bot features!")
        return

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    client = get_client()
    if not client:
        await update.message.reply_text("ai chat is not available right now. use /help to see what i can do!")
        return

    gemini_tools = build_tools()
    config = types.GenerateContentConfig(
        system_instruction=build_system_instruction(chat_id),
        tools=gemini_tools,
        tool_config=types.ToolConfig(function_calling_config=types.FunctionCallingConfig(mode="AUTO")),
    )

    now = now_se()
    session = user_sessions.get(chat_id)
    if session and (now - session["last_used"]).total_seconds() / 60 > SESSION_TIMEOUT:
        session = None

    if len(user_sessions) > 200:
        stale = [uid for uid, s in user_sessions.items() if (now - s["last_used"]).total_seconds() / 60 > SESSION_TIMEOUT]
        for uid in stale:
            del user_sessions[uid]

    chat_session = session["chat"] if session else None
    used_model = session["model_name"] if session else None

    parts = []
    if voice_bytes:
        parts.append(types.Part.from_bytes(data=voice_bytes, mime_type=voice_mime))
        parts.append(types.Part(text=(
            "(voice message. transcribe and respond in the same language. "
            "if they ask to create a goal, call add_goal. "
            "if they mention a technique, call search_technique. "
            "if they want to focus or drill, call set_focus_technique. "
            "if they want to save a note, tell them to use /note command.)"
        )))
    if user_text:
        parts.append(types.Part(text=user_text))

    last_error = None
    delay = 1.0

    for model in MODEL_CANDIDATES:
        for attempt in range(3):
            try:
                if chat_session and used_model == model and attempt == 0:
                    chat = chat_session
                else:
                    chat = client.chats.create(model=model, config=config, history=load_history(chat_id))

                response = chat.send_message(parts)
                response, collected_urls, called_tools = await run_tool_loop(chat, chat_id, response)

                reply = ""
                for p in response.candidates[0].content.parts:
                    if hasattr(p, "text") and p.text:
                        reply += p.text
                if not reply:
                    reply = "i can help with your BJJ training. try asking about your notes, goals, or schedule!"

                reply = clean_response(reply)

                if collected_urls:
                    reply = re.sub(r'https?://\S+', '', reply).strip()
                    reply = re.sub(r'\s{2,}', ' ', reply).rstrip(':').strip()
                    for url in collected_urls:
                        reply += f"\n{url}"

                user_sessions[chat_id] = {"chat": chat, "model_name": model, "last_used": now}
                save_history(chat_id, user_text or "(voice message)", reply)
                increment_usage(chat_id, db)
                increment_global()
                remaining -= 1
                if remaining <= 3:
                    reply += f"\n\n({remaining} ai messages left today)"
                await update.message.reply_text(reply)
                return

            except Exception as err:
                last_error = err
                es = str(err).lower()
                rate = "429" in es or "quota" in es or "rate" in es
                notfound = "404" in es or "not found" in es or "no longer available" in es or "not supported" in es

                if rate and attempt < 2:
                    logger.warning(f"{model} rate limited (attempt {attempt + 1}), waiting {delay}s")
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, 10.0)
                    chat_session = used_model = None
                    continue
                if notfound:
                    logger.warning(f"{model} not found, trying next")
                    break
                if rate:
                    logger.warning(f"{model} rate limited after retries, trying next")
                    break
                logger.error(f"Gemini error ({model}) for {chat_id}: {err}")
                break

    user_sessions.pop(chat_id, None)
    es = str(last_error).lower() if last_error else ""
    logger.error(f"Gemini API error for {chat_id}: {last_error}")

    if "429" in es or "quota" in es or "rate" in es:
        await update.message.reply_text("too many messages too fast. wait a minute and try again! meanwhile you can use all commands from /help.")
    else:
        await update.message.reply_text("something went wrong with the ai. try again or use /help for all bot features!")
