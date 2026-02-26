# AGENTS.md

## Cursor Cloud specific instructions

### Overview
This is a Python Telegram bot for tracking BJJ (Brazilian Jiu-Jitsu) training. It is a single-process application (`python main.py`) using `python-telegram-bot` v22.6 with polling, flat JSON file storage (in `data/`), Pillow-based image generation, and optional Google Gemini AI chat.

### Running the bot
- Requires a valid `TELEGRAM_BOT_TOKEN` in `.env` (see `readme.md` "setup for developers").
- `GEMINI_API_KEY` is optional; without it all `/command`-based features work but free-text/voice AI chat replies with "ai chat is not available right now".
- Start: `python main.py` — the process runs forever (polling). It will exit immediately if no valid token is set.

### Linting
- No project-level linter config exists. Use `flake8 --max-line-length=120 .` for basic checks.
- Pre-existing lint warnings (mostly E501 line-length in `techniques_data.py` and a few F-codes) are part of the baseline.

### Testing
- No test suite exists in the repo. Core offline modules can be tested with quick Python scripts:
  - `modules/database.py` — JSON load/save, no external deps.
  - `modules/note_image.py` — generates PNG buffers from note data.
  - `modules/app_map.py` — generates the app-map PNG.
  - `modules/techniques_data.py` — data-only module (`all_techniques` dict).
- Bot handler testing requires a live Telegram bot token.

### Key gotchas
- The `data/` directory is auto-created by `database.py` on import. It is gitignored.
- `.env` is gitignored. You must create it manually with at least `TELEGRAM_BOT_TOKEN=...`.
- Fonts live in `/workspace/fonts/` and are bundled in the repo (no install needed).
- The app uses `Europe/Stockholm` timezone (`modules/helpers.py`).
