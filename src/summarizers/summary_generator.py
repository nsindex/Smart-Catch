import json
import urllib.error
import urllib.request
from typing import Any

from src.utils.llm_sanitizer import sanitize_llm_input

_OLLAMA_API_URL = "http://localhost:11434/api/generate"
_OLLAMA_MODEL = "gemma3n:e4b"
_OLLAMA_TIMEOUT_SECONDS = 12


def _is_safe_summary(text: str) -> bool:
    if not isinstance(text, str):
        return False
    stripped = " ".join(text.split())
    if not stripped or len(stripped) > 240:
        return False
    if any(token in stripped for token in ("```", "---", "#", "\n", "\r")):
        return False
    return True


def _build_ollama_summary_prompt(title: str, source_name: str) -> str:
    safe_title = sanitize_llm_input(title, limit=300)
    safe_source = sanitize_llm_input(source_name, limit=100)
    return (
        f"The following is an article title from {safe_source}.\n"
        "Write a one-sentence summary in English describing what this article is likely about.\n"
        "Output only the summary sentence, nothing else.\n\n"
        f"Title: {safe_title}"
    )


def _generate_summary_with_ollama(title: str, source_name: str) -> str | None:
    if not title:
        return None

    prompt = _build_ollama_summary_prompt(title, source_name)
    payload = {
        "model": _OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "stop": ["\n\n", "---", "```"],
        },
    }
    request = urllib.request.Request(
        _OLLAMA_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=_OLLAMA_TIMEOUT_SECONDS) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError:
        # Ollama未起動・接続不可の場合はフォールバックへ
        return None
    except (TimeoutError, ValueError, OSError):
        return None

    result = response_data.get("response")
    if not isinstance(result, str) or not result.strip():
        return None

    result = result.strip()
    if not _is_safe_summary(result):
        return None

    return result


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

    # Ollamaで要約生成を試みる
    ollama_summary = _generate_summary_with_ollama(title, source_name)
    if ollama_summary:
        return ollama_summary

    # Ollama失敗時はテンプレート文字列にフォールバック
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
