import json
from pathlib import Path


DEFAULT_CONFIG_PATH = Path("config/config.json")


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict:
    path = Path(config_path)

    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as config_file:
            return json.load(config_file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in configuration file: {path}") from exc
    except OSError as exc:
        raise OSError(f"Failed to read configuration file: {path}") from exc