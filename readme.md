# bjj training bot

a telegram bot that helps you track your bjj journey. log sessions, set goals, build a technique toolbox, chat with an AI training partner, and get reminders before class.

each user has their own saved data. clearing the chat or starting a new one does not erase anything.

## quick start

open the bot on telegram and type `/start`. a menu appears with four sections: my training, learn, bjj knowledge, and settings. type `/help` at any time to reopen it.

you can also just send a text or voice message and the AI will help you.

## ai chat

send any text or voice message and the bot responds like a training partner. it knows your notes, goals, schedule, focus, and stats. you can ask it about techniques, save notes by voice, set a focus, add goals, or update your schedule just by chatting.

the bot speaks whatever language you write in.

## notes

type `/note` and write what you did (1 to 20 words). the bot saves it with the date and time, then offers to set a goal based on what you wrote.

type `/notes` to view your notes as handwritten style images. pages are numbered and you can go forward or back.

## goals

type `/goal` to set something you want to improve (1 to 7 words). you can have up to 3 active goals.

type `/goals` to see your active goals. from there you can mark one as complete, remove it, or set a completed goal for spaced repetition (reminders at 1, 2, 3, and 6 months).

to add more goals, complete or remove one first.

## technique library

type `/technique` to browse the video library organized by category: escapes, guard passes, sweeps, submissions, takedowns, and more.

when viewing a technique you can:
- focus on it for 2 weeks
- mark it as known and add it to your toolbox

## focus

type `/focus` to see the technique you are working on. the bot reminds you about it daily.

when you feel comfortable:
- move it to your toolbox
- stop focusing to clear it

you can only have one focus at a time. pick a new one from `/technique` after clearing the current one.

## toolbox

type `/toolbox` to see all techniques you marked as known. techniques in your toolbox show a check mark in the library so you can see what you still need to learn.

## training schedule

type `/schedule` to set the days and times you train (half hour slots supported). the bot sends a reminder 1 hour before each class with your last session, current goals, and focus technique. after training it reminds you to take a note.

you can add multiple days, remove individual entries, or clear the whole schedule.

## daily check in

every day the bot asks if you trained. your answer gets logged so you can track consistency and build a training streak.

## stats

type `/stats` to see your progress: sessions this week and month, training streak, active goals, focus, toolbox size, and total notes.

## reminders

type `/reminders` to customize the time for each reminder: daily check in, daily focus, weekly goal review (Monday), and spaced repetition refresh.

## export and import

type `/export` to download your data as a readable txt or a full json backup. the bot sends the file directly in the chat.

type `/import` to restore a json backup (max 1 MB).

## app map

type `/map` to see a visual tree of how the bot is organized.

## bjj knowledge

quick reference material available from the menu or by command:

- `/mindset` mental approach
- `/habits` training consistency
- `/etiquette` mat conduct
- `/dos` what to focus on
- `/donts` common mistakes
- `/scoring` ibjjf competition points
- `/illegal` banned moves at white belt

## all commands

| command | what it does |
|---|---|
| `/start` | open the bot |
| `/help` | open the menu |
| `/note` | log a training session |
| `/notes` | view your notes |
| `/goal` | set a goal (max 3) |
| `/goals` | view and manage goals |
| `/focus` | current technique focus |
| `/technique` | browse technique library |
| `/toolbox` | techniques you know |
| `/stats` | your progress |
| `/schedule` | set training days and times |
| `/reminders` | customize reminder times |
| `/export` | save your data |
| `/import` | restore a backup |
| `/map` | visual app map |
| `/cancel` | cancel current action |

## setup for developers

1. get a bot token from [@BotFather](https://t.me/BotFather) on telegram
2. create a `.env` file in the project root:

```
TELEGRAM_BOT_TOKEN=your token here
GEMINI_API_KEY=your gemini api key here
MONTHLY_AI_LIMIT=10000
```

to get a free Gemini API key go to [aistudio.google.com](https://aistudio.google.com), sign in, and create an API key. paste it into the `.env` file.

3. install dependencies: `pip install -r requirements.txt`
4. run the bot: `python main.py`

user data is stored as json files in the `data/` folder, one file per user. the bot supports hundreds of users on a 1 GB server.
