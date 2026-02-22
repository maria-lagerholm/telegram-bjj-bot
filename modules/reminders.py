from datetime import datetime, time, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .database import load_database, save_database
from .helpers import get_current_week


async def send_daily_focus_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    database = load_database(chat_id)

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
    database = load_database(chat_id)
    week = get_current_week()

    active_goals = []
    for g in database["goals"]:
        if g.get("status", "active") == "active":
            active_goals.append(g)

    if active_goals:
        message = f"*week {week}*\n\nyour active goals:\n\n"
        for goal in active_goals:
            message += f"  • {goal['goals']}\n"
    else:
        message = f"*new week ({week})*\n\nset a goal with /goal!"

    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode="Markdown",
    )


async def send_daily_checkin(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    today = datetime.now().strftime("%Y-%m-%d")

    database = load_database(chat_id)
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


async def checkin_callback(update, context):
    query = update.callback_query
    await query.answer()

    trained = query.data == "checkin_yes"
    today = datetime.now().strftime("%Y-%m-%d")
    day_name = datetime.now().strftime("%A")

    chat_id = query.message.chat_id
    database = load_database(chat_id)

    for entry in database.get("training_log", []):
        if entry["date"] == today:
            if entry["trained"]:
                status = "trained"
            else:
                status = "rest day"
            await query.edit_message_text(f"already logged today as *{status}*.", parse_mode="Markdown")
            return

    database["training_log"].append({
        "date": today,
        "day": day_name,
        "trained": trained,
        "logged_at": datetime.now().isoformat(),
    })
    save_database(chat_id, database)

    if trained:
        streak = get_current_streak(database["training_log"])
        msg = "nice! logged as a training day."
        if streak > 1:
            msg += f"\n🔥 {streak}-day streak!"
        msg += "\n\nuse /note to log what you learned."
    else:
        msg = "rest day logged. recovery is part of the game 💪"

    await query.edit_message_text(msg)


def get_current_streak(training_log):
    trained_dates = []
    for entry in training_log:
        if entry["trained"]:
            trained_dates.append(entry["date"])
    trained_dates.sort(reverse=True)

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
    chat_id = context.job.chat_id
    database = load_database(chat_id)
    today = datetime.now().strftime("%Y-%m-%d")

    for goal in database.get("goals", []):
        if goal.get("status") != "completed":
            continue

        schedule = goal.get("refresh_schedule", [])
        idx = goal.get("refresh_index", 0)

        if idx >= len(schedule):
            continue

        if schedule[idx] <= today:
            interval_label = ["1 month", "2 months", "3 months", "6 months"]
            if idx < len(interval_label):
                label = interval_label[idx]
            else:
                label = f"reminder {idx + 1}"

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
    chat_id = context.job.chat_id
    database = load_database(chat_id)

    notes = database.get("notes", [])
    last_note = None
    if notes:
        last_note = notes[-1]

    active_goals = []
    for g in database.get("goals", []):
        if g.get("status", "active") == "active":
            active_goals.append(g)

    active_drill = database.get("active_drill")

    message = "*pretraining recap* 🥋\n\n"

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

    message += (
        "_have a great session!_\n\n"
        "remember to take a note after training. use /note to log what you learned. "
        "pay attention during demonstrations so you can write it down later!"
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode="Markdown",
    )


def parse_time(time_str, default_h, default_m):
    try:
        parts = time_str.split(":")
        return time(hour=int(parts[0]), minute=int(parts[1]))
    except (ValueError, IndexError, AttributeError):
        return time(hour=default_h, minute=default_m)


def schedule_pretraining_jobs(job_queue, chat_id):
    prefix = f"pretrain_{chat_id}_"
    for job in job_queue.jobs():
        if job.name and job.name.startswith(prefix):
            job.schedule_removal()

    database = load_database(chat_id)
    schedule = database.get("schedule", [])

    day_map = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }

    for entry in schedule:
        day_name = entry["day"]
        time_str = entry["time"]

        day_num = day_map.get(day_name)
        if day_num is None:
            continue

        try:
            parts = time_str.split(":")
            hour = int(parts[0])
            if len(parts) > 1:
                minute = int(parts[1])
            else:
                minute = 0
        except (ValueError, IndexError):
            continue

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


def schedule_all_reminders(chat_id, job_queue):
    database = load_database(chat_id)
    rt = database.get("reminder_times", {})

    checkin_time = parse_time(rt.get("daily_checkin", "20:00"), 20, 0)
    focus_time = parse_time(rt.get("focus_reminder", "09:00"), 9, 0)
    goal_time = parse_time(rt.get("goal_reminder", "08:00"), 8, 0)
    refresh_time = parse_time(rt.get("refresh_reminder", "10:00"), 10, 0)

    focus_name = f"focus_reminder_{chat_id}"
    for job in job_queue.get_jobs_by_name(focus_name):
        job.schedule_removal()

    goal_name = f"goal_reminder_{chat_id}"
    for job in job_queue.get_jobs_by_name(goal_name):
        job.schedule_removal()

    checkin_name = f"checkin_{chat_id}"
    for job in job_queue.get_jobs_by_name(checkin_name):
        job.schedule_removal()

    refresh_name = f"refresh_{chat_id}"
    for job in job_queue.get_jobs_by_name(refresh_name):
        job.schedule_removal()

    job_queue.run_daily(
        send_daily_focus_reminder,
        time=focus_time,
        chat_id=chat_id,
        name=focus_name,
    )

    job_queue.run_daily(
        send_weekly_goal_reminder,
        time=goal_time,
        days=(0,),
        chat_id=chat_id,
        name=goal_name,
    )

    job_queue.run_daily(
        send_daily_checkin,
        time=checkin_time,
        chat_id=chat_id,
        name=checkin_name,
    )

    job_queue.run_daily(
        send_refresh_reminders,
        time=refresh_time,
        chat_id=chat_id,
        name=refresh_name,
    )

    schedule_pretraining_jobs(job_queue, chat_id)


async def setup_reminders(update, context):
    chat_id = update.effective_chat.id
    job_queue = context.application.job_queue
    schedule_all_reminders(chat_id, job_queue)
