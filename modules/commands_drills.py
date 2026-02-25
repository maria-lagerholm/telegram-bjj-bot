from datetime import timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .database import load_database, save_database
from .techniques_data import all_techniques
from .helpers import now_se


async def focus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    database = load_database(chat_id)
    active_drill = database.get("active_drill")

    if not active_drill:
        await update.message.reply_text(
            "*current focus*\n\n"
            "you have no focus technique set.\n\n"
            "use /technique to browse the library and pick one to focus on.",
            parse_mode="Markdown",
        )
        return

    start_date = active_drill.get("start_date", "")[:10]
    days_left = 0
    try:
        end_dt = datetime.fromisoformat(active_drill["end_date"])
        days_left = max(0, (end_dt - now_se()).days)
    except (ValueError, KeyError):
        pass

    message = (
        "*current focus*\n\n"
        f"*{active_drill['technique']}*\n"
        f"_{active_drill.get('description', '')}_\n\n"
        f"started: {start_date}\n"
        f"time left: {days_left} days\n\n"
        f"[watch tutorial]({active_drill.get('video_url', '')})"
    )

    keyboard = [
        [InlineKeyboardButton("✓ learned it, move to toolbox", callback_data="focus_totoolbox")],
        [InlineKeyboardButton("✕ stop focusing", callback_data="focus_stop")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)


async def focus_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    chat_id = query.message.chat_id
    database = load_database(chat_id)
    active_drill = database.get("active_drill")

    if data == "focus_totoolbox":
        if not active_drill:
            await query.edit_message_text("no active focus to move.")
            return

        toolbox = database.get("toolbox", [])
        key = active_drill.get("toolbox_key", "")
        already_in = False
        if key:
            for entry in toolbox:
                if entry["key"] == key:
                    already_in = True
                    break

        if key and not already_in:
            toolbox.append({
                "key": key,
                "name": active_drill["technique"],
                "category": active_drill.get("category", ""),
                "added_at": now_se().isoformat(),
            })

        database["drill_queue"].append({
            "technique": active_drill["technique"],
            "outcome": "toolbox",
            "finished_at": now_se().isoformat(),
        })

        database["active_drill"] = None
        save_database(chat_id, database)

        await query.edit_message_text(
            f"✓ *{active_drill['technique']}* moved to your toolbox!\n\n"
            "use /technique to pick a new focus or /toolbox to see what you know.",
            parse_mode="Markdown",
        )

    elif data == "focus_stop":
        if not active_drill:
            await query.edit_message_text("no active focus to stop.")
            return

        database["drill_queue"].append({
            "technique": active_drill["technique"],
            "outcome": "stopped",
            "finished_at": now_se().isoformat(),
        })

        database["active_drill"] = None
        save_database(chat_id, database)

        await query.edit_message_text(
            f"stopped focusing on *{active_drill['technique']}*.\n\n"
            "no worries, you can always come back to it later.\n"
            "use /technique to pick a new one.",
            parse_mode="Markdown",
        )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    database = load_database(chat_id)

    total_notes = len(database["notes"])

    active_goals = 0
    completed_goals = 0
    for g in database["goals"]:
        if g.get("status", "active") == "active":
            active_goals += 1
        elif g.get("status") == "completed":
            completed_goals += 1

    active_drill = database.get("active_drill")
    if active_drill:
        focus_text = active_drill["technique"]
    else:
        focus_text = "none"

    first_date = "n/a"
    this_week_notes = 0
    if database["notes"]:
        all_dates = set()
        for note in database["notes"]:
            all_dates.add(note["date"])
        first_date = sorted(all_dates)[0]

        seven_days_ago = (now_se() - timedelta(days=7)).strftime("%Y-%m-%d")
        for note in database["notes"]:
            if note["date"] >= seven_days_ago:
                this_week_notes += 1

    training_log = database.get("training_log", [])
    total_checkins = len(training_log)
    days_trained = 0
    for entry in training_log:
        if entry["trained"]:
            days_trained += 1
    days_rest = total_checkins - days_trained

    seven_days_ago_str = (now_se() - timedelta(days=7)).strftime("%Y-%m-%d")
    thirty_days_ago_str = (now_se() - timedelta(days=30)).strftime("%Y-%m-%d")
    week_trained = 0
    month_trained = 0
    for entry in training_log:
        if entry["trained"] and entry["date"] >= seven_days_ago_str:
            week_trained += 1
        if entry["trained"] and entry["date"] >= thirty_days_ago_str:
            month_trained += 1

    streak = 0
    current = now_se().date()
    trained_dates = []
    for entry in training_log:
        if entry["trained"]:
            trained_dates.append(entry["date"])
    trained_dates.sort(reverse=True)
    for date_str in trained_dates:
        log_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if log_date == current:
            streak += 1
            current = current - timedelta(days=1)
        else:
            break

    toolbox = database.get("toolbox", [])
    total_techniques = 0
    for cat in all_techniques.values():
        total_techniques += len(cat["items"])
    toolbox_count = len(toolbox)

    message = (
        "*training stats*\n\n"
        "*activity:*\n"
        f"  this week: *{week_trained}* sessions\n"
        f"  this month: *{month_trained}* sessions\n"
        f"  total trained: *{days_trained}* days\n"
        f"  rest days: *{days_rest}*\n"
    )

    if streak > 0:
        message += f"  🔥 streak: *{streak}* days\n"

    message += (
        f"\n*progress:*\n"
        f"  focus: *{focus_text}*\n"
        f"  goals: *{active_goals}* active, *{completed_goals}* completed\n"
        f"  toolbox: *{toolbox_count}/{total_techniques}* techniques\n"
        f"  notes: *{total_notes}* total, *{this_week_notes}* this week\n"
    )

    drill_history = database.get("drill_queue", [])
    learned = 0
    for d in drill_history:
        if d.get("outcome") == "toolbox":
            learned += 1
    if drill_history:
        message += f"  past focuses: *{len(drill_history)}* ({learned} moved to toolbox)\n"

    if database["notes"]:
        message += f"\n_training since {first_date}_"

    await update.message.reply_text(message, parse_mode="Markdown")
