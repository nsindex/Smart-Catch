def classify_entries(entries: list[dict], keywords: list[str]) -> list[dict]:
    if not isinstance(entries, list):
        raise TypeError("entries must be a list.")

    if not isinstance(keywords, list):
        raise TypeError("keywords must be a list.")

    for entry in entries:
        if not isinstance(entry, dict):
            raise TypeError("Each entry must be a dict.")

    for keyword in keywords:
        if not isinstance(keyword, str):
            raise TypeError("Each keyword must be a string.")

    classified_entries = []

    for entry in entries:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        target_text = f"{title} {summary}".lower()

        matched_keywords = [
            keyword for keyword in keywords if keyword.lower() in target_text
        ]

        classified_entries.append(
            {
                "source": entry.get("source", ""),
                "source_url": entry.get("source_url", ""),
                "title": title,
                "url": entry.get("url", ""),
                "published_at": entry.get("published_at", ""),
                "summary": summary,
                "matched": len(matched_keywords) > 0,
                "matched_keywords": matched_keywords,
            }
        )

    return classified_entries
