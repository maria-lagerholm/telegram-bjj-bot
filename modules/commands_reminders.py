from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .database import load_database, save_database
from .reminders import schedule_all_reminders

reminder_labels = {
    "daily_checkin": "daily check in (did you train?)",
    "focus_reminder": "daily focus reminder",
    "goal_reminder": "weekly goal reminder (Monday)",
    "refresh_reminder": "spaced repetition refresh",
}

reminder_defaults = {
    "daily_checkin": "20:00",
    "focus_reminder": "09:00",
    "goal_reminder": "08:00",
    "refresh_reminder": "10:00",
}


async def reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    db = load_database(chat_id)
    times = db.get("reminder_times", reminder_defaults)

    message = "*your reminder times*\n\n"
    for key, label in reminder_labels.items():
        current = times.get(key, reminder_defaults[key])
        message += f"  • {label}: *{current}*\n"
    message += "\ntap a reminder to change its time:"

    keyboard = []
    for key, label in reminder_labels.items():
        short_label = label[:30]
        keyboard.append([
            InlineKeyboardButton(
                f"change: {short_label}",
                callback_data=f"remtime_pick_{key}",
            )
        ])

    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def reminder_time_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("remtime_pick_"):
        key = data[len("remtime_pick_"):]
        if key not in reminder_labels:
            return

        context.user_data["remtime_pending_key"] = key
        label = reminder_labels[key]

        hours = list(range(6, 23))
        times_list = []
        for h in hours:
            times_list.append(f"{h:02d}:00")
            times_list.append(f"{h:02d}:30")

        keyboard = []
        row = []
        for t in times_list:
            row.append(InlineKeyboardButton(t, callback_data=f"remtime_set_{t}"))
            if len(row) == 4:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("cancel", callback_data="remtime_cancel")])

        await query.edit_message_text(
            f"*{label}*\n\npick a new time:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data.startswith("remtime_set_"):
        time_str = data[len("remtime_set_"):]
        key = context.user_data.pop("remtime_pending_key", None)
        if not key or key not in reminder_labels:
            await query.edit_message_text("something went wrong. use /reminders again.")
            return

        chat_id = query.message.chat_id
        db = load_database(chat_id)
        if "reminder_times" not in db:
            db["reminder_times"] = dict(reminder_defaults)
        db["reminder_times"][key] = time_str
        save_database(chat_id, db)

        schedule_all_reminders(chat_id, context.application.job_queue)

        label = reminder_labels[key]
        await query.edit_message_text(
            f"*{label}* set to *{time_str}*\n\n"
            "use /reminders to see all your reminder times.",
            parse_mode="Markdown",
        )

    elif data == "remtime_cancel":
        context.user_data.pop("remtime_pending_key", None)
        await query.edit_message_text("cancelled. use /reminders to try again.")
