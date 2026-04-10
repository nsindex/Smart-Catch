````markdown
## 前提：Smart-Catch バグ修正タスク

Smart-CatchはPython製のRSSモニタリングツールです。
以下のソースコードと問題分析を読んで、**指定された修正を実装してください。**

---

## プロジェクト構成（関係するファイルのみ）

### config/config.json（現状）
```json
"deduplication": {
    "enabled": false,
    "mode": "url_and_title"
}
```

### src/pipelines/rss_pipeline.py
[rss_pipeline.pyの内容をそのまま貼る]
import logging

from pathlib import Path

from typing import Callable

  

from src.action_generators.action_generator import build_action_suggestions

from src.classifiers.keyword_classifier import classify_entries

from src.config_loader import load_config

from src.deduplicators.article_deduplicator import deduplicate_articles

from src.fetchers.rss_fetcher import fetch_rss_entries

from src.normalizers.rss_normalizer import normalize_rss_entries

from src.report_generators.daily_report_generator import build_daily_report

from src.summarizers.summary_generator import generate_missing_summaries

from src.topic_extractors.topic_extractor import assign_topics

from src.topic_summarizers.topic_summarizer import summarize_topics

from src.translators.markdown_translator import translate_markdown_to_japanese

from src.utils.file_manager import purge_old_files

from src.writers.file_writer import save_markdown_file, save_markdown_history_file

from src.writers.markdown_writer import build_markdown

  
  

LOGGER = logging.getLogger(__name__)

  
  

def run_rss_pipeline(

    config_path: str = "config/config.json",

    progress_callback: Callable[[str, str], None] | None = None,

) -> tuple[str, list[str]]:

    LOGGER.info("Pipeline started")

  

    def emit_progress(level: str, message: str) -> None:

        if progress_callback is None:

            return

        try:

            progress_callback(level, message)

        except Exception:

            LOGGER.warning("Progress callback failed", exc_info=True)

  

    try:

        config = load_config(config_path)

        rss_configs = config["sources"]["rss"]

  

        if not rss_configs:

            raise ValueError("No RSS source configuration found.")

  

        summary_generation_config = config.get("summary_generation", {})

        summary_generation_enabled = summary_generation_config.get("enabled", False)

        deduplication_config = config.get("deduplication", {})

        deduplication_enabled = deduplication_config.get("enabled", False)

        deduplication_mode = deduplication_config.get("mode", "url_only")

        output_config = config.get("output", {})

        save_history = output_config.get("save_history", False)

  

        exploration_dir = output_config.get("exploration_dir", "output/exploration")

        monitoring_dir = config["output"]["monitoring_dir"]

        monitoring_archive_dir = str(Path(monitoring_dir) / "archive")

  

        purged_files: list[str] = []

        purged_files.extend(purge_old_files(exploration_dir, days_old=3))

        purged_files.extend(purge_old_files(monitoring_archive_dir, days_old=3))

        purged_files.extend(purge_old_files(monitoring_dir, days_old=7))

        LOGGER.info("Purge completed: %s file(s) removed", len(purged_files))

        emit_progress("INFO", f"古い出力を {len(purged_files)} 件整理しました")

  

        all_fetched_entries = []

  

        for rss_config in rss_configs:

            source_name = rss_config.get("name", rss_config.get("url", "unknown"))

            LOGGER.info("RSS fetch started: %s", source_name)

            fetched_entries = fetch_rss_entries(rss_config)

            LOGGER.info(

                "RSS fetch completed: %s (%s entries)",

                source_name,

                len(fetched_entries),

            )

            all_fetched_entries.extend(fetched_entries)

  

        LOGGER.info("Fetched total entries: %s", len(all_fetched_entries))

        emit_progress("INFO", f"RSS取得完了: {len(all_fetched_entries)} 件")

  

        normalized_entries = normalize_rss_entries(all_fetched_entries)

        LOGGER.info("Normalization completed: %s entries", len(normalized_entries))

  

        empty_summary_count = sum(

            1 for entry in normalized_entries if not entry.get("summary")

        )

        normalized_entries = generate_missing_summaries(

            normalized_entries,

            enabled=summary_generation_enabled,

        )

        remaining_empty_summary_count = sum(

            1 for entry in normalized_entries if not entry.get("summary")

        )

        LOGGER.info(

            "Summary generation completed: generated=%s remaining_empty=%s enabled=%s",

            empty_summary_count - remaining_empty_summary_count,

            remaining_empty_summary_count,

            summary_generation_enabled,

        )

        emit_progress(

            "INFO",

            "要約生成完了: "

            f"{empty_summary_count - remaining_empty_summary_count} 件を補完",

        )

  

        keywords = config["monitoring"]["keywords"]

        keyword_weights = config["monitoring"].get("keyword_weights", {})

        classified_entries = classify_entries(

            normalized_entries,

            keywords,

            keyword_weights=keyword_weights,

        )

        matched_count = sum(

            1 for article in classified_entries if article.get("matched") is True

        )

        LOGGER.info(

            "Classification completed: total=%s matched=%s",

            len(classified_entries),

            matched_count,

        )

        emit_progress(

            "INFO",

            f"分類完了: 全{len(classified_entries)}件 / 監視一致{matched_count}件",

        )

  

        source_min_scores = {

            cfg.get("name", cfg.get("url", "unknown")): cfg["min_score"]

            for cfg in rss_configs

            if "min_score" in cfg

        }

        if source_min_scores:

            before_filter = len(classified_entries)

            classified_entries = [

                a for a in classified_entries

                if a.get("score", 0) >= source_min_scores.get(a.get("source", ""), 0)

            ]

            LOGGER.info(

                "Min score filtering: before=%s after=%s",

                before_filter,

                len(classified_entries),

            )

  

        dedup_before_count = len(classified_entries)

        classified_entries = deduplicate_articles(

            classified_entries,

            enabled=deduplication_enabled,

            mode=deduplication_mode,

        )

        LOGGER.info(

            "Deduplication completed: before=%s after=%s enabled=%s mode=%s",

            dedup_before_count,

            len(classified_entries),

            deduplication_enabled,

            deduplication_mode,

        )

  

        classified_entries = assign_topics(classified_entries)

        topic_count = len({article.get("topic_id") for article in classified_entries})

        LOGGER.info(

            "Topic extraction completed: total=%s topics=%s",

            len(classified_entries),

            topic_count,

        )

  

        topic_summaries = summarize_topics(classified_entries)

        LOGGER.info(

            "Topic summarization completed: topic_summaries=%s",

            len(topic_summaries),

        )

        emit_progress("INFO", f"トピック要約完了: {len(topic_summaries)} 件")

  

        daily_report = build_daily_report(classified_entries, topic_summaries)

        LOGGER.info("Daily report generation completed")

  

        action_suggestions = build_action_suggestions(

            classified_entries,

            topic_summaries,

        )

        LOGGER.info("Action suggestions generation completed")

  

        exploration_articles = classified_entries

        monitoring_articles = [

            article for article in classified_entries if article.get("matched") is True

        ]

        LOGGER.info(

            "Article split completed: exploration=%s monitoring=%s",

            len(exploration_articles),

            len(monitoring_articles),

        )

  

        exploration_markdown = build_markdown(

            exploration_articles,

            topic_summaries=topic_summaries,

            daily_report=daily_report,

            action_suggestions=action_suggestions,

        )

        monitoring_markdown = build_markdown(monitoring_articles)

        LOGGER.info("Markdown generation completed")

        emit_progress("INFO", "Markdown生成完了")

  

        exploration_path = save_markdown_file(

            exploration_markdown,

            config["output"]["exploration_dir"],

        )

        monitoring_path = save_markdown_file(

            monitoring_markdown,

            monitoring_archive_dir,

            "monitored_articles.md",

        )

        LOGGER.info("Exploration markdown saved: %s", exploration_path)

        LOGGER.info("Monitoring markdown saved: %s", monitoring_path)

        emit_progress("INFO", "英語Markdown保存完了")

  

        LOGGER.info("Japanese translation started")

        emit_progress("INFO", "日本語翻訳を開始しました")

        exploration_markdown_ja = translate_markdown_to_japanese(

            exploration_markdown,

            document_type="exploration",

            use_ollama=False,

        )

        monitoring_markdown_ja = translate_markdown_to_japanese(

            monitoring_markdown,

            document_type="monitoring",

            use_ollama=True,

        )

        LOGGER.info("Japanese translation completed")

        emit_progress("INFO", "日本語翻訳完了")

  

        exploration_ja_path = save_markdown_file(

            exploration_markdown_ja,

            config["output"]["exploration_dir"],

            "collected_articles_ja.md",

        )

        monitoring_ja_path = save_markdown_file(

            monitoring_markdown_ja,

            monitoring_archive_dir,

            "monitored_articles_ja.md",

        )

        LOGGER.info("Exploration Japanese markdown saved: %s", exploration_ja_path)

        LOGGER.info("Monitoring Japanese markdown saved: %s", monitoring_ja_path)

        emit_progress("INFO", "日本語Markdown保存完了")

  

        if save_history:

            exploration_history_path = save_markdown_history_file(

                exploration_markdown,

                config["output"]["exploration_dir"],

                "collected_articles.md",

            )

            monitoring_history_path = save_markdown_history_file(

                monitoring_markdown,

                monitoring_archive_dir,

                "monitored_articles.md",

            )

            exploration_history_ja_path = save_markdown_history_file(

                exploration_markdown_ja,

                config["output"]["exploration_dir"],

                "collected_articles_ja.md",

            )

            monitoring_history_ja_path = save_markdown_history_file(

                monitoring_markdown_ja,

                monitoring_dir,

                "monitored_articles_ja.md",

            )

            LOGGER.info("Exploration history markdown saved: %s", exploration_history_path)

            LOGGER.info("Monitoring history markdown saved: %s", monitoring_history_path)

            LOGGER.info("Exploration Japanese history markdown saved: %s", exploration_history_ja_path)

            LOGGER.info("Monitoring Japanese history markdown saved: %s", monitoring_history_ja_path)

  

        LOGGER.info("Pipeline completed")

        emit_progress("INFO", "パイプライン完了")

  

        return exploration_markdown, purged_files

    except Exception:

        LOGGER.exception("Pipeline failed")

        raise
### src/fetchers/rss_fetcher.py
[rss_fetcher.pyの内容をそのまま貼る]
import ipaddress

from urllib.parse import urlparse

  

import feedparser

  
  

def validate_rss_url(url: str) -> None:

    """RSS URLのスキームとホストを検証する。http/https のみ許可。

    localhost・プライベートIP・ループバックアドレスは拒否する。

    """

    if not isinstance(url, str) or not url.strip():

        raise ValueError("RSS URL must be a non-empty string.")

  

    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:

        raise ValueError(f"RSS URL must use http/https scheme, got: {parsed.scheme!r}")

  

    host = (parsed.hostname or "").lower()

    if not host:

        raise ValueError("RSS URL must include a host.")

  

    if host == "localhost":

        raise ValueError("localhost is not allowed in RSS URL.")

  

    try:

        ip = ipaddress.ip_address(host)

        if ip.is_private or ip.is_loopback or ip.is_link_local:

            raise ValueError(f"private/local addresses are not allowed: {host}")

    except ValueError as exc:

        if "private" in str(exc) or "local" in str(exc):

            raise

        # ホスト名（IPでない）の場合は通過

  
  

def fetch_rss_entries(rss_config: dict) -> list[dict]:

    if "url" not in rss_config or not rss_config["url"]:

        raise ValueError("RSS configuration must include a non-empty 'url'.")

  

    source_url = rss_config["url"]

    validate_rss_url(source_url)

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
### src/classifiers/keyword_classifier.py
[keyword_classifier.pyの内容をそのまま貼る]
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
### src/deduplicators/article_deduplicator.py
[article_deduplicator.pyの内容をそのまま貼る]
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
### src/summarizers/summary_generator.py
[summary_generator.pyの内容をそのまま貼る]
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
---

## 判明している問題と原因

### 問題A：同一記事が毎日出続ける【最重要】
**原因：**
`deduplicate_articles()`はセッション内の重複しか除去しない。
実行をまたいで「過去に出力したURL」を記憶する仕組みがない。
さらに `config.json` で `"enabled": false` になっているため、
セッション内重複除去すら機能していない。

### 問題B：古い記事が混入する
**原因：**
`fetch_rss_entries()` が `feed.entries[:max_items]` で取得しており、
公開日によるフィルタが存在しない。
Meta AI 研究フィードは2025年9月の記事（約6ヶ月前）を返し続けている。

### 問題C：一致キーワードに重複が出る
**原因：**
`keyword_classifier.py` の `matched_keywords` はリストで管理されており
重複除去をしていない。英語キーワード（"agent", "agents"）と
日本語キーワード（"エージェント"）が翻訳後に同じ語になることで
出力上に重複が生じる。

### 問題D：Ollamaの要約が英語で出力される
**原因：**
`_build_ollama_summary_prompt()` のプロンプトが
`"Write a one-sentence summary in English"` と明示的に英語を指定している。

### 問題E：Ollama未起動時にスコアが変動する
**原因：**
Ollama接続失敗時は `_build_local_summary()` のテンプレートにフォールバックする。
テンプレート要約とOllama要約では本文が異なるため、
キーワードマッチ数が変わりスコアが変動する。

---

## 実装してほしい修正（優先度順）

### 修正1：実行間の重複除去（SQLiteによる既出URL管理）

`src/deduplicators/seen_articles_db.py` を新規作成してください。

**要件：**
- SQLiteファイル（`output/seen_articles.db`）で既出URLを永続管理する
- 関数 `filter_seen_articles(entries, db_path)` を実装する
  - 引数 `entries`: `list[dict]`（各dictは `url` キーを持つ）
  - 戻り値: 未出力のものだけに絞ったリスト
- 関数 `mark_articles_as_seen(entries, db_path)` を実装する
  - 処理完了後に呼び出すことで、今回出力したURLをDBに記録する
- DBには `url`（TEXT, PRIMARY KEY）と `first_seen`（TEXT, ISO日付）を保存する

`src/pipelines/rss_pipeline.py` の修正：
- `classify_entries()` の後、`deduplicate_articles()` の前に
  `filter_seen_articles()` を呼び出す処理を挿入する
- パイプライン成功時の最後に `mark_articles_as_seen()` を呼び出す
- `config.json` の `"deduplication": {"enabled": true}` に変更する

### 修正2：公開日フィルタの追加

`src/fetchers/rss_fetcher.py` の `fetch_rss_entries()` に
公開日フィルタを追加してください。

**要件：**
- `rss_config` に `max_age_days`（int）を指定できるようにする
- `max_age_days` が指定されている場合、
  `(現在日時 - 公開日) > max_age_days` の記事はリストから除外する
- 公開日のパースに失敗した記事はフィルタせず通過させる（安全側に倒す）
- `max_items` は日付フィルタ後に適用する

`config.json` の修正：
```json
{
  "name": "Meta AI Research",
  "url": "https://engineering.fb.com/category/ai-research/feed/",
  "max_items": 5,
  "max_age_days": 7
}
```
全ソースに `"max_age_days": 14` をデフォルトで追加してください。

### 修正3：一致キーワードの重複除去

`src/classifiers/keyword_classifier.py` の `classify_entries()` を修正してください。

**要件：**
- `matched_keywords` をリストで収集した後、
  出力前に重複を除去する
- 順序を保持する（`list(dict.fromkeys(matched_keywords))`）

### 修正4：Ollama要約を日本語で出力

`src/summarizers/summary_generator.py` の
`_build_ollama_summary_prompt()` を修正してください。

**要件：**
- プロンプトを以下に変更する：
````

以下は {source_name} の記事タイトルです。 この記事が何について書かれているかを、日本語で1文で要約してください。 要約文のみを出力し、それ以外は何も出力しないでください。

タイトル: {title}

```
- `_is_safe_summary()` の長さ上限を240から400に引き上げる
  （日本語は文字数が増えるため）

---

## 実装時の注意

- 既存のテストが通ること（`tests/` 以下）
- 新規ファイル作成時はエラーハンドリングを追加すること（DBアクセス失敗時は警告ログを出してスキップ）
- `config.json` の変更はバックアップを作ってから行うこと
- 修正ごとに何を変えたかをコメントで明記すること

---

## 修正しない項目（スコープ外）

- topic_idの変動（topic_extractor.pyの問題だが今回は対象外）
- GUIへの反映（gui_app.pyは変更しない）
- Meta AI研究フィード自体のURL調査（config変更で対処済みとする）
```