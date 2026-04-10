"""tests/test_seen_articles_db.py

seen_articles_db モジュールのユニットテスト。
テスト用 DB は tmp_path フィクスチャを使って一時ディレクトリに作成する。
"""

import sqlite3
from pathlib import Path

import pytest

from src.deduplicators.seen_articles_db import filter_seen_articles, mark_articles_as_seen


# ---------------------------------------------------------------------------
# filter_seen_articles
# ---------------------------------------------------------------------------

class TestFilterSeenArticles:
    def test_empty_entries_returns_empty(self, tmp_path):
        db = str(tmp_path / "seen.db")
        result = filter_seen_articles([], db)
        assert result == []

    def test_all_new_articles_pass_through(self, tmp_path):
        db = str(tmp_path / "seen.db")
        entries = [
            {"url": "https://example.com/a"},
            {"url": "https://example.com/b"},
        ]
        result = filter_seen_articles(entries, db)
        assert result == entries

    def test_seen_urls_are_filtered(self, tmp_path):
        db = str(tmp_path / "seen.db")
        entries = [
            {"url": "https://example.com/a"},
            {"url": "https://example.com/b"},
        ]
        mark_articles_as_seen(entries, db)

        new_entries = [
            {"url": "https://example.com/a"},   # 既出
            {"url": "https://example.com/c"},   # 新規
        ]
        result = filter_seen_articles(new_entries, db)
        assert len(result) == 1
        assert result[0]["url"] == "https://example.com/c"

    def test_entry_without_url_passes_through(self, tmp_path):
        """url キーを持たない記事はフィルタせず通過させる。"""
        db = str(tmp_path / "seen.db")
        entries = [{"title": "no url here"}]
        result = filter_seen_articles(entries, db)
        assert result == entries

    def test_entry_with_empty_url_passes_through(self, tmp_path):
        """url が空文字の記事はフィルタせず通過させる。"""
        db = str(tmp_path / "seen.db")
        entries = [{"url": ""}]
        result = filter_seen_articles(entries, db)
        assert result == entries

    def test_raises_type_error_for_non_list(self, tmp_path):
        db = str(tmp_path / "seen.db")
        with pytest.raises(TypeError):
            filter_seen_articles("not a list", db)  # type: ignore[arg-type]

    def test_db_created_automatically(self, tmp_path):
        """DB ファイルと親ディレクトリが自動生成されること。"""
        db = str(tmp_path / "subdir" / "seen.db")
        filter_seen_articles([], db)
        assert Path(db).exists()


# ---------------------------------------------------------------------------
# mark_articles_as_seen
# ---------------------------------------------------------------------------

class TestMarkArticlesAsSeen:
    def test_inserts_urls_into_db(self, tmp_path):
        db = str(tmp_path / "seen.db")
        entries = [
            {"url": "https://example.com/x"},
            {"url": "https://example.com/y"},
        ]
        mark_articles_as_seen(entries, db)

        with sqlite3.connect(db) as conn:
            rows = conn.execute("SELECT url FROM seen_articles ORDER BY url").fetchall()
        assert [r[0] for r in rows] == [
            "https://example.com/x",
            "https://example.com/y",
        ]

    def test_first_seen_is_recorded(self, tmp_path):
        db = str(tmp_path / "seen.db")
        entries = [{"url": "https://example.com/z"}]
        mark_articles_as_seen(entries, db)

        with sqlite3.connect(db) as conn:
            row = conn.execute("SELECT first_seen FROM seen_articles").fetchone()
        # ISO形式であることを確認（YYYY-MM-DDTHH:MM:SSZ）
        assert row[0].endswith("Z")
        assert "T" in row[0]

    def test_duplicate_insert_is_ignored(self, tmp_path):
        """同一 URL を 2 回登録してもエラーにならない（INSERT OR IGNORE）。"""
        db = str(tmp_path / "seen.db")
        entries = [{"url": "https://example.com/dup"}]
        mark_articles_as_seen(entries, db)
        mark_articles_as_seen(entries, db)

        with sqlite3.connect(db) as conn:
            count = conn.execute("SELECT COUNT(*) FROM seen_articles").fetchone()[0]
        assert count == 1

    def test_entries_without_url_are_skipped(self, tmp_path):
        """url キーがない、または空の記事はスキップされる。"""
        db = str(tmp_path / "seen.db")
        entries = [
            {"title": "no url"},
            {"url": ""},
            {"url": "https://example.com/valid"},
        ]
        mark_articles_as_seen(entries, db)

        with sqlite3.connect(db) as conn:
            rows = conn.execute("SELECT url FROM seen_articles").fetchall()
        assert len(rows) == 1
        assert rows[0][0] == "https://example.com/valid"

    def test_empty_entries_does_nothing(self, tmp_path):
        db = str(tmp_path / "seen.db")
        mark_articles_as_seen([], db)
        # DB が作成されてもテーブルがなくても問題ない（0件なので _open_db も呼ばれない）
        # ただし呼んでも例外が出ないことを確認する
        assert True

    def test_raises_type_error_for_non_list(self, tmp_path):
        db = str(tmp_path / "seen.db")
        with pytest.raises(TypeError):
            mark_articles_as_seen({"url": "x"}, db)  # type: ignore[arg-type]

    def test_db_created_automatically(self, tmp_path):
        """DB ファイルと親ディレクトリが自動生成されること。"""
        db = str(tmp_path / "nested" / "deep" / "seen.db")
        entries = [{"url": "https://example.com/autodir"}]
        mark_articles_as_seen(entries, db)
        assert Path(db).exists()
