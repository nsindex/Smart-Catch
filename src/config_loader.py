import json
from pathlib import Path


DEFAULT_CONFIG_PATH = Path("config/config.json")


def _require_key(config: dict, key: str) -> object:
    if key not in config:
        raise ValueError(f"{key} is required")
    return config[key]


def _validate_optional_str(config: dict, key_path: str) -> None:
    if key_path in config and not isinstance(config[key_path], str):
        raise ValueError(f"{key_path} must be a string")


def _validate_optional_bool(config: dict, key_path: str) -> None:
    if key_path in config and not isinstance(config[key_path], bool):
        raise ValueError(f"{key_path} must be a bool")


def validate_config(config: dict) -> None:
    if not isinstance(config, dict):
        raise ValueError("config root must be an object")

    sources = _require_key(config, "sources")
    if not isinstance(sources, dict):
        raise ValueError("sources must be an object")

    rss_sources = _require_key(sources, "rss")
    if not isinstance(rss_sources, list):
        raise ValueError("sources.rss must be a list")

    for index, rss_source in enumerate(rss_sources):
        if not isinstance(rss_source, dict):
            raise ValueError(f"sources.rss[{index}] must be an object")

        url = rss_source.get("url")
        if not isinstance(url, str) or not url.strip():
            raise ValueError(
                f"sources.rss[{index}].url must be a non-empty string"
            )

        if "min_score" in rss_source:
            min_score = rss_source["min_score"]
            if not isinstance(min_score, int) or min_score < 0:
                raise ValueError(
                    f"sources.rss[{index}].min_score must be a non-negative integer"
                )

    monitoring = _require_key(config, "monitoring")
    if not isinstance(monitoring, dict):
        raise ValueError("monitoring must be an object")

    keywords = _require_key(monitoring, "keywords")
    if not isinstance(keywords, list):
        raise ValueError("monitoring.keywords must be a list")

    if "min_score" in monitoring:
        min_score = monitoring["min_score"]
        if not isinstance(min_score, int) or min_score < 0:
            raise ValueError("monitoring.min_score must be a non-negative integer")

    if "keyword_weights" in monitoring and not isinstance(
        monitoring["keyword_weights"], dict
    ):
        raise ValueError("monitoring.keyword_weights must be an object")

    deduplication = config.get("deduplication")
    if deduplication is not None:
        if not isinstance(deduplication, dict):
            raise ValueError("deduplication must be an object")
        _validate_optional_bool(deduplication, "enabled")
        _validate_optional_str(deduplication, "mode")

    output = config.get("output")
    if output is not None:
        if not isinstance(output, dict):
            raise ValueError("output must be an object")
        _validate_optional_str(output, "exploration_dir")
        _validate_optional_str(output, "monitoring_dir")
        _validate_optional_bool(output, "save_history")

    logging_config = config.get("logging")
    if logging_config is not None:
        if not isinstance(logging_config, dict):
            raise ValueError("logging must be an object")
        _validate_optional_str(logging_config, "level")
        _validate_optional_bool(logging_config, "save_to_file")
        _validate_optional_str(logging_config, "log_dir")


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict:
    path = Path(config_path)

    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in configuration file: {path}") from exc
    except OSError as exc:
        raise OSError(f"Failed to read configuration file: {path}") from exc

    validate_config(config)
    return config
