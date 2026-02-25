from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .database import load_database, save_database
from .reminders import schedule_all_reminders


async def reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    db = load_database(chat_id)
    schedule = db.get("schedule", [])
    disabled = db.get("reminders_disabled", False)

    if not schedule:
        await update.message.reply_text(
            "no training schedule set yet. use /schedule first, "
            "reminders are created automatically from your schedule."
        )
        return

    status = "off" if disabled else "on"
    message = f"*your reminders* ({status})\n\n"
    message += "reminders are based on your /schedule:\n\n"

    for entry in schedule:
        message += f"  {entry['day']} at {entry['time']}\n"
        message += f"    1h before: pretraining recap\n"
        message += f"    1h after: note reminder\n\n"

    message += "refresh reminders for completed goals run on mondays.\n"

    if disabled:
        keyboard = [[InlineKeyboardButton("turn reminders on", callback_data="rem_toggle_on")]]
    else:
        keyboard = [[InlineKeyboardButton("turn reminders off", callback_data="rem_toggle_off")]]

    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def reminder_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    chat_id = query.message.chat_id
    db = load_database(chat_id)

    if data == "rem_toggle_off":
        db["reminders_disabled"] = True
        save_database(chat_id, db)
        schedule_all_reminders(chat_id, context.application.job_queue)
        await query.edit_message_text("reminders turned off. use /reminders to turn them back on.")

    elif data == "rem_toggle_on":
        db["reminders_disabled"] = False
        save_database(chat_id, db)
        schedule_all_reminders(chat_id, context.application.job_queue)
        await query.edit_message_text("reminders turned on. use /reminders to see details.")
