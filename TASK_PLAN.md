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

## 4. 次タスク（NEXT）

### T16 GUI / Web化
Status: NEXT

目的  
・CLI以外の操作手段を提供する

想定内容  
・ローカルGUI  
・将来的なWeb UI

---

## 5. 保留タスク（BACKLOG）

なし

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
・exploration 保存可能  
・monitoring 保存可能  
・0件時も動作継続可能  
・責務分離構造を維持したまま拡張可能  
・summary 空記事への補助要約経路を追加済み  
・keyword_weights を使った score 調整可能  
・設定で切替可能な重複排除を追加済み  
・設定で切替可能なログ機構を追加済み  
