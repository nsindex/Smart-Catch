import logging

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
from src.writers.file_writer import save_markdown_file, save_markdown_history_file
from src.writers.markdown_writer import build_markdown


LOGGER = logging.getLogger(__name__)


def run_rss_pipeline(config_path: str = "config/config.json") -> str:
    LOGGER.info("Pipeline started")

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

        exploration_path = save_markdown_file(
            exploration_markdown,
            config["output"]["exploration_dir"],
        )
        monitoring_path = save_markdown_file(
            monitoring_markdown,
            config["output"]["monitoring_dir"],
            "monitored_articles.md",
        )
        LOGGER.info("Exploration markdown saved: %s", exploration_path)
        LOGGER.info("Monitoring markdown saved: %s", monitoring_path)

        if save_history:
            exploration_history_path = save_markdown_history_file(
                exploration_markdown,
                config["output"]["exploration_dir"],
                "collected_articles.md",
            )
            monitoring_history_path = save_markdown_history_file(
                monitoring_markdown,
                config["output"]["monitoring_dir"],
                "monitored_articles.md",
            )
            LOGGER.info("Exploration history markdown saved: %s", exploration_history_path)
            LOGGER.info("Monitoring history markdown saved: %s", monitoring_history_path)

        LOGGER.info("Pipeline completed")

        return exploration_markdown
    except Exception:
        LOGGER.exception("Pipeline failed")
        raise
