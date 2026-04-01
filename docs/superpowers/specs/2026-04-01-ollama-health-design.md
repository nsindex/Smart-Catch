# Ollama起動検知・自動起動 設計ドキュメント

**作成日:** 2026-04-01  
**ステータス:** 承認済み（レビュー反映済み）

---

## 概要

アプリ起動時・Run実行時にOllamaの起動状態を自動チェックし、未起動の場合は `ollama serve` をバックグラウンド起動する。起動失敗時はWARNINGログを出力して既存のフォールバック動作（定型文）で処理を続行する。

---

## アーキテクチャ

### 新規ファイル

```
src/utils/
├── __init__.py        ← 新規（空ファイル）
└── ollama_health.py   ← 新規
```

### 変更ファイル

| ファイル | 変更内容 |
|----------|----------|
| `gui_app.py` | 起動時・Run実行前の2箇所に呼び出しを追加 |
| `docs/ARCHITECTURE.md` | `src/utils/` ディレクトリを追記 |

### 変更しないファイル

- `src/summarizers/summary_generator.py`（既存フォールバック維持）
- `src/translators/markdown_translator.py`（既存フォールバック維持）
- `src/pipelines/rss_pipeline.py`
- `app.py`（今回スコープ外）

---

## `src/utils/ollama_health.py`

### 公開API

```python
def is_ollama_running() -> bool:
    """localhost:11434/api/tags にGETリクエストを送り、Ollamaの起動を確認する。
    タイムアウト2秒。200応答ならTrue、それ以外はFalse。"""

def ensure_ollama_running() -> bool:
    """Ollamaが未起動の場合、ollama serve をバックグラウンドで起動する。
    time.sleep(0.5) × 最大10回ポーリングで起動確認（最大5秒待機）。
    起動済みなら即True。起動失敗ならFalse。"""
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
        # Popen ハンドルは意図的に保持しない。
        # ollama serve はデーモンとして動作し続けるため .wait() は不要。
        # 複数回呼ばれた場合、2回目の Popen はポート競合で即終了する（安全）。
    except OSError:
        # FileNotFoundError（PATH未登録）を含む全OS例外を捕捉
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
| `ollama` が PATH にない | `OSError`（`FileNotFoundError` を含む）を捕捉してFalse |
| `ollama serve` が5秒で応答なし | ポーリングタイムアウトでFalse |
| `ollama serve` が即エラー終了 | 次のポーリングで `is_ollama_running()` がFalseのままFalse |
| 2回目以降の `ensure_ollama_running()` 呼び出し | `is_ollama_running()` がTrueなら即True返却。Falseでも `Popen` がポート競合で即終了するだけで安全 |

---

## `gui_app.py` の変更

### 1. 起動時チェック（`__init__`）

**挿入位置：** `self._load_keywords()` の呼び出し後、最終行として追加：

```python
self.root.after(100, self._check_ollama_on_startup)
```

`root.after(100, ...)` を使うことで `mainloop()` 開始後（100ms後）にチェックを実行する。
これにより `ensure_ollama_running()` の最大5秒ブロックは **メインループ開始後** に発生し、ウィンドウが "Not Responding" にならない。
（ただし、ウィンドウは応答するが操作はブロックされる。自動起動中は `update_idletasks()` 不要。）

新規メソッド：

```python
def _check_ollama_on_startup(self) -> None:
    from src.utils.ollama_health import ensure_ollama_running, is_ollama_running
    if is_ollama_running():
        self._append_result("INFO", "Ollama: 起動確認済み")
        return
    self._append_result("WARNING", "Ollama未起動。自動起動を試みています...")
    success = ensure_ollama_running()
    if success:
        self._append_result("INFO", "Ollama: 自動起動成功")
    else:
        self._append_result("WARNING", "Ollama起動失敗。要約・翻訳はフォールバックになります")
```

### 2. Run実行前チェック（`run_pipeline`）

**挿入位置：** `try` ブロック内、config ファイル存在チェックの直後：

```python
from src.utils.ollama_health import is_ollama_running
if not is_ollama_running():
    self._append_result("WARNING", "Ollama未起動。要約・翻訳はフォールバックで処理します")
```

`try` ブロック内に配置することで、例外発生時も `finally` の `_set_running_state(False)` が確実に実行される。

---

## ログ出力仕様

| タイミング | 状況 | レベル | メッセージ |
|-----------|------|--------|-----------|
| 起動時 | 起動確認済み | INFO | `Ollama: 起動確認済み` |
| 起動時 | 未起動・自動起動試行 | WARNING | `Ollama未起動。自動起動を試みています...` |
| 起動時 | 自動起動成功 | INFO | `Ollama: 自動起動成功` |
| 起動時 | 自動起動失敗 | WARNING | `Ollama起動失敗。要約・翻訳はフォールバックになります` |
| Run時 | 未起動 | WARNING | `Ollama未起動。要約・翻訳はフォールバックで処理します` |
| Run時 | 起動確認OK | （なし） | ログなし（ノイズ抑制） |

---

## 制約・スコープ外

- `app.py`（CLI）への適用は今回スコープ外
- `root.after(100, ...)` により `mainloop()` 開始後に実行されるため、起動時の5秒ブロック中もウィンドウは「応答なし」にならない。ただし、自動起動待機中はユーザー操作がブロックされる（許容範囲）
- GUIスレッド化は今回対象外
- 既存フォールバック動作（`summary_generator.py` / `markdown_translator.py`）は変更しない
