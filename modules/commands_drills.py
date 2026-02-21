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
    
    # count from history
    drills_solid = 0
    for drill in database["drill_queue"]:
        if drill.get("drilled_count", 0) >= 5:
            drills_solid += 1
            
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
    
    message = (
        "*training stats*\n\n"
        f"total notes: *{total_notes}*\n"
        f"this week: *{this_week_notes}*\n"
        f"goals set: *{total_goals}*\n"
        f"past drills solid (5+ reps): *{drills_solid}*\n"
        f"active drill: *{active_drill_text}*\n"
    )
    
    if database["notes"]:
        message += f"\n_training since {first_date}_"
    
    await update.message.reply_text(message, parse_mode="Markdown")