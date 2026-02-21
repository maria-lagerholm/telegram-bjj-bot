import io
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .database import load_database


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Offer export format options."""
    keyboard = [
        [InlineKeyboardButton("📄 readable .txt", callback_data="export_txt")],
        [InlineKeyboardButton("💾 full backup .json", callback_data="export_json")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "*export your data*\n\n"
        "choose a format:\n"
        "• *txt* — human-readable summary of all your data\n"
        "• *json* — full raw backup (can be re-imported later)\n\n"
        "_the file will be sent right here in chat. "
        "you can then save it to google drive, email it, or store it anywhere._",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def export_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle export format selection."""
    query = update.callback_query
    await query.answer()
    data = query.data

    database = load_database()

    if data == "export_txt":
        content = _build_txt_export(database)
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


def _build_txt_export(db: dict) -> str:
    """Build a human-readable text export of all user data."""
    lines = []
    now = datetime.now()
    lines.append("=" * 50)
    lines.append("BJJ TRAINING DATA EXPORT")
    lines.append(f"exported: {now.strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 50)
    lines.append("")

    # --- GOALS ---
    goals = db.get("goals", [])
    active_goals = [g for g in goals if g.get("status", "active") == "active"]
    completed_goals = [g for g in goals if g.get("status") == "completed"]
    removed_goals = [g for g in goals if g.get("status") == "removed"]

    lines.append("-" * 50)
    lines.append("GOALS")
    lines.append("-" * 50)

    if active_goals:
        lines.append("")
        lines.append("Active:")
        for g in active_goals:
            week = g.get("week", "")
            lines.append(f"  • {g['goals']}  ({week})")
    if completed_goals:
        lines.append("")
        lines.append("Completed:")
        for g in completed_goals:
            completed_at = g.get("completed_at", "")
            if completed_at:
                try:
                    completed_at = datetime.fromisoformat(completed_at).strftime("%Y-%m-%d")
                except (ValueError, TypeError):
                    pass
            lines.append(f"  ✓ {g['goals']}  (completed {completed_at})")
            # show refresh schedule if any
            schedule = g.get("refresh_schedule", [])
            idx = g.get("refresh_index", 0)
            if schedule:
                remaining = schedule[idx:]
                if remaining:
                    lines.append(f"    refresh reminders: {', '.join(remaining)}")
    if removed_goals:
        lines.append("")
        lines.append("Removed:")
        for g in removed_goals:
            lines.append(f"  ✕ {g['goals']}")
    if not goals:
        lines.append("  (no goals set)")
    lines.append("")

    # --- TRAINING NOTES ---
    notes = db.get("notes", [])
    lines.append("-" * 50)
    lines.append(f"TRAINING NOTES ({len(notes)} total)")
    lines.append("-" * 50)

    if notes:
        for note in reversed(notes):
            date_str = note.get("date", "")
            time_str = note.get("time", "")
            day_str = note.get("day", "")
            header = f"{date_str} ({day_str})"
            if time_str:
                header += f" {time_str}"
            lines.append("")
            lines.append(header)
            lines.append(note.get("text", ""))
            techs = note.get("techniques", [])
            if techs:
                lines.append(f"  detected techniques: {', '.join(techs)}")
    else:
        lines.append("  (no notes yet)")
    lines.append("")

    # --- ACTIVE DRILL ---
    active_drill = db.get("active_drill")
    lines.append("-" * 50)
    lines.append("ACTIVE DRILL")
    lines.append("-" * 50)

    if active_drill:
        lines.append(f"  technique: {active_drill.get('technique', '')}")
        lines.append(f"  reps: {active_drill.get('drilled_count', 0)}")
        lines.append(f"  started: {active_drill.get('start_date', '')[:10]}")
        lines.append(f"  ends: {active_drill.get('end_date', '')[:10]}")
        lines.append(f"  video: {active_drill.get('video_url', '')}")
    else:
        lines.append("  (no active drill)")
    lines.append("")

    # --- DRILL HISTORY ---
    drill_history = db.get("drill_queue", [])
    if drill_history:
        lines.append("-" * 50)
        lines.append(f"DRILL HISTORY ({len(drill_history)} drills)")
        lines.append("-" * 50)
        for d in reversed(drill_history):
            lines.append(f"  • {d.get('technique', '?')} — {d.get('drilled_count', 0)} reps (finished {d.get('finished_at', '')[:10]})")
        lines.append("")

    # --- TRAINING LOG ---
    training_log = db.get("training_log", [])
    if training_log:
        days_trained = sum(1 for e in training_log if e.get("trained"))
        days_rest = len(training_log) - days_trained

        lines.append("-" * 50)
        lines.append(f"TRAINING LOG ({len(training_log)} check-ins)")
        lines.append("-" * 50)
        lines.append(f"  trained: {days_trained} days")
        lines.append(f"  rest: {days_rest} days")
        lines.append("")
        lines.append("  recent:")
        for entry in reversed(training_log[-30:]):
            status = "✓ trained" if entry.get("trained") else "— rest"
            lines.append(f"    {entry.get('date', '?')} {status}")
        if len(training_log) > 30:
            lines.append(f"    …and {len(training_log) - 30} more")
        lines.append("")

    # --- TOOLBOX ---
    toolbox = db.get("toolbox", [])
    if toolbox:
        lines.append("-" * 50)
        lines.append(f"TOOLBOX ({len(toolbox)} techniques you know)")
        lines.append("-" * 50)

        by_category = {}
        for entry in toolbox:
            cat = entry.get("category", "other")
            by_category.setdefault(cat, []).append(entry.get("name", "?"))

        for cat_name, techs in by_category.items():
            lines.append(f"  {cat_name}:")
            for name in techs:
                lines.append(f"    ✓ {name}")
        lines.append("")

    # --- SCHEDULE ---
    schedule = db.get("schedule", [])
    if schedule:
        lines.append("-" * 50)
        lines.append("TRAINING SCHEDULE")
        lines.append("-" * 50)
        for entry in schedule:
            lines.append(f"  • {entry.get('day', '?')} at {entry.get('time', '?')}")
        lines.append("")

    lines.append("=" * 50)
    lines.append("END OF EXPORT")
    lines.append("=" * 50)

    return "\n".join(lines)
