import uuid
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from .database import load_database, save_database
from .helpers import get_current_week

state_goal_setting = 1

max_active_goals = 3
refresh_intervals = [30, 60, 90, 180]


def count_active_goals(database):
    count = 0
    for g in database.get("goals", []):
        if g.get("status", "active") == "active":
            count += 1
    return count


def find_goal(goals, goal_id):
    for g in goals:
        if g.get("id") == goal_id:
            return g
    return None


async def goal_start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    database = load_database(chat_id)
    active_count = count_active_goals(database)

    if active_count >= max_active_goals:
        await update.message.reply_text(
            f"you already have *{active_count}* active goals (max {max_active_goals}).\n\n"
            "complete or remove one first with /goals before adding a new one.",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    week = get_current_week()
    remaining = max_active_goals - active_count
    prompt_message = (
        f"*goal for {week}*  ({active_count}/{max_active_goals} slots used)\n\n"
        "examples:\n"
        "• _keep elbows tight during rolls_\n"
        "• _practice being relaxed during training_\n"
        "• _be more attentive during demonstrations_\n"
        "• _survive side control for 30 seconds_\n"
        "• _attempt one sweep per roll_\n"
        "• _focus on breathing under pressure_\n"
        "• _ask coach one question per class_\n\n"
        "_keep it short: 1 to 7 words_\n\n"
        "/cancel to abort"
    )
    await update.message.reply_text(prompt_message, parse_mode="Markdown")
    return state_goal_setting


async def goal_receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    database = load_database(chat_id)

    if count_active_goals(database) >= max_active_goals:
        await update.message.reply_text(
            f"you already have {max_active_goals} active goals. complete or remove one first with /goals.",
        )
        return ConversationHandler.END

    week = get_current_week()
    goal_text = update.message.text.strip()

    word_count = len(goal_text.split())
    if word_count < 1:
        await update.message.reply_text("goal can't be empty. write at least 1 word.")
        return state_goal_setting
    if word_count > 7:
        await update.message.reply_text(
            f"that's {word_count} words. keep it to 7 or fewer.\n"
            "try again or /cancel to abort."
        )
        return state_goal_setting

    new_goal = {
        "id": uuid.uuid4().hex[:8],
        "week": week,
        "goals": goal_text,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "refresh_schedule": [],
        "refresh_index": 0,
    }

    database["goals"].append(new_goal)
    save_database(chat_id, database)

    active_count = count_active_goals(database)
    confirmation_message = f"goal saved for {week}:\n\n_{goal_text}_\n\n({active_count}/{max_active_goals} goal slots used)"
    await update.message.reply_text(confirmation_message, parse_mode="Markdown")
    return ConversationHandler.END


async def goals_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    database = load_database(chat_id)

    goals = database.get("goals", [])
    if not goals:
        await update.message.reply_text("no goals yet. use /goal!")
        return

    active_goals = []
    completed_goals = []
    for g in goals:
        if g.get("status", "active") == "active":
            active_goals.append(g)
        elif g.get("status") == "completed":
            completed_goals.append(g)

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

    keyboard = []
    for goal in active_goals:
        gid = goal.get("id", "")
        if not gid:
            continue
        short = goal["goals"]
        if len(short) > 25:
            short = short[:25] + "…"
        keyboard.append([
            InlineKeyboardButton(f"✓ {short}", callback_data=f"goal_done_{gid}"),
            InlineKeyboardButton("✕", callback_data=f"goal_rm_{gid}"),
        ])

    if keyboard:
        message += "_tap ✓ to complete, ✕ to remove_"
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, parse_mode="Markdown")


async def goal_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    chat_id = query.message.chat_id
    database = load_database(chat_id)
    goals = database.get("goals", [])

    if data.startswith("goal_done_"):
        goal_id = data[len("goal_done_"):]
        goal = find_goal(goals, goal_id)
        if not goal:
            await query.edit_message_text("goal not found.")
            return

        goal["status"] = "completed"
        goal["completed_at"] = datetime.now().isoformat()

        goal["refresh_schedule"] = []
        goal["refresh_index"] = 0
        for days in refresh_intervals:
            remind_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            goal["refresh_schedule"].append(remind_date)

        save_database(chat_id, database)

        date_1m = (datetime.now() + timedelta(days=refresh_intervals[0])).strftime("%b %d")
        date_2m = (datetime.now() + timedelta(days=refresh_intervals[1])).strftime("%b %d")
        date_3m = (datetime.now() + timedelta(days=refresh_intervals[2])).strftime("%b %d")
        date_6m = (datetime.now() + timedelta(days=refresh_intervals[3])).strftime("%b %d")

        await query.edit_message_text(
            f"✓ *{goal['goals']}* completed!\n\n"
            f"refresh reminders scheduled:\n"
            f"  • 1 month  ({date_1m})\n"
            f"  • 2 months ({date_2m})\n"
            f"  • 3 months ({date_3m})\n"
            f"  • 6 months ({date_6m})\n\n"
            f"_you'll get a reminder to refresh this skill_",
            parse_mode="Markdown",
        )

    elif data.startswith("goal_rm_"):
        goal_id = data[len("goal_rm_"):]
        goal = find_goal(goals, goal_id)
        if not goal:
            await query.edit_message_text("goal not found.")
            return

        goal["status"] = "removed"
        save_database(chat_id, database)

        await query.edit_message_text(f"removed: _{goal['goals']}_", parse_mode="Markdown")

    elif data.startswith("goal_refresh_"):
        goal_id = data[len("goal_refresh_"):]
        goal = find_goal(goals, goal_id)
        if not goal:
            await query.edit_message_text("goal not found.")
            return

        goal["refresh_index"] = goal.get("refresh_index", 0) + 1
        save_database(chat_id, database)

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
