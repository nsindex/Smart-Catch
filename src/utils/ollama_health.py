import subprocess
import time
import urllib.request

_DEFAULT_OLLAMA_HOST = "http://localhost:11434"
OLLAMA_CHECK_TIMEOUT = 2  # seconds
OLLAMA_START_POLL_INTERVAL = 0.5  # seconds
OLLAMA_START_MAX_ATTEMPTS = 10  # max 5 seconds total


def is_ollama_running(ollama_host: str = _DEFAULT_OLLAMA_HOST) -> bool:
    """/api/tags にGETリクエストを送り、Ollamaの起動を確認する。
    タイムアウト2秒。200応答ならTrue、それ以外はFalse。
    """
    health_url = f"{ollama_host}/api/tags"
    try:
        with urllib.request.urlopen(health_url, timeout=OLLAMA_CHECK_TIMEOUT):
            return True
    except Exception:
        return False


def ensure_ollama_running(ollama_host: str = _DEFAULT_OLLAMA_HOST) -> bool:
    """Ollamaが未起動の場合、ollama serve をバックグラウンドで起動する。
    time.sleep(0.5) × 最大10回ポーリングで起動確認（最大5秒待機）。
    起動済みなら即True。起動失敗ならFalse。
    Popen ハンドルは意図的に保持しない（ollama はデーモンのため .wait() 不要）。
    複数回呼ばれても安全（2回目の Popen はポート競合で即終了する）。
    """
    if is_ollama_running(ollama_host):
        return True

    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        # FileNotFoundError（PATH未登録）を含む全OS例外を捕捉
        return False

    for _ in range(OLLAMA_START_MAX_ATTEMPTS):
        time.sleep(OLLAMA_START_POLL_INTERVAL)
        if is_ollama_running(ollama_host):
            return True

    return False
