from . import data


def screen_articles(articles):
    kept = []
    events = []
    for article in articles:
        if data.INJECTION_RE.search(article["body"]):
            events.append(("WITHHOLD", f"{article['id']}: prompt attack pattern in document"))
        else:
            fenced = dict(article)
            fenced["body"] = data.FENCE_PREFIX + article["body"]
            kept.append(fenced)
    return kept, events
