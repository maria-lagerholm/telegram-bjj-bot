from datetime import datetime, time, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from .database import load_database, save_database
from .reminders import schedule_pretraining_jobs

state_schedule_day = 10
state_schedule_time = 11

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
# python weekday(): Monday=0 … Sunday=6
DAY_TO_NUM = {d: i for i, d in enumerate(DAYS_OF_WEEK)}


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current schedule and offer to add/clear."""
    db = load_database()
    schedule = db.get("schedule", [])

    message = "*your bjj schedule*\n\n"

    if schedule:
        for entry in sorted(schedule, key=lambda e: (DAY_TO_NUM.get(e["day"], 7), e["time"])):
            message += f"  • *{entry['day']}* at {entry['time']}\n"
        message += "\n"
    else:
        message += "no training days set yet.\n\n"

    message += "tap a day to add a training session:"

    keyboard = []
    row = []
    for i, day in enumerate(DAYS_OF_WEEK):
        row.append(InlineKeyboardButton(day[:3], callback_data=f"sched_day_{day}"))
        if len(row) == 4 or i == len(DAYS_OF_WEEK) - 1:
            keyboard.append(row)
            row = []

    if schedule:
        keyboard.append([InlineKeyboardButton("🗑 clear entire schedule", callback_data="sched_clear")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)


async def schedule_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle schedule-related inline buttons."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("sched_day_"):
        day = data[len("sched_day_"):]
        if day not in DAYS_OF_WEEK:
            return

        context.user_data["sched_pending_day"] = day

        # offer common class times
        keyboard = []
        common_times = ["06:00", "07:00", "08:00", "09:00", "10:00",
                        "11:00", "12:00", "17:00", "18:00", "19:00", "20:00", "21:00"]
        row = []
        for t in common_times:
            row.append(InlineKeyboardButton(t, callback_data=f"sched_time_{t}"))
            if len(row) == 4:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        keyboard.append([InlineKeyboardButton("« cancel", callback_data="sched_cancel")])

        await query.edit_message_text(
            f"*{day}* — pick your class time:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data.startswith("sched_time_"):
        time_str = data[len("sched_time_"):]
        day = context.user_data.pop("sched_pending_day", None)
        if not day:
            await query.edit_message_text("something went wrong. use /schedule again.")
            return

        db = load_database()

        # avoid duplicates
        for entry in db["schedule"]:
            if entry["day"] == day and entry["time"] == time_str:
                await query.edit_message_text(
                    f"you already have *{day}* at {time_str} on your schedule!",
                    parse_mode="Markdown",
                )
                return

        db["schedule"].append({
            "day": day,
            "time": time_str,
            "added_at": datetime.now().isoformat(),
        })
        save_database(db)

        # reschedule pre-training reminder jobs
        chat_id = query.message.chat_id
        schedule_pretraining_jobs(context.application.job_queue, chat_id)

        await query.edit_message_text(
            f"added *{day}* at {time_str} to your schedule.\n\n"
            f"you'll get a pre-training recap 1 hour before class.\n"
            f"use /schedule to see your full schedule.",
            parse_mode="Markdown",
        )

    elif data.startswith("sched_rm_"):
        # remove a single entry
        idx_str = data[len("sched_rm_"):]
        try:
            idx = int(idx_str)
        except ValueError:
            return

        db = load_database()
        schedule = db.get("schedule", [])
        if 0 <= idx < len(schedule):
            removed = schedule.pop(idx)
            save_database(db)
            chat_id = query.message.chat_id
            schedule_pretraining_jobs(context.application.job_queue, chat_id)
            await query.edit_message_text(
                f"removed *{removed['day']}* at {removed['time']}.\nuse /schedule to see updates.",
                parse_mode="Markdown",
            )
        else:
            await query.edit_message_text("entry not found. use /schedule.")

    elif data == "sched_clear":
        db = load_database()
        db["schedule"] = []
        save_database(db)
        chat_id = query.message.chat_id
        schedule_pretraining_jobs(context.application.job_queue, chat_id)
        await query.edit_message_text("schedule cleared. use /schedule to set new training days.")

    elif data == "sched_cancel":
        context.user_data.pop("sched_pending_day", None)
        await query.edit_message_text("cancelled. use /schedule to try again.")
