import logging
from pathlib import Path
from typing import Callable

from src.action_generators.action_generator import build_action_suggestions
from src.classifiers.keyword_classifier import classify_entries
from src.config_loader import load_config
from src.deduplicators.article_deduplicator import deduplicate_articles
from src.deduplicators.seen_articles_db import filter_seen_articles, mark_articles_as_seen
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


def _build_source_min_score_map(
    rss_configs: list[dict],
    default_min_score: int,
) -> dict[str, int]:
    min_scores: dict[str, int] = {}
    for cfg in rss_configs:
        source_name = cfg.get("name", cfg.get("url", "unknown"))
        min_scores[source_name] = cfg.get("min_score", default_min_score)
    return min_scores


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
        seen_articles_db_path = str(
            Path(output_config.get("base_dir", "output")) / "seen_articles.db"
        )

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
        default_min_score = config["monitoring"].get("min_score", 0)
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

        source_min_scores = _build_source_min_score_map(rss_configs, default_min_score)
        before_filter = len(classified_entries)
        classified_entries = [
            a for a in classified_entries
            if a.get("score", 0) >= source_min_scores.get(a.get("source", ""), default_min_score)
        ]
        LOGGER.info(
            "Min score filtering: default=%s before=%s after=%s",
            default_min_score,
            before_filter,
            len(classified_entries),
        )

        # 修正1: 実行をまたいだ既出URL除去（SQLite永続化）
        seen_before_count = len(classified_entries)
        classified_entries = filter_seen_articles(classified_entries, seen_articles_db_path)
        LOGGER.info(
            "Seen-articles filter: before=%s after=%s",
            seen_before_count,
            len(classified_entries),
        )
        emit_progress("INFO", f"既出記事を除外: {seen_before_count - len(classified_entries)} 件スキップ")

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

        # 修正1: 今回出力した記事URLをDBに記録する
        mark_articles_as_seen(classified_entries, seen_articles_db_path)
        LOGGER.info("Seen-articles DB updated")

        LOGGER.info("Pipeline completed")
        emit_progress("INFO", "パイプライン完了")

        return exploration_markdown, purged_files
    except Exception:
        LOGGER.exception("Pipeline failed")
        raise
