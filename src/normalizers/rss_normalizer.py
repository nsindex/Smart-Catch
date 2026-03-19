def normalize_rss_entries(entries: list[dict]) -> list[dict]:
    if not isinstance(entries, list):
        raise TypeError("entries must be a list.")

    normalized_entries = []

    for entry in entries:
        if not isinstance(entry, dict):
            raise TypeError("Each entry must be a dict.")

        normalized_entries.append(
            {
                "source": entry.get("source_name", ""),
                "source_url": entry.get("source_url", ""),
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "published_at": entry.get("published", ""),
                "summary": entry.get("summary", ""),
            }
        )

    return normalized_entries
