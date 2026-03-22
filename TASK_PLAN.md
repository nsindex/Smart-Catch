# TASK_PLAN（更新版 v2.0）

## 1. 目的

本ドキュメントは、Smart-Catch の開発タスクを
**T単位（機能単位）で管理**し、CODEX が 1タスク単位で実装・確認・ドキュメント同期まで進められる状態を作ることを目的とする。

本ドキュメントにおける「タスク」とは、`Txx` 形式のIDを持つ項目のみを指す。  
細かい実装手順はここでは分解しすぎず、各タスクの完了条件と停止条件を明確にする。

---

## 2. 現在の開発フェーズ

・MVP完成済み  
・複数RSS対応済み  
・Markdown保存対応済み  
・Monitoring / Exploration 分離完了  
・補助要約生成追加済み  
・スコアリング改善済み  
・重複排除追加済み  
・ログ機構追加済み  
・ローカルGUI改善済み  
・自動実行対応済み  
・トピック抽出 / 要約基盤追加済み  
・Exploration でのトピック表示追加済み  
・日次レポート生成追加済み  
・現在は拡張フェーズにある

---

## 3. 完了済みタスク（DONE）

### T01 設定読込
Status: DONE

目的  
・設定ファイルを読み込めるようにする

完了状態  
・`config_loader.py` 実装済み  
・JSON読込可能

---

### T02 RSS取得
Status: DONE

目的  
・RSS記事を取得できるようにする

完了状態  
・`rss_fetcher.py` 実装済み  
・feedparser による取得可能  
・基本的な例外処理あり

---

### T03 正規化
Status: DONE

目的  
・取得データを共通構造へ変換する

完了状態  
・`rss_normalizer.py` 実装済み  
・キー統一  
・欠損吸収  
・summary の HTML 除去  
・HTMLエンティティ復元

---

### T04 キーワード判定
Status: DONE

目的  
・記事の一致判定を行う

完了状態  
・`keyword_classifier.py` 実装済み  
・title / summary に対する部分一致  
・`matched` / `matched_keywords` / `score` を付与

---

### T05 Markdown生成
Status: DONE

目的  
・記事一覧をMarkdown文字列へ変換する

完了状態  
・`markdown_writer.py` 実装済み  
・構造化Markdown出力可能

---

### T06 パイプライン接続
Status: DONE

目的  
・各モジュールを接続して処理を流す

完了状態  
・`rss_pipeline.py` 実装済み  
・取得 → 正規化 → 判定 → Markdown生成 の流れを接続済み

---

### T07 CLI実装
Status: DONE

目的  
・CLIから実行できるようにする

完了状態  
・`app.py` 実装済み  
・引数処理  
・標準出力表示  
・例外処理

---

### T08 E2E動作確認
Status: DONE

目的  
・最小パイプラインが最後まで動くことを確認する

完了状態  
・CLIから実行成功  
・Markdown出力確認  
・HTML除去確認

---

### T09 Markdown保存機能
Status: DONE

目的  
・標準出力だけでなく Markdown をファイル保存できるようにする

完了状態  
・`file_writer.py` 追加済み  
・exploration 出力を保存可能  
・既存の CLI 出力仕様維持

---

### T10 複数RSS対応
Status: DONE

目的  
・複数のRSSソースを統合処理できるようにする

完了状態  
・configで複数RSSを扱える  
・pipelineでループ処理済み  
・結果を1つの出力へ統合

---

### T11 Monitoring / Exploration 分離
Status: DONE

目的  
・全記事出力と重要記事出力を分離する

完了状態  
・Exploration = 全記事  
・Monitoring = `matched == True` の記事  
・`output/exploration/collected_articles.md` 保存  
・`output/monitoring/monitored_articles.md` 保存  
・Monitoring 0件でも落ちないことを確認済み  
・CLI出力は従来どおり exploration を維持

---

### T12 LLM Summary生成
Status: DONE

目的  
・summary が空の記事に対して、補助的な要約文を生成できるようにする

完了状態  
・`summary_generation.enabled` を config で切替可能  
・`src/summarizers/summary_generator.py` を追加済み  
・summary 空記事に対してのみ補助要約を試行  
・失敗時は元記事のまま継続  
・既存 Exploration / Monitoring / CLI 出力仕様を維持

---

### T13 スコアリング改善
Status: DONE

目的  
・記事の重要度をより適切に評価できるようにする

完了状態  
・`monitoring.keyword_weights` を config で指定可能  
・weight 未設定 keyword は 1 で動作  
・title / summary 一致箇所の差を score に反映  
・`matched` / `matched_keywords` の既存仕様維持

---

### T14 重複排除
Status: DONE

目的  
・同一または類似記事の重複出力を減らす

完了状態  
・`deduplication.enabled` / `deduplication.mode` を config で指定可能  
・`src/deduplicators/article_deduplicator.py` を追加済み  
・URL 完全一致重複を除去可能  
・正規化タイトル一致重複を除去可能  
・残存優先順位は score → summary 長 → 先着  
・既存 Exploration / Monitoring / CLI 出力仕様を維持

---

### T15 ログ機構
Status: DONE

目的  
・処理状況と失敗原因を追跡しやすくする

完了状態  
・`src/logging_config.py` を追加済み  
・config の `logging` 設定に従ってログ初期化可能  
・INFO レベルで基本処理進行を記録可能  
・`save_to_file=true` で `logs/smart_catch.log` 保存可能  
・`save_to_file=false` でファイル保存停止可能  
・致命エラー内容をログへ記録可能  
・既存 CLI / Exploration / Monitoring / 保存仕様を維持

---

### T16 GUI / Web化（T16-A / T16-B ローカルGUI）
Status: DONE

目的  
・CLI以外のローカル実行入口を追加し、使いやすさを改善する

完了状態  
・`gui_app.py` を追加済み  
・config パス指定で既存 pipeline を実行可能  
・成功 / 失敗を画面表示可能  
・Exploration / Monitoring 保存先を表示可能  
・時刻付き追記ログ形式の結果表示を追加済み  
・Run ボタンの多重実行防止を追加済み  
・出力ファイルを開く導線を追加済み  
・既存 CLI 挙動を維持  
・Web化は未実装  

---

### T17 自動実行（Windowsタスクスケジューラ対応）
Status: DONE

目的  
・Windows タスク スケジューラから定期実行しやすい入口を追加する

完了状態  
・`run_smart_catch.bat` を追加済み  
・`.venv\Scripts\python.exe` を使って既存 `app.py` を起動可能  
・作業ディレクトリを保証可能  
・config 未指定 / 指定の両方に対応  
・README に Windows タスク スケジューラ手順を同期済み

---
### T18 設定バリデーション
Status: DONE

目的  
・config/config.json の不正を実行前に検出し、設定エラーとして明確に停止させる  

完了状態  
・`src/config_loader.py` に validate_config を実装済み  
・JSON構造 / 必須キー / 型チェックを実装済み  
・異常系（A〜Dテスト）で正しくエラー検出できることを確認済み  
・正常系で既存機能に影響がないことを確認済み  

---
### T19 トピック抽出（topic_id付与）
Status: DONE

目的  
・収集した記事にトピックIDを付与し、話題単位での整理を可能にする

完了状態  
・`src/topic_extractors/topic_extractor.py` を追加済み  
・各記事 dict に `topic_id` を付与可能  
・matched_keywords と title / summary 語の最小ルールで topic 判定可能

---

### T20 トピック要約（内部データ生成）
Status: DONE

目的  
・`topic_id` ごとに記事をまとめ、トピック単位の要約データを生成できるようにする

完了状態  
・`src/topic_summarizers/topic_summarizer.py` を追加済み  
・`topic_id` / `article_count` / `top_keywords` / `summary` を生成可能  
・matched_keywords 優先の設計を維持  
・title / summary 語抽出時に最小限の stopwords を除外済み

---

### T21 トピック表示（Markdown反映）
Status: DONE

目的  
・生成済みの topic summaries を Exploration Markdown に表示し、人間が読める形にする

完了状態  
・Exploration Markdown 先頭に `Topic Summaries` 節を表示可能  
・`topic_id` / `article_count` / `top_keywords` / `summary` を表示可能  
・その後に既存の `# Collected Articles` が続く  
・Monitoring Markdown の既存形式を維持

---
### T22 日次レポート生成
Status: DONE

目的  
・収集・分類・トピック化・要約済みの情報から、その日読むべき日次レポートを生成できるようにする

完了状態  
・`src/report_generators/daily_report_generator.py` を追加済み  
・`generated_at` / `topic_count` / `top_topics` / `highlight_articles` / `summary` を生成可能  
・Exploration Markdown 先頭に `# Daily Report` 節を追加可能  
・その後に既存の `## Topic Summaries` と `# Collected Articles` が続く  
・Monitoring Markdown の既存形式を維持

---

## 6. タスク実行ルール

・1タスク = 1機能単位で扱う  
・CODEX は T単位で実装・確認・必要な資料更新まで行う  
・人間は T完了時のみ確認と承認を行う  
・途中の細かい手順分割は、原則として TASK_PLAN には書かない  
・各タスクは必ず完了条件・確認方法・停止条件を持つ  
・停止条件に触れた場合は自走せず停止して報告する

---

## 7. タスク終了時のルール

・タスク完了時は `Status: DONE` に更新する  
・次に実行すべきタスクが既に定義されている場合のみ、そのタスクを `NEXT` にする  
・ `TASK_PLAN.md` に存在しない新規タスクの作成は禁止  
・ `NEXT` タスクが存在しない場合は停止する  
・タスク完了時は「全タスク完了」または「次タスク待ち」と明示して終了する  
・次タスクは必ず人間の指示を待つ

---

## 8. 現在の到達点

本プロジェクトは以下の状態にある。

・複数RSS取得可能  
・正規化 / 判定 / Markdown生成可能  
・CLI実行可能  
・ローカルGUI実行可能  
・exploration 保存可能  
・monitoring 保存可能  
・0件時も動作継続可能  
・責務分離構造を維持したまま拡張可能  
・summary 空記事への補助要約経路を追加済み  
・keyword_weights を使った score 調整可能  
・設定で切替可能な重複排除を追加済み  
・設定で切替可能なログ機構を追加済み  
・GUIで進行状態と結果確認が可能  
・Windows タスク スケジューラ向けの自動実行入口を追加済み  
・記事ごとの topic_id 付与が可能  
・topic 単位の要約データを内部生成可能  
・Exploration Markdown 先頭で topic summaries を確認可能  
・Exploration Markdown 先頭で daily report を確認可能  



