import uuid
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from .database import load_database, save_database
from .helpers import find_techniques_in_text, get_current_week
from .note_image import render_note_image, render_notes_page

state_note_writing = 2
notes_per_page = 3


async def note_start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%A, %b %d")
    await update.message.reply_text(
        f"*training note: {today}*\n\n"
        "what did you learn?\n"
        "• techniques practiced\n"
        "• what went well\n"
        "• what to work on\n\n"
        "_keep it short: 1 to 20 words_\n\n"
        "/cancel to abort",
        parse_mode="Markdown",
    )
    return state_note_writing


async def note_receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    db = load_database(chat_id)
    text = update.message.text.strip()
    wc = len(text.split())

    if wc < 1:
        await update.message.reply_text("note can't be empty. write at least 1 word.")
        return state_note_writing
    if wc > 20:
        await update.message.reply_text(f"that's {wc} words. keep it to 20 or fewer.\ntry again or /cancel to abort.")
        return state_note_writing

    now = datetime.now()
    techs = find_techniques_in_text(text)
    db["notes"].append({
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "day": now.strftime("%A"),
        "text": text,
        "techniques": techs,
        "created_at": now.isoformat(),
    })
    save_database(chat_id, db)

    reply = "note saved!\n\n"
    if techs:
        reply += f"detected: {', '.join(techs)}\n\n"

    hint = _extract_work_on(text)
    if hint:
        reply += f"sounds like you want to work on:\n_{hint}_\n"
        context.user_data["pending_goal_text"] = hint
        await update.message.reply_text(
            reply,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("set as goal", callback_data="notegoal_yes"),
                InlineKeyboardButton("no thanks", callback_data="notegoal_no"),
            ]]),
        )
    else:
        await update.message.reply_text(reply)
    return ConversationHandler.END


def _extract_work_on(text):
    lower = text.lower()
    triggers = [
        "need to work on", "needs work", "want to work on", "work on",
        "need to improve", "want to improve", "improve my", "improve on",
        "should drill", "need to drill", "want to drill",
        "must practice", "need to practice", "want to practice",
        "goal:", "goal is", "struggling with", "still struggling",
        "need more reps", "gotta get better at", "focus on", "need to focus",
    ]
    for trigger in triggers:
        idx = lower.find(trigger)
        if idx == -1:
            continue
        after = text[idx + len(trigger):].strip().lstrip(":").strip()
        for end in ("\n", ".", "!"):
            ei = after.find(end)
            if ei != -1:
                after = after[:ei].strip()
                break
        if after:
            return after
    return None


async def note_goal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data != "notegoal_yes":
        context.user_data.pop("pending_goal_text", None)
        original = query.message.text or ""
        await query.edit_message_text(original.split("sounds like")[0].strip() or "note saved!")
        return

    goal_text = context.user_data.pop("pending_goal_text", None)
    if not goal_text:
        await query.edit_message_text("couldn't find the goal text, use /goal to set one manually.")
        return

    chat_id = query.message.chat_id
    db = load_database(chat_id)
    active = sum(1 for g in db.get("goals", []) if g.get("status", "active") == "active")

    if active >= 3:
        await query.edit_message_text(f"you already have {active} active goals (max 3).\ncomplete or remove one first with /goals.")
        return

    db["goals"].append({
        "id": uuid.uuid4().hex[:8],
        "week": get_current_week(),
        "goals": goal_text,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "refresh_schedule": [],
        "refresh_index": 0,
    })
    save_database(chat_id, db)
    await query.edit_message_text(
        f"goal set for {get_current_week()}:\n\n_{goal_text}_\n\n({active + 1}/3 goal slots used)",
        parse_mode="Markdown",
    )


async def send_notes_page(target, chat_id, page):
    db = load_database(chat_id)
    notes = db.get("notes", [])
    if not notes:
        await target.reply_text("no notes yet. use /note after training!")
        return

    page_images = render_notes_page(notes)
    total = max(1, len(page_images))
    page = max(1, min(page, total))

    await target.reply_photo(photo=page_images[page - 1])

    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("« prev", callback_data=f"notespage_{page - 1}"))
    buttons.append(InlineKeyboardButton(f"{page} / {total}", callback_data="notespage_noop"))
    if page < total:
        buttons.append(InlineKeyboardButton("next »", callback_data=f"notespage_{page + 1}"))

    await target.reply_text(
        f"_page {page} of {total}  ({len(notes)} notes total)_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([buttons]),
    )


async def notes_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_notes_page(update.message, update.effective_chat.id, page=1)


async def notes_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "notespage_noop":
        return
    page = int(query.data.replace("notespage_", ""))
    await send_notes_page(query.message, query.message.chat_id, page)
