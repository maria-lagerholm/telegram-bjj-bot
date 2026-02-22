import os
import logging
from dotenv import load_dotenv
from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)

from modules.commands_basic import cancel_command, timeout_handler
from modules.commands_menu import (
    start_command,
    help_command,
    menu_callback,
    menucmd_callback,
)
from modules.commands_info import (
    mindset_command,
    habits_command,
    etiquette_command,
    dos_command,
    donts_command,
    scoring_command,
    illegal_command,
)
from modules.commands_techniques import (
    technique_command,
    technique_callback,
    toolbox_command,
)
from modules.commands_goals import (
    goal_start_conversation,
    goal_receive_text,
    goals_list_command,
    goal_action_callback,
    state_goal_setting,
)
from modules.commands_notes import (
    note_start_conversation,
    note_receive_text,
    note_goal_callback,
    notes_list_command,
    notes_page_callback,
    journal_manage_command,
    note_manage_callback,
    note_edit_receive,
    state_note_writing,
    state_note_editing,
)
from modules.commands_drills import (
    focus_command,
    focus_callback,
    stats_command,
)
from modules.commands_schedule import schedule_command, schedule_callback
from modules.commands_export import (
    export_command,
    export_callback,
    import_start_command,
    import_receive_file,
    state_import_waiting,
)
from modules.reminders import setup_reminders, checkin_callback
from modules.commands_reminders import reminders_command, reminder_time_callback
from modules.app_map import render_app_map
from modules.ai_chat import handle_chat_message

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def map_command(update, context):
    img_buf = render_app_map()
    await update.message.reply_photo(
        photo=img_buf,
        caption="here's how the bot is organized. tap /help to open the menu.",
    )


async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("note", "log a training note"),
        BotCommand("notes", "view my notes"),
        BotCommand("journal", "edit or delete notes"),
        BotCommand("goal", "set a goal"),
        BotCommand("goals", "view my goals"),
        BotCommand("focus", "current technique focus"),
        BotCommand("technique", "browse techniques"),
        BotCommand("schedule", "training schedule"),
        BotCommand("stats", "my progress"),
        BotCommand("help", "open menu"),
    ])


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token or token == "your-token-here":
        print("set TELEGRAM_BOT_TOKEN in .env")
        print("get one from @BotFather on Telegram")
        return

    app = Application.builder().token(token).post_init(post_init).build()

    cmd_fallback = MessageHandler(filters.COMMAND, cancel_command)

    goal_conversation = ConversationHandler(
        entry_points=[CommandHandler("goal", goal_start_conversation)],
        states={
            state_goal_setting: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, goal_receive_text)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(filters.ALL, timeout_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel_command), cmd_fallback],
        conversation_timeout=120,
    )

    note_conversation = ConversationHandler(
        entry_points=[CommandHandler("note", note_start_conversation)],
        states={
            state_note_writing: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, note_receive_text)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(filters.ALL, timeout_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel_command), cmd_fallback],
        conversation_timeout=120,
    )

    note_edit_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(note_manage_callback, pattern="^noteedit_")],
        states={
            state_note_editing: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, note_edit_receive)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(filters.ALL, timeout_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel_command), cmd_fallback],
        conversation_timeout=120,
    )

    import_conversation = ConversationHandler(
        entry_points=[CommandHandler("import", import_start_command)],
        states={
            state_import_waiting: [
                MessageHandler(filters.Document.ALL, import_receive_file)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(filters.ALL, timeout_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel_command), cmd_fallback],
        conversation_timeout=120,
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mindset", mindset_command))
    app.add_handler(CommandHandler("habits", habits_command))
    app.add_handler(CommandHandler("technique", technique_command))
    app.add_handler(CallbackQueryHandler(technique_callback, pattern="^tech"))
    app.add_handler(CommandHandler("etiquette", etiquette_command))
    app.add_handler(CommandHandler("dos", dos_command))
    app.add_handler(CommandHandler("donts", donts_command))
    app.add_handler(CommandHandler("scoring", scoring_command))
    app.add_handler(CommandHandler("illegal", illegal_command))
    app.add_handler(goal_conversation)
    app.add_handler(note_conversation)
    app.add_handler(note_edit_conversation)
    app.add_handler(import_conversation)

    app.add_handler(CommandHandler("focus", focus_command))
    app.add_handler(CommandHandler("drill", focus_command))
    app.add_handler(CommandHandler("goals", goals_list_command))
    app.add_handler(CommandHandler("notes", notes_list_command))
    app.add_handler(CommandHandler("journal", journal_manage_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("toolbox", toolbox_command))
    app.add_handler(CommandHandler("schedule", schedule_command))
    app.add_handler(CommandHandler("export", export_command))
    app.add_handler(CommandHandler("reminders", reminders_command))
    app.add_handler(CommandHandler("map", map_command))

    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(menucmd_callback, pattern="^menucmd_"))
    app.add_handler(CallbackQueryHandler(goal_action_callback, pattern="^goal_"))
    app.add_handler(CallbackQueryHandler(checkin_callback, pattern="^checkin_"))
    app.add_handler(CallbackQueryHandler(note_goal_callback, pattern="^notegoal_"))
    app.add_handler(CallbackQueryHandler(notes_page_callback, pattern="^notespage_"))
    app.add_handler(CallbackQueryHandler(note_manage_callback, pattern="^notedel_"))
    app.add_handler(CallbackQueryHandler(note_manage_callback, pattern="^notemanage_"))
    app.add_handler(CallbackQueryHandler(reminder_time_callback, pattern="^remtime_"))
    app.add_handler(CallbackQueryHandler(schedule_callback, pattern="^sched_"))
    app.add_handler(CallbackQueryHandler(export_callback, pattern="^export_"))
    app.add_handler(CallbackQueryHandler(focus_callback, pattern="^focus_"))

    # ai chat: catch plain text or voice messages (must be last)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chat_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_chat_message))

    app.add_handler(CommandHandler("start", setup_reminders), group=1)

    print("BJJ Bot running! Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
