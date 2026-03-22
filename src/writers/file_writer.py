from datetime import date
from pathlib import Path


def save_markdown_file(
    markdown: str, output_dir: str, filename: str = "collected_articles.md"
) -> str:
    path = Path(output_dir) / filename

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")
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

    path = Path(filename)
    history_filename = f"{path.stem}_{date_str}{path.suffix}"
    return save_markdown_file(markdown, output_dir, history_filename)
