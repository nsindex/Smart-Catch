"""seen_articles_db.py

SQLite を使って実行をまたいだ既出 URL を永続管理するモジュール。
DB ファイル: output/seen_articles.db

Public API:
    filter_seen_articles(entries, db_path) -> list[dict]
    mark_articles_as_seen(entries, db_path) -> None
"""

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

LOGGER = logging.getLogger(__name__)

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS seen_articles (
    url        TEXT PRIMARY KEY,
    first_seen TEXT NOT NULL
)
"""


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(_CREATE_TABLE_SQL)
    conn.commit()


def _open_db(db_path: str) -> sqlite3.Connection:
    """DB ファイルの親ディレクトリを作成してから接続する。"""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(path))


def filter_seen_articles(entries: list[dict], db_path: str) -> list[dict]:
    """entries のうち、DB に登録されていない記事だけを返す。

    Args:
        entries: 各 dict は "url" キーを持つ記事リスト。
        db_path: SQLite ファイルのパス（例: "output/seen_articles.db"）。

    Returns:
        未出力の記事だけに絞ったリスト。DB アクセス失敗時は entries をそのまま返す。
    """
    if not isinstance(entries, list):
        raise TypeError("entries must be a list.")

    try:
        with _open_db(db_path) as conn:
            _ensure_table(conn)
            cursor = conn.execute("SELECT url FROM seen_articles")
            seen_urls: set[str] = {row[0] for row in cursor.fetchall()}
    except Exception:
        LOGGER.warning(
            "filter_seen_articles: DB アクセス失敗。フィルタをスキップします。",
            exc_info=True,
        )
        return entries

    filtered = [
        entry for entry in entries
        if not entry.get("url") or entry["url"] not in seen_urls
    ]
    LOGGER.info(
        "filter_seen_articles: %d件 -> %d件（%d件を既出としてスキップ）",
        len(entries),
        len(filtered),
        len(entries) - len(filtered),
    )
    return filtered


def mark_articles_as_seen(entries: list[dict], db_path: str) -> None:
    """entries の URL を「出力済み」として DB に記録する。

    Args:
        entries: 各 dict は "url" キーを持つ記事リスト。
        db_path: SQLite ファイルのパス。

    DB アクセス失敗時は警告ログを出してスキップする（呼び出し元は例外を受け取らない）。
    """
    if not isinstance(entries, list):
        raise TypeError("entries must be a list.")

    urls_to_mark = [
        entry["url"]
        for entry in entries
        if isinstance(entry, dict) and entry.get("url")
    ]

    if not urls_to_mark:
        return

    first_seen = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        with _open_db(db_path) as conn:
            _ensure_table(conn)
            conn.executemany(
                "INSERT OR IGNORE INTO seen_articles (url, first_seen) VALUES (?, ?)",
                [(url, first_seen) for url in urls_to_mark],
            )
            conn.commit()
        LOGGER.info("mark_articles_as_seen: %d件を DB に記録しました", len(urls_to_mark))
    except Exception:
        LOGGER.warning(
            "mark_articles_as_seen: DB 書き込み失敗。スキップします。",
            exc_info=True,
        )
