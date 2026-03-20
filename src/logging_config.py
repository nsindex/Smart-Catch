import logging
from pathlib import Path


DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE = "smart_catch.log"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def setup_logging(logging_config: dict | None = None) -> None:
    config = logging_config or {}
    level_name = str(config.get("level", DEFAULT_LOG_LEVEL)).upper()
    level = getattr(logging, level_name, logging.INFO)

    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if config.get("save_to_file", False):
        log_dir = Path(config.get("log_dir", DEFAULT_LOG_DIR))
        log_dir.mkdir(parents=True, exist_ok=True)
        handlers.append(
            logging.FileHandler(log_dir / DEFAULT_LOG_FILE, encoding="utf-8")
        )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)

    formatter = logging.Formatter(LOG_FORMAT)
    for handler in handlers:
        handler.setLevel(level)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
