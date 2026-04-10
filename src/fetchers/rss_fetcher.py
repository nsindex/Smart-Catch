import ipaddress
import logging
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

import feedparser

LOGGER = logging.getLogger(__name__)


def _should_exclude_entry(source_url: str, entry_link: str, rss_config: dict) -> bool:
    if not isinstance(entry_link, str) or not entry_link.strip():
        return False

    parsed_source = urlparse(source_url)
    parsed_link = urlparse(entry_link)
    if parsed_link.scheme not in {"http", "https"}:
        return False

    if parsed_source.hostname == "openai.com" and parsed_link.hostname == "openai.com":
        if parsed_link.path.startswith("/academy/"):
            return True

    for prefix in rss_config.get("exclude_url_prefixes", []):
        if isinstance(prefix, str) and prefix and entry_link.startswith(prefix):
            return True

    return False


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


def _parse_published(entry) -> datetime | None:
    """feedparser エントリから公開日時を UTC aware datetime で返す。

    パース失敗時は None を返す（安全側に倒す）。
    """
    # feedparser が struct_time として parsed_time を提供している場合はそちらを優先
    published_parsed = getattr(entry, "published_parsed", None)
    if published_parsed is not None:
        try:
            import calendar
            ts = calendar.timegm(published_parsed)
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except Exception:
            pass

    # 文字列から直接パース（RFC 2822 形式）
    published_str = entry.get("published", "") if isinstance(entry, dict) else getattr(entry, "published", "")
    if published_str:
        try:
            dt = parsedate_to_datetime(published_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass

    return None


def fetch_rss_entries(rss_config: dict) -> list[dict]:
    if "url" not in rss_config or not rss_config["url"]:
        raise ValueError("RSS configuration must include a non-empty 'url'.")

    source_url = rss_config["url"]
    validate_rss_url(source_url)
    source_name = rss_config.get("name", "")
    max_items = rss_config.get("max_items")
    # 修正2: 公開日フィルタ設定を取得
    max_age_days = rss_config.get("max_age_days")

    if max_items is not None:
        if not isinstance(max_items, int) or max_items < 1:
            raise ValueError("'max_items' must be a positive integer.")

    if max_age_days is not None:
        if not isinstance(max_age_days, int) or max_age_days < 1:
            raise ValueError("'max_age_days' must be a positive integer.")

    exclude_url_prefixes = rss_config.get("exclude_url_prefixes")
    if exclude_url_prefixes is not None:
        if not isinstance(exclude_url_prefixes, list) or not all(
            isinstance(prefix, str) for prefix in exclude_url_prefixes
        ):
            raise ValueError("'exclude_url_prefixes' must be a list of strings.")

    feed = feedparser.parse(source_url)

    if getattr(feed, "status", 200) >= 400:
        raise ValueError(f"Failed to fetch RSS feed: {source_url}")

    if getattr(feed, "bozo", 0) and not getattr(feed, "entries", []):
        raise ValueError(f"Invalid RSS feed: {source_url}")

    entries = list(feed.entries)

    # 修正2: 公開日フィルタ（max_items 適用前に実行）
    if max_age_days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        before_count = len(entries)
        filtered = []
        for entry in entries:
            published_dt = _parse_published(entry)
            if published_dt is None:
                # パース失敗 → 安全側に倒して通過させる
                filtered.append(entry)
            elif published_dt >= cutoff:
                filtered.append(entry)
        entries = filtered
        LOGGER.info(
            "Date filter applied: source=%s max_age_days=%s before=%s after=%s",
            source_name,
            max_age_days,
            before_count,
            len(entries),
        )

    before_exclude_count = len(entries)
    entries = [
        entry
        for entry in entries
        if not _should_exclude_entry(
            source_url,
            entry.get("link", "") if isinstance(entry, dict) else getattr(entry, "link", ""),
            rss_config,
        )
    ]
    if len(entries) != before_exclude_count:
        LOGGER.info(
            "Entry URL filter applied: source=%s before=%s after=%s",
            source_name,
            before_exclude_count,
            len(entries),
        )

    # max_items は日付フィルタ後に適用する
    if max_items is not None:
        entries = entries[:max_items]

    return [
        {
            "source_name": source_name,
            "source_url": source_url,
            "title": entry.get("title", "") if isinstance(entry, dict) else getattr(entry, "title", ""),
            "link": entry.get("link", "") if isinstance(entry, dict) else getattr(entry, "link", ""),
            "summary": entry.get("summary", "") if isinstance(entry, dict) else getattr(entry, "summary", ""),
            "published": entry.get("published", "") if isinstance(entry, dict) else getattr(entry, "published", ""),
            "raw_entry": entry,
        }
        for entry in entries
    ]
