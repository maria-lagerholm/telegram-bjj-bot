import uuid
from datetime import timedelta

from .database import load_database, save_database
from .techniques_data import all_techniques
from .helpers import now_se
from .youtube_search import youtube_search_url


tool_get_notes = {
    "name": "get_training_notes",
    "description": "Retrieve the user's recent training notes.",
    "parameters": {"type": "object", "properties": {
        "count": {"type": "integer", "description": "How many recent notes to return. Default 5, max 15."},
    }},
}

tool_get_goals = {
    "name": "get_goals",
    "description": "Retrieve the user's active and completed goals.",
    "parameters": {"type": "object", "properties": {}},
}

tool_get_schedule = {
    "name": "get_schedule",
    "description": "Retrieve the user's training schedule.",
    "parameters": {"type": "object", "properties": {}},
}

tool_get_focus = {
    "name": "get_focus_and_toolbox",
    "description": "Retrieve the user's focus technique and toolbox.",
    "parameters": {"type": "object", "properties": {}},
}

tool_get_stats = {
    "name": "get_training_stats",
    "description": "Retrieve the user's training statistics.",
    "parameters": {"type": "object", "properties": {}},
}

tool_search_technique = {
    "name": "search_technique",
    "description": (
        "Search the technique database by name. Call when a technique name appears. "
        "Returns details, video link, and available actions. "
        "If not found in the database, returns a YouTube search link."
    ),
    "parameters": {"type": "object", "properties": {
        "query": {"type": "string", "description": "Technique name to search for."},
    }, "required": ["query"]},
}

tool_list_techniques = {
    "name": "list_techniques",
    "description": (
        "List BJJ techniques. With a category (escapes, submissions, sweeps, guardpasses, "
        "takedowns, positions, ukemi, selfdefense) lists all in that category. Without lists categories."
    ),
    "parameters": {"type": "object", "properties": {
        "category": {"type": "string", "description": "Category name or empty for all categories."},
    }},
}

tool_set_focus = {
    "name": "set_focus_technique",
    "description": (
        "Set a technique as the user's focus for 2 weeks. "
        "Call search_technique first to get the key, then call this with 'category:techid'."
    ),
    "parameters": {"type": "object", "properties": {
        "technique_key": {"type": "string", "description": "Key in format 'category:techid'."},
    }, "required": ["technique_key"]},
}

tool_add_goal = {
    "name": "add_goal",
    "description": (
        "Add a training goal (1 to 7 words, max 3 active). "
        "Call IMMEDIATELY when the user says 'create a goal' or 'set a goal'."
    ),
    "parameters": {"type": "object", "properties": {
        "goal_text": {"type": "string", "description": "Goal text (1 to 7 words)."},
    }, "required": ["goal_text"]},
}

tool_add_schedule = {
    "name": "add_schedule_entry",
    "description": "Add a training day and time. Day: Monday to Sunday. Time: HH:MM format.",
    "parameters": {"type": "object", "properties": {
        "day": {"type": "string", "description": "Day of week, e.g. 'Monday'."},
        "time": {"type": "string", "description": "Time in HH:MM, e.g. '18:30'."},
    }, "required": ["day", "time"]},
}

tool_add_to_toolbox = {
    "name": "add_to_toolbox",
    "description": "Mark a technique as known. Use 'category:techid' key from search_technique.",
    "parameters": {"type": "object", "properties": {
        "technique_key": {"type": "string", "description": "Key in format 'category:techid'."},
    }, "required": ["technique_key"]},
}

all_tools = [
    tool_get_notes, tool_get_goals, tool_get_schedule, tool_get_focus, tool_get_stats,
    tool_search_technique, tool_list_techniques, tool_set_focus,
    tool_add_goal, tool_add_schedule, tool_add_to_toolbox,
]

action_tools = [
    tool_search_technique, tool_list_techniques, tool_set_focus,
    tool_add_goal, tool_add_schedule, tool_add_to_toolbox,
]


def exec_get_notes(chat_id, args):
    db = load_database(chat_id)
    notes = db.get("notes", [])
    if not notes:
        return "User has no training notes yet.\nCOMMAND: /note to log your first note"
    count = min(int(args.get("count", 5)), 15)
    lines = [f"{n.get('date', '')} {n.get('time', '')}: {n.get('text', '')}" for n in notes[-count:]]
    lines.append("\nCOMMAND: /notes to view all notes, /note to add a new one")
    return "\n".join(lines)


def exec_get_goals(chat_id, _args):
    db = load_database(chat_id)
    active = [g["goals"] for g in db.get("goals", []) if g.get("status", "active") == "active"]
    done = [g["goals"] for g in db.get("goals", []) if g.get("status") == "completed"]
    parts = []
    parts.append("Active goals: " + ", ".join(active) if active else "No active goals.")
    if done:
        parts.append("Completed goals (recent): " + ", ".join(done[-5:]))
    parts.append("\nCOMMAND: /goals to manage goals, /goal to set a new one")
    return "\n".join(parts)


def exec_get_schedule(chat_id, _args):
    db = load_database(chat_id)
    schedule = db.get("schedule", [])
    if not schedule:
        return "No training schedule set.\nCOMMAND: /schedule to set your training days and times"
    entries = [f"{s['day']} at {s['time']}" for s in schedule]
    return "Training schedule: " + ", ".join(entries) + "\nCOMMAND: /schedule to change your schedule"


def exec_get_focus(chat_id, _args):
    db = load_database(chat_id)
    parts = []
    drill = db.get("active_drill")
    parts.append(f"Current focus: {drill['technique']}" if drill else "No focus technique set.")
    toolbox = db.get("toolbox", [])
    if toolbox:
        names = [t["name"] for t in toolbox[:20]]
        parts.append(f"Toolbox ({len(toolbox)} techniques): " + ", ".join(names))
    else:
        parts.append("Toolbox is empty.")
    parts.append("\nCOMMAND: /focus to set or change focus, /toolbox to view known techniques, /technique to browse all")
    return "\n".join(parts)


def exec_get_stats(chat_id, _args):
    db = load_database(chat_id)
    total_notes = len(db.get("notes", []))
    log = db.get("training_log", [])
    trained = sum(1 for e in log if e.get("trained"))
    seven_ago = (now_se() - timedelta(days=7)).strftime("%Y-%m-%d")
    week_count = sum(1 for e in log if e.get("trained") and e["date"] >= seven_ago)
    active_goals = sum(1 for g in db.get("goals", []) if g.get("status") == "active")
    done_goals = sum(1 for g in db.get("goals", []) if g.get("status") == "completed")

    streak = 0
    current = now_se().date()
    dates = sorted([e["date"] for e in log if e.get("trained")], reverse=True)
    for ds in dates:
        if datetime.strptime(ds, "%Y-%m-%d").date() == current:
            streak += 1
            current -= timedelta(days=1)
        else:
            break

    return (
        f"Sessions this week: {week_count}. Total trained: {trained} days. "
        f"Streak: {streak} days. Notes: {total_notes}. "
        f"Goals: {active_goals} active, {done_goals} completed."
        f"\nCOMMAND: /stats for full stats, /goals to manage goals, /notes to view notes"
    )


def exec_search_technique(_chat_id, args):
    query = args.get("query", "").lower().strip()
    if not query:
        return "No technique name provided."

    matches = []
    for ck, cat in all_techniques.items():
        for tk, tech in cat.get("items", {}).items():
            name = tech.get("name", "").lower()
            if query in name or query in tk:
                matches.append((ck, tk, tech))

    if not matches:
        for ck, cat in all_techniques.items():
            for tk, tech in cat.get("items", {}).items():
                name = tech.get("name", "").lower()
                if any(w in name or w in tk for w in query.split()):
                    matches.append((ck, tk, tech))

    if not matches:
        url = youtube_search_url(query)
        return (
            f"No technique '{query}' in the database. "
            f"Here is a YouTube search for it:\nEXACT_VIDEO_URL: {url}\n"
            "COMMAND: /technique to browse all techniques in the database"
        )

    results = []
    for ck, tk, tech in matches[:10]:
        line = f"TECHNIQUE: {tech.get('name', '')}\nKEY: {ck}:{tk}\nDESCRIPTION: {tech.get('description', '')}"
        video = tech.get("video_url", "")
        if video:
            line += f"\nEXACT_VIDEO_URL: {video}"
        results.append(line)

    results.append(
        "To set as focus, call set_focus_technique with the KEY. "
        "To add to toolbox, call add_to_toolbox with the KEY.\n"
        "COMMAND: /focus to set as focus technique, /toolbox to view known techniques"
    )
    return "\n---\n".join(results)


def exec_list_techniques(_chat_id, args):
    category = args.get("category", "").lower().strip()

    if not category:
        lines = [f"{c.get('name', k)} ({len(c.get('items', {}))} techniques)" for k, c in all_techniques.items()]
        lines.append("\nCOMMAND: /technique to browse all techniques")
        return "Available categories:\n" + "\n".join(lines)

    cat = all_techniques.get(category)
    if not cat:
        for k, v in all_techniques.items():
            if category in k or category in v.get("name", "").lower():
                cat = v
                break
    if not cat:
        return f"No category '{category}' found. Available: escapes, submissions, sweeps, guardpasses, takedowns, positions, ukemi, selfdefense."

    items = cat.get("items", {})
    lines = [f"Category: {cat.get('name', category)} ({len(items)} techniques)\n"]
    for i, (tk, tech) in enumerate(items.items(), 1):
        line = f"{i}. {tech.get('name', tk)}"
        video = tech.get("video_url", "")
        if video:
            line += f"\n   EXACT_VIDEO_URL: {video}"
        lines.append(line)
    lines.append("\nCOMMAND: /focus to set a technique as focus, /toolbox to view known techniques, /technique to browse all")
    return "\n".join(lines)


def _find_by_key(key):
    if ":" not in key:
        return None
    cat_id, tech_id = key.split(":", 1)
    cat_id, tech_id = cat_id.strip(), tech_id.strip()
    cat = all_techniques.get(cat_id)
    if not cat:
        for k, v in all_techniques.items():
            if cat_id in k or cat_id in v.get("name", "").lower():
                cat, cat_id = v, k
                break
    if not cat:
        return None
    tech = cat.get("items", {}).get(tech_id)
    if not tech:
        for tk, tv in cat.get("items", {}).items():
            if tech_id in tk or tech_id in tv.get("name", "").lower():
                tech, tech_id = tv, tk
                break
    if not tech:
        return None
    return cat_id, tech_id, tech


def _find_by_name(query):
    q = query.lower().strip()
    for ck, cat in all_techniques.items():
        for tk, tech in cat.get("items", {}).items():
            name = tech.get("name", "").lower()
            if q in name or q in tk:
                return ck, tk, tech
    for ck, cat in all_techniques.items():
        for tk, tech in cat.get("items", {}).items():
            name = tech.get("name", "").lower()
            if any(w in name or w in tk for w in q.split()):
                return ck, tk, tech
    return None


def exec_set_focus(chat_id, args):
    key = args.get("technique_key", "").strip()
    if not key:
        return "ERROR: no technique_key. Call search_technique first."
    found = _find_by_key(key) or _find_by_name(key)
    if not found:
        return f"ERROR: technique '{key}' not found.\nCOMMAND: /technique to browse all"
    cat_id, tech_id, tech = found
    db = load_database(chat_id)
    db["active_drill"] = {
        "technique": tech["name"],
        "description": tech.get("description", ""),
        "video_url": tech.get("video_url", ""),
        "category": all_techniques[cat_id]["name"],
        "toolbox_key": f"{cat_id}:{tech_id}",
        "start_date": now_se().isoformat(),
        "end_date": (now_se() + timedelta(days=14)).isoformat(),
    }
    save_database(chat_id, db)
    result = f"Done! '{tech['name']}' is now your focus for 2 weeks."
    video = tech.get("video_url", "")
    if video:
        result += f"\nEXACT_VIDEO_URL: {video}"
    result += "\nCOMMAND: /focus to view your current focus"
    return result


def exec_add_goal(chat_id, args):
    text = args.get("goal_text", "").strip()
    if not text:
        return "ERROR: empty goal."
    wc = len(text.split())
    if wc > 7:
        return f"ERROR: goal is {wc} words, max 7."
    if wc < 1:
        return "ERROR: goal is empty."
    db = load_database(chat_id)
    active = sum(1 for g in db.get("goals", []) if g.get("status", "active") == "active")
    if active >= 3:
        return f"ERROR: {active} active goals (max 3). Complete or remove one first.\nCOMMAND: /goals to manage goals"
    now = now_se()
    db["goals"].append({
        "id": uuid.uuid4().hex[:8],
        "week": f"{now.isocalendar()[0]}-W{now.isocalendar()[1]:02d}",
        "goals": text,
        "status": "active",
        "created_at": now.isoformat(),
        "completed_at": None,
        "refresh_schedule": [],
        "refresh_index": 0,
    })
    save_database(chat_id, db)
    return f"Goal saved: \"{text}\" ({active + 1}/3 slots used).\nCOMMAND: /goals to manage goals"


def exec_add_schedule(chat_id, args):
    day = args.get("day", "").strip()
    time_str = args.get("time", "").strip()
    valid = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    matched = None
    for d in valid:
        if day.lower() == d.lower() or day.lower()[:3] == d.lower()[:3]:
            matched = d
            break
    if not matched:
        return f"ERROR: invalid day '{day}'."
    if not time_str or ":" not in time_str or len(time_str) < 4:
        return "ERROR: invalid time. Use HH:MM format."
    db = load_database(chat_id)
    for e in db.get("schedule", []):
        if e["day"] == matched and e["time"] == time_str:
            return f"'{matched}' at {time_str} is already on the schedule.\nCOMMAND: /schedule to view schedule"
    db["schedule"].append({"day": matched, "time": time_str, "added_at": now_se().isoformat()})
    save_database(chat_id, db)
    return f"Added {matched} at {time_str} to the schedule.\nCOMMAND: /schedule to view or change schedule"


def exec_add_to_toolbox(chat_id, args):
    key = args.get("technique_key", "").strip()
    if not key:
        return "ERROR: no technique_key. Call search_technique first."
    found = _find_by_key(key) or _find_by_name(key)
    if not found:
        return f"ERROR: technique '{key}' not found.\nCOMMAND: /technique to browse all"
    cat_id, tech_id, tech = found
    full_key = f"{cat_id}:{tech_id}"
    db = load_database(chat_id)
    toolbox = db.get("toolbox", [])
    for e in toolbox:
        if e["key"] == full_key:
            return f"'{tech['name']}' is already in the toolbox.\nCOMMAND: /toolbox to view known techniques"
    toolbox.append({
        "key": full_key,
        "name": tech["name"],
        "category": all_techniques[cat_id]["name"],
        "added_at": now_se().isoformat(),
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
    "set_focus_technique": exec_set_focus,
    "add_goal": exec_add_goal,
    "add_schedule_entry": exec_add_schedule,
    "add_to_toolbox": exec_add_to_toolbox,
}
