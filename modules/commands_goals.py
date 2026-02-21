import uuid
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from .database import load_database, save_database
from .helpers import get_current_week

state_goal_setting = 1

MAX_ACTIVE_GOALS = 3

# spaced repetition intervals (in days): 1 month, 2 months, 3 months, 6 months
REFRESH_INTERVALS = [30, 60, 90, 180]


def _count_active_goals(database: dict) -> int:
    return sum(1 for g in database.get("goals", []) if g.get("status", "active") == "active")


async def goal_start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = load_database()
    active_count = _count_active_goals(database)

    if active_count >= MAX_ACTIVE_GOALS:
        await update.message.reply_text(
            f"you already have *{active_count}* active goals (max {MAX_ACTIVE_GOALS}).\n\n"
            "complete or remove one first with /goals before adding a new one.",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    week = get_current_week()
    remaining = MAX_ACTIVE_GOALS - active_count
    prompt_message = (
        f"*goal for {week}*  ({active_count}/{MAX_ACTIVE_GOALS} slots used)\n\n"
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

    # double-check limit in case something changed
    if _count_active_goals(database) >= MAX_ACTIVE_GOALS:
        await update.message.reply_text(
            f"you already have {MAX_ACTIVE_GOALS} active goals. complete or remove one first with /goals.",
        )
        return ConversationHandler.END

    week = get_current_week()
    goal_text = update.message.text.strip()

    new_goal = {
        "id": uuid.uuid4().hex[:8],
        "week": week,
        "goals": goal_text,
        "status": "active",            # active | completed | removed
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "refresh_schedule": [],         # list of ISO dates for spaced reminders
        "refresh_index": 0,            # which interval we're on
    }

    database["goals"].append(new_goal)
    save_database(database)

    active_count = _count_active_goals(database)
    confirmation_message = f"goal saved for {week}:\n\n_{goal_text}_\n\n({active_count}/{MAX_ACTIVE_GOALS} goal slots used)"
    await update.message.reply_text(confirmation_message, parse_mode="Markdown")
    return ConversationHandler.END


async def goals_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = load_database()

    goals = database.get("goals", [])
    if not goals:
        await update.message.reply_text("no goals yet. use /goal!")
        return

    active_goals = [g for g in goals if g.get("status", "active") == "active"]
    completed_goals = [g for g in goals if g.get("status") == "completed"]

    message = "*goals*\n\n"

    if active_goals:
        message += "*active:*\n"
        for goal in active_goals:
            week = goal.get("week", "")
            message += f"  • {goal['goals']}  _({week})_\n"
        message += "\n"

    if completed_goals:
        last_five = completed_goals[-5:]
        message += "*completed:*\n"
        for goal in reversed(last_five):
            message += f"  ✓ ~{goal['goals']}~\n"
        if len(completed_goals) > 5:
            message += f"  _…and {len(completed_goals) - 5} more_\n"
        message += "\n"

    if not active_goals and not completed_goals:
        message += "all goals removed. use /goal to set a new one!\n"

    # build inline buttons for each active goal
    keyboard = []
    for goal in active_goals:
        gid = goal.get("id", "")
        if not gid:
            continue
        keyboard.append([
            InlineKeyboardButton(f"✓ {_short(goal['goals'])}", callback_data=f"goal_done_{gid}"),
            InlineKeyboardButton("✕", callback_data=f"goal_rm_{gid}"),
        ])

    if keyboard:
        message += "_tap ✓ to complete, ✕ to remove_"
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, parse_mode="Markdown")


async def goal_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle complete / remove / refresh-acknowledge buttons."""
    query = update.callback_query
    await query.answer()
    data = query.data

    database = load_database()
    goals = database.get("goals", [])

    if data.startswith("goal_done_"):
        goal_id = data[len("goal_done_"):]
        goal = _find_goal(goals, goal_id)
        if not goal:
            await query.edit_message_text("goal not found.")
            return

        goal["status"] = "completed"
        goal["completed_at"] = datetime.now().isoformat()

        # schedule spaced repetition reminders
        goal["refresh_schedule"] = []
        goal["refresh_index"] = 0
        for days in REFRESH_INTERVALS:
            remind_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            goal["refresh_schedule"].append(remind_date)

        save_database(database)

        next_refresh = goal["refresh_schedule"][0]
        await query.edit_message_text(
            f"✓ *{goal['goals']}* completed!\n\n"
            f"refresh reminders scheduled:\n"
            f"  • 1 month  ({_format_date(REFRESH_INTERVALS[0])})\n"
            f"  • 2 months ({_format_date(REFRESH_INTERVALS[1])})\n"
            f"  • 3 months ({_format_date(REFRESH_INTERVALS[2])})\n"
            f"  • 6 months ({_format_date(REFRESH_INTERVALS[3])})\n\n"
            f"_you'll get a reminder to refresh this skill_",
            parse_mode="Markdown",
        )

    elif data.startswith("goal_rm_"):
        goal_id = data[len("goal_rm_"):]
        goal = _find_goal(goals, goal_id)
        if not goal:
            await query.edit_message_text("goal not found.")
            return

        goal["status"] = "removed"
        save_database(database)

        await query.edit_message_text(f"removed: _{goal['goals']}_", parse_mode="Markdown")

    elif data.startswith("goal_refresh_"):
        # user acknowledged a refresh reminder
        goal_id = data[len("goal_refresh_"):]
        goal = _find_goal(goals, goal_id)
        if not goal:
            await query.edit_message_text("goal not found.")
            return

        # advance to next interval
        goal["refresh_index"] = goal.get("refresh_index", 0) + 1
        save_database(database)

        remaining = len(goal.get("refresh_schedule", [])) - goal["refresh_index"]
        if remaining > 0:
            await query.edit_message_text(
                f"nice! *{goal['goals']}* refreshed 💪\n\n"
                f"_{remaining} more reminder(s) scheduled_",
                parse_mode="Markdown",
            )
        else:
            await query.edit_message_text(
                f"*{goal['goals']}* fully locked in! all refreshes done 🏆",
                parse_mode="Markdown",
            )


def _find_goal(goals: list, goal_id: str):
    for g in goals:
        if g.get("id") == goal_id:
            return g
    return None


def _short(text: str, limit: int = 25) -> str:
    """Shorten text for button labels."""
    return text[:limit] + "…" if len(text) > limit else text


def _format_date(days_from_now: int) -> str:
    return (datetime.now() + timedelta(days=days_from_now)).strftime("%b %d")
