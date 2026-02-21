"""
Telegram BJJ White Belt Bot
- Stores your BJJ protocol & guide
- Set weekly goals
- Log training notes after each session
- Tracks techniques to drill with reminders
"""

import json
import os
import logging
from datetime import datetime, time, timedelta
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Data persistence --------------------------------------------------------

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

PROTOCOL_FILE = Path(__file__).parent / "bjj_white_belt_guide.txt"
DB_FILE = DATA_DIR / "bot_data.json"


def load_db() -> dict:
    if DB_FILE.exists():
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {
        "goals": [],          # list of {week, goals, created_at}
        "notes": [],           # list of {date, text, techniques, created_at}
        "drill_queue": [],     # list of {technique, added_at, drilled_count, last_reminded}
    }


def save_db(db: dict) -> None:
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2, default=str)


# --- Protocol text -----------------------------------------------------------

def get_protocol() -> str:
    if PROTOCOL_FILE.exists():
        return PROTOCOL_FILE.read_text()
    return "Protocol file not found. Place bjj_white_belt_guide.txt next to bot.py."


# --- Helpers -----------------------------------------------------------------

def current_week() -> str:
    """Return ISO week string like '2026-W08'."""
    now = datetime.now()
    return f"{now.isocalendar()[0]}-W{now.isocalendar()[1]:02d}"


def week_display(week_str: str) -> str:
    """Make week string more readable."""
    return week_str


# --- Command handlers --------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🥋 *BJJ Training Bot*\n\n"
        "I'll help you stay on track with your BJJ journey!\n\n"
        "*Commands:*\n"
        "/protocol — View your BJJ white belt guide\n"
        "/scoring — Competition scoring quick-reference\n"
        "/illegal — Illegal techniques for white belt\n"
        "/goal — Set a goal for this week\n"
        "/goals — View current & past goals\n"
        "/note — Log a training note\n"
        "/notes — View your training notes\n"
        "/drill — Add a technique to your drill queue\n"
        "/drills — View your drill queue\n"
        "/drilled — Mark a technique as drilled\n"
        "/stats — Your training stats\n"
        "/help — Show this message\n\n"
        "After each training, just use /note to log what you learned. "
        "I'll remember everything and remind you what to drill! 💪"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)


# --- Protocol ----------------------------------------------------------------

async def protocol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    full = get_protocol()
    # Split into sections for readability — send up to the scoring table
    lines = full.split("\n")
    # Find where scoring section starts
    cut = None
    for i, line in enumerate(lines):
        if line.startswith("Competition Scoring"):
            cut = i
            break
    if cut:
        core = "\n".join(lines[:cut]).strip()
    else:
        core = full

    await update.message.reply_text(
        f"📋 *Your BJJ Protocol*\n\n{core}",
        parse_mode="Markdown",
    )


async def scoring(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🏆 *Competition Scoring (IBJJF — White Belt Adult)*\n"
        "Match duration: 5 min. Submission wins instantly.\n\n"
        "```\n"
        "Position        Pts  How to Score\n"
        "─────────────── ───  ─────────────────────────\n"
        "Takedown         +2  Take down, hold top 3s\n"
        "Sweep            +2  Guard bottom → top, 3s\n"
        "Guard Pass       +3  Pass guard, stabilise 3s\n"
        "Knee on Belly    +2  KoB, back on mat, 3s\n"
        "Mount            +4  Sit on torso, knees down 3s\n"
        "Back Control     +4  Both hooks in, chest-back 3s\n"
        "```"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def illegal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🚫 *Illegal for White Belt (IBJJF)*\n\n"
        "• Heel hooks (inside/outside/reverse)\n"
        "• Knee reaping\n"
        "• Toe holds\n"
        "• Bicep / calf slicers\n"
        "• Neck cranks / cervical locks\n"
        "• Spinal locks without choke\n"
        "• Scissors takedown (kani basami)\n"
        "• Slamming\n"
        "• Flying guard pull\n"
        "• Wrist locks\n\n"
        "_Immediate DQ if used in competition._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# --- Goals -------------------------------------------------------------------

GOAL_SETTING = 1


async def goal_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    week = current_week()
    await update.message.reply_text(
        f"🎯 *Set your goal for {week}*\n\n"
        "Type your goal(s) for this week.\n"
        "Examples:\n"
        "• _Keep elbows tight from bottom_\n"
        "• _Hit 3 hip escapes every roll_\n"
        "• _Survive side control for 30s_\n\n"
        "Send /cancel to abort.",
        parse_mode="Markdown",
    )
    return GOAL_SETTING


async def goal_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    db = load_db()
    week = current_week()
    goal_text = update.message.text.strip()

    db["goals"].append({
        "week": week,
        "goals": goal_text,
        "created_at": datetime.now().isoformat(),
    })
    save_db(db)

    await update.message.reply_text(
        f"✅ Goal saved for {week}:\n\n_{goal_text}_\n\n"
        "Stay focused! I'll remind you about your goals. 🥋",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def goals_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    if not db["goals"]:
        await update.message.reply_text(
            "No goals set yet. Use /goal to set your first one!"
        )
        return

    week = current_week()
    current = [g for g in db["goals"] if g["week"] == week]
    past = [g for g in db["goals"] if g["week"] != week]

    text = "🎯 *Your Goals*\n\n"
    if current:
        text += f"*This week ({week}):*\n"
        for g in current:
            text += f"  • {g['goals']}\n"
        text += "\n"

    if past:
        text += "*Previous weeks:*\n"
        # Show last 10
        for g in reversed(past[-10:]):
            text += f"  _{g['week']}_ — {g['goals']}\n"

    await update.message.reply_text(text, parse_mode="Markdown")


# --- Training Notes ----------------------------------------------------------

NOTE_WRITING = 2


async def note_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    today = datetime.now().strftime("%A, %b %d")
    await update.message.reply_text(
        f"📝 *Training Note — {today}*\n\n"
        "Write what you learned today. Include:\n"
        "• Techniques practiced\n"
        "• What went well\n"
        "• What to work on\n\n"
        "💡 _Tip: mention specific techniques and I'll add them to your drill queue!_\n\n"
        "Send /cancel to abort.",
        parse_mode="Markdown",
    )
    return NOTE_WRITING


async def note_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    db = load_db()
    note_text = update.message.text.strip()
    now = datetime.now()

    # Try to extract technique-like keywords (simple heuristic)
    techniques_found = extract_techniques(note_text)

    db["notes"].append({
        "date": now.strftime("%Y-%m-%d"),
        "day": now.strftime("%A"),
        "text": note_text,
        "techniques": techniques_found,
        "created_at": now.isoformat(),
    })

    # Auto-add discovered techniques to drill queue
    new_drills = []
    existing = {d["technique"].lower() for d in db["drill_queue"]}
    for tech in techniques_found:
        if tech.lower() not in existing:
            db["drill_queue"].append({
                "technique": tech,
                "added_at": now.isoformat(),
                "drilled_count": 0,
                "last_reminded": None,
            })
            new_drills.append(tech)
            existing.add(tech.lower())

    save_db(db)

    reply = f"✅ Training note saved!\n\n"
    if techniques_found:
        reply += f"🔍 Techniques detected: {', '.join(techniques_found)}\n"
    if new_drills:
        reply += f"➕ Added to drill queue: {', '.join(new_drills)}\n"
    reply += "\nKeep showing up! 🥋"

    await update.message.reply_text(reply)
    return ConversationHandler.END


def extract_techniques(text: str) -> list[str]:
    """Simple keyword-based technique extraction."""
    known_techniques = [
        # Escapes & movements
        "hip escape", "shrimp", "bridge", "technical stand-up", "granby roll",
        "elbow escape", "trap and roll", "upa",
        # Guard
        "closed guard", "half guard", "open guard", "butterfly guard",
        "de la riva", "spider guard", "lasso guard", "x-guard",
        "single leg x", "rubber guard",
        # Passes
        "torreando", "double under", "knee slice", "knee cut",
        "leg drag", "smash pass", "over-under", "stack pass",
        "long step", "body lock pass",
        # Sweeps
        "scissor sweep", "flower sweep", "hip bump", "butterfly sweep",
        "tripod sweep", "pendulum sweep", "sickle sweep",
        # Takedowns
        "single leg", "double leg", "hip throw", "ankle pick",
        "osoto gari", "arm drag", "snap down", "collar drag",
        # Submissions
        "armbar", "triangle", "rear naked choke", "rnc",
        "guillotine", "kimura", "americana", "omoplata",
        "ezekiel", "cross choke", "collar choke", "bow and arrow",
        "arm triangle", "darce", "anaconda", "north-south choke",
        "loop choke", "baseball choke",
        # Positions & controls
        "mount", "side control", "back control", "knee on belly",
        "turtle", "north-south", "crucifix",
        # Grips & concepts
        "seatbelt", "underhook", "overhook", "frames",
        "collar grip", "sleeve grip",
    ]
    text_lower = text.lower()
    found = []
    for tech in known_techniques:
        if tech in text_lower:
            found.append(tech.title())
    return found


async def notes_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    if not db["notes"]:
        await update.message.reply_text(
            "No training notes yet. Use /note after your next session!"
        )
        return

    text = "📝 *Training Notes*\n\n"
    # Show last 10 notes
    for n in reversed(db["notes"][-10:]):
        date_str = n.get("day", "")
        text += f"*{n['date']}* ({date_str})\n"
        # Truncate long notes for the list view
        preview = n["text"][:120]
        if len(n["text"]) > 120:
            preview += "…"
        text += f"{preview}\n"
        if n.get("techniques"):
            text += f"_Techniques: {', '.join(n['techniques'])}_\n"
        text += "\n"

    total = len(db["notes"])
    if total > 10:
        text += f"_Showing last 10 of {total} notes._\n"

    await update.message.reply_text(text, parse_mode="Markdown")


# --- Drill Queue -------------------------------------------------------------

DRILL_ADDING = 3


async def drill_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "🔄 *Add to Drill Queue*\n\n"
        "What technique do you want to drill?\n"
        "Example: _scissor sweep_, _hip escape from mount_\n\n"
        "Send /cancel to abort.",
        parse_mode="Markdown",
    )
    return DRILL_ADDING


async def drill_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    db = load_db()
    tech = update.message.text.strip()
    now = datetime.now()

    # Check for duplicates
    existing = {d["technique"].lower() for d in db["drill_queue"]}
    if tech.lower() in existing:
        await update.message.reply_text(
            f"'{tech}' is already in your drill queue! Use /drills to see your list."
        )
        return ConversationHandler.END

    db["drill_queue"].append({
        "technique": tech,
        "added_at": now.isoformat(),
        "drilled_count": 0,
        "last_reminded": None,
    })
    save_db(db)

    await update.message.reply_text(
        f"✅ Added *{tech}* to your drill queue!\n\n"
        "I'll remind you to practice it. Use /drilled after you've worked on it.",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def drills_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    if not db["drill_queue"]:
        await update.message.reply_text(
            "Your drill queue is empty. Log a training note with /note or "
            "add techniques manually with /drill!"
        )
        return

    text = "🔄 *Your Drill Queue*\n\n"
    for i, d in enumerate(db["drill_queue"], 1):
        count = d.get("drilled_count", 0)
        bar = "🟢" if count >= 5 else "🟡" if count >= 2 else "🔴"
        text += f"{bar} *{i}.* {d['technique']} — drilled {count}x\n"

    text += (
        "\n_Use /drilled to mark a technique as practiced._\n"
        "_🔴 = needs work  🟡 = getting there  🟢 = solid_"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def drilled(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    if not db["drill_queue"]:
        await update.message.reply_text("Your drill queue is empty!")
        return

    # Build inline keyboard with technique names
    keyboard = []
    for i, d in enumerate(db["drill_queue"]):
        keyboard.append([
            InlineKeyboardButton(
                f"{d['technique']} (drilled {d.get('drilled_count', 0)}x)",
                callback_data=f"drilled_{i}",
            )
        ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Which technique did you drill? 👇",
        reply_markup=reply_markup,
    )


async def drilled_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("drilled_"):
        return

    idx = int(data.split("_")[1])
    db = load_db()

    if idx >= len(db["drill_queue"]):
        await query.edit_message_text("Something went wrong, try again.")
        return

    db["drill_queue"][idx]["drilled_count"] = (
        db["drill_queue"][idx].get("drilled_count", 0) + 1
    )
    tech = db["drill_queue"][idx]["technique"]
    count = db["drill_queue"][idx]["drilled_count"]
    save_db(db)

    msgs = {
        1: "First rep done! Keep going 💪",
        2: "Twice now — building that muscle memory!",
        3: "Three times! The technique is starting to stick.",
        5: "Five reps! You're getting solid at this. 🟢",
        10: "TEN times! This is becoming second nature! 🔥",
    }
    encouragement = msgs.get(count, f"Rep #{count} done!")

    await query.edit_message_text(
        f"✅ *{tech}* — drilled {count}x\n\n{encouragement}",
        parse_mode="Markdown",
    )


# --- Stats -------------------------------------------------------------------

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()

    total_notes = len(db["notes"])
    total_goals = len(db["goals"])
    total_drills = len(db["drill_queue"])
    drills_solid = sum(1 for d in db["drill_queue"] if d.get("drilled_count", 0) >= 5)

    # Training frequency
    if db["notes"]:
        dates = sorted(set(n["date"] for n in db["notes"]))
        first_date = dates[0]
        this_week_notes = sum(
            1 for n in db["notes"]
            if n["date"] >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        )
    else:
        first_date = "N/A"
        this_week_notes = 0

    # All techniques mentioned
    all_techs = set()
    for n in db["notes"]:
        for t in n.get("techniques", []):
            all_techs.add(t)

    text = (
        "📊 *Your BJJ Training Stats*\n\n"
        f"📝 Total training notes: *{total_notes}*\n"
        f"📅 Sessions this week: *{this_week_notes}*\n"
        f"🎯 Goals set: *{total_goals}*\n"
        f"🔄 Techniques in drill queue: *{total_drills}*\n"
        f"🟢 Techniques solid (5+ reps): *{drills_solid}*\n"
        f"🧠 Unique techniques logged: *{len(all_techs)}*\n"
    )

    if db["notes"]:
        text += f"\n_Training since {first_date}_\n"

    text += "\nKeep training, keep learning! OSS! 🥋"
    await update.message.reply_text(text, parse_mode="Markdown")


# --- Cancel handler for conversations ---------------------------------------

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Cancelled. 👍")
    return ConversationHandler.END


# --- Scheduled reminders -----------------------------------------------------

async def daily_drill_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a daily reminder about techniques to drill."""
    chat_id = context.job.chat_id
    db = load_db()

    if not db["drill_queue"]:
        return

    # Pick techniques that need the most work (lowest drilled_count)
    sorted_drills = sorted(db["drill_queue"], key=lambda d: d.get("drilled_count", 0))
    top_3 = sorted_drills[:3]

    text = "🔔 *Daily Drill Reminder*\n\nFocus on these today:\n\n"
    for d in top_3:
        count = d.get("drilled_count", 0)
        text += f"  • *{d['technique']}* (drilled {count}x)\n"

    text += "\n_Drill with intention, not desperation!_ 🥋"

    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")


async def weekly_goal_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Weekly reminder about current goals."""
    chat_id = context.job.chat_id
    db = load_db()
    week = current_week()
    current = [g for g in db["goals"] if g["week"] == week]

    if current:
        text = f"🎯 *Weekly Goal Check-in ({week})*\n\nYour goals this week:\n\n"
        for g in current:
            text += f"  • {g['goals']}\n"
        text += "\nHow's your progress? Stay focused! 💪"
    else:
        text = (
            f"🎯 *New Week ({week})!*\n\n"
            "You haven't set any goals yet. Use /goal to set one!\n\n"
            "_\"Set small, specific goals.\"_ — Your Protocol"
        )

    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")


async def post_start_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set up scheduled jobs when a user first interacts."""
    chat_id = update.effective_chat.id
    job_queue = context.application.job_queue

    # Remove existing jobs for this chat to avoid duplicates
    current_jobs = job_queue.get_jobs_by_name(f"drill_reminder_{chat_id}")
    for job in current_jobs:
        job.schedule_removal()
    current_jobs = job_queue.get_jobs_by_name(f"goal_reminder_{chat_id}")
    for job in current_jobs:
        job.schedule_removal()

    # Daily drill reminder at 09:00
    job_queue.run_daily(
        daily_drill_reminder,
        time=time(hour=9, minute=0),
        chat_id=chat_id,
        name=f"drill_reminder_{chat_id}",
    )

    # Weekly goal reminder on Monday at 08:00
    job_queue.run_daily(
        weekly_goal_reminder,
        time=time(hour=8, minute=0),
        days=(0,),  # Monday
        chat_id=chat_id,
        name=f"goal_reminder_{chat_id}",
    )


# --- Main --------------------------------------------------------------------

def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "your-token-here":
        print("=" * 50)
        print("ERROR: Set your TELEGRAM_BOT_TOKEN in .env")
        print("Get one from @BotFather on Telegram")
        print("=" * 50)
        return

    app = Application.builder().token(token).build()

    # Conversation: set goal
    goal_conv = ConversationHandler(
        entry_points=[CommandHandler("goal", goal_start)],
        states={GOAL_SETTING: [MessageHandler(filters.TEXT & ~filters.COMMAND, goal_receive)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Conversation: training note
    note_conv = ConversationHandler(
        entry_points=[CommandHandler("note", note_start)],
        states={NOTE_WRITING: [MessageHandler(filters.TEXT & ~filters.COMMAND, note_receive)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Conversation: add drill
    drill_conv = ConversationHandler(
        entry_points=[CommandHandler("drill", drill_start)],
        states={DRILL_ADDING: [MessageHandler(filters.TEXT & ~filters.COMMAND, drill_receive)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("protocol", protocol))
    app.add_handler(CommandHandler("scoring", scoring))
    app.add_handler(CommandHandler("illegal", illegal))
    app.add_handler(goal_conv)
    app.add_handler(note_conv)
    app.add_handler(drill_conv)
    app.add_handler(CommandHandler("goals", goals_list))
    app.add_handler(CommandHandler("notes", notes_list))
    app.add_handler(CommandHandler("drills", drills_list))
    app.add_handler(CommandHandler("drilled", drilled))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(drilled_callback, pattern="^drilled_"))

    # Schedule reminders when /start is called
    app.add_handler(CommandHandler("start", post_start_schedule), group=1)

    print("🥋 BJJ Bot is running! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
