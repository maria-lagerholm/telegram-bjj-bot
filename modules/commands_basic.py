from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


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
        "/goal : set weekly goal\n"
        "/goals : view all goals\n"
        "/note : log session\n"
        "/notes : view all notes\n"
        "/drill : add technique\n"
        "/drills : view queue\n"
        "/drilled : mark as done\n"
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
    text = (
        "*technical focus*\n\n"
        "• keep elbows tight (t-rex arms)\n"
        "• grip with intention, not desperation\n"
        "• focus on position before submission\n"
        "• learn fundamental positions: mount, side control, guard, back, turtle\n"
        "• prioritize defense and escapes\n"
        "• move your hips, not just arms\n"
        "• play guard\n"
        "• drill basics: shrimps, bridges, technical standup\n\n"
        "_the best white belt skill is being hard to submit._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def etiquette_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*mat etiquette*\n\n"
        "• don't coach from sidelines during rolling unless asked\n"
        "• always move deliberately with control\n"
        "• tap early, tap often\n"
        "• respect your training partners\n\n"
        "_your training partner is helping you learn._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def dos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*what to do*\n\n"
        "• keep elbows tight (t-rex arms)\n"
        "• grip with intention, not desperation\n"
        "• focus on position before submission\n"
        "• prioritize defense and escapes\n"
        "• move your hips, not just arms\n"
        "• play guard\n"
        "• drill basics: shrimps, bridges, technical standup\n"
        "• tap early, tap often\n"
        "_be hard to submit. that's the best white belt skill._"
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
        "*penalties (each foul escalates):*\n"
        "```\n"
        "1st foul   +1 advantage to opponent\n"
        "2nd foul   +1 advantage to opponent\n"
        "3rd foul   +2 points to opponent\n"
        "4th foul   disqualification\n"
        "```\n\n"
        "*what earns a foul:*\n"
        "• stalling / not engaging\n"
        "• fleeing the mat\n"
        "• grabbing inside sleeve or pant\n"
        "• lack of combativeness\n"
        "• talking to ref without permission\n\n"
        "*serious fouls (instant dq):*\n"
        "• any illegal technique for your belt\n"
        "• slamming opponent\n"
        "• striking or biting\n\n"
        "*tiebreaker order:*\n"
        "points > advantages > ref decision"
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
