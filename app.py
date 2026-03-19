import sys

from src.output_handler import save_markdown
from src.pipelines.rss_pipeline import run_rss_pipeline_outputs


def main() -> int:
    args = sys.argv[1:]

    if len(args) > 1:
        print("Usage: python app.py [config_path]", file=sys.stderr)
        return 1

    config_path = args[0] if args else "config/config.json"

    try:
        exploration_markdown, monitoring_markdown = run_rss_pipeline_outputs(config_path)
        monitoring_output_path = save_markdown(
            monitoring_markdown, "output/monitoring/latest.md"
        )
        exploration_output_path = save_markdown(
            exploration_markdown, "output/exploration/latest.md"
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(exploration_markdown)
    print(f"Saved to: {monitoring_output_path}")
    print(f"Saved to: {exploration_output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
