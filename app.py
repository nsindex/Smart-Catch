import sys

from src.output_handler import save_markdown
from src.pipelines.rss_pipeline import run_rss_pipeline


def main() -> int:
    args = sys.argv[1:]

    if len(args) > 1:
        print("Usage: python app.py [config_path]", file=sys.stderr)
        return 1

    config_path = args[0] if args else "config/config.json"

    try:
        markdown = run_rss_pipeline(config_path)
        output_path = save_markdown(markdown)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(markdown)
    print(f"Saved to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
