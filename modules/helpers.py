from datetime import datetime


def get_current_week():
    now = datetime.now()
    year = now.isocalendar()[0]
    week = now.isocalendar()[1]
    return f"{year}-W{week:02d}"


def find_techniques_in_text(text):
    known_techniques = [
        "hip escape", "shrimp", "bridge", "technical stand-up", "granby roll",
        "elbow escape", "trap and roll", "upa",
        "closed guard", "half guard", "open guard", "butterfly guard",
        "de la riva", "spider guard", "lasso guard", "x-guard",
        "single leg x", "rubber guard",
        "torreando", "double under", "knee slice", "knee cut",
        "leg drag", "smash pass", "over-under", "stack pass",
        "long step", "body lock pass",
        "scissor sweep", "flower sweep", "hip bump", "butterfly sweep",
        "tripod sweep", "pendulum sweep", "sickle sweep",
        "single leg", "double leg", "hip throw", "ankle pick",
        "osoto gari", "arm drag", "snap down", "collar drag",
        "armbar", "triangle", "rear naked choke", "rnc",
        "guillotine", "kimura", "americana", "omoplata",
        "ezekiel", "cross choke", "collar choke", "bow and arrow",
        "arm triangle", "darce", "anaconda", "north-south choke",
        "loop choke", "baseball choke",
        "mount", "side control", "back control", "knee on belly",
        "turtle", "north-south", "crucifix",
        "seatbelt", "underhook", "overhook", "frames",
        "collar grip", "sleeve grip",
    ]

    text_lowercase = text.lower()
    found_techniques = []

    for technique in known_techniques:
        if technique in text_lowercase:
            found_techniques.append(technique.title())

    return found_techniques
