import re


WHITESPACE_PATTERN = re.compile(r"\s+")


def _normalize_title(title: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", title.strip().lower())


def _is_better_article(candidate: dict, current: dict) -> bool:
    candidate_score = candidate.get("score", 0)
    current_score = current.get("score", 0)
    if candidate_score != current_score:
        return candidate_score > current_score

    candidate_summary_length = len(candidate.get("summary", ""))
    current_summary_length = len(current.get("summary", ""))
    if candidate_summary_length != current_summary_length:
        return candidate_summary_length > current_summary_length

    return False


def deduplicate_articles(entries: list[dict], enabled: bool = False, mode: str = "url_only") -> list[dict]:
    if not enabled:
        return entries

    if not isinstance(entries, list):
        raise TypeError("entries must be a list.")

    if mode not in {"url_only", "url_and_title"}:
        raise ValueError("deduplication mode must be 'url_only' or 'url_and_title'.")

    deduplicated_entries = []

    for entry in entries:
        if not isinstance(entry, dict):
            raise TypeError("Each entry must be a dict.")

        duplicate_index = None
        entry_url = entry.get("url", "")
        entry_title = _normalize_title(entry.get("title", ""))

        for index, existing_entry in enumerate(deduplicated_entries):
            existing_url = existing_entry.get("url", "")
            existing_title = _normalize_title(existing_entry.get("title", ""))

            url_matches = bool(entry_url) and entry_url == existing_url
            title_matches = (
                mode == "url_and_title"
                and bool(entry_title)
                and entry_title == existing_title
            )

            if url_matches or title_matches:
                duplicate_index = index
                break

        if duplicate_index is None:
            deduplicated_entries.append(entry)
            continue

        if _is_better_article(entry, deduplicated_entries[duplicate_index]):
            deduplicated_entries[duplicate_index] = entry

    return deduplicated_entries
