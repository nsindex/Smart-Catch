# PROGRESS.md

## 現在の状況
👉 現在のフェーズ：安定運用中

## 直近の作業内容（2026-04-02）

### セキュリティ修正 4件（feature/security-fixes）

- `src/fetchers/rss_fetcher.py`：`validate_rss_url()` 追加（http/https のみ許可・localhost/プライベートIP拒否）
- `src/utils/file_manager.py`：`resolve_safe_output_dir()` 追加（output/ 配下への書き込みを強制）・`purge_old_files()` に適用
- `src/writers/file_writer.py`：`atomic_write_text()` 追加・全 write_text をアトミック書き込みに置換・パストラバーサル防止
- `src/translators/markdown_translator.py`：翻訳キャッシュ保存をアトミック化・Ollama プロンプトへサニタイズ適用
- `src/summarizers/summary_generator.py`：Ollama プロンプトへサニタイズ適用
- `src/utils/llm_sanitizer.py`：新規作成（`sanitize_llm_input()` — 制御文字除去・長さ制限・プロンプトインジェクション対策）
- Codex レビューで発見したパス二重化バグ（`output/output/exploration`）を修正
- `tests/` ディレクトリ新設・27件のテストをすべて PASS

## 次にやること
- feature/security-fixes を main にマージする（PR作成）

## 現在のブランチ
- `feature/security-fixes`（main へのマージ待ち）

---

## 直近の作業内容（2026-04-01）

### 翻訳・要約改善
- `markdown_translator.py`：Ollamaリクエストに `temperature=0` / `stop` トークンを追加（出力安定化）
- `markdown_translator.py`：`URLError` を `reason` で分岐し、タイムアウトと接続拒否でキャッシュ戦略を分離
- `summary_generator.py`：Ollamaによる英語1文要約生成を追加（`_generate_summary_with_ollama`）
- `summary_generator.py`：`_is_safe_summary` によるOllama出力サニタイズを追加
- Ollama未起動時はテンプレート文字列へフォールバック（既存動作を維持）

### RSSソース追加
- `config/config.json`：Zenn・Qiitaを追加（feedparserで取得確認済み、max_items: 10）

### ドキュメント整備
- `CLAUDE.md` を新規作成（プロジェクト概要・アーキテクチャ・開発ルール・ディレクトリ構成）
- `docs/` フォルダを作成し Template 構成に移行
  - `docs/AGENTS.md`（Templateからコピー）
  - `docs/ARCHITECTURE.md`（Smart-Catch用に更新）
  - `docs/DECISIONS.md`（新規・今日の設計判断を記録）
  - `docs/PROJECT_CONTEXT.md`（Smart-Catch用に更新）
  - `docs/TASK_PLAN.md`（T36・T37を追記）
- ルートの旧ドキュメント4ファイルを削除
- `.gitignore` に `output/` と `*.bak` を追加（シェル展開バグも修正）

### Codexレビュー
- コミット前に Codex でレビューを実施
- 指摘2点（URLErrorタイムアウト分岐・サニタイズ漏れ）を修正してからコミット

## 現在のブランチ
- `main`（PR#5マージ済み）

## 直近の作業内容（2026-04-01 追記その2）

### Ollama起動検知・自動起動
- `src/utils/ollama_health.py` を新規作成（`is_ollama_running()` / `ensure_ollama_running()`）
- `gui_app.py`：起動時に `root.after(100, ...)` でOllamaチェック・自動起動を試みる
- `gui_app.py`：Run実行前に `is_ollama_running()` をチェックし、未起動ならWARNING表示
- 既存フォールバック（定型文）は維持

## 直近の作業内容（2026-04-01 追記）

### GUIキーワード管理タブ追加
- `gui_app.py`：`ttk.Notebook` を導入し「メイン」「キーワード管理」2タブ構成に変更
- キーワード管理タブ：`monitoring.keywords` の表示・追加・削除・保存機能を実装
- 保存はアトミック書き込み（tmp→rename）、Browse時にキーワードリストを自動再読み込み
- ウィンドウサイズ 760×560 → 900×600 に変更

## 直近の作業内容（2026-04-01 追記その3）

### RSSソース追加
- feedparser で取得検証後、3ソースを追加
  - Google DeepMind Blog（status=200、100件）
  - Meta AI Research / engineering.fb.com（status=200、9件）※ai.meta.com/blog/feed/ は404のため代替
  - ITmedia AI（status=200、20件、日本語）
- Anthropic Blog は公開RSSフィードが確認できないため追加見送り

### キーワード強化
- `monitoring.keywords` を21件 → 45件に拡充
  - ツール系13件: Cursor, Copilot, Windsurf, Devin, Bolt, Dify, LangChain, LlamaIndex, Ollama, Perplexity, Gemini, Grok, OpenCLAW
  - 技術系7件: RAG, fine-tuning, プロンプトエンジニアリング, MCP, エージェント, マルチモーダル, embedding
  - 人物系4件: Altman, Dario, LeCun, Hinton

### PR・マージ
- PR#5 `feature/ollama-summary-and-translator-fix` → `main` マージ・ブランチ削除完了

## 次にやること
- `python app.py` を実行して動作確認

## 既知の問題
- Ollama未起動時は要約が定型文にフォールバック（設計上の許容範囲）

## セッション終了: 2026-04-01 18:02

セッション終了: 2026-04-01 18:04

セッション終了: 2026-04-01 18:05

セッション終了: 2026-04-02 12:20

セッション終了: 2026-04-02 12:22

セッション終了: 2026-04-02 13:20

セッション終了: 2026-04-02 13:22

セッション終了: 2026-04-02 13:25

セッション終了: 2026-04-02 14:06

セッション終了: 2026-04-02 14:11

セッション終了: 2026-04-02 14:13

セッション終了: 2026-04-02 14:17

セッション終了: 2026-04-02 15:12

セッション終了: 2026-04-02 15:13

セッション終了: 2026-04-02 15:14

セッション終了: 2026-04-02 15:19

セッション終了: 2026-04-02 15:22

セッション終了: 2026-04-02 15:24

セッション終了: 2026-04-02 15:26

セッション終了: 2026-04-02 15:28

セッション終了: 2026-04-02 15:31

セッション終了: 2026-04-02 15:37

セッション終了: 2026-04-02 15:38

セッション終了: 2026-04-02 15:38

セッション終了: 2026-04-02 15:42

セッション終了: 2026-04-07 08:42

セッション終了: 2026-04-07 08:43

セッション終了: 2026-04-07 08:50

セッション終了: 2026-04-07 09:02

セッション終了: 2026-04-07 09:05
