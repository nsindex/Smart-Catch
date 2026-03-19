import feedparser


def fetch_rss_entries(rss_config: dict) -> list[dict]:
    if "url" not in rss_config or not rss_config["url"]:
        raise ValueError("RSS configuration must include a non-empty 'url'.")

    source_url = rss_config["url"]
    source_name = rss_config.get("name", "")
    max_items = rss_config.get("max_items")

    if max_items is not None:
        if not isinstance(max_items, int) or max_items < 1:
            raise ValueError("'max_items' must be a positive integer.")

    feed = feedparser.parse(source_url)

    if getattr(feed, "status", 200) >= 400:
        raise ValueError(f"Failed to fetch RSS feed: {source_url}")

    if getattr(feed, "bozo", 0) and not getattr(feed, "entries", []):
        raise ValueError(f"Invalid RSS feed: {source_url}")

    entries = feed.entries[:max_items] if max_items is not None else feed.entries

    return [
        {
            "source_name": source_name,
            "source_url": source_url,
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "summary": entry.get("summary", ""),
            "published": entry.get("published", ""),
            "raw_entry": entry,
        }
        for entry in entries
    ]