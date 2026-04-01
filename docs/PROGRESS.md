# PROGRESS.md

## 現在の状況
👉 現在のフェーズ：安定運用中

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
- `feature/ollama-summary-and-translator-fix`（未マージ）
- mainへのPRは未作成

## 直近の作業内容（2026-04-01 追記）

### GUIキーワード管理タブ追加
- `gui_app.py`：`ttk.Notebook` を導入し「メイン」「キーワード管理」2タブ構成に変更
- キーワード管理タブ：`monitoring.keywords` の表示・追加・削除・保存機能を実装
- 保存はアトミック書き込み（tmp→rename）、Browse時にキーワードリストを自動再読み込み
- ウィンドウサイズ 760×560 → 900×600 に変更

## 次にやること
- `python app.py` を実行して今日の変更の動作確認
- Qiitaノイズ対策（min_score設定）
- 翻訳混在の軽微な修正（TERM_MAP処理順）
- `feature/ollama-summary-and-translator-fix` → `main` へのPR作成

## 既知の問題
- Ollama未起動時は要約が定型文にフォールバック（設計上の許容範囲）
- 翻訳でTERM_MAPが部分一致上書きするため混在が残る
- 今日の変更後に `app.py` の動作確認が未実施

## セッション終了: 2026-04-01 18:02

セッション終了: 2026-04-01 18:04

セッション終了: 2026-04-01 18:05
