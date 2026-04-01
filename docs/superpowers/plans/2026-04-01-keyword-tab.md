# キーワード管理タブ Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `gui_app.py` に `ttk.Notebook` を導入し、「メイン」タブと「キーワード管理」タブを追加する。

**Architecture:** 既存の `SmartCatchGUI` クラスに `ttk.Notebook` を導入し、`_build_widgets()` を `_build_notebook()` / `_build_main_tab(frame)` / `_build_keyword_tab(frame)` に分割する。キーワードは起動時とBrowse時に読み込み、保存はアトミック書き込みで行う。

**Tech Stack:** Python 3.10, tkinter, tkinter.ttk, json, pathlib

---

## ファイルマップ

| ファイル | 変更内容 |
|----------|----------|
| `gui_app.py` | 全変更はここのみ |

---

### Task 1: ttk import・ウィンドウサイズ変更・Notebook scaffold

**Files:**
- Modify: `gui_app.py`

このタスクでは既存の動作を壊さずに Notebook の骨格だけを作る。
`_build_widgets()` はそのままにし、`_build_notebook()` を新規追加して `__init__` から呼ぶ構造に切り替える。

- [ ] **Step 1: `from tkinter import ttk` を追加する**

`gui_app.py` 冒頭のインポートブロックに追加：

```python
from tkinter import ttk
```

- [ ] **Step 2: ウィンドウサイズを変更する**

`__init__` の `self.root.geometry("760x560")` を変更：

```python
self.root.geometry("900x600")
```

- [ ] **Step 3: `_build_notebook()` を追加し `__init__` から呼ぶ**

`__init__` の `self._build_widgets()` を以下に置き換える：

```python
self._build_notebook()
```

クラスに `_build_notebook()` メソッドを追加（`_build_widgets` の直前に挿入）：

```python
def _build_notebook(self) -> None:
    self.root.columnconfigure(0, weight=1)
    self.root.rowconfigure(0, weight=1)

    self.notebook = ttk.Notebook(self.root)
    self.notebook.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

    main_frame = tk.Frame(self.notebook)
    self.notebook.add(main_frame, text="メイン")

    keyword_frame = tk.Frame(self.notebook)
    self.notebook.add(keyword_frame, text="キーワード管理")

    self._build_main_tab(main_frame)
    self._build_keyword_tab(keyword_frame)
```

- [ ] **Step 4: GUIが起動することを手動確認する**

```bash
cd C:\AI_DEV\projects-B\Smart-Catch
.venv\Scripts\activate
python gui_app.py
```

期待：ウィンドウが900×600で開き、「メイン」「キーワード管理」の2タブが表示される。
「メイン」タブは空、「キーワード管理」タブは空。エラーなし。

- [ ] **Step 5: コミット**

```bash
git add gui_app.py
git commit -m "feat: add ttk.Notebook scaffold with two tabs"
```

---

### Task 2: 既存ウィジェットをメインタブに移動

**Files:**
- Modify: `gui_app.py`

`_build_widgets()` の内容を `_build_main_tab(frame)` に移植する。
`self.root` に対するレイアウト設定を `frame` に切り替えるのが核心。

- [ ] **Step 1: `_build_main_tab(frame)` メソッドを追加する**

`_build_widgets()` の内容をコピーして `_build_main_tab` として追加。
変更点は `self.root` → `frame` のみ：

```python
def _build_main_tab(self, frame: tk.Frame) -> None:
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(4, weight=1)

    tk.Label(frame, text="Config Path").grid(
        row=0, column=0, padx=12, pady=12, sticky="w"
    )
    tk.Entry(frame, textvariable=self.config_path_var).grid(
        row=0, column=1, padx=12, pady=12, sticky="ew"
    )
    tk.Button(frame, text="Browse", command=self.browse_config).grid(
        row=0, column=2, padx=12, pady=12, sticky="ew"
    )

    self.run_button = tk.Button(frame, text="Run", command=self.run_pipeline)
    self.run_button.grid(row=1, column=0, padx=12, pady=4, sticky="ew")
    tk.Label(frame, textvariable=self.status_var, anchor="w").grid(
        row=1, column=1, columnspan=2, padx=12, pady=4, sticky="ew"
    )

    tk.Label(frame, text="Exploration Output").grid(
        row=2, column=0, padx=12, pady=4, sticky="w"
    )
    tk.Label(frame, textvariable=self.exploration_path_var, anchor="w").grid(
        row=2, column=1, padx=12, pady=4, sticky="ew"
    )
    self.open_exploration_button = tk.Button(
        frame,
        text="Open",
        command=lambda: self.open_output_file(self.exploration_path_var.get()),
        state=tk.DISABLED,
    )
    self.open_exploration_button.grid(
        row=2, column=2, padx=12, pady=4, sticky="ew"
    )

    tk.Label(frame, text="Monitoring Output").grid(
        row=3, column=0, padx=12, pady=4, sticky="w"
    )
    tk.Label(frame, textvariable=self.monitoring_path_var, anchor="w").grid(
        row=3, column=1, padx=12, pady=4, sticky="ew"
    )
    self.open_monitoring_button = tk.Button(
        frame,
        text="Open",
        command=lambda: self.open_output_file(self.monitoring_path_var.get()),
        state=tk.DISABLED,
    )
    self.open_monitoring_button.grid(
        row=3, column=2, padx=12, pady=4, sticky="ew"
    )

    self.result_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
    self.result_text.grid(
        row=4, column=0, columnspan=3, padx=12, pady=12, sticky="nsew"
    )
    self.result_text.configure(state=tk.DISABLED)
```

- [ ] **Step 2: `_build_widgets()` を削除する**

`_build_widgets()` メソッド全体を削除する。

- [ ] **Step 3: GUIが正常に動作することを手動確認する**

```bash
python gui_app.py
```

期待：
- 「メイン」タブに既存のウィジェットが全部表示される
- Config Path入力欄、Run ボタン、Output ラベル、ログエリアが正常に表示される
- ウィンドウをリサイズするとログエリアが追従して伸縮する

- [ ] **Step 4: コミット**

```bash
git add gui_app.py
git commit -m "feat: move existing widgets into main tab frame"
```

---

### Task 3: キーワード管理タブのUI構築（静的）

**Files:**
- Modify: `gui_app.py`

Listbox・Entry・ボタンを配置する。この時点ではデータは繋がなくてよい。
削除ボタンの enable/disable だけ `<<ListboxSelect>>` で動かす。

- [ ] **Step 1: `_build_keyword_tab(frame)` を追加する**

```python
def _build_keyword_tab(self, frame: tk.Frame) -> None:
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    # --- Listbox + Scrollbar ---
    list_frame = tk.Frame(frame)
    list_frame.grid(row=0, column=0, columnspan=3, padx=12, pady=12, sticky="nsew")
    list_frame.columnconfigure(0, weight=1)
    list_frame.rowconfigure(0, weight=1)

    self.keyword_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
    self.keyword_listbox.grid(row=0, column=0, sticky="nsew")
    scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.keyword_listbox.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    self.keyword_listbox.configure(yscrollcommand=scrollbar.set)
    self.keyword_listbox.bind("<<ListboxSelect>>", self._on_keyword_select)

    # --- 追加エリア ---
    tk.Label(frame, text="追加:").grid(row=1, column=0, padx=12, pady=4, sticky="w")
    self.keyword_entry = tk.Entry(frame)
    self.keyword_entry.grid(row=1, column=1, padx=4, pady=4, sticky="ew")
    tk.Button(frame, text="追加", command=self._add_keyword).grid(
        row=1, column=2, padx=12, pady=4, sticky="ew"
    )

    # --- 削除・保存ボタン ---
    self.delete_keyword_button = tk.Button(
        frame, text="選択したキーワードを削除", command=self._delete_keyword, state=tk.DISABLED
    )
    self.delete_keyword_button.grid(row=2, column=0, columnspan=2, padx=12, pady=8, sticky="ew")
    tk.Button(frame, text="保存", command=self._save_keywords).grid(
        row=2, column=2, padx=12, pady=8, sticky="ew"
    )
```

- [ ] **Step 2: `_on_keyword_select()` を追加する**

```python
def _on_keyword_select(self, event: tk.Event) -> None:
    selected = self.keyword_listbox.curselection()
    self.delete_keyword_button.configure(
        state=tk.NORMAL if selected else tk.DISABLED
    )
```

- [ ] **Step 3: スタブメソッドを追加する（後のタスクで実装）**

```python
def _add_keyword(self) -> None:
    pass

def _delete_keyword(self) -> None:
    pass

def _save_keywords(self) -> None:
    pass
```

- [ ] **Step 4: 手動確認**

```bash
python gui_app.py
```

期待：
- 「キーワード管理」タブにListbox・Entry・ボタンが表示される
- Listboxで項目を選択すると「選択したキーワードを削除」が enabled になる
- 注意：tkinterの `<<ListboxSelect>>` は選択解除（別の場所クリック）では発火しない場合がある。削除ボタンの disabled 復帰は削除実行後（`_delete_keyword` 内で明示的に `disabled` セット）で担保する。

- [ ] **Step 5: コミット**

```bash
git add gui_app.py
git commit -m "feat: add keyword tab UI layout with listbox and buttons"
```

---

### Task 4: キーワード読み込み（起動時）

**Files:**
- Modify: `gui_app.py`

起動時に `config.json` から `monitoring.keywords` を読み込んで Listbox に表示する。

- [ ] **Step 1: `_load_keywords()` メソッドを追加する**

```python
def _load_keywords(self) -> None:
    """config_path_varが指すconfig.jsonからkeywordsを読み込みListboxに反映する。"""
    self.keyword_listbox.delete(0, tk.END)
    config_path = Path(self.config_path_var.get())
    if not config_path.exists():
        self._append_result("ERROR", f"キーワード読み込み失敗: ファイルが見つかりません: {config_path}")
        return
    try:
        with config_path.open(encoding="utf-8") as f:
            config = json.load(f)
        keywords = config.get("monitoring", {}).get("keywords")
        if keywords is None:
            self._append_result("ERROR", "キーワード読み込み失敗: monitoring.keywords キーが見つかりません")
            return
        for kw in keywords:
            self.keyword_listbox.insert(tk.END, kw)
    except Exception as exc:
        self._append_result("ERROR", f"キーワード読み込み失敗: {exc}")
```

注意：`json` は `gui_app.py` の先頭インポートに追加する：

```python
import json
```

- [ ] **Step 2: `__init__` の末尾で `_load_keywords()` を呼ぶ**

`_append_result("INFO", "Smart-Catch local GUI is ready.")` の直後に追加：

```python
self._load_keywords()
```

- [ ] **Step 3: 手動確認**

```bash
python gui_app.py
```

期待：
- 「キーワード管理」タブを開くと `config/config.json` のキーワードがListboxに表示される
- "AI", "人工知能", "生成AI", "ChatGPT" ... が一覧表示される

- [ ] **Step 4: コミット**

```bash
git add gui_app.py
git commit -m "feat: load keywords from config.json on startup"
```

---

### Task 5: キーワード追加・削除の実装

**Files:**
- Modify: `gui_app.py`

追加・削除ボタンのロジックを実装する（config.jsonへの書き込みはまだ行わない）。

- [ ] **Step 1: `_add_keyword()` を実装する**

既存のスタブを置き換える：

```python
def _add_keyword(self) -> None:
    keyword = self.keyword_entry.get().strip()
    if not keyword:
        return
    existing = list(self.keyword_listbox.get(0, tk.END))
    if keyword in existing:
        return
    self.keyword_listbox.insert(tk.END, keyword)
    self.keyword_entry.delete(0, tk.END)
```

- [ ] **Step 2: `_delete_keyword()` を実装する**

既存のスタブを置き換える：

```python
def _delete_keyword(self) -> None:
    selected = self.keyword_listbox.curselection()
    if not selected:
        return
    self.keyword_listbox.delete(selected[0])
    self.delete_keyword_button.configure(state=tk.DISABLED)
```

- [ ] **Step 3: 手動確認**

```bash
python gui_app.py
```

期待：
- 追加欄に "テスト" と入力して「追加」→ Listboxに追加される
- Entry がクリアされる
- 同じキーワードを再度追加しても重複しない
- 空文字で追加しても何も起きない
- Listboxで "テスト" を選択して「選択したキーワードを削除」→ 削除される
- 削除後、削除ボタンが disabled に戻る

- [ ] **Step 4: コミット**

```bash
git add gui_app.py
git commit -m "feat: implement keyword add and delete in listbox"
```

---

### Task 6: キーワード保存の実装（アトミック書き込み）

**Files:**
- Modify: `gui_app.py`

「保存」ボタンで Listbox の内容を `config.json` に書き戻す。
アトミック書き込み（tmp → rename）で安全に保存する。

- [ ] **Step 1: `_save_keywords()` を実装する**

既存のスタブを置き換える：

```python
def _save_keywords(self) -> None:
    config_path = Path(self.config_path_var.get())
    tmp_path = config_path.with_suffix(".tmp")
    try:
        with config_path.open(encoding="utf-8") as f:
            config = json.load(f)
        keywords = list(self.keyword_listbox.get(0, tk.END))
        config.setdefault("monitoring", {})["keywords"] = keywords
        tmp_path.write_text(
            json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        tmp_path.replace(config_path)
        self._append_result("INFO", f"キーワードを保存しました ({len(keywords)} 件): {config_path}")
    except Exception as exc:
        self._append_result("ERROR", f"キーワード保存失敗: {exc}")
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
```

- [ ] **Step 2: 手動確認（保存 → ファイル確認）**

```bash
python gui_app.py
```

操作手順：
1. 「キーワード管理」タブで "保存テスト" を追加
2. 「保存」ボタンを押す
3. メインタブのログに "キーワードを保存しました" が表示されることを確認
4. エディタで `config/config.json` を開き `monitoring.keywords` に "保存テスト" が追加されていることを確認
5. `keyword_weights` 等の他フィールドが保持されていることを確認

- [ ] **Step 3: コミット**

```bash
git add gui_app.py
git commit -m "feat: implement keyword save with atomic write to config.json"
```

---

### Task 7: Browse時のキーワード再読み込み

**Files:**
- Modify: `gui_app.py`

Browse でファイルを選択したとき、キーワードリストを新しい config から再読み込みする。

- [ ] **Step 1: `browse_config()` に `_load_keywords()` 呼び出しを追加する**

既存の `browse_config()` の `if selected_path:` ブロック末尾に1行追加：

```python
def browse_config(self) -> None:
    selected_path = filedialog.askopenfilename(
        title="Select config.json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        initialdir=str(Path(DEFAULT_CONFIG_PATH).parent),
    )
    if selected_path:
        self.config_path_var.set(selected_path)
        self._append_result("INFO", f"Config path selected: {selected_path}")
        self._load_keywords()   # ← この1行を追加
```

- [ ] **Step 2: 手動確認**

```bash
python gui_app.py
```

期待：
- Browse で別の config ファイルを選択すると Listbox が新しい config のキーワードで更新される
- （同一ファイルを選択した場合もリストが再読み込みされる）

- [ ] **Step 3: コミット**

```bash
git add gui_app.py
git commit -m "feat: reload keywords when config path changed via Browse"
```

---

### Task 8: 最終動作確認

- [ ] **Step 1: `python gui_app.py` で全機能を通しテスト**

```bash
cd C:\AI_DEV\projects-B\Smart-Catch
.venv\Scripts\activate
python gui_app.py
```

確認項目：
- [ ] 起動時にキーワードが表示される
- [ ] キーワードを追加できる
- [ ] キーワードを削除できる
- [ ] 「保存」でconfig.jsonが更新される
- [ ] Browseで別configを選ぶとキーワードリストが更新される
- [ ] メインタブのRunが正常に動作する（既存機能が壊れていない）
- [ ] ウィンドウリサイズ時にログエリアが追従する
- [ ] `.tmp` ファイルが残っていない

- [ ] **Step 2: PROGRESS.md を更新する**

`docs/PROGRESS.md` の「次にやること」からキーワード管理タブを削除し、完了済みに移動する。

- [ ] **Step 3: 最終コミット**

```bash
git add gui_app.py docs/PROGRESS.md
git commit -m "docs: mark keyword-tab feature as complete in PROGRESS.md"
```
