from datetime import datetime, timedelta

from .database import load_database, save_database
from .techniques_data import all_techniques
from .helpers import find_techniques_in_text


tool_get_notes = {
    "name": "get_training_notes",
    "description": (
        "Retrieve the user's recent training notes. "
        "Call this when the user asks about their notes, training history, "
        "what they practiced, or what they learned."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "count": {
                "type": "integer",
                "description": "How many recent notes to return. Default 5, max 15.",
            }
        },
    },
}

tool_get_goals = {
    "name": "get_goals",
    "description": (
        "Retrieve the user's active and recently completed goals. "
        "Call this when the user asks about their goals, progress, or what to work on."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
    },
}

tool_get_schedule = {
    "name": "get_schedule",
    "description": (
        "Retrieve the user's training schedule (days and times). "
        "Call this when the user asks about their schedule or upcoming training."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
    },
}

tool_get_focus = {
    "name": "get_focus_and_toolbox",
    "description": (
        "Retrieve the user's current focus technique and their toolbox of known techniques. "
        "Call this when the user asks about what technique they are drilling, "
        "what they already know, or their toolbox."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
    },
}

tool_get_stats = {
    "name": "get_training_stats",
    "description": (
        "Retrieve the user's training statistics: sessions this week, streak, "
        "total notes, total goals completed. "
        "Call this when the user asks about their stats, progress, or activity."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
    },
}

tool_search_technique = {
    "name": "search_technique",
    "description": (
        "Search the technique database for a BJJ technique by name. "
        "Call this whenever the user mentions a technique, submission, sweep, "
        "escape, pass, takedown, or position. Returns the technique details, "
        "video link, and available actions (set as focus, add to toolbox). "
        "ALWAYS call this when a technique name appears in the conversation."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The technique name to search for, e.g. 'kimura', 'armbar', 'scissor sweep'.",
            }
        },
        "required": ["query"],
    },
}

tool_list_techniques = {
    "name": "list_techniques",
    "description": (
        "List available BJJ techniques. "
        "If a category is given (escapes, submissions, sweeps, guardpasses, "
        "takedowns, positions, ukemi, selfdefense), list all techniques in that category. "
        "If no category is given, list all category names. "
        "ALWAYS call this when the user asks what techniques are available, "
        "what they can practice, or asks to see a list of techniques."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": (
                    "Category to list. One of: escapes, submissions, sweeps, "
                    "guardpasses, takedowns, positions, ukemi, selfdefense. "
                    "Leave empty to list all categories."
                ),
            }
        },
    },
}

tool_save_note = {
    "name": "save_training_note",
    "description": (
        "Save a training note for the user. "
        "Call this ONLY after the user has confirmed they want to save. "
        "When the user describes what they practiced, trained, or learned, "
        "first ask if they want to save it as a note. "
        "If they say yes, call this tool with the note text. "
        "The note must be between 1 and 20 words."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "note_text": {
                "type": "string",
                "description": "The training note text to save (1 to 20 words).",
            }
        },
        "required": ["note_text"],
    },
}

all_tools = [
    tool_get_notes,
    tool_get_goals,
    tool_get_schedule,
    tool_get_focus,
    tool_get_stats,
    tool_search_technique,
    tool_list_techniques,
    tool_save_note,
]

# Action-only tools: these actually do something or search.
# Read tools (notes, goals, schedule, focus, stats) are pre-fetched into the system prompt.
action_tools = [
    tool_search_technique,
    tool_list_techniques,
    tool_save_note,
]


def exec_get_notes(chat_id, args):
    db = load_database(chat_id)
    notes = db.get("notes", [])
    if not notes:
        return "User has no training notes yet.\nCOMMAND: /note to log your first note"
    count = min(int(args.get("count", 5)), 15)
    recent = notes[-count:]
    lines = []
    for n in recent:
        d = n.get("date", "")
        t = n.get("time", "")
        text = n.get("text", "")
        lines.append(f"{d} {t}: {text}")
    lines.append(f"\nCOMMAND: /notes to view all notes, /note to add a new one")
    return "\n".join(lines)


def exec_get_goals(chat_id, _args):
    db = load_database(chat_id)
    active = []
    completed = []
    for g in db.get("goals", []):
        s = g.get("status", "active")
        if s == "active":
            active.append(g["goals"])
        elif s == "completed":
            completed.append(g["goals"])
    parts = []
    if active:
        parts.append("Active goals: " + ", ".join(active))
    else:
        parts.append("No active goals.")
    if completed:
        parts.append("Completed goals (recent): " + ", ".join(completed[-5:]))
    parts.append(f"\nCOMMAND: /goals to manage goals, /goal to set a new one")
    return "\n".join(parts)


def exec_get_schedule(chat_id, _args):
    db = load_database(chat_id)
    schedule = db.get("schedule", [])
    if not schedule:
        return "No training schedule set.\nCOMMAND: /schedule to set your training days and times"
    entries = []
    for s in schedule:
        entries.append(f"{s['day']} at {s['time']}")
    return "Training schedule: " + ", ".join(entries) + "\nCOMMAND: /schedule to change your schedule"


def exec_get_focus(chat_id, _args):
    db = load_database(chat_id)
    parts = []
    drill = db.get("active_drill")
    if drill:
        parts.append(f"Current focus: {drill['technique']}")
    else:
        parts.append("No focus technique set.")
    toolbox = db.get("toolbox", [])
    if toolbox:
        names = [t["name"] for t in toolbox[:20]]
        parts.append(f"Toolbox ({len(toolbox)} techniques): " + ", ".join(names))
    else:
        parts.append("Toolbox is empty.")
    parts.append(f"\nCOMMAND: /focus to set or change focus, /toolbox to view known techniques, /technique to browse all")
    return "\n".join(parts)


def exec_get_stats(chat_id, _args):
    db = load_database(chat_id)
    total_notes = len(db.get("notes", []))
    log = db.get("training_log", [])
    trained = 0
    for e in log:
        if e.get("trained"):
            trained += 1
    seven_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    week_count = 0
    for e in log:
        if e.get("trained") and e["date"] >= seven_ago:
            week_count += 1
    active_goals = 0
    done_goals = 0
    for g in db.get("goals", []):
        if g.get("status") == "active":
            active_goals += 1
        elif g.get("status") == "completed":
            done_goals += 1
    streak = 0
    current = datetime.now().date()
    sorted_dates = []
    for e in log:
        if e.get("trained"):
            sorted_dates.append(e["date"])
    sorted_dates.sort(reverse=True)
    for ds in sorted_dates:
        if datetime.strptime(ds, "%Y-%m-%d").date() == current:
            streak += 1
            current = current - timedelta(days=1)
        else:
            break
    return (
        f"Sessions this week: {week_count}. "
        f"Total trained: {trained} days. "
        f"Streak: {streak} days. "
        f"Notes: {total_notes}. "
        f"Goals: {active_goals} active, {done_goals} completed."
        f"\nCOMMAND: /stats for full stats, /goals to manage goals, /notes to view notes"
    )


def exec_search_technique(_chat_id, args):
    query = args.get("query", "").lower().strip()
    if not query:
        return "No technique name provided."

    matches = []
    for category_key, category in all_techniques.items():
        for tech_key, tech in category.get("items", {}).items():
            name = tech.get("name", "").lower()
            if query in name or query in tech_key:
                matches.append(tech)

    if not matches:
        for category_key, category in all_techniques.items():
            for tech_key, tech in category.get("items", {}).items():
                name = tech.get("name", "").lower()
                words = query.split()
                for w in words:
                    if w in name or w in tech_key:
                        matches.append(tech)
                        break

    if not matches:
        return f"No technique found for '{query}'. Try a different name or use /technique to browse all.\nCOMMAND: /technique to browse all techniques"

    results = []
    for tech in matches[:10]:
        name = tech.get("name", "")
        desc = tech.get("description", "")
        video = tech.get("video_url", "")
        line = f"TECHNIQUE: {name}\nDESCRIPTION: {desc}"
        if video:
            line += f"\nEXACT_VIDEO_URL: {video}"
        results.append(line)

    results.append("COMMAND: /focus to set as focus technique, /toolbox to view known techniques")
    return "\n---\n".join(results)


def exec_list_techniques(_chat_id, args):
    category = args.get("category", "").lower().strip()

    if not category:
        lines = []
        for cat_key, cat in all_techniques.items():
            count = len(cat.get("items", {}))
            lines.append(f"{cat.get('name', cat_key)} ({count} techniques)")
        lines.append("\nCOMMAND: /technique to browse all techniques")
        return "Available categories:\n" + "\n".join(lines)

    cat = all_techniques.get(category)
    if not cat:
        for cat_key, cat_val in all_techniques.items():
            if category in cat_key or category in cat_val.get("name", "").lower():
                cat = cat_val
                break

    if not cat:
        return f"No category '{category}' found. Available: escapes, submissions, sweeps, guardpasses, takedowns, positions, ukemi, selfdefense."

    items = cat.get("items", {})
    lines = [f"Category: {cat.get('name', category)} ({len(items)} techniques)\n"]
    i = 1
    for tech_key, tech in items.items():
        name = tech.get("name", tech_key)
        video = tech.get("video_url", "")
        line = f"{i}. {name}"
        if video:
            line += f"\n   EXACT_VIDEO_URL: {video}"
        lines.append(line)
        i += 1

    lines.append("\nCOMMAND: /focus to set a technique as focus, /toolbox to view known techniques, /technique to browse all")
    return "\n".join(lines)


def exec_save_note(chat_id, args):
    note_text = args.get("note_text", "").strip()
    if not note_text:
        return "ERROR: empty note, nothing saved."

    word_count = len(note_text.split())
    if word_count > 20:
        return f"ERROR: note is {word_count} words, max 20. Ask the user to shorten it."
    if word_count < 1:
        return "ERROR: note is empty."

    db = load_database(chat_id)
    now = datetime.now()
    techniques_found = find_techniques_in_text(note_text)

    new_note = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "day": now.strftime("%A"),
        "text": note_text,
        "techniques": techniques_found,
        "created_at": now.isoformat(),
    }
    db["notes"].append(new_note)
    save_database(chat_id, db)

    result = f"Note saved: \"{note_text}\""
    if techniques_found:
        result += f" (detected techniques: {', '.join(techniques_found)})"
    result += "\nCOMMAND: /notes to view all notes, /goal to set a goal based on this"
    return result


tool_executors = {
    "get_training_notes": exec_get_notes,
    "get_goals": exec_get_goals,
    "get_schedule": exec_get_schedule,
    "get_focus_and_toolbox": exec_get_focus,
    "get_training_stats": exec_get_stats,
    "search_technique": exec_search_technique,
    "list_techniques": exec_list_techniques,
    "save_training_note": exec_save_note,
}
