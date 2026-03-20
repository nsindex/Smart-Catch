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
