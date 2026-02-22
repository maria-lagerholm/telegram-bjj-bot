import re


off_topic_keywords = [
    "politic", "religion", "sex", "porn", "crypto", "bitcoin",
    "stock market", "invest", "gambl", "dating", "tinder",
    "hack", "crack", "pirat", "torrent", "weapon",
]


def is_off_topic(text):
    lower = text.lower()
    for kw in off_topic_keywords:
        if kw in lower:
            return True
    return False


emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002702-\U000027B0"
    "\U0000FE00-\U0000FE0F"
    "\U0000200D"
    "\U000025A0-\U000025FF"
    "\U00002600-\U000026FF"
    "]+",
    flags=re.UNICODE,
)


def clean_response(text):
    text = text.replace("\u2014", ",")
    text = text.replace("\u2013", ",")
    text = text.replace(" - ", ", ")
    text = emoji_pattern.sub("", text)
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.lstrip("#").strip()
        if line.startswith("#"):
            cleaned.append(stripped)
        else:
            cleaned.append(line)
    text = "\n".join(cleaned)
    if len(text) > 2000:
        text = text[:2000] + "..."
    return text.strip()
