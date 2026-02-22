from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("cancelled.")
    return ConversationHandler.END
