from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .techniques_data import all_techniques
from .database import load_database, save_database


def toolbox_key(cat_id, tech_id):
    return f"{cat_id}:{tech_id}"


def get_toolbox(db):
    toolbox_keys = set()
    for entry in db.get("toolbox", []):
        toolbox_keys.add(entry["key"])
    return toolbox_keys


async def technique_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    db = load_database(chat_id)
    toolbox = get_toolbox(db)

    keyboard = []
    for cat_id, cat_data in all_techniques.items():
        total = len(cat_data["items"])
        known = 0
        for tech_id in cat_data["items"]:
            if toolbox_key(cat_id, tech_id) in toolbox:
                known += 1
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
    chat_id = query.message.chat_id
    db = load_database(chat_id)
    toolbox = get_toolbox(db)

    if data == "tech_main":
        keyboard = []
        for cat_id, cat_data in all_techniques.items():
            total = len(cat_data["items"])
            known = 0
            for tech_id in cat_data["items"]:
                if toolbox_key(cat_id, tech_id) in toolbox:
                    known += 1
            label = cat_data["name"]
            if known > 0:
                label += f" ({known}/{total} ✓)"
            keyboard.append([InlineKeyboardButton(label, callback_data=f"techcat_{cat_id}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "*techniques library*\n\nchoose a category:",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
        return

    if data.startswith("techcat_"):
        cat_id = data.split("_")[1]
        if cat_id not in all_techniques:
            return

        category = all_techniques[cat_id]
        keyboard = []
        for tech_id, tech_data in category["items"].items():
            key = toolbox_key(cat_id, tech_id)
            prefix = "✓ " if key in toolbox else ""
            keyboard.append([InlineKeyboardButton(
                f"{prefix}{tech_data['name']}",
                callback_data=f"techitem_{cat_id}_{tech_id}",
            )])

        keyboard.append([InlineKeyboardButton("« back to categories", callback_data="tech_main")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"*{category['name']}*\n\nchoose a technique:",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )

    elif data.startswith("techitem_"):
        parts = data.split("_")
        cat_id = parts[1]
        tech_id = parts[2]

        if cat_id not in all_techniques or tech_id not in all_techniques[cat_id]["items"]:
            return

        tech = all_techniques[cat_id]["items"][tech_id]
        key = toolbox_key(cat_id, tech_id)
        known = key in toolbox

        text = (
            f"*{tech['name']}*\n\n"
            f"{tech['description']}\n\n"
            f"[watch tutorial]({tech['video_url']})"
        )

        keyboard = []

        if known:
            keyboard.append([InlineKeyboardButton("✓ in your toolbox, remove", callback_data=f"techunknow_{cat_id}_{tech_id}")])
        else:
            keyboard.append([InlineKeyboardButton("focus on this (2 weeks)", callback_data=f"techdrill_{cat_id}_{tech_id}")])
            keyboard.append([InlineKeyboardButton("I know this, add to toolbox", callback_data=f"techknow_{cat_id}_{tech_id}")])

        keyboard.append([InlineKeyboardButton("« back", callback_data=f"techcat_{cat_id}")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup, disable_web_page_preview=False)

    elif data.startswith("techknow_"):
        parts = data.split("_")
        cat_id = parts[1]
        tech_id = parts[2]

        if cat_id not in all_techniques or tech_id not in all_techniques[cat_id]["items"]:
            return

        tech = all_techniques[cat_id]["items"][tech_id]
        key = toolbox_key(cat_id, tech_id)

        if key not in toolbox:
            db["toolbox"].append({
                "key": key,
                "name": tech["name"],
                "category": all_techniques[cat_id]["name"],
                "added_at": datetime.now().isoformat(),
            })
            save_database(chat_id, db)

        keyboard = [
            [InlineKeyboardButton("✓ in your toolbox, remove", callback_data=f"techunknow_{cat_id}_{tech_id}")],
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
        parts = data.split("_")
        cat_id = parts[1]
        tech_id = parts[2]

        if cat_id not in all_techniques or tech_id not in all_techniques[cat_id]["items"]:
            return

        tech = all_techniques[cat_id]["items"][tech_id]
        key = toolbox_key(cat_id, tech_id)

        new_toolbox = []
        for entry in db.get("toolbox", []):
            if entry["key"] != key:
                new_toolbox.append(entry)
        db["toolbox"] = new_toolbox
        save_database(chat_id, db)

        keyboard = [
            [InlineKeyboardButton("focus on this (2 weeks)", callback_data=f"techdrill_{cat_id}_{tech_id}")],
            [InlineKeyboardButton("I know this, add to toolbox", callback_data=f"techknow_{cat_id}_{tech_id}")],
            [InlineKeyboardButton("« back", callback_data=f"techcat_{cat_id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"*{tech['name']}*\n\n"
            f"{tech['description']}\n\n"
            f"[watch tutorial]({tech['video_url']})",
            parse_mode="Markdown",
            reply_markup=reply_markup,
            disable_web_page_preview=False,
        )

    elif data.startswith("techdrill_"):
        parts = data.split("_")
        cat_id = parts[1]
        tech_id = parts[2]

        if cat_id not in all_techniques or tech_id not in all_techniques[cat_id]["items"]:
            return

        tech = all_techniques[cat_id]["items"][tech_id]

        db = load_database(chat_id)

        end_date = datetime.now() + timedelta(days=14)

        db["active_drill"] = {
            "technique": tech["name"],
            "description": tech["description"],
            "video_url": tech["video_url"],
            "category": all_techniques[cat_id]["name"],
            "toolbox_key": toolbox_key(cat_id, tech_id),
            "start_date": datetime.now().isoformat(),
            "end_date": end_date.isoformat(),
        }

        save_database(chat_id, db)

        text = (
            f"*{tech['name']}* set as your focus!\n\n"
            "you'll be reminded about this for the next 2 weeks.\n"
            "use /focus to see it or move it to your toolbox when you've got it down."
        )

        keyboard = [[InlineKeyboardButton("« back to technique", callback_data=f"techitem_{cat_id}_{tech_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)


async def toolbox_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    db = load_database(chat_id)
    toolbox = db.get("toolbox", [])

    if not toolbox:
        await update.message.reply_text(
            "*your toolbox*\n\n"
            "empty! browse /technique and mark the ones you know.",
            parse_mode="Markdown",
        )
        return

    by_category = {}
    for entry in toolbox:
        cat = entry.get("category", "other")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(entry["name"])

    total_available = 0
    for cat in all_techniques.values():
        total_available += len(cat["items"])
    total_known = len(toolbox)

    message = f"*your toolbox* ({total_known}/{total_available})\n\n"

    for cat_name, techs in by_category.items():
        message += f"*{cat_name}:*\n"
        for name in techs:
            message += f"  ✓ {name}\n"
        message += "\n"

    message += "_browse /technique to add more_"

    await update.message.reply_text(message, parse_mode="Markdown")
