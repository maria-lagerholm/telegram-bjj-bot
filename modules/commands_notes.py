import uuid
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from .database import load_database, save_database
from .helpers import find_techniques_in_text, get_current_week
from .note_image import render_notes_page

state_note_writing = 2
state_note_editing = 3
manage_per_page = 5


def _backfill_ids(notes):
    changed = False
    for n in notes:
        if "id" not in n:
            n["id"] = uuid.uuid4().hex[:8]
            changed = True
    return changed


def _find_note(notes, note_id):
    for i, n in enumerate(notes):
        if n.get("id") == note_id:
            return i
    return -1


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
        await update.message.reply_text(
            f"that's {wc} words. keep it to 20 or fewer.\ntry again or /cancel to abort."
        )
        return state_note_writing

    now = datetime.now()
    techs = find_techniques_in_text(text)
    db["notes"].append({
        "id": uuid.uuid4().hex[:8],
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
        await query.edit_message_text(
            f"you already have {active} active goals (max 3).\n"
            "complete or remove one first with /goals."
        )
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

    if _backfill_ids(notes):
        save_database(chat_id, db)

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


async def journal_manage_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_manage_page(update.message, update.effective_chat.id, 1)


async def _send_manage_page(target, chat_id, page):
    db = load_database(chat_id)
    notes = db.get("notes", [])
    if not notes:
        await target.reply_text("no notes yet. use /note after training!")
        return

    if _backfill_ids(notes):
        save_database(chat_id, db)

    total_pages = max(1, -(-len(notes) // manage_per_page))
    page = max(1, min(page, total_pages))
    start = (page - 1) * manage_per_page
    end = start + manage_per_page
    page_notes = notes[start:end]

    msg = f"*journal* (page {page}/{total_pages})\n\n"
    keyboard = []
    for n in page_notes:
        date = n.get("date", "")
        time = n.get("time", "")
        text = n.get("text", "")
        short = text[:30] + "..." if len(text) > 30 else text
        label = f"{date} {time}: {short}" if time else f"{date}: {short}"
        msg += f"• {label}\n"
        nid = n.get("id", "")
        keyboard.append([
            InlineKeyboardButton(f"✏️ {short[:18]}", callback_data=f"noteedit_{nid}"),
            InlineKeyboardButton("🗑", callback_data=f"notedel_{nid}"),
        ])

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("« prev", callback_data=f"notemanage_{page - 1}"))
    if page < total_pages:
        nav.append(InlineKeyboardButton("next »", callback_data=f"notemanage_{page + 1}"))
    if nav:
        keyboard.append(nav)

    await target.reply_text(
        msg + "\n_tap ✏️ to edit or 🗑 to delete_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def note_manage_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("notemanage_"):
        page = int(data.replace("notemanage_", ""))
        chat_id = query.message.chat_id
        await _send_manage_page(query.message, chat_id, page)
        return

    if data.startswith("notedel_"):
        nid = data.replace("notedel_", "")
        chat_id = query.message.chat_id
        db = load_database(chat_id)
        notes = db.get("notes", [])
        idx = _find_note(notes, nid)
        if idx == -1:
            await query.edit_message_text("note not found, it may have been deleted already.")
            return
        removed = notes.pop(idx)
        save_database(chat_id, db)
        short = removed.get("text", "")[:25]
        await query.edit_message_text(f"deleted: _{short}_\n\nuse /journal to manage notes.", parse_mode="Markdown")
        return

    if data.startswith("noteedit_"):
        nid = data.replace("noteedit_", "")
        chat_id = query.message.chat_id
        db = load_database(chat_id)
        notes = db.get("notes", [])
        idx = _find_note(notes, nid)
        if idx == -1:
            await query.edit_message_text("note not found.")
            return
        note = notes[idx]
        context.user_data["editing_note_id"] = nid
        await query.edit_message_text(
            f"*editing note from {note.get('date', '')}*\n\n"
            f"current: _{note.get('text', '')}_\n\n"
            "type the new text (1 to 20 words)\n/cancel to abort",
            parse_mode="Markdown",
        )
        return state_note_editing


async def note_edit_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    wc = len(text.split())

    if wc < 1:
        await update.message.reply_text("note can't be empty. write at least 1 word.")
        return state_note_editing
    if wc > 20:
        await update.message.reply_text(
            f"that's {wc} words. keep it to 20 or fewer.\ntry again or /cancel to abort."
        )
        return state_note_editing

    nid = context.user_data.pop("editing_note_id", None)
    if not nid:
        await update.message.reply_text("edit session expired. use /journal to try again.")
        return ConversationHandler.END

    db = load_database(chat_id)
    notes = db.get("notes", [])
    idx = _find_note(notes, nid)
    if idx == -1:
        await update.message.reply_text("note not found, it may have been deleted.")
        return ConversationHandler.END

    notes[idx]["text"] = text
    notes[idx]["techniques"] = find_techniques_in_text(text)
    save_database(chat_id, db)
    await update.message.reply_text("note updated!")
    return ConversationHandler.END
