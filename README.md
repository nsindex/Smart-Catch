# TASK_PLAN（更新版 v2.1）

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

## 4. 次タスク（NEXT）

T18 設定バリデーション

---

## 5. 保留タスク（BACKLOG）

なし

---

## 6. 予定タスク（TODO）

### T18 設定バリデーション
Status: TODO

目的  
・`config/config.json` の不正を実行前に検出し、曖昧な実行時エラーではなく「設定エラー」として明確に停止させる  
・現在の課題である config バリデーション不足を解消する

方針  
・既存構造を変更しない  
・pipeline / CLI / GUI の責務は変更しない  
・`config_loader.py` に最小限のバリデーションのみ追加する  
・新規依存は追加しない  
・JSON構造 / 必須キー / 型チェックに限定する

変更対象  
・`src/config_loader.py`

変更禁止  
・`src/pipelines/rss_pipeline.py`  
・`app.py`  
・`gui_app.py`  
・新規ライブラリ追加  
・設定構造の変更

実装内容  
・config 読込後に `validate_config(config)` を実行する

以下の検証を行う。

■ 構造チェック  
・ルートが dict であること

■ 必須キー  
・`sources` が存在すること  
・`sources.rss` が存在すること  
・`monitoring` が存在すること  
・`monitoring.keywords` が存在すること

■ 型チェック  
・`sources` は dict  
・`sources.rss` は list  
・`sources.rss[i]` は dict  
・`sources.rss[i].url` は非空の str

・`monitoring` は dict  
・`monitoring.keywords` は list  
・`monitoring.keyword_weights` は存在時 dict

・`deduplication.enabled` は存在時 bool  
・`deduplication.mode` は存在時 str

・`output.exploration_dir` は存在時 str  
・`output.monitoring_dir` は存在時 str

・`logging.level` は存在時 str  
・`logging.save_to_file` は存在時 bool  
・`logging.log_dir` は存在時 str

エラー仕様  
・不正時は `ValueError` を送出する

例:  
・`sources is required`  
・`sources.rss must be a list`  
・`sources.rss[0].url must be a non-empty string`  
・`monitoring.keywords must be a list`

完了条件  
・正常な config で従来通り実行できる  
・構造不正を検出できる  
・必須キー不足を検出できる  
・型不正を検出できる  
・既存機能（pipeline / CLI / GUI）に影響がない

確認方法  
1. 正常系  
`python app.py config/config.json` が成功する

2. 異常系（必須キー欠如）  
`sources` を削除 → エラーになる

3. 異常系（型不正）  
`sources.rss` を文字列に変更 → エラーになる

4. 異常系（値不正）  
`sources.rss[0].url` を空文字 → エラーになる

5. GUI確認  
不正 config でも既存のエラー表示経路で処理される

備考  
・本タスクでは最小限のバリデーションのみ扱う  
・将来的に検証処理が増加した場合は validator モジュール分離を検討する

---

## 7. タスク実行ルール

・1タスク = 1機能単位で扱う  
・CODEX は T単位で実装・確認・必要な資料更新まで行う  
・人間は T完了時のみ確認と承認を行う  
・途中の細かい手順分割は、原則として TASK_PLAN には書かない  
・各タスクは必ず完了条件・確認方法・停止条件を持つ  
・停止条件に触れた場合は自走せず停止して報告する

---

## 8. タスク終了時のルール

・タスク完了時は `Status: DONE` に更新する  
・次に実行すべきタスクが既に定義されている場合のみ、そのタスクを `NEXT` にする  
・ `TASK_PLAN.md` に存在しない新規タスクの作成は禁止  
・ `NEXT` タスクが存在しない場合は停止する  
・タスク完了時は「全タスク完了」または「次タスク待ち」と明示して終了する  
・次タスクは必ず人間の指示を待つ

---

## 9. 現在の到達点

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

## Exploration Markdown のトピック表示

Exploration Markdown では、記事一覧の前に Topic Summaries 節が表示されます。
ここでは topic_id ごとに記事数、主要キーワード、短い要約を確認できます。

- Exploration: Topic Summaries の後に従来どおり # Collected Articles が続きます
- Monitoring: 既存どおり記事一覧のみを表示します




## Exploration Markdown の日次レポート

Exploration Markdown では、先頭に Daily Report 節が表示されます。
ここでは生成時刻、主要トピック、注目記事、全体サマリを確認できます。

- Exploration: Daily Report の後に Topic Summaries、その後に # Collected Articles が続きます
- Monitoring: 既存どおり記事一覧のみを表示します



## Exploration Markdown の行動提案

Exploration Markdown では、Daily Report の後に Action Suggestions 節が表示されます。
ここでは優先トピック、注目記事、推奨行動を確認できます。

- Exploration: Daily Report の後に Action Suggestions、その後に Topic Summaries と # Collected Articles が続きます
- Monitoring: 既存どおり記事一覧のみを表示します



## Markdown の履歴保存

`output.save_history` を `true` にすると、最新ファイルに加えて日付付き履歴ファイルも保存します。
未指定または `false` の場合は、既存運用を壊さないよう最新ファイルのみを保存します。

- Exploration: `collected_articles.md` と `collected_articles_YYYY-MM-DD.md`
- Monitoring: `monitored_articles.md` と `monitored_articles_YYYY-MM-DD.md`
- 同日再実行時は同じ履歴ファイル名を上書きします
