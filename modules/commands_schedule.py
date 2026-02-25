from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .database import load_database, save_database
from .reminders import schedule_all_reminders
from .helpers import now_se

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_to_num = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    db = load_database(chat_id)
    schedule = db.get("schedule", [])

    message = "*your bjj schedule*\n\n"

    sorted_schedule = []
    if schedule:
        sorted_schedule = sorted(schedule, key=lambda e: (day_to_num.get(e["day"], 7), e["time"]))

    if sorted_schedule:
        for entry in sorted_schedule:
            message += f"  • *{entry['day']}* at {entry['time']}\n"
        message += "\n"
    else:
        message += "no training days set yet.\n\n"

    message += "tap a day to add a training session:"

    keyboard = []
    row = []
    for i, day in enumerate(days_of_week):
        row.append(InlineKeyboardButton(day[:3], callback_data=f"sched_day_{day}"))
        if len(row) == 4 or i == len(days_of_week) - 1:
            keyboard.append(row)
            row = []

    if sorted_schedule:
        for entry in sorted_schedule:
            idx = schedule.index(entry)
            keyboard.append([InlineKeyboardButton(
                f"✕ remove {entry['day']} {entry['time']}",
                callback_data=f"sched_rm_{idx}",
            )])
        keyboard.append([InlineKeyboardButton("🗑 clear entire schedule", callback_data="sched_clear")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)


async def schedule_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("sched_day_"):
        day = data[len("sched_day_"):]
        if day not in days_of_week:
            return

        context.user_data["sched_pending_day"] = day

        keyboard = []
        common_hours = [6, 7, 8, 9, 10, 11, 12, 17, 18, 19, 20, 21]
        common_times = []
        for h in common_hours:
            common_times.append(f"{h:02d}:00")
            common_times.append(f"{h:02d}:30")
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
            f"*{day}* pick your class time:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data.startswith("sched_time_"):
        time_str = data[len("sched_time_"):]
        day = context.user_data.pop("sched_pending_day", None)
        if not day:
            await query.edit_message_text("something went wrong. use /schedule again.")
            return

        chat_id = query.message.chat_id
        db = load_database(chat_id)

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
            "added_at": now_se().isoformat(),
        })
        save_database(chat_id, db)

        schedule_all_reminders(chat_id, context.application.job_queue)

        await query.edit_message_text(
            f"added *{day}* at {time_str} to your schedule.\n\n"
            f"you'll get a pretraining recap 1 hour before class.\n"
            f"use /schedule to see your full schedule.",
            parse_mode="Markdown",
        )

    elif data.startswith("sched_rm_"):
        idx_str = data[len("sched_rm_"):]
        try:
            idx = int(idx_str)
        except ValueError:
            return

        chat_id = query.message.chat_id
        db = load_database(chat_id)
        schedule = db.get("schedule", [])
        if 0 <= idx < len(schedule):
            removed = schedule.pop(idx)
            save_database(chat_id, db)
            schedule_all_reminders(chat_id, context.application.job_queue)
            await query.edit_message_text(
                f"removed *{removed['day']}* at {removed['time']}.\nuse /schedule to see updates.",
                parse_mode="Markdown",
            )
        else:
            await query.edit_message_text("entry not found. use /schedule.")

    elif data == "sched_clear":
        chat_id = query.message.chat_id
        db = load_database(chat_id)
        db["schedule"] = []
        save_database(chat_id, db)
        schedule_all_reminders(chat_id, context.application.job_queue)
        await query.edit_message_text("schedule cleared. use /schedule to set new training days.")

    elif data == "sched_cancel":
        context.user_data.pop("sched_pending_day", None)
        await query.edit_message_text("cancelled. use /schedule to try again.")
