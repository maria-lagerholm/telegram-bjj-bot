import uuid
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from .database import load_database, save_database
from .helpers import find_techniques_in_text, get_current_week

state_note_writing = 2


async def note_start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%A, %b %d")
    prompt_message = (
        f"*training note: {today}*\n\n"
        "what did you learn?\n"
        "• techniques practiced\n"
        "• what went well\n"
        "• what to work on\n\n"
        "/cancel to abort"
    )
    await update.message.reply_text(prompt_message, parse_mode="Markdown")
    return state_note_writing


async def note_receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    database = load_database(chat_id)
    note_text = update.message.text.strip()
    now = datetime.now()
    
    techniques_found = find_techniques_in_text(note_text)
    
    new_note = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "day": now.strftime("%A"),
        "text": note_text,
        "techniques": techniques_found,
        "created_at": now.isoformat(),
    }
    
    database["notes"].append(new_note)
    
    save_database(chat_id, database)
    
    reply = "note saved!\n\n"
    
    if techniques_found:
        techniques_list = ", ".join(techniques_found)
        reply += f"detected: {techniques_list}\n\n"
    
    # look for "work on" phrases to suggest setting a goal
    work_on_hint = _extract_work_on(note_text)

    if work_on_hint:
        reply += f"sounds like you want to work on:\n_{work_on_hint}_\n"
        keyboard = [
            [
                InlineKeyboardButton("set as goal", callback_data="notegoal_yes"),
                InlineKeyboardButton("no thanks", callback_data="notegoal_no"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # stash the extracted text so the callback can use it
        context.user_data["pending_goal_text"] = work_on_hint
        await update.message.reply_text(reply, reply_markup=reply_markup)
    else:
        await update.message.reply_text(reply)

    return ConversationHandler.END


def _extract_work_on(text: str) -> str | None:
    """Pull out what the user wants to work on from their note."""
    lower = text.lower()

    # ordered list of trigger phrases
    triggers = [
        "need to work on",
        "needs work",
        "want to work on",
        "work on",
        "need to improve",
        "want to improve",
        "improve my",
        "improve on",
        "should drill",
        "need to drill",
        "want to drill",
        "must practice",
        "need to practice",
        "want to practice",
        "goal:",
        "goal is",
        "struggling with",
        "still struggling",
        "need more reps",
        "gotta get better at",
        "focus on",
        "need to focus",
    ]

    for trigger in triggers:
        idx = lower.find(trigger)
        if idx == -1:
            continue
        # grab the rest of the sentence after the trigger
        after = text[idx + len(trigger):].strip().lstrip(":").strip()
        # take up to the first sentence-ending punctuation or newline
        for end_char in ("\n", ".", "!"):
            end_idx = after.find(end_char)
            if end_idx != -1:
                after = after[:end_idx].strip()
                break
        if after:
            return after

    return None


async def note_goal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the 'set as goal' / 'no thanks' buttons after a note."""
    query = update.callback_query
    await query.answer()

    if query.data == "notegoal_yes":
        goal_text = context.user_data.pop("pending_goal_text", None)
        if not goal_text:
            await query.edit_message_text("couldn't find the goal text, use /goal to set one manually.")
            return

        chat_id = query.message.chat_id
        database = load_database(chat_id)

        # enforce 3-goal limit
        active_count = sum(1 for g in database.get("goals", []) if g.get("status", "active") == "active")
        if active_count >= 3:
            await query.edit_message_text(
                f"you already have {active_count} active goals (max 3).\n"
                "complete or remove one first with /goals.",
            )
            return

        week = get_current_week()
        database["goals"].append({
            "id": uuid.uuid4().hex[:8],
            "week": week,
            "goals": goal_text,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "refresh_schedule": [],
            "refresh_index": 0,
        })
        save_database(chat_id, database)

        active_count += 1
        await query.edit_message_text(
            f"goal set for {week}:\n\n_{goal_text}_\n\n({active_count}/3 goal slots used)",
            parse_mode="Markdown",
        )
    else:
        # "no thanks"
        context.user_data.pop("pending_goal_text", None)
        original = query.message.text or ""
        # strip the "sounds like…" part, keep just the note-saved confirmation
        clean = original.split("sounds like")[0].strip()
        await query.edit_message_text(clean or "note saved!")


async def notes_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    database = load_database(chat_id)
    
    if not database["notes"]:
        await update.message.reply_text("no notes yet. use /note after training!")
        return
    
    message = "*training notes*\n\n"
    
    last_ten_notes = database["notes"][-10:]
    for note in reversed(last_ten_notes):
        date_string = note.get("day", "")
        time_string = note.get("time", "")
        time_part = f" {time_string}" if time_string else ""
        message += f"*{note['date']}* ({date_string}{time_part})\n"
        
        preview = note["text"][:120]
        if len(note["text"]) > 120:
            preview += "…"
        message += f"{preview}\n"
        
        if note.get("techniques"):
            techniques_list = ", ".join(note["techniques"])
            message += f"_{techniques_list}_\n"
        
        message += "\n"
    
    total_notes = len(database["notes"])
    if total_notes > 10:
        message += f"_last 10 of {total_notes} notes_\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")
