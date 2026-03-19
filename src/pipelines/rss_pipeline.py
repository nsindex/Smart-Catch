from src.classifiers.keyword_classifier import classify_entries
from src.config_loader import load_config
from src.fetchers.rss_fetcher import fetch_rss_entries
from src.normalizers.rss_normalizer import normalize_rss_entries
from src.writers.markdown_writer import build_markdown


def run_rss_pipeline(config_path: str = "config/config.json") -> str:
    config = load_config(config_path)
    rss_configs = config["sources"]["rss"]

    if not rss_configs:
        raise ValueError("No RSS source configuration found.")

    rss_config = rss_configs[0]
    fetched_entries = fetch_rss_entries(rss_config)
    normalized_entries = normalize_rss_entries(fetched_entries)
    keywords = config["monitoring"]["keywords"]
    classified_entries = classify_entries(normalized_entries, keywords)

    return build_markdown(classified_entries)
