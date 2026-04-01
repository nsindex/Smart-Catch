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