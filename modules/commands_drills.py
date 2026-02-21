from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from .database import load_database, save_database


async def drills_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = load_database()
    active_drill = database.get("active_drill")
    
    if not active_drill:
        await update.message.reply_text(
            "you have no active drill!\n\n"
            "use /technique to browse the library and select a technique to focus on for the next 2 weeks.",
            parse_mode="Markdown"
        )
        return
    
    end_date = datetime.fromisoformat(active_drill["end_date"])
    days_left = (end_date - datetime.now()).days
    if days_left < 0:
        days_left = 0
        
    count = active_drill.get("drilled_count", 0)
    
    message = (
        "*active drill goal*\n\n"
        f"*{active_drill['technique']}*\n"
        f"reps completed: {count}\n"
        f"time remaining: {days_left} days\n\n"
        f"_{active_drill['description']}_\n\n"
        f"[watch tutorial]({active_drill['video_url']})\n\n"
        "use /drilled when you practice it."
    )
    
    keyboard = [[InlineKeyboardButton("stop drilling this", callback_data="stop_drill")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)


async def stop_drill_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    database = load_database()
    active_drill = database.get("active_drill")
    
    if not active_drill:
        await query.edit_message_text("no active drill to stop.")
        return
        
    # save to history
    database["drill_queue"].append({
        "technique": active_drill["technique"],
        "drilled_count": active_drill["drilled_count"],
        "finished_at": datetime.now().isoformat()
    })
    
    database["active_drill"] = None
    save_database(database)
    
    await query.edit_message_text(
        f"stopped drilling *{active_drill['technique']}*.\n\n"
        "you completed it with {active_drill['drilled_count']} reps.\n"
        "use /technique to choose a new one!",
        parse_mode="Markdown"
    )


async def drilled_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = load_database()
    active_drill = database.get("active_drill")
    
    if not active_drill:
        await update.message.reply_text("you have no active drill to mark as done! use /technique to set one.")
        return
    
    current_count = active_drill.get("drilled_count", 0)
    database["active_drill"]["drilled_count"] = current_count + 1
    
    save_database(database)
    
    new_count = current_count + 1
    
    encouragement_messages = {
        1: "first rep!",
        2: "building muscle memory!",
        3: "starting to stick!",
        5: "getting solid!",
        10: "second nature!",
    }
    
    encouragement = encouragement_messages.get(new_count, f"rep #{new_count}")
    
    confirmation_message = f"*{active_drill['technique']}* ({new_count}x)\n\n{encouragement}"
    await update.message.reply_text(confirmation_message, parse_mode="Markdown")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from datetime import timedelta
    database = load_database()
    
    total_notes = len(database["notes"])
    total_goals = len(database["goals"])

    active_drill = database.get("active_drill")
    active_drill_text = active_drill["technique"] if active_drill else "none"
    
    if database["notes"]:
        all_dates = [note["date"] for note in database["notes"]]
        unique_dates = sorted(set(all_dates))
        first_date = unique_dates[0]
        
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        this_week_notes = sum(1 for note in database["notes"] if note["date"] >= seven_days_ago)
    else:
        first_date = "n/a"
        this_week_notes = 0

    # training check-in stats
    training_log = database.get("training_log", [])
    total_checkins = len(training_log)
    days_trained = sum(1 for e in training_log if e["trained"])
    days_rest = total_checkins - days_trained

    seven_days_ago_str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    thirty_days_ago_str = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    week_trained = sum(1 for e in training_log if e["trained"] and e["date"] >= seven_days_ago_str)
    month_trained = sum(1 for e in training_log if e["trained"] and e["date"] >= thirty_days_ago_str)

    # current streak
    streak = 0
    current = datetime.now().date()
    trained_dates = sorted(
        [e["date"] for e in training_log if e["trained"]],
        reverse=True,
    )
    for date_str in trained_dates:
        log_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if log_date == current:
            streak += 1
            current = current - timedelta(days=1)
        else:
            break
    
    message = (
        "*training stats*\n\n"
        "*activity:*\n"
        f"  this week: *{week_trained}* sessions\n"
        f"  this month: *{month_trained}* sessions\n"
        f"  total trained: *{days_trained}* days\n"
        f"  rest days: *{days_rest}*\n"
    )

    if streak > 0:
        message += f"  🔥 streak: *{streak}* days\n"

    # toolbox stats
    toolbox = database.get("toolbox", [])
    from .techniques_data import TECHNIQUES
    total_techniques = sum(len(cat["items"]) for cat in TECHNIQUES.values())
    toolbox_count = len(toolbox)

    message += (
        f"\n*notes & drills:*\n"
        f"  total notes: *{total_notes}*\n"
        f"  notes this week: *{this_week_notes}*\n"
        f"  goals set: *{total_goals}*\n"
        f"  active drill: *{active_drill_text}*\n"
        f"  toolbox: *{toolbox_count}/{total_techniques}* techniques\n"
    )
    
    if database["notes"]:
        message += f"\n_training since {first_date}_"
    
    await update.message.reply_text(message, parse_mode="Markdown")