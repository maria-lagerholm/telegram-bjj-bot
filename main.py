import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)

from modules.commands_basic import (
    start_command,
    help_command,
    mindset_command,
    habits_command,
    technique_command,
    technique_callback,
    toolbox_command,
    etiquette_command,
    dos_command,
    donts_command,
    scoring_command,
    illegal_command,
    cancel_command,
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
    state_note_writing,
)
from modules.commands_drills import (
    drills_list_command,
    drilled_command,
    stats_command,
    stop_drill_callback,
)
from modules.commands_schedule import schedule_command, schedule_callback
from modules.commands_export import export_command, export_callback
from modules.reminders import setup_reminders, checkin_callback

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token or token == "your-token-here":
        print("=" * 50)
        print("ERROR: Set TELEGRAM_BOT_TOKEN in .env")
        print("Get one from @BotFather on Telegram")
        print("=" * 50)
        return
    
    app = Application.builder().token(token).build()
    
    goal_conversation = ConversationHandler(
        entry_points=[CommandHandler("goal", goal_start_conversation)],
        states={
            state_goal_setting: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, goal_receive_text)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    
    note_conversation = ConversationHandler(
        entry_points=[CommandHandler("note", note_start_conversation)],
        states={
            state_note_writing: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, note_receive_text)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
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
    
    # Both /drill and /drills now show the active 2-week drill
    app.add_handler(CommandHandler("drill", drills_list_command))
    app.add_handler(CommandHandler("drills", drills_list_command))
    app.add_handler(CommandHandler("goals", goals_list_command))
    app.add_handler(CommandHandler("notes", notes_list_command))
    app.add_handler(CommandHandler("drilled", drilled_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("toolbox", toolbox_command))
    app.add_handler(CommandHandler("schedule", schedule_command))
    app.add_handler(CommandHandler("export", export_command))
    
    app.add_handler(CallbackQueryHandler(goal_action_callback, pattern="^goal_"))
    app.add_handler(CallbackQueryHandler(checkin_callback, pattern="^checkin_"))
    app.add_handler(CallbackQueryHandler(note_goal_callback, pattern="^notegoal_"))
    app.add_handler(CallbackQueryHandler(schedule_callback, pattern="^sched_"))
    app.add_handler(CallbackQueryHandler(export_callback, pattern="^export_"))
    app.add_handler(CallbackQueryHandler(stop_drill_callback, pattern="^stop_drill$"))
    app.add_handler(CommandHandler("start", setup_reminders), group=1)
    
    print("BJJ Bot running! Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
