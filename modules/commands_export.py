import io
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from .database import load_database, save_database

state_import_waiting = "IMPORT_WAITING_FILE"


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📄 readable .txt", callback_data="export_txt")],
        [InlineKeyboardButton("💾 full backup .json", callback_data="export_json")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "*export your data*\n\n"
        "choose a format:\n"
        "• *txt* human-readable summary of all your data\n"
        "• *json* full raw backup (can be re-imported later)\n\n"
        "_the file will be sent right here in chat. "
        "you can then save it to google drive, email it, or store it anywhere._",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def export_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    chat_id = query.message.chat_id
    database = load_database(chat_id)

    if data == "export_txt":
        content = build_txt_export(database)
        filename = f"bjj_training_data_{datetime.now().strftime('%Y-%m-%d')}.txt"
        buf = io.BytesIO(content.encode("utf-8"))
        buf.name = filename

        await query.edit_message_text("generating your export…")
        await query.message.reply_document(
            document=buf,
            filename=filename,
            caption="here's your training data! save it somewhere safe 🤙",
        )

    elif data == "export_json":
        content = json.dumps(database, indent=2, default=str, ensure_ascii=False)
        filename = f"bjj_backup_{datetime.now().strftime('%Y-%m-%d')}.json"
        buf = io.BytesIO(content.encode("utf-8"))
        buf.name = filename

        await query.edit_message_text("generating your backup…")
        await query.message.reply_document(
            document=buf,
            filename=filename,
            caption="full backup! you can keep this to restore your data later 💾",
        )


async def import_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*import backup*\n\n"
        "send me a .json backup file that was exported from this bot.\n\n"
        "this will replace all your current data with the data from the file.\n"
        "make sure to /export first if you want to keep your current data.\n\n"
        "/cancel to abort",
        parse_mode="Markdown",
    )
    return state_import_waiting


async def import_receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document

    if not doc:
        await update.message.reply_text("please send a .json file.")
        return state_import_waiting

    if not doc.file_name.endswith(".json"):
        await update.message.reply_text(
            "that doesn't look like a .json file. please send the backup file you exported."
        )
        return state_import_waiting

    try:
        file = await doc.get_file()
        file_bytes = await file.download_as_bytearray()
        data = json.loads(file_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        await update.message.reply_text(
            "could not read that file. make sure it is a valid .json backup."
        )
        return state_import_waiting
    except Exception:
        await update.message.reply_text(
            "something went wrong downloading the file. please try again."
        )
        return state_import_waiting

    expected_keys = {"goals", "notes"}
    if not isinstance(data, dict) or not expected_keys.intersection(data.keys()):
        await update.message.reply_text(
            "this file does not look like a bjj bot backup. "
            "it should contain goals, notes, and other training data."
        )
        return state_import_waiting

    defaults = {
        "goals": [],
        "notes": [],
        "drill_queue": [],
        "active_drill": None,
        "training_log": [],
        "toolbox": [],
        "schedule": [],
    }
    for key, default_val in defaults.items():
        if key not in data:
            data[key] = default_val

    chat_id = update.effective_chat.id
    save_database(chat_id, data)

    summary_parts = []
    notes_count = len(data.get("notes", []))
    if notes_count:
        summary_parts.append(f"{notes_count} notes")
    goals_count = len(data.get("goals", []))
    if goals_count:
        summary_parts.append(f"{goals_count} goals")
    toolbox_count = len(data.get("toolbox", []))
    if toolbox_count:
        summary_parts.append(f"{toolbox_count} techniques in toolbox")
    log_count = len(data.get("training_log", []))
    if log_count:
        summary_parts.append(f"{log_count} training log entries")

    if summary_parts:
        summary = ", ".join(summary_parts)
    else:
        summary = "empty backup"

    await update.message.reply_text(
        f"backup restored!\n\nimported: {summary}\n\n"
        "your data has been updated. use /help to continue.",
    )
    return ConversationHandler.END


def build_txt_export(db):
    lines = []
    now = datetime.now()
    lines.append("BJJ Training Data")
    lines.append(f"Exported {now.strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    goals = db.get("goals", [])
    active_goals = []
    completed_goals = []
    removed_goals = []
    for g in goals:
        if g.get("status", "active") == "active":
            active_goals.append(g)
        elif g.get("status") == "completed":
            completed_goals.append(g)
        elif g.get("status") == "removed":
            removed_goals.append(g)

    lines.append("GOALS")
    lines.append("")

    if active_goals:
        lines.append("Active")
        for g in active_goals:
            week = g.get("week", "")
            lines.append(f"  {g['goals']}  ({week})")
    if completed_goals:
        lines.append("Completed")
        for g in completed_goals:
            completed_at = g.get("completed_at", "")
            if completed_at:
                try:
                    completed_at = datetime.fromisoformat(completed_at).strftime("%Y-%m-%d")
                except (ValueError, TypeError):
                    pass
            lines.append(f"  {g['goals']}  (completed {completed_at})")
            schedule = g.get("refresh_schedule", [])
            idx = g.get("refresh_index", 0)
            if schedule:
                remaining = schedule[idx:]
                if remaining:
                    lines.append(f"    refresh reminders: {', '.join(remaining)}")
    if removed_goals:
        lines.append("Removed")
        for g in removed_goals:
            lines.append(f"  {g['goals']}")
    if not goals:
        lines.append("  no goals set")
    lines.append("")

    notes = db.get("notes", [])
    lines.append(f"TRAINING NOTES ({len(notes)} total)")
    lines.append("")

    if notes:
        for note in reversed(notes):
            date_str = note.get("date", "")
            time_str = note.get("time", "")
            day_str = note.get("day", "")
            header = f"{date_str} ({day_str})"
            if time_str:
                header += f" {time_str}"
            lines.append(header)
            lines.append(note.get("text", ""))
            techs = note.get("techniques", [])
            if techs:
                lines.append(f"  techniques: {', '.join(techs)}")
            lines.append("")
    else:
        lines.append("  no notes yet")
        lines.append("")

    active_drill = db.get("active_drill")
    lines.append("CURRENT FOCUS")
    lines.append("")

    if active_drill:
        lines.append(f"  {active_drill.get('technique', '')}")
        lines.append(f"  started {active_drill.get('start_date', '')[:10]}")
        lines.append(f"  ends {active_drill.get('end_date', '')[:10]}")
        lines.append(f"  video: {active_drill.get('video_url', '')}")
    else:
        lines.append("  no focus set")
    lines.append("")

    drill_history = db.get("drill_queue", [])
    if drill_history:
        lines.append(f"FOCUS HISTORY ({len(drill_history)} techniques)")
        lines.append("")
        for d in reversed(drill_history):
            outcome = d.get("outcome", "stopped")
            lines.append(f"  {d.get('technique', '?')} ({outcome}, {d.get('finished_at', '')[:10]})")
        lines.append("")

    training_log = db.get("training_log", [])
    if training_log:
        days_trained = 0
        for e in training_log:
            if e.get("trained"):
                days_trained += 1
        days_rest = len(training_log) - days_trained

        lines.append(f"TRAINING LOG ({len(training_log)} check-ins)")
        lines.append("")
        lines.append(f"  trained: {days_trained} days")
        lines.append(f"  rest: {days_rest} days")
        lines.append("")
        for entry in reversed(training_log[-30:]):
            if entry.get("trained"):
                status = "trained"
            else:
                status = "rest"
            lines.append(f"  {entry.get('date', '?')} {status}")
        if len(training_log) > 30:
            lines.append(f"  ...and {len(training_log) - 30} more")
        lines.append("")

    toolbox = db.get("toolbox", [])
    if toolbox:
        lines.append(f"TOOLBOX ({len(toolbox)} techniques you know)")
        lines.append("")

        by_category = {}
        for entry in toolbox:
            cat = entry.get("category", "other")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(entry.get("name", "?"))

        for cat_name, techs in by_category.items():
            lines.append(f"  {cat_name}")
            for name in techs:
                lines.append(f"    {name}")
        lines.append("")

    schedule = db.get("schedule", [])
    if schedule:
        lines.append("TRAINING SCHEDULE")
        lines.append("")
        for entry in schedule:
            lines.append(f"  {entry.get('day', '?')} at {entry.get('time', '?')}")
        lines.append("")

    return "\n".join(lines)
