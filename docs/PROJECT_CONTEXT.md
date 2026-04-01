# PROJECT_CONTEXT.md

## 1. プロジェクト概要

本プロジェクトは、公開されている複数のRSSフィードから記事情報を取得し、
キーワードベースで判定・スコアリング・トピック分類を行い、
最終的にMarkdown形式で整理・出力・保存するローカルアプリケーションである。

処理はローカルで実行される。
外部クラウドAPIやデータベースは使用せず、必要に応じてローカルOllamaを翻訳・要約用途で利用できる。
CLIおよびローカルGUIの両方から実行可能である。

本システムは単なる情報収集ツールではなく、
**情報の構造化・要約・意思決定支援まで行うパイプライン**として設計されている。

---

## 2. 現在の機能範囲

現在の実装には以下が含まれる。

### データ取得・前処理
・複数RSSフィードからの記事取得（Hugging Face / OpenAI / Zenn / Qiita）
・記事データの正規化（HTML除去・エンティティ復元）
・summary 空記事への補助要約生成（Ollama英語1文、失敗時はテンプレートフォールバック）

### 判定・整理
・キーワードベースの一致判定
・keyword_weights によるスコアリング
・設定で切替可能な重複排除

### 構造化
・記事ごとの `topic_id` 付与
・トピック単位での要約生成（topic summaries）

### 可視化・意思決定支援
・日次レポート生成（Daily Report）
・行動提案生成（Action Suggestions）

### 出力
・Markdown文字列生成
・CLI標準出力
・Exploration / Monitoring 分離出力
・英語版Markdownファイル保存
・日本語版Markdownファイル保存（Ollama翻訳 → 辞書フォールバック）
・履歴保存（configで切替可能）

### 実行環境
・CLI実行（app.py）
・ローカルGUI実行（gui_app.py）
・Windowsタスクスケジューラ対応（自動実行）

---

## 3. 入力仕様

入力は設定ファイル（JSON）によって与えられる。

主な項目は以下である。

・RSSソース一覧
・キーワード一覧
・キーワード重み設定（任意）
・重複排除設定
・要約生成設定
・出力先設定
・履歴保存設定（output.save_history）
・ログ設定

CLI / GUI から設定ファイルパスを指定可能であり、
未指定時は `config/config.json` を使用する。

---

## 4. 出力仕様

出力はMarkdown形式であり、以下の2系統を持つ。

### Exploration（全体分析）

・全記事を対象
・CLI標準出力対象
・保存対象

構造：

# Daily Report
# Action Suggestions
## Topic Summaries
# Collected Articles

保存先：
- `output/exploration/collected_articles.md`
- `output/exploration/collected_articles_ja.md`

履歴保存（有効時）：
- `collected_articles_YYYY-MM-DD.md`
- `collected_articles_ja_YYYY-MM-DD.md`

---

### Monitoring（重要記事）

・`matched == True` の記事のみ対象
・保存対象

保存先：
- `output/monitoring/monitored_articles.md`
- `output/monitoring/monitored_articles_ja.md`

履歴保存（有効時）：
- `monitored_articles_YYYY-MM-DD.md`
- `monitored_articles_ja_YYYY-MM-DD.md`

---

### Logging

・コンソール出力
・設定に応じたファイル出力
・保存先: `logs/smart_catch.log`

---

### GUI

・実行中 / 成功 / 失敗表示
・保存先表示
・時刻付き結果表示
・出力ファイルオープン導線

---

## 5. 処理フロー

現在の処理は以下のパイプラインで構成される。

load_config
→ setup_logging
→ fetch
→ normalize
→ summarize(optional / Ollama → templateフォールバック)
→ classify / score
→ deduplicate(optional)
→ assign_topics
→ summarize_topics
→ build_daily_report
→ build_action_suggestions
→ split
→ markdown生成
→ 保存（英語版）
→ 日本語翻訳（Ollama → 辞書フォールバック）
→ 保存（日本語版）
→ 履歴保存
→ 出力 / GUI表示
→ ログ記録

---

## 6. 設計方針

本プロジェクトは責務分離を最重要とする。

・fetcher：取得のみ
・normalizer：整形のみ
・summarizer：補助要約のみ
・classifier：判定とスコアのみ
・deduplicator：重複除去のみ
・topic_extractor：トピック付与のみ
・topic_summarizer：トピック要約のみ
・report_generator：日次レポート生成のみ
・action_generator：行動提案生成のみ
・translator：出力済みMarkdownの日本語化のみ
・writer：文字列生成のみ
・file_writer：保存のみ
・pipeline：接続と順序制御のみ
・CLI：入口のみ
・GUI：入口のみ

---

## 7. 変更ポリシー

変更は以下に従う。

・1タスク = 1責務
・変更範囲は最小
・既存責務を侵さない
・出力仕様を破壊しない
・依存追加は原則禁止

---

## 8. 現在の到達状態

・複数RSS取得可能（Hugging Face / OpenAI / Zenn / Qiita）
・正規化 / 判定 / Markdown生成可能
・トピック分類可能
・トピック要約可能
・日次レポート生成可能
・行動提案生成可能
・Exploration / Monitoring 分離可能
・英語版Markdown保存可能
・日本語版Markdown保存可能
・履歴保存可能
・CLI / GUI 両対応
・自動実行対応済み
・ローカルOllama優先の翻訳レイヤー導入済み
・Ollama要約生成導入済み（失敗時テンプレートフォールバック）
・現在は安定運用フェーズにある

---

## 9. 今後の拡張方向

・週次レポート
・通知連携
・Web UI
・API化

---

## 10. 現在のフェーズ

👉 MVP + 自動化 + 意思決定支援 + 日本語閲覧対応 完成
👉 現在は安定運用フェーズ
