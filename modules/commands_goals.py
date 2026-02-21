from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from .database import load_database, save_database
from .helpers import get_current_week

state_goal_setting = 1


async def goal_start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    week = get_current_week()
    prompt_message = (
        f"*goal for {week}*\n\n"
        "examples:\n"
        "• _keep elbows tight_\n"
        "• _hit 3 hip escapes per roll_\n"
        "• _survive side control 30s_\n\n"
        "/cancel to abort"
    )
    await update.message.reply_text(prompt_message, parse_mode="Markdown")
    return state_goal_setting


async def goal_receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = load_database()
    week = get_current_week()
    goal_text = update.message.text.strip()
    
    new_goal = {
        "week": week,
        "goals": goal_text,
        "created_at": datetime.now().isoformat(),
    }
    
    database["goals"].append(new_goal)
    save_database(database)
    
    confirmation_message = f"goal saved for {week}:\n\n_{goal_text}_"
    await update.message.reply_text(confirmation_message, parse_mode="Markdown")
    return ConversationHandler.END


async def goals_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = load_database()
    
    if not database["goals"]:
        await update.message.reply_text("no goals yet. use /goal!")
        return
    
    week = get_current_week()
    current_week_goals = []
    past_goals = []
    
    for goal in database["goals"]:
        if goal["week"] == week:
            current_week_goals.append(goal)
        else:
            past_goals.append(goal)
    
    message = "*goals*\n\n"
    
    if current_week_goals:
        message += f"*this week ({week}):*\n"
        for goal in current_week_goals:
            message += f"  • {goal['goals']}\n"
        message += "\n"
    
    if past_goals:
        message += "*previous:*\n"
        last_ten_goals = past_goals[-10:]
        for goal in reversed(last_ten_goals):
            message += f"  _{goal['week']}_: {goal['goals']}\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")
