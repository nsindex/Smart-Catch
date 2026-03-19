STRONG_KEYWORDS = {"openai", "claude", "claude code", "codex", "chatgpt"}


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
        title_lower = title.lower()
        summary_lower = summary.lower()
        matched_keywords = []
        score = 0

        for keyword in keywords:
            keyword_lower = keyword.lower()
            in_title = keyword_lower in title_lower
            in_summary = keyword_lower in summary_lower

            if not in_title and not in_summary:
                continue

            matched_keywords.append(keyword)
            score += 2 if in_title else 1

            if keyword_lower in STRONG_KEYWORDS:
                score += 2

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
