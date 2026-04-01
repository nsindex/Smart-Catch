import os
from pathlib import Path
import pytest
from src.writers.file_writer import atomic_write_text


def test_atomic_write_creates_file(tmp_path):
    target = tmp_path / "output" / "test.md"
    atomic_write_text(target, "hello")
    assert target.read_text(encoding="utf-8") == "hello"


def test_atomic_write_no_tmp_left(tmp_path):
    target = tmp_path / "test.md"
    atomic_write_text(target, "content")
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert tmp_files == [], f"tmp file left: {tmp_files}"


def test_atomic_write_overwrites_existing(tmp_path):
    target = tmp_path / "test.md"
    target.write_text("old", encoding="utf-8")
    atomic_write_text(target, "new")
    assert target.read_text(encoding="utf-8") == "new"


def test_atomic_write_creates_parent_dir(tmp_path):
    target = tmp_path / "subdir" / "nested" / "test.md"
    atomic_write_text(target, "data")
    assert target.exists()
