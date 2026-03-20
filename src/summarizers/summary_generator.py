from typing import Any


def _build_local_summary(entry: dict[str, Any]) -> str:
    title = str(entry.get("title", "")).strip()
    source_name = str(entry.get("source_name", entry.get("source", ""))).strip()
    published = str(entry.get("published", entry.get("published_at", ""))).strip()
    raw_entry = entry.get("raw_entry") or {}

    tag_terms = []
    if isinstance(raw_entry, dict):
        tags = raw_entry.get("tags", [])
        if isinstance(tags, list):
            for tag in tags:
                if isinstance(tag, dict):
                    term = str(tag.get("term", "")).strip()
                    if term:
                        tag_terms.append(term)

    summary_parts = []

    if title:
        summary_parts.append(f"Title: {title}.")
    if source_name:
        summary_parts.append(f"Source: {source_name}.")
    if published:
        summary_parts.append(f"Published: {published}.")
    if tag_terms:
        summary_parts.append(f"Topics: {', '.join(tag_terms[:5])}.")

    summary_parts.append("Original feed summary was not provided.")

    return " ".join(summary_parts)


def generate_missing_summaries(entries: list[dict], enabled: bool = False) -> list[dict]:
    if not enabled:
        return entries

    if not isinstance(entries, list):
        raise TypeError("entries must be a list.")

    processed_entries = []

    for entry in entries:
        if not isinstance(entry, dict):
            raise TypeError("Each entry must be a dict.")

        if entry.get("summary"):
            processed_entries.append(entry)
            continue

        try:
            generated_summary = _build_local_summary(entry)
        except Exception:
            processed_entries.append(entry)
            continue

        if not generated_summary:
            processed_entries.append(entry)
            continue

        updated_entry = dict(entry)
        updated_entry["summary"] = generated_summary
        processed_entries.append(updated_entry)

    return processed_entries
