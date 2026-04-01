import os
import tempfile
from datetime import date
from pathlib import Path

from src.utils.file_manager import get_unique_path, resolve_safe_output_dir


def atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    """一時ファイル経由のアトミック書き込み。クラッシュ時に途中書きファイルが残らない。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        Path(tmp_name).replace(path)
    except Exception:
        tmp = Path(tmp_name)
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise


def save_markdown_file(
    markdown: str, output_dir: str, filename: str = "collected_articles.md"
) -> str:
    safe_dir = resolve_safe_output_dir(output_dir)
    path = safe_dir / filename

    try:
        atomic_write_text(path, markdown)
    except OSError as exc:
        raise OSError(f"Failed to save markdown file: {path}") from exc

    return str(path)


def save_markdown_history_file(
    markdown: str,
    output_dir: str,
    filename: str = "collected_articles.md",
    date_str: str | None = None,
) -> str:
    if date_str is None:
        date_str = date.today().isoformat()

    if not isinstance(date_str, str) or not date_str:
        raise ValueError("date_str must be a non-empty string.")

    base = Path(filename)
    history_filename = f"{base.stem}_{date_str}{base.suffix}"
    unique_path = get_unique_path(Path(output_dir) / history_filename)
    return save_markdown_file(markdown, output_dir, unique_path.name)
