# Ollama起動検知・自動起動 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ollamaの起動状態をアプリ起動時・Run実行時に自動チェックし、未起動なら自動起動を試みてGUIにWARNINGを表示する。

**Architecture:** `src/utils/ollama_health.py` に `is_ollama_running()` / `ensure_ollama_running()` を実装し、`gui_app.py` の `__init__`（`root.after` 経由）と `run_pipeline()` の `try` ブロック内から呼び出す。既存の翻訳・要約フォールバックは変更しない。

**Tech Stack:** Python 3.10, urllib.request, subprocess, time, tkinter

---

## ファイルマップ

| ファイル | 操作 | 内容 |
|----------|------|------|
| `src/utils/__init__.py` | 新規作成 | 空ファイル（パッケージ化） |
| `src/utils/ollama_health.py` | 新規作成 | `is_ollama_running()` / `ensure_ollama_running()` |
| `gui_app.py` | 変更 | 起動時・Run時チェック追加 |
| `docs/ARCHITECTURE.md` | 変更 | `src/utils/` を追記 |

---

### Task 1: `src/utils/` パッケージ作成と `is_ollama_running()` 実装

**Files:**
- Create: `src/utils/__init__.py`
- Create: `src/utils/ollama_health.py`

- [ ] **Step 1: `src/utils/__init__.py` を作成する（空ファイル）**

```bash
# Windows Git Bash
touch src/utils/__init__.py
```

または Write ツールで空ファイルを作成（内容なし）。

- [ ] **Step 2: `src/utils/ollama_health.py` に `is_ollama_running()` を実装する**

```python
import subprocess
import time
import urllib.request

OLLAMA_HEALTH_URL = "http://localhost:11434/api/tags"
OLLAMA_CHECK_TIMEOUT = 2  # seconds
OLLAMA_START_POLL_INTERVAL = 0.5  # seconds
OLLAMA_START_MAX_ATTEMPTS = 10  # max 5 seconds total


def is_ollama_running() -> bool:
    """localhost:11434/api/tags にGETリクエストを送り、Ollamaの起動を確認する。
    タイムアウト2秒。200応答ならTrue、それ以外はFalse。
    """
    try:
        with urllib.request.urlopen(OLLAMA_HEALTH_URL, timeout=OLLAMA_CHECK_TIMEOUT):
            return True
    except Exception:
        return False


def ensure_ollama_running() -> bool:
    """Ollamaが未起動の場合、ollama serve をバックグラウンドで起動する。
    time.sleep(0.5) × 最大10回ポーリングで起動確認（最大5秒待機）。
    起動済みなら即True。起動失敗ならFalse。
    Popen ハンドルは意図的に保持しない（ollama はデーモンのため .wait() 不要）。
    複数回呼ばれても安全（2回目の Popen はポート競合で即終了する）。
    """
    if is_ollama_running():
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
        if is_ollama_running():
            return True

    return False
```

- [ ] **Step 3: インポートが通ることを確認する**

```bash
cd C:\AI_DEV\projects-B\Smart-Catch
.venv/Scripts/python -c "from src.utils.ollama_health import is_ollama_running, ensure_ollama_running; print('OK')"
```

期待出力: `OK`

- [ ] **Step 4: `is_ollama_running()` の動作を手動確認する**

Ollama が起動している場合:
```bash
.venv/Scripts/python -c "from src.utils.ollama_health import is_ollama_running; print(is_ollama_running())"
```
期待: `True`

Ollama が停止している場合（または未インストール）:
期待: `False`（2秒後に返る）

- [ ] **Step 5: コミット**

```bash
git add src/utils/__init__.py src/utils/ollama_health.py
git commit -m "feat: add ollama_health utility with is_ollama_running and ensure_ollama_running"
```

---

### Task 2: `gui_app.py` に起動時チェックを追加

**Files:**
- Modify: `gui_app.py`

現在の `__init__` の末尾は以下（`gui_app.py` 33-35行）：
```python
self._build_notebook()
self._append_result("INFO", "Smart-Catch local GUI is ready.")
self._load_keywords()
```

- [ ] **Step 1: `__init__` の末尾に `root.after` 呼び出しを追加する**

`self._load_keywords()` の直後（`__init__` の最終行として）に追加：

```python
self.root.after(100, self._check_ollama_on_startup)
```

- [ ] **Step 2: `_check_ollama_on_startup()` メソッドを追加する**

`_load_keywords()` メソッドの直前（または直後）に追加：

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

- [ ] **Step 3: インポートエラーがないことを確認する**

```bash
.venv/Scripts/python -c "import gui_app; print('OK')"
```

期待: `OK`

- [ ] **Step 4: GUI起動して動作を手動確認する**

```bash
python gui_app.py
```

期待（Ollama起動中の場合）：
- ウィンドウが表示される
- 約100ms後にログエリアに `[INFO] Ollama: 起動確認済み` が表示される

期待（Ollama未起動の場合）：
- `[WARNING] Ollama未起動。自動起動を試みています...` が表示される
- 数秒後に `[INFO] Ollama: 自動起動成功` または `[WARNING] Ollama起動失敗。...` が表示される
- 確認中もウィンドウが「応答なし」にならない

- [ ] **Step 5: コミット**

```bash
git add gui_app.py
git commit -m "feat: add Ollama startup check via root.after on GUI launch"
```

---

### Task 3: `gui_app.py` の `run_pipeline()` に Run時チェックを追加

**Files:**
- Modify: `gui_app.py`

現在の `run_pipeline()` の `try` ブロック内（`gui_app.py` 約226-232行）：
```python
try:
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(...)
    if not config_file.is_file():
        raise FileNotFoundError(...)

    setup_logging()   # ← ここの直前に追加
```

- [ ] **Step 1: config ファイル存在チェックの直後、`setup_logging()` の直前に追加する**

```python
    from src.utils.ollama_health import is_ollama_running
    if not is_ollama_running():
        self._append_result("WARNING", "Ollama未起動。要約・翻訳はフォールバックで処理します")
```

- [ ] **Step 2: インポートエラーがないことを確認する**

```bash
.venv/Scripts/python -c "import gui_app; print('OK')"
```

期待: `OK`

- [ ] **Step 3: GUI で Run を実行して動作を手動確認する**

```bash
python gui_app.py
```

Ollama未起動の状態で Run ボタンを押す：
- ログに `[WARNING] Ollama未起動。要約・翻訳はフォールバックで処理します` が表示される
- パイプラインはその後も続行される（フォールバックで処理される）
- Run完了後、Run ボタンが再度 enabled になる

- [ ] **Step 4: コミット**

```bash
git add gui_app.py
git commit -m "feat: add Ollama availability warning before pipeline run"
```

---

### Task 4: `docs/ARCHITECTURE.md` を更新する

**Files:**
- Modify: `docs/ARCHITECTURE.md`

- [ ] **Step 1: `docs/ARCHITECTURE.md` を読んで `src/` のディレクトリ一覧を確認する**

`src/` 配下のモジュール一覧が記載されているセクションを探す。

- [ ] **Step 2: `src/utils/` のエントリを追加する**

既存の `src/` 配下のリストに以下を追加：

```
src/utils/
└── ollama_health.py    # Ollama起動確認・自動起動ユーティリティ
```

- [ ] **Step 3: コミット**

```bash
git add docs/ARCHITECTURE.md
git commit -m "docs: add src/utils/ to ARCHITECTURE.md"
```

---

### Task 5: 最終動作確認・push

- [ ] **Step 1: インポート総合確認**

```bash
cd C:\AI_DEV\projects-B\Smart-Catch
.venv/Scripts/python -c "
from src.utils.ollama_health import is_ollama_running, ensure_ollama_running
import gui_app
print('All imports OK')
"
```

期待: `All imports OK`

- [ ] **Step 2: GUI 起動して全シナリオを確認する**

```bash
python gui_app.py
```

確認項目：
- [ ] 起動時ログに Ollama 状態が表示される
- [ ] Run 実行時、Ollama 未起動なら WARNING が表示される
- [ ] Run はフォールバックで正常に完了する
- [ ] ウィンドウが「応答なし」にならない
- [ ] キーワード管理タブが引き続き動作する

- [ ] **Step 3: リモートにプッシュする**

```bash
git push origin feature/ollama-summary-and-translator-fix
```

- [ ] **Step 4: `docs/PROGRESS.md` を更新する**

「次にやること」から Ollama起動検知を削除し、完了済みに移動する。

```bash
git add docs/PROGRESS.md
git commit -m "docs: update PROGRESS.md - ollama health check complete"
git push origin feature/ollama-summary-and-translator-fix
```
