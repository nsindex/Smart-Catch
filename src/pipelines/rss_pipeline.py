from src.classifiers.keyword_classifier import classify_entries
from src.config_loader import load_config
from src.fetchers.rss_fetcher import fetch_rss_entries
from src.normalizers.rss_normalizer import normalize_rss_entries
from src.writers.markdown_writer import build_markdown


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

    monitoring_entries = [entry for entry in classified_entries if entry.get("matched")]

    exploration_markdown = build_markdown(classified_entries)
    monitoring_markdown = build_markdown(monitoring_entries)

    return exploration_markdown, monitoring_markdown


def run_rss_pipeline(config_path: str = "config/config.json") -> str:
    exploration_markdown, _ = run_rss_pipeline_outputs(config_path)
    return exploration_markdown
