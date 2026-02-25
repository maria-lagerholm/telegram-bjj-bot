from urllib.parse import quote_plus


def youtube_search_url(query):
    q = quote_plus(f"BJJ {query} technique tutorial")
    return f"https://www.youtube.com/results?search_query={q}"
