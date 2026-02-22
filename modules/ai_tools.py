import uuid
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

tool_set_focus = {
    "name": "set_focus_technique",
    "description": (
        "Set a BJJ technique as the user's current focus for 2 weeks. "
        "Call this when the user says they want to focus on, drill, or practice a specific technique. "
        "First call search_technique to find the exact technique, then call this with the technique key. "
        "The technique_key must be in the format 'category:techid' (e.g. 'submissions:kimura')."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "technique_key": {
                "type": "string",
                "description": "The technique key in format 'category:techid', e.g. 'submissions:kimura'.",
            }
        },
        "required": ["technique_key"],
    },
}

tool_add_goal = {
    "name": "add_goal",
    "description": (
        "Add a new training goal for the user. "
        "Call this when the user says they want to set a goal or work on something specific. "
        "The goal must be 1 to 7 words. The user can have at most 3 active goals. "
        "Ask the user to confirm before saving."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "goal_text": {
                "type": "string",
                "description": "The goal text (1 to 7 words).",
            }
        },
        "required": ["goal_text"],
    },
}

tool_add_schedule = {
    "name": "add_schedule_entry",
    "description": (
        "Add a training day and time to the user's schedule. "
        "Call this when the user says they train on a specific day and time. "
        "Day must be one of: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday. "
        "Time must be in HH:MM format (e.g. '18:30')."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "day": {
                "type": "string",
                "description": "Day of the week, e.g. 'Monday', 'Tuesday'.",
            },
            "time": {
                "type": "string",
                "description": "Time in HH:MM format, e.g. '18:30'.",
            },
        },
        "required": ["day", "time"],
    },
}

tool_add_to_toolbox = {
    "name": "add_to_toolbox",
    "description": (
        "Mark a technique as known and add it to the user's toolbox. "
        "Call this when the user says they already know a technique. "
        "The technique_key must be in the format 'category:techid' (e.g. 'submissions:kimura')."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "technique_key": {
                "type": "string",
                "description": "The technique key in format 'category:techid', e.g. 'submissions:kimura'.",
            }
        },
        "required": ["technique_key"],
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
    tool_set_focus,
    tool_add_goal,
    tool_add_schedule,
    tool_add_to_toolbox,
]

# Action-only tools: these actually do something or search.
# Read tools (notes, goals, schedule, focus, stats) are pre-fetched into the system prompt.
action_tools = [
    tool_search_technique,
    tool_list_techniques,
    tool_save_note,
    tool_set_focus,
    tool_add_goal,
    tool_add_schedule,
    tool_add_to_toolbox,
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
                matches.append((category_key, tech_key, tech))

    if not matches:
        for category_key, category in all_techniques.items():
            for tech_key, tech in category.get("items", {}).items():
                name = tech.get("name", "").lower()
                words = query.split()
                for w in words:
                    if w in name or w in tech_key:
                        matches.append((category_key, tech_key, tech))
                        break

    if not matches:
        return f"No technique found for '{query}'. Try a different name or use /technique to browse all.\nCOMMAND: /technique to browse all techniques"

    results = []
    for cat_key, tech_key, tech in matches[:10]:
        name = tech.get("name", "")
        desc = tech.get("description", "")
        video = tech.get("video_url", "")
        key = f"{cat_key}:{tech_key}"
        line = f"TECHNIQUE: {name}\nKEY: {key}\nDESCRIPTION: {desc}"
        if video:
            line += f"\nEXACT_VIDEO_URL: {video}"
        results.append(line)

    results.append(
        "To set as focus, call set_focus_technique with the KEY above. "
        "To add to toolbox, call add_to_toolbox with the KEY above.\n"
        "COMMAND: /focus to set as focus technique, /toolbox to view known techniques"
    )
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


def _find_technique_by_key(technique_key):
    """Resolve 'category:techid' to (cat_id, tech_id, tech_data) or None."""
    if ":" not in technique_key:
        return None
    parts = technique_key.split(":", 1)
    cat_id = parts[0].strip()
    tech_id = parts[1].strip()
    cat = all_techniques.get(cat_id)
    if not cat:
        for k, v in all_techniques.items():
            if cat_id in k or cat_id in v.get("name", "").lower():
                cat = v
                cat_id = k
                break
    if not cat:
        return None
    tech = cat.get("items", {}).get(tech_id)
    if not tech:
        for tk, tv in cat.get("items", {}).items():
            if tech_id in tk or tech_id in tv.get("name", "").lower():
                tech = tv
                tech_id = tk
                break
    if not tech:
        return None
    return cat_id, tech_id, tech


def _find_technique_by_name(query):
    """Fuzzy search by name, return (cat_id, tech_id, tech_data) or None."""
    query = query.lower().strip()
    for cat_id, cat in all_techniques.items():
        for tech_id, tech in cat.get("items", {}).items():
            name = tech.get("name", "").lower()
            if query in name or query in tech_id:
                return cat_id, tech_id, tech
    for cat_id, cat in all_techniques.items():
        for tech_id, tech in cat.get("items", {}).items():
            name = tech.get("name", "").lower()
            for w in query.split():
                if w in name or w in tech_id:
                    return cat_id, tech_id, tech
    return None


def exec_set_focus(chat_id, args):
    technique_key = args.get("technique_key", "").strip()
    if not technique_key:
        return "ERROR: no technique_key provided. Call search_technique first to find the key."

    result = _find_technique_by_key(technique_key)
    if not result:
        result = _find_technique_by_name(technique_key)
    if not result:
        return f"ERROR: technique '{technique_key}' not found. Use search_technique to find the correct key.\nCOMMAND: /technique to browse all techniques"

    cat_id, tech_id, tech = result

    db = load_database(chat_id)
    end_date = datetime.now() + timedelta(days=14)

    db["active_drill"] = {
        "technique": tech["name"],
        "description": tech.get("description", ""),
        "video_url": tech.get("video_url", ""),
        "category": all_techniques[cat_id]["name"],
        "toolbox_key": f"{cat_id}:{tech_id}",
        "start_date": datetime.now().isoformat(),
        "end_date": end_date.isoformat(),
    }
    save_database(chat_id, db)

    video = tech.get("video_url", "")
    result_text = f"Done! '{tech['name']}' is now your focus for 2 weeks."
    if video:
        result_text += f"\nEXACT_VIDEO_URL: {video}"
    result_text += "\nCOMMAND: /focus to view your current focus"
    return result_text


def exec_add_goal(chat_id, args):
    goal_text = args.get("goal_text", "").strip()
    if not goal_text:
        return "ERROR: empty goal."

    word_count = len(goal_text.split())
    if word_count > 7:
        return f"ERROR: goal is {word_count} words, max 7. Ask the user to shorten it."
    if word_count < 1:
        return "ERROR: goal is empty."

    db = load_database(chat_id)
    active_count = 0
    for g in db.get("goals", []):
        if g.get("status", "active") == "active":
            active_count += 1

    if active_count >= 3:
        return f"ERROR: user already has {active_count} active goals (max 3). They must complete or remove one first.\nCOMMAND: /goals to manage goals"

    now = datetime.now()
    year = now.isocalendar()[0]
    week = now.isocalendar()[1]
    week_str = f"{year}-W{week:02d}"

    new_goal = {
        "id": uuid.uuid4().hex[:8],
        "week": week_str,
        "goals": goal_text,
        "status": "active",
        "created_at": now.isoformat(),
        "completed_at": None,
        "refresh_schedule": [],
        "refresh_index": 0,
    }
    db["goals"].append(new_goal)
    save_database(chat_id, db)

    return f"Goal saved: \"{goal_text}\" ({active_count + 1}/3 slots used).\nCOMMAND: /goals to manage goals"


def exec_add_schedule(chat_id, args):
    day = args.get("day", "").strip()
    time_str = args.get("time", "").strip()

    valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    matched_day = None
    for d in valid_days:
        if day.lower() == d.lower() or day.lower()[:3] == d.lower()[:3]:
            matched_day = d
            break
    if not matched_day:
        return f"ERROR: invalid day '{day}'. Must be one of: {', '.join(valid_days)}."

    if not time_str or len(time_str) < 4:
        return "ERROR: invalid time. Use HH:MM format (e.g. '18:30')."

    if ":" not in time_str:
        return "ERROR: invalid time format. Use HH:MM (e.g. '18:30')."

    db = load_database(chat_id)
    for entry in db.get("schedule", []):
        if entry["day"] == matched_day and entry["time"] == time_str:
            return f"'{matched_day}' at {time_str} is already on the schedule.\nCOMMAND: /schedule to view schedule"

    db["schedule"].append({
        "day": matched_day,
        "time": time_str,
        "added_at": datetime.now().isoformat(),
    })
    save_database(chat_id, db)

    return f"Added {matched_day} at {time_str} to the schedule.\nCOMMAND: /schedule to view or change schedule"


def exec_add_to_toolbox(chat_id, args):
    technique_key = args.get("technique_key", "").strip()
    if not technique_key:
        return "ERROR: no technique_key provided. Call search_technique first."

    result = _find_technique_by_key(technique_key)
    if not result:
        result = _find_technique_by_name(technique_key)
    if not result:
        return f"ERROR: technique '{technique_key}' not found.\nCOMMAND: /technique to browse all techniques"

    cat_id, tech_id, tech = result
    key = f"{cat_id}:{tech_id}"

    db = load_database(chat_id)
    toolbox = db.get("toolbox", [])

    for entry in toolbox:
        if entry["key"] == key:
            return f"'{tech['name']}' is already in the toolbox.\nCOMMAND: /toolbox to view known techniques"

    toolbox.append({
        "key": key,
        "name": tech["name"],
        "category": all_techniques[cat_id]["name"],
        "added_at": datetime.now().isoformat(),
    })
    db["toolbox"] = toolbox
    save_database(chat_id, db)

    return f"'{tech['name']}' added to the toolbox.\nCOMMAND: /toolbox to view known techniques"


tool_executors = {
    "get_training_notes": exec_get_notes,
    "get_goals": exec_get_goals,
    "get_schedule": exec_get_schedule,
    "get_focus_and_toolbox": exec_get_focus,
    "get_training_stats": exec_get_stats,
    "search_technique": exec_search_technique,
    "list_techniques": exec_list_techniques,
    "save_training_note": exec_save_note,
    "set_focus_technique": exec_set_focus,
    "add_goal": exec_add_goal,
    "add_schedule_entry": exec_add_schedule,
    "add_to_toolbox": exec_add_to_toolbox,
}
