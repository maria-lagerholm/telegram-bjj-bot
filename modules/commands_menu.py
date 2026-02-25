from datetime import timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .techniques_data import all_techniques
from .database import load_database
from .commands_techniques import toolbox_key, get_toolbox
from .app_map import render_app_map
from .helpers import now_se


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 my training", callback_data="menu_training")],
        [InlineKeyboardButton("📚 learn", callback_data="menu_learn")],
        [InlineKeyboardButton("🥋 bjj knowledge", callback_data="menu_knowledge")],
        [InlineKeyboardButton("⚙️ settings", callback_data="menu_settings")],
    ])


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "*bjj training bot*\n\n"
        "welcome! choose a section below to get started.\n"
        "use /note after each training!"
    )
    await update.message.reply_text(
        welcome_message,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_command(update, context)


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_main":
        await query.edit_message_text(
            "*bjj training bot*\n\n"
            "choose a section below to get started.\n"
            "use /note after each training!",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )

    elif data == "menu_training":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("write a note", callback_data="menucmd_note")],
            [InlineKeyboardButton("view my notes", callback_data="menucmd_notes")],
            [InlineKeyboardButton("manage notes", callback_data="menucmd_journal")],
            [InlineKeyboardButton("set a goal (max 3)", callback_data="menucmd_goal")],
            [InlineKeyboardButton("view my goals", callback_data="menucmd_goals")],
            [InlineKeyboardButton("current focus", callback_data="menucmd_focus")],
            [InlineKeyboardButton("my progress", callback_data="menucmd_stats")],
            [InlineKeyboardButton("« back", callback_data="menu_main")],
        ])
        await query.edit_message_text(
            "*📝 my training*\n\n"
            "track your sessions, goals, and progress.",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

    elif data == "menu_learn":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("technique library", callback_data="menucmd_technique")],
            [InlineKeyboardButton("my toolbox", callback_data="menucmd_toolbox")],
            [InlineKeyboardButton("« back", callback_data="menu_main")],
        ])
        await query.edit_message_text(
            "*📚 learn*\n\n"
            "browse techniques and track what you know.",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

    elif data == "menu_knowledge":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("mindset", callback_data="menucmd_mindset")],
            [InlineKeyboardButton("training habits", callback_data="menucmd_habits")],
            [InlineKeyboardButton("mat etiquette", callback_data="menucmd_etiquette")],
            [InlineKeyboardButton("what to do", callback_data="menucmd_dos")],
            [InlineKeyboardButton("what not to do", callback_data="menucmd_donts")],
            [InlineKeyboardButton("competition scoring", callback_data="menucmd_scoring")],
            [InlineKeyboardButton("illegal moves", callback_data="menucmd_illegal")],
            [InlineKeyboardButton("« back", callback_data="menu_main")],
        ])
        await query.edit_message_text(
            "*🥋 bjj knowledge*\n\n"
            "tips, rules, and etiquette for the mats.",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

    elif data == "menu_settings":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("training schedule", callback_data="menucmd_schedule")],
            [InlineKeyboardButton("reminder times", callback_data="menucmd_reminders")],
            [InlineKeyboardButton("export my data", callback_data="menucmd_export")],
            [InlineKeyboardButton("import backup", callback_data="menucmd_import")],
            [InlineKeyboardButton("app map", callback_data="menucmd_map")],
            [InlineKeyboardButton("developer", url="https://www.linkedin.com/in/marialagerholm/")],
            [InlineKeyboardButton("« back", callback_data="menu_main")],
        ])
        await query.edit_message_text(
            "*⚙️ settings*\n\n"
            "manage your schedule, reminders, and data.",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )


async def menucmd_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cmd = query.data.replace("menucmd_", "")

    if cmd in ("note", "goal", "journal"):
        await query.message.reply_text(
            f"type /{cmd} to get started.",
        )
        return

    if cmd == "import":
        await query.message.reply_text(
            "type /import to start restoring a backup.",
        )
        return

    await dispatch_menu_command(cmd, query, context)


async def dispatch_menu_command(cmd, query, context):
    chat_id = query.message.chat_id

    info_commands = {
        "mindset": (
            "*mindset & attitude*\n\n"
            "• focus on learning, not winning\n"
            "• be coachable, accept corrections gracefully\n"
            "• celebrate small victories\n\n"
            "_progress is not linear. you'll feel stuck, then it clicks._"
        ),
        "habits": (
            "*training habits*\n\n"
            "• write down what you learned after every class\n"
            "• review notes before next session\n"
            "• set small, specific goals\n\n"
            "_example: this week, keep elbows tight_"
        ),
        "etiquette": (
            "*mat etiquette*\n\n"
            "• don't coach from sidelines during rolling unless asked\n"
            "• respect your training partners\n"
            "• ensure your gi and gear are clean\n"
            "• trim your nails and maintain hygiene\n\n"
            "_your training partner is helping you learn._"
        ),
        "dos": (
            "*what to do on the mats*\n\n"
            "• keep elbows tight to your body (t-rex arms)\n"
            "• grip with intention, don't burn out your forearms\n"
            "• secure your position before attempting a submission\n"
            "• prioritize defense and survival first\n"
            "• move your hips constantly (shrimp!)\n"
            "• breathe calmly to save energy\n"
            "• tap early to avoid injury, tap often to learn\n\n"
            "_surviving a bad position is your first victory._"
        ),
        "donts": (
            "*what not to do*\n\n"
            "• move erratically: always move deliberately with control\n"
            "• do techniques you haven't been taught\n"
            "• reach behind you when someone is on your back: protect your neck, control their hands, work your escape\n"
            "• post hands on mat from bottom: it exposes your arms to kimuras and armbars, frame on your opponent instead\n"
            "• cross ankles when on someone's back: it gives up a free ankle lock, keep hooks in properly\n"
            "• try to submit from inside guard: pass the guard first\n\n"
            "_these mistakes get you submitted or injured._"
        ),
        "scoring": (
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
        ),
        "illegal": (
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
        ),
    }

    if cmd in info_commands:
        await query.message.reply_text(info_commands[cmd], parse_mode="Markdown")
        return

    if cmd == "technique":
        db = load_database(chat_id)
        toolbox_set = get_toolbox(db)
        keyboard = []
        for cat_id, cat_data in all_techniques.items():
            total = len(cat_data["items"])
            known = 0
            for tech_id in cat_data["items"]:
                if toolbox_key(cat_id, tech_id) in toolbox_set:
                    known += 1
            label = cat_data["name"]
            if known > 0:
                label += f" ({known}/{total} ✓)"
            keyboard.append([InlineKeyboardButton(label, callback_data=f"techcat_{cat_id}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "*techniques library*\n\nchoose a category:",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
        return

    if cmd == "toolbox":
        db = load_database(chat_id)
        toolbox = db.get("toolbox", [])
        if not toolbox:
            await query.message.reply_text(
                "*your toolbox*\n\nempty! browse /technique and mark the ones you know.",
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
        await query.message.reply_text(message, parse_mode="Markdown")
        return

    if cmd == "notes":
        from .commands_notes import send_notes_page
        await send_notes_page(query.message, chat_id, page=1)
        return

    if cmd == "goals":
        db = load_database(chat_id)
        goals = db.get("goals", [])
        if not goals:
            await query.message.reply_text("no goals yet. use /goal!")
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
            for g in active_goals:
                message += f"  • {g['goals']}  _({g.get('week', '')})_\n"
            message += "\n"
        if completed_goals:
            last_five = completed_goals[-5:]
            message += "*completed:*\n"
            for g in reversed(last_five):
                message += f"  ✓ ~{g['goals']}~\n"
            if len(completed_goals) > 5:
                message += f"  _…and {len(completed_goals) - 5} more_\n"
            message += "\n"
        if not active_goals and not completed_goals:
            message += "all goals removed. use /goal to set a new one!\n"
        keyboard = []
        for g in active_goals:
            gid = g.get("id", "")
            if not gid:
                continue
            short = g["goals"][:20]
            if len(g["goals"]) > 20:
                short += "…"
            keyboard.append([
                InlineKeyboardButton(f"✓ {short}", callback_data=f"goal_done_{gid}"),
                InlineKeyboardButton("✕", callback_data=f"goal_rm_{gid}"),
            ])
        if keyboard:
            message += "_tap ✓ to complete, ✕ to remove_"
            await query.message.reply_text(
                message,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await query.message.reply_text(message, parse_mode="Markdown")
        return

    if cmd == "focus":
        db = load_database(chat_id)
        active_drill = db.get("active_drill")
        if not active_drill:
            await query.message.reply_text(
                "*current focus*\n\nyou have no focus technique set.\n\n"
                "use /technique to browse the library and pick one to focus on.",
                parse_mode="Markdown",
            )
            return
        start_date = active_drill.get("start_date", "")[:10]
        days_left = 0
        try:
            end_dt = datetime.fromisoformat(active_drill["end_date"])
            days_left = max(0, (end_dt - now_se()).days)
        except (ValueError, KeyError):
            pass
        message = (
            "*current focus*\n\n"
            f"*{active_drill['technique']}*\n"
            f"_{active_drill.get('description', '')}_\n\n"
            f"started: {start_date}\n"
            f"time left: {days_left} days\n\n"
            f"[watch tutorial]({active_drill.get('video_url', '')})"
        )
        keyboard = [
            [InlineKeyboardButton("✓ learned it, move to toolbox", callback_data="focus_totoolbox")],
            [InlineKeyboardButton("✕ stop focusing", callback_data="focus_stop")],
        ]
        await query.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if cmd == "stats":
        db = load_database(chat_id)
        total_notes = len(db.get("notes", []))
        active_goals = 0
        completed_goals = 0
        for g in db.get("goals", []):
            if g.get("status", "active") == "active":
                active_goals += 1
            elif g.get("status") == "completed":
                completed_goals += 1
        active_drill = db.get("active_drill")
        if active_drill:
            focus_text = active_drill["technique"]
        else:
            focus_text = "none"
        notes = db.get("notes", [])
        first_date = "n/a"
        this_week_notes = 0
        if notes:
            all_dates = set()
            for n in notes:
                all_dates.add(n["date"])
            first_date = sorted(all_dates)[0]
            seven_ago = (now_se() - timedelta(days=7)).strftime("%Y-%m-%d")
            for n in notes:
                if n["date"] >= seven_ago:
                    this_week_notes += 1
        training_log = db.get("training_log", [])
        days_trained = 0
        for e in training_log:
            if e["trained"]:
                days_trained += 1
        days_rest = len(training_log) - days_trained
        seven_ago_str = (now_se() - timedelta(days=7)).strftime("%Y-%m-%d")
        thirty_ago_str = (now_se() - timedelta(days=30)).strftime("%Y-%m-%d")
        week_trained = 0
        month_trained = 0
        for e in training_log:
            if e["trained"] and e["date"] >= seven_ago_str:
                week_trained += 1
            if e["trained"] and e["date"] >= thirty_ago_str:
                month_trained += 1
        streak = 0
        current = now_se().date()
        trained_dates = []
        for e in training_log:
            if e["trained"]:
                trained_dates.append(e["date"])
        trained_dates.sort(reverse=True)
        for d in trained_dates:
            if datetime.strptime(d, "%Y-%m-%d").date() == current:
                streak += 1
                current = current - timedelta(days=1)
            else:
                break
        toolbox = db.get("toolbox", [])
        total_techniques = 0
        for cat in all_techniques.values():
            total_techniques += len(cat["items"])
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
        message += (
            f"\n*progress:*\n"
            f"  focus: *{focus_text}*\n"
            f"  goals: *{active_goals}* active, *{completed_goals}* completed\n"
            f"  toolbox: *{len(toolbox)}/{total_techniques}* techniques\n"
            f"  notes: *{total_notes}* total, *{this_week_notes}* this week\n"
        )
        drill_history = db.get("drill_queue", [])
        learned = 0
        for d in drill_history:
            if d.get("outcome") == "toolbox":
                learned += 1
        if drill_history:
            message += f"  past focuses: *{len(drill_history)}* ({learned} moved to toolbox)\n"
        if notes:
            message += f"\n_training since {first_date}_"
        await query.message.reply_text(message, parse_mode="Markdown")
        return

    if cmd == "reminders":
        from .commands_reminders import reminder_labels, reminder_defaults
        db = load_database(chat_id)
        rt = db.get("reminder_times", reminder_defaults)
        message = "*your reminder times*\n\n"
        for key, label in reminder_labels.items():
            current = rt.get(key, reminder_defaults[key])
            message += f"  • {label}: *{current}*\n"
        message += "\ntap a reminder to change its time:"
        keyboard = []
        for key, label in reminder_labels.items():
            short_label = label[:30]
            keyboard.append([InlineKeyboardButton(
                f"change: {short_label}",
                callback_data=f"remtime_pick_{key}",
            )])
        await query.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if cmd == "map":
        img_buf = render_app_map()
        await query.message.reply_photo(
            photo=img_buf,
            caption="here's how the bot is organized. tap /help to open the menu.",
        )
        return

    await query.message.reply_text(f"type /{cmd} to continue.")
