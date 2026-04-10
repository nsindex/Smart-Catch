import json

from src.config_loader import load_config


def test_load_config_normalizes_ollama_host(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "sources": {"rss": []},
                "monitoring": {"keywords": []},
                "ollama": {"host": " http://127.0.0.1:11434/ "},
            }
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config["ollama"]["host"] == "http://127.0.0.1:11434"
