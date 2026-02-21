from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from .database import load_database, save_database
from .helpers import find_techniques_in_text

state_note_writing = 2


async def note_start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%A, %b %d")
    prompt_message = (
        f"*training note: {today}*\n\n"
        "what did you learn?\n"
        "• techniques practiced\n"
        "• what went well\n"
        "• what to work on\n\n"
        "/cancel to abort"
    )
    await update.message.reply_text(prompt_message, parse_mode="Markdown")
    return state_note_writing


async def note_receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = load_database()
    note_text = update.message.text.strip()
    now = datetime.now()
    
    techniques_found = find_techniques_in_text(note_text)
    
    new_note = {
        "date": now.strftime("%Y-%m-%d"),
        "day": now.strftime("%A"),
        "text": note_text,
        "techniques": techniques_found,
        "created_at": now.isoformat(),
    }
    
    database["notes"].append(new_note)
    
    new_drills = []
    existing_techniques = set()
    
    for drill in database["drill_queue"]:
        existing_techniques.add(drill["technique"].lower())
    
    for technique in techniques_found:
        if technique.lower() not in existing_techniques:
            new_drill = {
                "technique": technique,
                "added_at": now.isoformat(),
                "drilled_count": 0,
                "last_reminded": None,
            }
            database["drill_queue"].append(new_drill)
            new_drills.append(technique)
            existing_techniques.add(technique.lower())
    
    save_database(database)
    
    reply = "note saved!\n\n"
    
    if techniques_found:
        techniques_list = ", ".join(techniques_found)
        reply += f"detected: {techniques_list}\n"
    
    if new_drills:
        new_drills_list = ", ".join(new_drills)
        reply += f"added to drills: {new_drills_list}\n"
    
    await update.message.reply_text(reply)
    return ConversationHandler.END


async def notes_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = load_database()
    
    if not database["notes"]:
        await update.message.reply_text("no notes yet. use /note after training!")
        return
    
    message = "*training notes*\n\n"
    
    last_ten_notes = database["notes"][-10:]
    for note in reversed(last_ten_notes):
        date_string = note.get("day", "")
        message += f"*{note['date']}* ({date_string})\n"
        
        preview = note["text"][:120]
        if len(note["text"]) > 120:
            preview += "…"
        message += f"{preview}\n"
        
        if note.get("techniques"):
            techniques_list = ", ".join(note["techniques"])
            message += f"_{techniques_list}_\n"
        
        message += "\n"
    
    total_notes = len(database["notes"])
    if total_notes > 10:
        message += f"_last 10 of {total_notes} notes_\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")
