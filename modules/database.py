import json
from pathlib import Path

data_directory = Path(__file__).parent.parent / "data"
data_directory.mkdir(exist_ok=True)

database_file = data_directory / "bot_data.json"
protocol_file = Path(__file__).parent.parent / "bjj_white_belt_guide.txt"


def load_database():
    if database_file.exists():
        with open(database_file, "r") as file:
            return json.load(file)
    
    new_database = {
        "goals": [],
        "notes": [],
        "drill_queue": [],
    }
    return new_database


def save_database(database):
    with open(database_file, "w") as file:
        json.dump(database, file, indent=2, default=str)


def get_protocol_text():
    if protocol_file.exists():
        return protocol_file.read_text()
    return "Protocol file not found."
