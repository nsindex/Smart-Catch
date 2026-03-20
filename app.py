import logging
import sys

from src.config_loader import load_config
from src.logging_config import setup_logging
from src.pipelines.rss_pipeline import run_rss_pipeline


LOGGER = logging.getLogger(__name__)


def main() -> int:
    args = sys.argv[1:]

    if len(args) > 1:
        print("Usage: python app.py [config_path]", file=sys.stderr)
        return 1

    config_path = args[0] if args else "config/config.json"
    setup_logging()

    try:
        config = load_config(config_path)
        setup_logging(config.get("logging", {}))
        LOGGER.info("CLI execution started with config: %s", config_path)
        markdown = run_rss_pipeline(config_path)
    except Exception as exc:
        LOGGER.exception("CLI execution failed")
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(markdown)
    LOGGER.info("CLI execution completed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
