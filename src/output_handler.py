from pathlib import Path


DEFAULT_OUTPUT_PATH = Path("output/latest.md")


def save_markdown(markdown: str, output_path: str | Path = DEFAULT_OUTPUT_PATH) -> str:
    path = Path(output_path)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")
    except OSError as exc:
        raise OSError(f"Failed to save markdown to: {path}") from exc

    return str(path)
