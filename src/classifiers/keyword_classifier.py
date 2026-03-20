def classify_entries(
    entries: list[dict], keywords: list[str], keyword_weights: dict | None = None
) -> list[dict]:
    if not isinstance(entries, list):
        raise TypeError("entries must be a list.")

    if not isinstance(keywords, list):
        raise TypeError("keywords must be a list.")

    if keyword_weights is None:
        keyword_weights = {}
    elif not isinstance(keyword_weights, dict):
        raise TypeError("keyword_weights must be a dict.")

    for entry in entries:
        if not isinstance(entry, dict):
            raise TypeError("Each entry must be a dict.")

    for keyword in keywords:
        if not isinstance(keyword, str):
            raise TypeError("Each keyword must be a string.")

    for keyword, weight in keyword_weights.items():
        if not isinstance(keyword, str):
            raise TypeError("Each keyword weight key must be a string.")
        if not isinstance(weight, int) or weight < 1:
            raise TypeError("Each keyword weight must be a positive integer.")

    classified_entries = []

    for entry in entries:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        title_lower = title.lower()
        summary_lower = summary.lower()
        matched_keywords = []
        score = 0

        for keyword in keywords:
            keyword_lower = keyword.lower()
            in_title = keyword_lower in title_lower
            in_summary = keyword_lower in summary_lower
            keyword_weight = keyword_weights.get(keyword, 1)

            if not in_title and not in_summary:
                continue

            matched_keywords.append(keyword)

            if in_title:
                score += keyword_weight * 2
            if in_summary:
                score += keyword_weight

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
                "score": score,
            }
        )

    return classified_entries
