# キーワード管理タブ 設計ドキュメント

**作成日:** 2026-04-01  
**対象ファイル:** `gui_app.py`  
**ステータス:** 承認済み（レビュー反映済み）

---

## 概要

既存の `gui_app.py`（tkinter製GUI）に `ttk.Notebook` を導入し、  
「メイン」タブと「キーワード管理」タブの2タブ構成に変更する。  
キーワード管理タブでは `config/config.json` の `monitoring.keywords` を表示・追加・削除・保存できる。

---

## アーキテクチャ

### クラス構造

```
SmartCatchGUI
├── ttk.Notebook
│   ├── Tab 1「メイン」  ← 既存ウィジェットをそのまま移動
│   └── Tab 2「キーワード管理」  ← 新規追加
```

### メソッド構成の変更

| 変更前 | 変更後 |
|--------|--------|
| `_build_widgets()` | `_build_notebook()` → `_build_main_tab(frame)` + `_build_keyword_tab(frame)` |

- 既存ウィジェットのロジックは変更しない
- `_build_main_tab()` は既存 `_build_widgets()` の内容をフレーム内に移動するだけ

### インポートの変更

`gui_app.py` の既存 tkinter インポートに以下を追加：

```python
from tkinter import ttk
```

### ウィンドウサイズ

既存の `760x560` から `900x600` に変更する（Notebookタブ分の余白確保のため）。

---

## キーワード管理タブ UI

```
┌─────────────────────────────────────────┐
│ Tab: メイン │ Tab: キーワード管理        │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ AI                              │   │
│  │ 人工知能                        │   │
│  │ 生成AI                          │   │
│  │ ChatGPT                         │   │
│  │ ...                             │   │
│  └─────────────────────────────────┘   │
│                                         │
│  追加: [________________] [追加]        │
│                                         │
│  [選択したキーワードを削除]  [保存]      │
│                                         │
└─────────────────────────────────────────┘
```

### コンポーネント

| コンポーネント | 役割 |
|----------------|------|
| `Listbox` + Scrollbar | キーワード一覧表示（単一選択） |
| `Entry` | 新しいキーワードの入力欄 |
| 追加ボタン | Entryの内容をListboxに追加 |
| 削除ボタン | 選択中のキーワードをListboxから削除 |
| 保存ボタン | Listbox内容を `config.json` に書き戻す |

### 削除ボタンのenable/disable

- 初期状態：`disabled`
- Listboxで項目が選択されたとき（`<<ListboxSelect>>` イベント）：`normal`
- 選択が解除されたとき：`disabled`

### Enterキーショートカット

追加EntryでEnterキーを押してもAddは発火しない（ボタン操作のみ）。これは意図的な設計。

---

## データフロー

### 読み込みタイミング

キーワードリストの読み込みは以下の2タイミングで行う：

1. **GUIの起動時**（`__init__` 内）：`config_path_var` の初期値（DEFAULT_CONFIG_PATH）から読み込む
2. **Browseでファイルを選択したとき**：`browse_config()` 内でキーワードリストを再読み込みする

こうすることで、configパスが変わった後もキーワードタブの内容が同期される。

### 保存

1. 現在の `config_path_var.get()` をパスとして使用する（読み込み時と同じパスを保証）
2. そのパスのJSONをまず読み込む
3. `monitoring.keywords` のみ Listbox の現在の内容で上書き（`keyword_weights` 等の他フィールドは保持）
4. **アトミック書き込み**：一時ファイルに書き出してからリネームする
   ```python
   tmp_path = path.with_suffix(".tmp")
   tmp_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
   tmp_path.replace(path)  # アトミックなリネーム
   ```
5. メインタブの `_append_result()` に成功/失敗を出力する（クラス内メソッドの呼び出しのため許容）

### エラーハンドリング

| ケース | 動作 |
|--------|------|
| `config.json` が見つからない | Listbox空で起動、`_append_result("ERROR", ...)` 出力 |
| `monitoring` キーまたは `monitoring.keywords` キーが存在しない | Listbox空で起動、`_append_result("ERROR", ...)` 出力 |
| 保存時に書き込み失敗 | `_append_result("ERROR", ...)` 出力、`config.json` は変更しない（一時ファイルが残る場合は削除） |
| 重複キーワードの追加 | 無視（大文字小文字区別あり。"AI" と "ai" は別キーワードとして扱う。意図的な仕様） |
| 空文字の追加 | 無視 |

---

## クロスタブ結合について

キーワードタブの保存結果を `_append_result()` でメインタブのログに出力する。  
`_append_result()` は `SmartCatchGUI` クラスのメソッドであり、同クラス内からの呼び出しのため許容する。  
将来タブを分離する場合はイベント経由に変更すること。

---

## 制約・スコープ外

- `monitoring.keyword_weights`（重み）の編集はスコープ外
- タブ切り替え時の自動再読み込みはしない
- 自動保存はしない（明示的な保存ボタン押下のみ）

---

## 実装時の注意（レビュー指摘）

- `_build_main_tab(frame)` に移動する際、`self.root.columnconfigure` / `self.root.rowconfigure` を `frame.columnconfigure` / `frame.rowconfigure` に変更すること。加えて `self.root.columnconfigure(0, weight=1)` と `self.root.rowconfigure(0, weight=1)` を設定してNotebook自体が伸縮するようにすること（これを漏らすとresult_textがウィンドウに追従しなくなる）。
- アトミック書き込みで `tmp_path.replace(path)` が失敗した場合は `try/finally` で一時ファイルを確実に削除すること。

---

## 変更ファイル

- `gui_app.py`：1ファイルのみ変更
  - `from tkinter import ttk` を追加
  - `geometry("900x600")` に変更
  - `_build_widgets()` を `_build_notebook()` / `_build_main_tab()` / `_build_keyword_tab()` に分割
  - `browse_config()` にキーワードリスト再読み込みを追加
  - キーワード保存メソッド `_save_keywords()` を追加
- 新規ファイルなし
