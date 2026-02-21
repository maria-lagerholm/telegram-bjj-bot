from datetime import time
from telegram.ext import ContextTypes

from .database import load_database
from .helpers import get_current_week


async def send_daily_drill_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    database = load_database()
    
    if not database["drill_queue"]:
        return
    
    sorted_drills = sorted(
        database["drill_queue"],
        key=lambda drill: drill.get("drilled_count", 0)
    )
    
    top_three_drills = sorted_drills[:3]
    
    message = "*daily drill reminder*\n\nfocus on:\n\n"
    for drill in top_three_drills:
        count = drill.get("drilled_count", 0)
        message += f"  • *{drill['technique']}* ({count}x)\n"
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode="Markdown"
    )


async def send_weekly_goal_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    database = load_database()
    week = get_current_week()
    
    current_week_goals = []
    for goal in database["goals"]:
        if goal["week"] == week:
            current_week_goals.append(goal)
    
    if current_week_goals:
        message = f"*week {week}*\n\nyour goals:\n\n"
        for goal in current_week_goals:
            message += f"  • {goal['goals']}\n"
    else:
        message = f"*new week ({week})*\n\nset a goal with /goal!"
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode="Markdown"
    )


async def setup_reminders(update, context):
    chat_id = update.effective_chat.id
    job_queue = context.application.job_queue
    
    drill_reminder_name = f"drill_reminder_{chat_id}"
    existing_drill_jobs = job_queue.get_jobs_by_name(drill_reminder_name)
    for job in existing_drill_jobs:
        job.schedule_removal()
    
    goal_reminder_name = f"goal_reminder_{chat_id}"
    existing_goal_jobs = job_queue.get_jobs_by_name(goal_reminder_name)
    for job in existing_goal_jobs:
        job.schedule_removal()
    
    job_queue.run_daily(
        send_daily_drill_reminder,
        time=time(hour=9, minute=0),
        chat_id=chat_id,
        name=drill_reminder_name,
    )
    
    job_queue.run_daily(
        send_weekly_goal_reminder,
        time=time(hour=8, minute=0),
        days=(0,),
        chat_id=chat_id,
        name=goal_reminder_name,
    )
