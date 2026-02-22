from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("cancelled.")
    return ConversationHandler.END


async def timeout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update and update.effective_message:
        await update.effective_message.reply_text("timed out. start again when ready.")
    return ConversationHandler.END
