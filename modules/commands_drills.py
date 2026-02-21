from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from .database import load_database, save_database

state_drill_adding = 3


async def drill_start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt_message = (
        "*add to drill queue*\n\n"
        "what technique?\n"
        "example: _scissor sweep_\n\n"
        "/cancel to abort"
    )
    await update.message.reply_text(prompt_message, parse_mode="Markdown")
    return state_drill_adding


async def drill_receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = load_database()
    technique = update.message.text.strip()
    now = datetime.now()
    
    existing_techniques = set()
    for drill in database["drill_queue"]:
        existing_techniques.add(drill["technique"].lower())
    
    if technique.lower() in existing_techniques:
        await update.message.reply_text(f"'{technique}' already in queue!")
        return ConversationHandler.END
    
    new_drill = {
        "technique": technique,
        "added_at": now.isoformat(),
        "drilled_count": 0,
        "last_reminded": None,
    }
    database["drill_queue"].append(new_drill)
    save_database(database)
    
    confirmation_message = f"added *{technique}* to drill queue!"
    await update.message.reply_text(confirmation_message, parse_mode="Markdown")
    return ConversationHandler.END


async def drills_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = load_database()
    
    if not database["drill_queue"]:
        await update.message.reply_text("drill queue empty. use /note or /drill!")
        return
    
    message = "*drill queue*\n\n"
    
    for i, drill in enumerate(database["drill_queue"], 1):
        count = drill.get("drilled_count", 0)
        
        if count >= 5:
            status_emoji = "[solid]"
        elif count >= 2:
            status_emoji = "[ok]"
        else:
            status_emoji = "[needs work]"
        
        message += f"{status_emoji} *{i}.* {drill['technique']} ({count}x)\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")


async def drilled_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = load_database()
    
    if not database["drill_queue"]:
        await update.message.reply_text("drill queue empty!")
        return
    
    keyboard = []
    for i, drill in enumerate(database["drill_queue"]):
        count = drill.get("drilled_count", 0)
        button_text = f"{drill['technique']} ({count}x)"
        button = InlineKeyboardButton(button_text, callback_data=f"drilled_{i}")
        keyboard.append([button])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("which technique?", reply_markup=reply_markup)


async def drilled_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    button_data = query.data
    
    if not button_data.startswith("drilled_"):
        return
    
    drill_index = int(button_data.split("_")[1])
    database = load_database()
    
    if drill_index >= len(database["drill_queue"]):
        await query.edit_message_text("error, try again.")
        return
    
    current_count = database["drill_queue"][drill_index].get("drilled_count", 0)
    database["drill_queue"][drill_index]["drilled_count"] = current_count + 1
    
    technique = database["drill_queue"][drill_index]["technique"]
    new_count = database["drill_queue"][drill_index]["drilled_count"]
    
    save_database(database)
    
    encouragement_messages = {
        1: "first rep!",
        2: "building muscle memory!",
        3: "starting to stick!",
        5: "getting solid!",
        10: "second nature!",
    }
    
    if new_count in encouragement_messages:
        encouragement = encouragement_messages[new_count]
    else:
        encouragement = f"rep #{new_count}"
    
    confirmation_message = f"*{technique}* ({new_count}x)\n\n{encouragement}"
    await query.edit_message_text(confirmation_message, parse_mode="Markdown")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = load_database()
    
    total_notes = len(database["notes"])
    total_goals = len(database["goals"])
    total_drills = len(database["drill_queue"])
    
    drills_solid = 0
    for drill in database["drill_queue"]:
        if drill.get("drilled_count", 0) >= 5:
            drills_solid += 1
    
    if database["notes"]:
        all_dates = []
        for note in database["notes"]:
            all_dates.append(note["date"])
        unique_dates = sorted(set(all_dates))
        first_date = unique_dates[0]
        
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        this_week_notes = 0
        for note in database["notes"]:
            if note["date"] >= seven_days_ago:
                this_week_notes += 1
    else:
        first_date = "n/a"
        this_week_notes = 0
    
    all_unique_techniques = set()
    for note in database["notes"]:
        for technique in note.get("techniques", []):
            all_unique_techniques.add(technique)
    
    message = (
        "*training stats*\n\n"
        f"total notes: *{total_notes}*\n"
        f"this week: *{this_week_notes}*\n"
        f"goals set: *{total_goals}*\n"
        f"in drill queue: *{total_drills}*\n"
        f"solid (5+ reps): *{drills_solid}*\n"
        f"unique techniques: *{len(all_unique_techniques)}*\n"
    )
    
    if database["notes"]:
        message += f"\n_training since {first_date}_"
    
    await update.message.reply_text(message, parse_mode="Markdown")
