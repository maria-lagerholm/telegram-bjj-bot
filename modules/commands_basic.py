from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from .techniques_data import TECHNIQUES
from .database import load_database, save_database


def _toolbox_key(cat_id: str, tech_id: str) -> str:
    """Consistent key for a technique in the toolbox."""
    return f"{cat_id}:{tech_id}"


def _get_toolbox(db: dict) -> set:
    """Return set of toolbox keys."""
    return set(e["key"] for e in db.get("toolbox", []))


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "*bjj training bot*\n\n"
        "*protocol:*\n"
        "/mindset : mental approach\n"
        "/habits : training consistency\n"
        "/technique : technical focus\n"
        "/etiquette : mat conduct\n"
        "/dos : what to focus on\n"
        "/donts : what to avoid\n\n"
        "*competition:*\n"
        "/scoring : point system\n"
        "/illegal : banned moves\n\n"
        "*training:*\n"
        "/goal : set weekly goal (max 3)\n"
        "/goals : view all goals\n"
        "/note : log session\n"
        "/notes : view all notes\n"
        "/drill : active drill\n"
        "/drilled : mark as done\n"
        "/toolbox : techniques you know\n"
        "/schedule : set training days\n"
        "/export : save your data\n"
        "/stats : your progress\n"
        "/help : this message\n\n"
        "use /note after each training!"
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_command(update, context)


async def mindset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*mindset & attitude*\n\n"
        "• focus on learning, not winning\n"
        "• be coachable, accept corrections gracefully\n"
        "• celebrate small victories\n\n"
        "_progress is not linear. you'll feel stuck, then it clicks._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def habits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*training habits*\n\n"
        "• write down what you learned after every class\n"
        "• review notes before next session\n"
        "• set small, specific goals\n\n"
        "_example: this week, keep elbows tight_"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def technique_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_database()
    toolbox = _get_toolbox(db)

    keyboard = []
    for cat_id, cat_data in TECHNIQUES.items():
        # count how many techniques in this category the user knows
        total = len(cat_data["items"])
        known = sum(
            1 for tech_id in cat_data["items"]
            if _toolbox_key(cat_id, tech_id) in toolbox
        )
        label = cat_data["name"]
        if known > 0:
            label += f" ({known}/{total} ✓)"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"techcat_{cat_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "*techniques library*\n\nchoose a category:"

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)


async def technique_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    db = load_database()
    toolbox = _get_toolbox(db)

    if data == "tech_main":
        keyboard = []
        for cat_id, cat_data in TECHNIQUES.items():
            total = len(cat_data["items"])
            known = sum(
                1 for tech_id in cat_data["items"]
                if _toolbox_key(cat_id, tech_id) in toolbox
            )
            label = cat_data["name"]
            if known > 0:
                label += f" ({known}/{total} ✓)"
            keyboard.append([InlineKeyboardButton(label, callback_data=f"techcat_{cat_id}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("*techniques library*\n\nchoose a category:", parse_mode="Markdown", reply_markup=reply_markup)
        return

    if data.startswith("techcat_"):
        cat_id = data.split("_")[1]
        if cat_id not in TECHNIQUES:
            return

        category = TECHNIQUES[cat_id]
        keyboard = []
        for tech_id, tech_data in category["items"].items():
            key = _toolbox_key(cat_id, tech_id)
            prefix = "✓ " if key in toolbox else ""
            keyboard.append([InlineKeyboardButton(
                f"{prefix}{tech_data['name']}",
                callback_data=f"techitem_{cat_id}_{tech_id}",
            )])

        keyboard.append([InlineKeyboardButton("« back to categories", callback_data="tech_main")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(f"*{category['name']}*\n\nchoose a technique:", parse_mode="Markdown", reply_markup=reply_markup)

    elif data.startswith("techitem_"):
        parts = data.split("_")
        cat_id = parts[1]
        tech_id = parts[2]

        if cat_id not in TECHNIQUES or tech_id not in TECHNIQUES[cat_id]["items"]:
            return

        tech = TECHNIQUES[cat_id]["items"][tech_id]
        key = _toolbox_key(cat_id, tech_id)
        known = key in toolbox

        text = (
            f"*{tech['name']}*\n\n"
            f"{tech['description']}\n\n"
            f"[watch tutorial]({tech['video_url']})"
        )

        keyboard = [
            [InlineKeyboardButton("set as active drill (2 weeks)", callback_data=f"techdrill_{cat_id}_{tech_id}")],
        ]

        if known:
            keyboard.append([InlineKeyboardButton("✓ in your toolbox — remove", callback_data=f"techunknow_{cat_id}_{tech_id}")])
        else:
            keyboard.append([InlineKeyboardButton("I know this — add to toolbox", callback_data=f"techknow_{cat_id}_{tech_id}")])

        keyboard.append([InlineKeyboardButton("« back", callback_data=f"techcat_{cat_id}")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup, disable_web_page_preview=False)

    elif data.startswith("techknow_"):
        # add technique to toolbox
        parts = data.split("_")
        cat_id = parts[1]
        tech_id = parts[2]

        if cat_id not in TECHNIQUES or tech_id not in TECHNIQUES[cat_id]["items"]:
            return

        tech = TECHNIQUES[cat_id]["items"][tech_id]
        key = _toolbox_key(cat_id, tech_id)

        if key not in toolbox:
            db["toolbox"].append({
                "key": key,
                "name": tech["name"],
                "category": TECHNIQUES[cat_id]["name"],
                "added_at": datetime.now().isoformat(),
            })
            save_database(db)

        # refresh the technique view with updated button
        text = (
            f"*{tech['name']}*\n\n"
            f"{tech['description']}\n\n"
            f"[watch tutorial]({tech['video_url']})"
        )

        keyboard = [
            [InlineKeyboardButton("set as active drill (2 weeks)", callback_data=f"techdrill_{cat_id}_{tech_id}")],
            [InlineKeyboardButton("✓ in your toolbox — remove", callback_data=f"techunknow_{cat_id}_{tech_id}")],
            [InlineKeyboardButton("« back", callback_data=f"techcat_{cat_id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"✓ *{tech['name']}* added to your toolbox!\n\n"
            f"{tech['description']}\n\n"
            f"[watch tutorial]({tech['video_url']})",
            parse_mode="Markdown",
            reply_markup=reply_markup,
            disable_web_page_preview=False,
        )

    elif data.startswith("techunknow_"):
        # remove technique from toolbox
        parts = data.split("_")
        cat_id = parts[1]
        tech_id = parts[2]

        if cat_id not in TECHNIQUES or tech_id not in TECHNIQUES[cat_id]["items"]:
            return

        tech = TECHNIQUES[cat_id]["items"][tech_id]
        key = _toolbox_key(cat_id, tech_id)

        db["toolbox"] = [e for e in db.get("toolbox", []) if e["key"] != key]
        save_database(db)

        text = (
            f"*{tech['name']}*\n\n"
            f"{tech['description']}\n\n"
            f"[watch tutorial]({tech['video_url']})"
        )

        keyboard = [
            [InlineKeyboardButton("set as active drill (2 weeks)", callback_data=f"techdrill_{cat_id}_{tech_id}")],
            [InlineKeyboardButton("I know this — add to toolbox", callback_data=f"techknow_{cat_id}_{tech_id}")],
            [InlineKeyboardButton("« back", callback_data=f"techcat_{cat_id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup, disable_web_page_preview=False)

    elif data.startswith("techdrill_"):
        parts = data.split("_")
        cat_id = parts[1]
        tech_id = parts[2]

        if cat_id not in TECHNIQUES or tech_id not in TECHNIQUES[cat_id]["items"]:
            return

        tech = TECHNIQUES[cat_id]["items"][tech_id]

        db = load_database()

        # 14 days from now
        end_date = datetime.now() + timedelta(days=14)

        db["active_drill"] = {
            "technique": tech['name'],
            "description": tech['description'],
            "video_url": tech['video_url'],
            "start_date": datetime.now().isoformat(),
            "end_date": end_date.isoformat(),
            "drilled_count": 0
        }

        save_database(db)

        text = (
            f"*{tech['name']}* set as your active drill!\n\n"
            "you'll be reminded to drill this for the next 2 weeks.\n"
            "use /drilled when you practice it."
        )

        keyboard = [[InlineKeyboardButton("« back to technique", callback_data=f"techitem_{cat_id}_{tech_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)


async def toolbox_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all techniques the user has marked as known."""
    db = load_database()
    toolbox = db.get("toolbox", [])

    if not toolbox:
        await update.message.reply_text(
            "*your toolbox*\n\n"
            "empty! browse /technique and mark the ones you know.",
            parse_mode="Markdown",
        )
        return

    # group by category
    by_category = {}
    for entry in toolbox:
        cat = entry.get("category", "other")
        by_category.setdefault(cat, []).append(entry["name"])

    # count total techniques available
    total_available = sum(len(cat["items"]) for cat in TECHNIQUES.values())
    total_known = len(toolbox)

    message = f"*your toolbox* ({total_known}/{total_available})\n\n"

    for cat_name, techs in by_category.items():
        message += f"*{cat_name}:*\n"
        for name in techs:
            message += f"  ✓ {name}\n"
        message += "\n"

    message += "_browse /technique to add more_"

    await update.message.reply_text(message, parse_mode="Markdown")


async def etiquette_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*mat etiquette*\n\n"
        "• don't coach from sidelines during rolling unless asked\n"
        "• respect your training partners\n"
        "• ensure your gi and gear are clean\n"
        "• trim your nails and maintain hygiene\n\n"
        "_your training partner is helping you learn._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def dos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*what to do on the mats*\n\n"
        "• keep elbows tight to your body (t-rex arms)\n"
        "• grip with intention, don't burn out your forearms\n"
        "• secure your position before attempting a submission\n"
        "• prioritize defense and survival first\n"
        "• move your hips constantly (shrimp!)\n"
        "• breathe calmly to save energy\n"
        "• tap early to avoid injury, tap often to learn\n\n"
        "_surviving a bad position is your first victory._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def donts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*what not to do*\n\n"
        "• move erratically: always move deliberately with control\n"
        "• do techniques you haven't been taught\n"
        "• reach behind you when someone is on your back: protect your neck, control their hands, work your escape\n"
        "• post hands on mat from bottom: it exposes your arms to kimuras and armbars, frame on your opponent instead\n"
        "• cross ankles when on someone's back: it gives up a free ankle lock, keep hooks in properly\n"
        "• try to submit from inside guard: pass the guard first\n\n"
        "_these mistakes get you submitted or injured._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def scoring_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*competition scoring (ibjjf)*\n"
        "match: 5 min. submission wins instantly.\n"
        "all positions must be held 3s to score.\n\n"
        "*points:*\n"
        "```\n"
        "takedown         +2\n"
        "sweep            +2\n"
        "knee on belly    +2\n"
        "guard pass       +3\n"
        "mount            +4\n"
        "back control     +4\n"
        "```\n\n"
        "*penalties:*\n"
        "```\n"
        "1st foul   +1 advantage to opponent\n"
        "2nd foul   +1 advantage to opponent\n"
        "3rd foul   +2 points to opponent\n"
        "4th foul   disqualification\n"
        "```\n\n"
        "*what earns a foul:*\n"
        "• stalling / not engaging\n"
        "• grabbing inside sleeve or pant\n"
        "• lack of combativeness\n"
        "*serious fouls (instant dq):*\n"
        "• any illegal technique for your belt\n"
        "• slamming opponent\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def illegal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*illegal for white belt*\n\n"
        "• heel hooks\n"
        "• knee reaping\n"
        "• toe holds\n"
        "• bicep/calf slicers\n"
        "• neck cranks\n"
        "• spinal locks without choke\n"
        "• scissors takedown\n"
        "• slamming\n"
        "• flying guard pull\n"
        "• wrist locks\n\n"
        "_immediate dq in competition_"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("cancelled.")
    return ConversationHandler.END
