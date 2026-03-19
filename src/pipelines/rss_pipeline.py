from src.classifiers.keyword_classifier import classify_entries
from src.config_loader import load_config
from src.fetchers.rss_fetcher import fetch_rss_entries
from src.normalizers.rss_normalizer import normalize_rss_entries
from src.writers.markdown_writer import build_markdown


def _deduplicate_entries(entries: list[dict]) -> list[dict]:
    deduplicated_entries = []
    seen_urls = set()
    seen_titles_without_url = set()

    for entry in entries:
        url = entry.get("url", "")
        title = entry.get("title", "")

        if url:
            if url in seen_urls:
                continue
            seen_urls.add(url)
        elif title:
            if title in seen_titles_without_url:
                continue
            seen_titles_without_url.add(title)

        deduplicated_entries.append(entry)

    return deduplicated_entries


def run_rss_pipeline_outputs(config_path: str = "config/config.json") -> tuple[str, str]:
    config = load_config(config_path)
    rss_configs = config["sources"]["rss"]

    if not rss_configs:
        raise ValueError("No RSS source configuration found.")

    keywords = config["monitoring"]["keywords"]
    classified_entries = []

    for rss_config in rss_configs:
        fetched_entries = fetch_rss_entries(rss_config)
        normalized_entries = normalize_rss_entries(fetched_entries)
        classified_entries.extend(classify_entries(normalized_entries, keywords))

    classified_entries = _deduplicate_entries(classified_entries)
    monitoring_entries = [entry for entry in classified_entries if entry.get("matched")]

    exploration_markdown = build_markdown(classified_entries)
    monitoring_markdown = build_markdown(monitoring_entries)

    return exploration_markdown, monitoring_markdown


def run_rss_pipeline(config_path: str = "config/config.json") -> str:
    exploration_markdown, _ = run_rss_pipeline_outputs(config_path)
    return exploration_markdown
