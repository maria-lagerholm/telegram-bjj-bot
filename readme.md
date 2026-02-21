# bjj training bot

a telegram bot that helps you track your bjj journey from white belt to blue belt. log your sessions, set goals, build a technique toolbox, and get reminders before class.

## getting started

open the bot on telegram and type `/start`. you will see a list of everything the bot can do. type `/help` at any time to see it again.

## after every class

type `/note` and write what you did. include what you practiced, what went well, and what you want to work on.

the bot will:
• save your note with the date and time
• detect if you mention something you want to work on and offer to set it as a goal

## goals

type `/goal` to set something you want to improve. you can have up to 3 active goals at a time.

type `/goals` to see your active goals. from there you can:
• mark a goal as complete
• remove a goal you no longer need
• set a completed goal for spaced repetition refresh (reminders at 1, 2, 3, and 6 months so you don't forget what you learned)

to add more goals, complete or remove one first.

## technique library

type `/technique` to browse the full video library organized by category (escapes, guard passes, sweeps, submissions, takedowns, and more).

when viewing a technique you can:
• **focus on this (2 weeks)** to set it as your current focus
• **I know this, add to toolbox** to mark it as something you already know

## focus

type `/focus` to see the technique you are currently working on. the bot will remind you about it daily.

when you feel comfortable with the technique:
• **learned it, move to toolbox** to add it to your collection of known techniques
• **stop focusing** to clear it without adding to toolbox

you can only have one focus at a time. pick a new one from `/technique` after clearing the current one.

## toolbox

type `/toolbox` to see all the techniques you have marked as known. this is your personal collection that grows as you learn.

techniques in your toolbox show a check mark in the technique library so you can see what you still need to learn.

## training schedule

type `/schedule` to set the days and times you train. the bot will send you a reminder 1 hour before each class with:
• what you did in your last session
• your current goals
• your current focus technique

you can add multiple days, remove individual entries, or clear the whole schedule.

## daily check in

every day the bot asks if you trained today. answer yes or no. this gets logged so you can track how consistent you are and build a training streak.

## stats

type `/stats` to see your overall progress including:
• total training sessions and notes
• current training streak
• active goals and focus
• toolbox size

## export your data

type `/export` to save all your data. you can choose:
• **txt** for a readable summary
• **json** for a full backup

the bot sends the file directly in the chat so you can save or forward it.

## reference material

these commands give you quick access to training advice:

• `/mindset` mental approach and attitude
• `/habits` training consistency tips
• `/etiquette` mat conduct and behavior
• `/dos` what to focus on as a beginner
• `/donts` common mistakes to avoid
• `/scoring` ibjjf competition point system
• `/illegal` banned techniques at white belt

## all commands

• `/help` show all commands
• `/note` log a training session
• `/notes` view your notes
• `/goal` set a goal (max 3)
• `/goals` view and manage goals
• `/focus` current technique focus
• `/technique` browse technique library
• `/toolbox` techniques you know
• `/stats` your progress
• `/schedule` set training days and times
• `/export` save your data
• `/mindset` mental approach
• `/habits` training consistency
• `/etiquette` mat conduct
• `/dos` what to focus on
• `/donts` what to avoid
• `/scoring` competition points
• `/illegal` banned moves

## setup (for developers)

1. get a bot token from [@BotFather](https://t.me/BotFather) on telegram
2. create a `.env` file in the project root:

```
TELEGRAM_BOT_TOKEN=your token here
CHAT_ID=your chat id
```

3. install dependencies: `pip install -r requirements.txt`
4. run the bot: `python main.py`
