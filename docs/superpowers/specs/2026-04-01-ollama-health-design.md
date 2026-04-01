# Ollama起動検知・自動起動 設計ドキュメント

**作成日:** 2026-04-01  
**ステータス:** 承認済み

---

## 概要

アプリ起動時・Run実行時にOllamaの起動状態を自動チェックし、未起動の場合は `ollama serve` をバックグラウンド起動する。起動失敗時はWARNINGログを出力して既存のフォールバック動作（定型文）で処理を続行する。

---

## アーキテクチャ

### 新規ファイル

```
src/utils/
└── ollama_health.py  ← 新規作成
```

### 変更ファイル

- `gui_app.py`：起動時・Run実行前の2箇所に呼び出しを追加

### 変更しないファイル

- `src/summarizers/summary_generator.py`（既存フォールバック維持）
- `src/translators/markdown_translator.py`（既存フォールバック維持）
- `src/pipelines/rss_pipeline.py`（変更なし）
- `app.py`（今回のスコープ外）

---

## `src/utils/ollama_health.py`

### 公開API

```python
def is_ollama_running() -> bool:
    """localhost:11434/api/tags にGETリクエストを送り、Ollamaの起動を確認する。
    タイムアウト2秒。200応答ならTrue、それ以外はFalse。"""

def ensure_ollama_running() -> bool:
    """Ollamaが未起動の場合、ollama serve をバックグラウンドで起動する。
    最大5秒（0.5秒×10回ポーリング）待って起動確認できたらTrue。
    起動済みの場合は即True。起動失敗時はFalse。"""
```

### `is_ollama_running()` 実装方針

```python
OLLAMA_HEALTH_URL = "http://localhost:11434/api/tags"
OLLAMA_CHECK_TIMEOUT = 2  # seconds

def is_ollama_running() -> bool:
    try:
        with urllib.request.urlopen(OLLAMA_HEALTH_URL, timeout=OLLAMA_CHECK_TIMEOUT):
            return True
    except Exception:
        return False
```

### `ensure_ollama_running()` 実装方針

```python
OLLAMA_START_POLL_INTERVAL = 0.5   # seconds
OLLAMA_START_MAX_ATTEMPTS = 10     # 最大5秒待機

def ensure_ollama_running() -> bool:
    if is_ollama_running():
        return True
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return False  # ollama コマンドが PATH にない
    except OSError:
        return False

    for _ in range(OLLAMA_START_MAX_ATTEMPTS):
        time.sleep(OLLAMA_START_POLL_INTERVAL)
        if is_ollama_running():
            return True
    return False
```

### エラーハンドリング

| ケース | 動作 |
|--------|------|
| `ollama` が PATH にない | `FileNotFoundError` を捕まえてFalse返却 |
| `ollama serve` が5秒で応答なし | False返却（ポーリングタイムアウト） |
| `ollama serve` が即エラー終了 | False返却（次のポーリングで `is_ollama_running()` がFalseのまま） |
| ネットワーク例外 | `is_ollama_running()` がFalse返却 |

---

## `gui_app.py` の変更

### 1. 起動時チェック（`__init__`）

`_load_keywords()` の呼び出し後に追加：

```python
self._check_ollama_on_startup()
```

新規メソッド：

```python
def _check_ollama_on_startup(self) -> None:
    from src.utils.ollama_health import ensure_ollama_running, is_ollama_running
    if is_ollama_running():
        self._append_result("INFO", "Ollama: 起動確認済み")
        return
    self._append_result("INFO", "Ollama未起動。自動起動を試みています...")
    self.root.update_idletasks()
    success = ensure_ollama_running()
    if success:
        self._append_result("INFO", "Ollama: 自動起動成功")
    else:
        self._append_result("WARNING", "Ollama起動失敗。要約・翻訳はフォールバックになります")
```

### 2. Run実行前チェック（`run_pipeline`）

`_set_running_state(True)` の直後に追加：

```python
from src.utils.ollama_health import is_ollama_running
if not is_ollama_running():
    self._append_result("WARNING", "Ollama未起動。要約・翻訳はフォールバックで処理します")
```

---

## ログ出力仕様

| タイミング | 状況 | ログレベル | メッセージ |
|-----------|------|-----------|-----------|
| 起動時 | 起動確認済み | INFO | `Ollama: 起動確認済み` |
| 起動時 | 未起動・自動起動試行 | INFO | `Ollama未起動。自動起動を試みています...` |
| 起動時 | 自動起動成功 | INFO | `Ollama: 自動起動成功` |
| 起動時 | 自動起動失敗 | WARNING | `Ollama起動失敗。要約・翻訳はフォールバックになります` |
| Run時 | 未起動 | WARNING | `Ollama未起動。要約・翻訳はフォールバックで処理します` |
| Run時 | 起動確認OK | （なし） | ログなし（ノイズ抑制） |

---

## 制約・スコープ外

- `app.py`（CLI）への適用は今回スコープ外
- GUIブロッキングを避けるため、起動時は `ensure_ollama_running()` の待機（最大5秒）を許容する
  - `__init__` はメインループ前に呼ばれるため、ウィンドウ表示が5秒遅れる可能性がある
  - 許容できない場合はスレッド化を検討（今回は対象外）
- 既存のフォールバック動作（`summary_generator.py` / `markdown_translator.py`）は変更しない
