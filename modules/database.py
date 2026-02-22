import json
from pathlib import Path

data_directory = Path(__file__).parent.parent / "data"
data_directory.mkdir(exist_ok=True)


def load_database(chat_id):
    path = data_directory / f"user_{chat_id}.json"
    if path.exists():
        with open(path, "r") as file:
            data = json.load(file)
            if "active_drill" not in data:
                data["active_drill"] = None
            if "training_log" not in data:
                data["training_log"] = []
            if "toolbox" not in data:
                data["toolbox"] = []
            if "schedule" not in data:
                data["schedule"] = []
            if "reminder_times" not in data:
                data["reminder_times"] = {
                    "daily_checkin": "20:00",
                    "focus_reminder": "09:00",
                    "goal_reminder": "08:00",
                    "refresh_reminder": "10:00",
                }
            if "ai_usage" not in data:
                data["ai_usage"] = {"date": "", "count": 0}
            if "ai_history" not in data:
                data["ai_history"] = []
            return data

    new_database = {
        "goals": [],
        "notes": [],
        "drill_queue": [],
        "active_drill": None,
        "training_log": [],
        "toolbox": [],
        "schedule": [],
        "reminder_times": {
            "daily_checkin": "20:00",
            "focus_reminder": "09:00",
            "goal_reminder": "08:00",
            "refresh_reminder": "10:00",
        },
        "ai_usage": {"date": "", "count": 0},
        "ai_history": [],
    }
    return new_database


def save_database(chat_id, database):
    path = data_directory / f"user_{chat_id}.json"
    with open(path, "w") as file:
        json.dump(database, file, indent=2, default=str, ensure_ascii=False)
