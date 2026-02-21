from datetime import datetime, time, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .database import load_database, save_database
from .helpers import get_current_week


async def send_daily_focus_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    database = load_database()

    active_drill = database.get("active_drill")
    if not active_drill:
        return

    days_left = 0
    try:
        end_dt = datetime.fromisoformat(active_drill["end_date"])
        days_left = max(0, (end_dt - datetime.now()).days)
    except (ValueError, KeyError):
        pass

    message = (
        "*focus reminder*\n\n"
        f"you're working on: *{active_drill['technique']}*\n"
        f"time left: {days_left} days\n\n"
        f"_{active_drill.get('description', '')}_\n\n"
        f"[watch tutorial]({active_drill.get('video_url', '')})"
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode="Markdown",
    )


async def send_weekly_goal_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    database = load_database()
    week = get_current_week()
    
    active_goals = [
        g for g in database["goals"]
        if g.get("status", "active") == "active"
    ]
    
    if active_goals:
        message = f"*week {week}*\n\nyour active goals:\n\n"
        for goal in active_goals:
            message += f"  • {goal['goals']}\n"
    else:
        message = f"*new week ({week})*\n\nset a goal with /goal!"
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode="Markdown"
    )


async def send_daily_checkin(context: ContextTypes.DEFAULT_TYPE):
    """Ask the user if they trained today."""
    chat_id = context.job.chat_id
    today = datetime.now().strftime("%Y-%m-%d")

    # don't ask twice on the same day
    database = load_database()
    for entry in database.get("training_log", []):
        if entry["date"] == today:
            return

    keyboard = [
        [
            InlineKeyboardButton("yes 🤙", callback_data="checkin_yes"),
            InlineKeyboardButton("no", callback_data="checkin_no"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text="did you train bjj today?",
        reply_markup=reply_markup,
    )


async def checkin_callback(context_or_update, context=None):
    """Handle yes/no response to the daily check-in."""
    # this is called as a CallbackQueryHandler, so first arg is Update
    update = context_or_update
    query = update.callback_query
    await query.answer()

    trained = query.data == "checkin_yes"
    today = datetime.now().strftime("%Y-%m-%d")
    day_name = datetime.now().strftime("%A")

    database = load_database()

    # prevent duplicate entries for the same day
    for entry in database.get("training_log", []):
        if entry["date"] == today:
            status = "trained" if entry["trained"] else "rest day"
            await query.edit_message_text(f"already logged today as *{status}*.", parse_mode="Markdown")
            return

    database["training_log"].append({
        "date": today,
        "day": day_name,
        "trained": trained,
        "logged_at": datetime.now().isoformat(),
    })
    save_database(database)

    if trained:
        # count current streak
        streak = _get_current_streak(database["training_log"])
        msg = f"nice! logged as a training day."
        if streak > 1:
            msg += f"\n🔥 {streak}-day streak!"
        msg += "\n\nuse /note to log what you learned."
    else:
        msg = "rest day logged. recovery is part of the game 💪"

    await query.edit_message_text(msg)


def _get_current_streak(training_log: list) -> int:
    """Count consecutive training days ending today."""
    trained_dates = sorted(
        [e["date"] for e in training_log if e["trained"]],
        reverse=True,
    )
    if not trained_dates:
        return 0

    streak = 0
    current = datetime.now().date()
    for date_str in trained_dates:
        log_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if log_date == current:
            streak += 1
            current = current - timedelta(days=1)
        else:
            break
    return streak


async def send_refresh_reminders(context: ContextTypes.DEFAULT_TYPE):
    """Check for completed goals that are due for a spaced repetition refresh."""
    chat_id = context.job.chat_id
    database = load_database()
    today = datetime.now().strftime("%Y-%m-%d")

    for goal in database.get("goals", []):
        if goal.get("status") != "completed":
            continue

        schedule = goal.get("refresh_schedule", [])
        idx = goal.get("refresh_index", 0)

        if idx >= len(schedule):
            continue  # all refreshes done

        if schedule[idx] <= today:
            interval_label = ["1 month", "2 months", "3 months", "6 months"]
            label = interval_label[idx] if idx < len(interval_label) else f"reminder {idx + 1}"

            keyboard = [[
                InlineKeyboardButton(
                    "got it, refreshed 💪",
                    callback_data=f"goal_refresh_{goal['id']}",
                )
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"*refresh reminder ({label})*\n\n"
                    f"remember this goal?\n"
                    f"*{goal['goals']}*\n\n"
                    f"_take a moment to drill or think about this today_"
                ),
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )


async def send_pretraining_recap(context: ContextTypes.DEFAULT_TYPE):
    """1 hour before a scheduled class: send last session notes + active goals."""
    chat_id = context.job.chat_id
    database = load_database()

    # --- last session note ---
    notes = database.get("notes", [])
    last_note = notes[-1] if notes else None

    # --- active goals (max 3) ---
    active_goals = [
        g for g in database.get("goals", [])
        if g.get("status", "active") == "active"
    ]

    # --- active drill ---
    active_drill = database.get("active_drill")

    # build message
    message = "*pre-training recap* 🥋\n\n"

    if active_goals:
        message += "*your goals:*\n"
        for g in active_goals[:3]:
            message += f"  • {g['goals']}\n"
        message += "\n"

    if last_note:
        message += f"*last session ({last_note['date']}):*\n"
        preview = last_note["text"][:300]
        if len(last_note["text"]) > 300:
            preview += "…"
        message += f"{preview}\n\n"

    if active_drill:
        message += (
            f"*focus technique:* {active_drill['technique']}\n"
            f"_{active_drill.get('description', '')}_\n\n"
        )

    if not active_goals and not last_note and not active_drill:
        message += "no notes or goals yet, focus on learning today!\n"

    message += "_have a great session! use /note afterwards to log what you learned._"

    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode="Markdown",
    )


def schedule_pretraining_jobs(job_queue, chat_id: int):
    """(Re)schedule pre-training recap jobs based on the user's saved schedule.

    Call this on /start and whenever the schedule changes.
    """
    # clear any existing pre-training jobs for this chat
    prefix = f"pretrain_{chat_id}_"
    for job in job_queue.jobs():
        if job.name and job.name.startswith(prefix):
            job.schedule_removal()

    database = load_database()
    schedule = database.get("schedule", [])

    day_map = {
        "Monday": 0, "Tuesday": 1, "Wednesday": 2,
        "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6,
    }

    for entry in schedule:
        day_name = entry["day"]
        time_str = entry["time"]  # e.g. "18:00"

        day_num = day_map.get(day_name)
        if day_num is None:
            continue

        try:
            parts = time_str.split(":")
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
        except (ValueError, IndexError):
            continue

        # 1 hour before class
        reminder_dt = datetime.combine(datetime.today(), time(hour=hour, minute=minute)) - timedelta(hours=1)
        remind_hour = reminder_dt.hour
        remind_minute = reminder_dt.minute

        job_name = f"pretrain_{chat_id}_{day_name}_{time_str}"

        job_queue.run_daily(
            send_pretraining_recap,
            time=time(hour=remind_hour, minute=remind_minute),
            days=(day_num,),
            chat_id=chat_id,
            name=job_name,
        )


async def setup_reminders(update, context):
    chat_id = update.effective_chat.id
    job_queue = context.application.job_queue
    
    focus_reminder_name = f"focus_reminder_{chat_id}"
    existing_focus_jobs = job_queue.get_jobs_by_name(focus_reminder_name)
    for job in existing_focus_jobs:
        job.schedule_removal()
    
    goal_reminder_name = f"goal_reminder_{chat_id}"
    existing_goal_jobs = job_queue.get_jobs_by_name(goal_reminder_name)
    for job in existing_goal_jobs:
        job.schedule_removal()

    checkin_name = f"checkin_{chat_id}"
    existing_checkin_jobs = job_queue.get_jobs_by_name(checkin_name)
    for job in existing_checkin_jobs:
        job.schedule_removal()
    
    job_queue.run_daily(
        send_daily_focus_reminder,
        time=time(hour=9, minute=0),
        chat_id=chat_id,
        name=focus_reminder_name,
    )
    
    job_queue.run_daily(
        send_weekly_goal_reminder,
        time=time(hour=8, minute=0),
        days=(0,),
        chat_id=chat_id,
        name=goal_reminder_name,
    )

    # daily check-in at 20:00 (evening – did you train today?)
    job_queue.run_daily(
        send_daily_checkin,
        time=time(hour=20, minute=0),
        chat_id=chat_id,
        name=checkin_name,
    )

    # spaced repetition refresh check at 10:00 daily
    refresh_name = f"refresh_{chat_id}"
    existing_refresh_jobs = job_queue.get_jobs_by_name(refresh_name)
    for job in existing_refresh_jobs:
        job.schedule_removal()

    job_queue.run_daily(
        send_refresh_reminders,
        time=time(hour=10, minute=0),
        chat_id=chat_id,
        name=refresh_name,
    )

    # schedule pre-training recaps based on user's BJJ schedule
    schedule_pretraining_jobs(job_queue, chat_id)
