# ARCHITECTURE.md

## 1. 目的

本ドキュメントは、Smart-Catch の現在の実装構造と責務分離を明確化することを目的とする。
ここで扱うのは将来理想形ではなく、現時点で実装済みの構造である。

---

## 2. 全体構成

現在のシステムは、以下の責務単位モジュールで構成される。

・設定読込層
・ログ初期化層
・取得層
・補助要約生成層
・正規化層
・判定・スコア算出層
・重複排除層
・トピック抽出層
・トピック要約層
・日次レポート生成層
・行動提案生成層
・翻訳層
・分離層
・出力生成層
・保存層
・実行制御層
・CLI入口層
・GUI入口層

---

## 3. 現在のディレクトリ構成

```text
Smart-Catch/
├── app.py                    # CLI エントリポイント
├── gui_app.py                # GUI エントリポイント（Tkinter）
├── run_smart_catch.bat       # Windows 実行バッチ
├── test_config.py
├── requirements.txt
├── CLAUDE.md
├── README.md
├── config/
│   └── config.json           # RSSソース・キーワード・スコア設定
├── docs/
│   ├── AGENTS.md
│   ├── ARCHITECTURE.md
│   ├── DECISIONS.md
│   ├── PROGRESS.md
│   ├── PROJECT_CONTEXT.md
│   └── TASK_PLAN.md
├── src/
│   ├── config_loader.py
│   ├── logging_config.py
│   ├── output_handler.py
│   ├── pipelines/
│   │   └── rss_pipeline.py           # メインパイプライン
│   ├── fetchers/
│   │   └── rss_fetcher.py
│   ├── normalizers/
│   │   └── rss_normalizer.py
│   ├── classifiers/
│   │   └── keyword_classifier.py
│   ├── deduplicators/
│   │   └── article_deduplicator.py
│   ├── summarizers/
│   │   └── summary_generator.py
│   ├── topic_extractors/
│   │   └── topic_extractor.py
│   ├── topic_summarizers/
│   │   └── topic_summarizer.py
│   ├── report_generators/
│   │   └── daily_report_generator.py
│   ├── action_generators/
│   │   └── action_generator.py
│   ├── translators/
│   │   └── markdown_translator.py
│   └── writers/
│       ├── markdown_writer.py
│       └── file_writer.py
├── output/
│   ├── exploration/
│   └── monitoring/
└── logs/
```

---

## 4. モジュール責務

### 4.1 config_loader.py

責務は以下の2点に限定する。

・設定ファイル（JSON）の読込
・実行前に必要な最小限の設定妥当性確認

### 4.2 logging_config.py

責務は logging 設定に従ったログ初期化のみである。

### 4.3 fetchers/rss_fetcher.py

責務はRSSの取得と浅い記事情報抽出のみである。

### 4.4 summarizers/summary_generator.py

責務は summary が空の記事に対する補助要約生成のみである。
Ollama英語1文要約を優先し、失敗時はテンプレート文字列にフォールバックする。
既存 summary は変更しない。
失敗時は元記事をそのまま返す。

### 4.5 normalizers/rss_normalizer.py

責務は取得済み記事データの正規化のみである。

### 4.6 classifiers/keyword_classifier.py

責務はキーワード一致判定と score 算出のみである。

### 4.7 deduplicators/article_deduplicator.py

責務は機械的に判定できる記事重複の除去のみである。

### 4.8 topic_extractors/topic_extractor.py

役割は記事に `topic_id` を付与することのみである。
優先順位は以下である。

1. `matched_keywords` の代表語
2. `source`
3. `other`

責務は topic の分類のみに限定される。

### 4.9 topic_summarizers/topic_summarizer.py

責務は `topic_id` ごとの要約データ生成のみである。

### 4.10 report_generators/daily_report_generator.py

責務は日次レポート内部データの生成のみである。

### 4.11 action_generators/action_generator.py

責務は行動提案内部データの生成のみである。

### 4.12 translators/markdown_translator.py

責務は出力済みMarkdownの日本語化のみである。
翻訳フォールバック順：完全一致マップ → Ollama（gemma3n:e4b） → 辞書翻訳（TERM_MAP/PHRASE_MAP）

### 4.13 writers/markdown_writer.py

責務はMarkdown文字列生成のみである。保存処理は行わない。

### 4.14 writers/file_writer.py

責務はMarkdown文字列の保存のみである。

### 4.15 pipelines/rss_pipeline.py

責務は既存モジュールの接続と実行順制御のみである。

### 4.16 gui_app.py

責務はローカルGUI入口のみである。

---

## 5. データフロー

load_config → setup_logging → fetch → normalize → summarize(optional) → classify/score → deduplicate(optional) → assign_topics → summarize_topics → build_daily_report → build_action_suggestions → split → markdown → save(english) → translate(japanese) → save(japanese) → save(history) → output

入口は以下の2系統である。

・CLI: `app.py` → `run_rss_pipeline()`
・GUI: `gui_app.py` → `run_rss_pipeline()`

---

## 6. 出力仕様

### Exploration

・全記事
・CLI標準出力対象
・保存ファイル
  - `output/exploration/collected_articles.md`
  - `output/exploration/collected_articles_ja.md`
  - `output/exploration/collected_articles_YYYY-MM-DD.md`
  - `output/exploration/collected_articles_ja_YYYY-MM-DD.md`

### Monitoring

・一致記事（matched == True）のみ
・保存ファイル
  - `output/monitoring/monitored_articles.md`
  - `output/monitoring/monitored_articles_ja.md`
  - `output/monitoring/monitored_articles_YYYY-MM-DD.md`
  - `output/monitoring/monitored_articles_ja_YYYY-MM-DD.md`

---

## 7. 例外処理方針

・各モジュールは自分の入力不正に対して最小限の例外を送出する
・summary_generator は記事単位の失敗を握りつぶし、元記事のまま継続する
・translator はOllama失敗時に辞書翻訳または原文で継続する
・pipeline は致命エラーをログに記録して再送出する
・CLI は例外を捕捉して標準エラーへ出す
・GUI は例外を捕捉して画面へ表示する

---

## 8. 設計原則

・1モジュール1責務
・変更範囲は最小
・責務外処理を持ち込まない
・writerは文字列生成のみ
・translatorは翻訳のみ
・保存処理は file_writer に限定する
・ログ初期化は logging_config に限定する
・pipelineは接続と順序制御に留める
・GUI は pipeline 再利用のみで処理本体を持たない
・依存追加は明示承認時のみ許可する

---

## 9. 将来拡張時の扱い

今後の拡張は既存責務を壊さず、新しい責務として追加することを前提とする。

・Web UI 追加
・通知連携
・週次レポート生成
