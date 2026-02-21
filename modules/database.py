import json
from pathlib import Path

data_directory = Path(__file__).parent.parent / "data"
data_directory.mkdir(exist_ok=True)

protocol_file = Path(__file__).parent.parent / "bjj_white_belt_guide.txt"


def _user_file(chat_id: int) -> Path:
    return data_directory / f"user_{chat_id}.json"


def load_database(chat_id: int) -> dict:
    path = _user_file(chat_id)
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
            return data

    new_database = {
        "goals": [],
        "notes": [],
        "drill_queue": [],
        "active_drill": None,
        "training_log": [],
        "toolbox": [],
        "schedule": [],
    }
    return new_database


def save_database(chat_id: int, database: dict):
    path = _user_file(chat_id)
    with open(path, "w") as file:
        json.dump(database, file, indent=2, default=str)


def get_protocol_text():
    if protocol_file.exists():
        return protocol_file.read_text()
    return "Protocol file not found."
