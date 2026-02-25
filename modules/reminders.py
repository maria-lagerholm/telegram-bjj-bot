from datetime import datetime, time, timedelta
from telegram.ext import ContextTypes

from .database import load_database, save_database
from .helpers import now_se, time_se, SE_TZ


async def send_pretraining_recap(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    database = load_database(chat_id)

    notes = database.get("notes", [])
    last_note = notes[-1] if notes else None

    active_goals = [g for g in database.get("goals", []) if g.get("status", "active") == "active"]
    active_drill = database.get("active_drill")

    message = "*pretraining recap*\n\n"

    if active_goals:
        message += "*your goals:*\n"
        for g in active_goals[:3]:
            message += f"  {g['goals']}\n"
        message += "\n"

    if last_note:
        message += f"*last session ({last_note['date']}):*\n"
        preview = last_note["text"][:300]
        if len(last_note["text"]) > 300:
            preview += "..."
        message += f"{preview}\n\n"

    if active_drill:
        message += (
            f"*focus technique:* {active_drill['technique']}\n"
            f"_{active_drill.get('description', '')}_\n\n"
        )

    if not active_goals and not last_note and not active_drill:
        message += "no notes or goals yet, focus on learning today!\n"

    message += "have a great session! pay attention during demonstrations."

    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode="Markdown",
    )


async def send_posttraining_note_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    await context.bot.send_message(
        chat_id=chat_id,
        text="how was training? use /note to write down what you learned today.",
    )


async def send_refresh_reminders(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    database = load_database(chat_id)
    today = now_se().strftime("%Y-%m-%d")

    for goal in database.get("goals", []):
        if goal.get("status") != "completed":
            continue

        schedule = goal.get("refresh_schedule", [])
        idx = goal.get("refresh_index", 0)

        if idx >= len(schedule):
            continue

        if schedule[idx] <= today:
            labels = ["1 month", "2 months", "3 months", "6 months"]
            label = labels[idx] if idx < len(labels) else f"reminder {idx + 1}"

            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [[InlineKeyboardButton(
                "got it, refreshed",
                callback_data=f"goal_refresh_{goal['id']}",
            )]]

            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"*refresh reminder ({label})*\n\n"
                    f"remember this goal?\n"
                    f"*{goal['goals']}*\n\n"
                    f"_take a moment to drill or think about this today_"
                ),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )


DAY_MAP = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6,
}


def _clear_jobs(job_queue, prefix):
    for job in job_queue.jobs():
        if job.name and job.name.startswith(prefix):
            job.schedule_removal()


def schedule_training_reminders(job_queue, chat_id):
    _clear_jobs(job_queue, f"pretrain_{chat_id}_")
    _clear_jobs(job_queue, f"posttrain_{chat_id}_")

    database = load_database(chat_id)
    schedule = database.get("schedule", [])
    reminders_off = database.get("reminders_disabled", False)

    if reminders_off:
        return

    for entry in schedule:
        day_name = entry["day"]
        time_str = entry["time"]
        day_num = DAY_MAP.get(day_name)
        if day_num is None:
            continue

        try:
            parts = time_str.split(":")
            hour, minute = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
        except (ValueError, IndexError):
            continue

        train_dt = datetime.combine(now_se().date(), time(hour=hour, minute=minute))

        pre_dt = train_dt - timedelta(hours=1)
        post_dt = train_dt + timedelta(hours=1)

        job_queue.run_daily(
            send_pretraining_recap,
            time=time_se(pre_dt.hour, pre_dt.minute),
            days=(day_num,),
            chat_id=chat_id,
            name=f"pretrain_{chat_id}_{day_name}_{time_str}",
        )

        job_queue.run_daily(
            send_posttraining_note_reminder,
            time=time_se(post_dt.hour, post_dt.minute),
            days=(day_num,),
            chat_id=chat_id,
            name=f"posttrain_{chat_id}_{day_name}_{time_str}",
        )


def schedule_refresh_job(job_queue, chat_id):
    name = f"refresh_{chat_id}"
    _clear_jobs(job_queue, name)
    job_queue.run_daily(
        send_refresh_reminders,
        time=time_se(10, 0),
        days=(0,),
        chat_id=chat_id,
        name=name,
    )


def schedule_all_reminders(chat_id, job_queue):
    schedule_training_reminders(job_queue, chat_id)
    schedule_refresh_job(job_queue, chat_id)


async def setup_reminders(update, context):
    chat_id = update.effective_chat.id
    job_queue = context.application.job_queue
    schedule_all_reminders(chat_id, job_queue)
