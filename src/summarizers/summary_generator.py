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
        summary_parts.append(f"{title} について扱っている。")
    else:
        summary_parts.append("対象記事の概要を簡潔にまとめる。")

    detail_parts = []
    if source_name:
        detail_parts.append(f"情報源は {source_name}")
    if published:
        detail_parts.append(f"公開日は {published}")
    if tag_terms:
        detail_parts.append(f"関連トピックは {', '.join(tag_terms[:5])}")

    if detail_parts:
        summary_parts.append("、".join(detail_parts) + "。")
    else:
        summary_parts.append("補助要約として基本情報を整理している。")

    summary_parts.append("元のフィード要約が無いため、題名と付随情報をもとに要点を確認しやすい形で補っている。")

    return "".join(summary_parts)


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
