# bjj training bot

a telegram bot that helps you track your bjj journey as a white belt.

## what it does

**protocol commands** (reference material from your guide)
* `/mindset` : mental approach and attitude
* `/habits` : training consistency tips
* `/technique` : technical focus points
* `/etiquette` : mat conduct
* `/donts` : common mistakes to avoid
* `/scoring` : ibjjf competition point system
* `/illegal` : banned techniques for white belt

**training commands** (track your progress)
* `/goal` : set a goal for the current week
* `/goals` : view current and past goals
* `/note` : log a training session
* `/notes` : view your training notes
* `/drill` : add a technique to practice
* `/drills` : view your drill queue
* `/drilled` : mark a technique as practiced
* `/stats` : see your training stats

**automatic features**
* detects technique names in your notes and adds them to your drill queue
* daily drill reminder at 9:00 am (picks the 3 you need most)
* weekly goal reminder on monday at 8:00 am

## setup

1. get a bot token from [@BotFather](https://t.me/BotFather) on telegram

2. create a `.env` file in the project root:
