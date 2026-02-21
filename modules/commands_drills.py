from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .database import load_database, save_database


async def focus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the user's current focus technique."""
    database = load_database()
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
    end_date = active_drill.get("end_date", "")[:10]
    days_left = 0
    try:
        end_dt = datetime.fromisoformat(active_drill["end_date"])
        days_left = max(0, (end_dt - datetime.now()).days)
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
    """Handle focus-related inline buttons."""
    query = update.callback_query
    await query.answer()
    data = query.data

    database = load_database()
    active_drill = database.get("active_drill")

    if data == "focus_totoolbox":
        if not active_drill:
            await query.edit_message_text("no active focus to move.")
            return

        # add to toolbox
        toolbox = database.get("toolbox", [])
        key = active_drill.get("toolbox_key", "")
        already_in = any(e["key"] == key for e in toolbox) if key else False

        if key and not already_in:
            toolbox.append({
                "key": key,
                "name": active_drill["technique"],
                "category": active_drill.get("category", ""),
                "added_at": datetime.now().isoformat(),
            })

        # save to history
        database["drill_queue"].append({
            "technique": active_drill["technique"],
            "outcome": "toolbox",
            "finished_at": datetime.now().isoformat(),
        })

        database["active_drill"] = None
        save_database(database)

        await query.edit_message_text(
            f"✓ *{active_drill['technique']}* moved to your toolbox!\n\n"
            "use /technique to pick a new focus or /toolbox to see what you know.",
            parse_mode="Markdown",
        )

    elif data == "focus_stop":
        if not active_drill:
            await query.edit_message_text("no active focus to stop.")
            return

        # save to history
        database["drill_queue"].append({
            "technique": active_drill["technique"],
            "outcome": "stopped",
            "finished_at": datetime.now().isoformat(),
        })

        database["active_drill"] = None
        save_database(database)

        await query.edit_message_text(
            f"stopped focusing on *{active_drill['technique']}*.\n\n"
            "no worries, you can always come back to it later.\n"
            "use /technique to pick a new one.",
            parse_mode="Markdown",
        )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = load_database()

    total_notes = len(database["notes"])
    total_goals = len(database["goals"])
    active_goals = sum(1 for g in database["goals"] if g.get("status", "active") == "active")
    completed_goals = sum(1 for g in database["goals"] if g.get("status") == "completed")

    active_drill = database.get("active_drill")
    focus_text = active_drill["technique"] if active_drill else "none"

    if database["notes"]:
        all_dates = [note["date"] for note in database["notes"]]
        unique_dates = sorted(set(all_dates))
        first_date = unique_dates[0]

        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        this_week_notes = sum(1 for note in database["notes"] if note["date"] >= seven_days_ago)
    else:
        first_date = "n/a"
        this_week_notes = 0

    # training check-in stats
    training_log = database.get("training_log", [])
    total_checkins = len(training_log)
    days_trained = sum(1 for e in training_log if e["trained"])
    days_rest = total_checkins - days_trained

    seven_days_ago_str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    thirty_days_ago_str = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    week_trained = sum(1 for e in training_log if e["trained"] and e["date"] >= seven_days_ago_str)
    month_trained = sum(1 for e in training_log if e["trained"] and e["date"] >= thirty_days_ago_str)

    # current streak
    streak = 0
    current = datetime.now().date()
    trained_dates = sorted(
        [e["date"] for e in training_log if e["trained"]],
        reverse=True,
    )
    for date_str in trained_dates:
        log_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if log_date == current:
            streak += 1
            current = current - timedelta(days=1)
        else:
            break

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

    # toolbox stats
    toolbox = database.get("toolbox", [])
    from .techniques_data import TECHNIQUES
    total_techniques = sum(len(cat["items"]) for cat in TECHNIQUES.values())
    toolbox_count = len(toolbox)

    message += (
        f"\n*progress:*\n"
        f"  focus: *{focus_text}*\n"
        f"  goals: *{active_goals}* active, *{completed_goals}* completed\n"
        f"  toolbox: *{toolbox_count}/{total_techniques}* techniques\n"
        f"  notes: *{total_notes}* total, *{this_week_notes}* this week\n"
    )

    # past focuses
    drill_history = database.get("drill_queue", [])
    learned = sum(1 for d in drill_history if d.get("outcome") == "toolbox")
    if drill_history:
        message += f"  past focuses: *{len(drill_history)}* ({learned} moved to toolbox)\n"

    if database["notes"]:
        message += f"\n_training since {first_date}_"

    await update.message.reply_text(message, parse_mode="Markdown")
