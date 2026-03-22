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
├── app.py
├── gui_app.py
├── config/
│   └── config.json
├── src/
│   ├── config_loader.py
│   ├── logging_config.py
│   ├── fetchers/
│   │   └── rss_fetcher.py
│   ├── normalizers/
│   │   └── rss_normalizer.py
│   ├── summarizers/
│   │   └── summary_generator.py
│   ├── deduplicators/
│   │   └── article_deduplicator.py
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
│   ├── classifiers/
│   │   └── keyword_classifier.py
│   ├── writers/
│   │   ├── markdown_writer.py
│   │   └── file_writer.py
│   └── pipelines/
│       └── rss_pipeline.py
├── TASK_PLAN.md
├── ARCHITECTURE.md
├── PROJECT_CONTEXT.md
└── README.md
```

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
既存 summary は変更しない。
失敗時は元記事をそのまま返す。

### 4.5 normalizers/rss_normalizer.py

責務は取得済み記事データの正規化のみである。

### 4.6 classifiers/keyword_classifier.py

責務はキーワード一致判定と score 算出のみである。

### 4.7 deduplicators/article_deduplicator.py

責務は機械的に判定できる記事重複の除去のみである。

### 4.8 Topic Extractor

役割は記事に `topic_id` を付与することのみである。
現在は、決定的な `topic_key` による分割型ロジックを採用している。

優先順位は以下である。

1. `matched_keywords` の代表語  
2. `source`  
3. `other`  

責務は topic の分類のみに限定される。
要約・評価・分析には関与しない。

### 4.9 topic_summarizers/topic_summarizer.py

責務は `topic_id` ごとの要約データ生成のみである。
現在は以下を扱う。

・topic ごとの article_count 集計  
・matched_keywords 優先の top_keywords 抽出  
・最小限のノイズ語除外  
・2〜3文の topic summary 生成  

### 4.10 report_generators/daily_report_generator.py

責務は日次レポート内部データの生成のみである。

### 4.11 action_generators/action_generator.py

責務は行動提案内部データの生成のみである。

### 4.12 translators/markdown_translator.py

責務は出力済みMarkdownの日本語化のみである。
現在は以下を扱う。

・英語版Markdownを入力として受け取る  
・固定ラベルの辞書変換  
・可変テキストの日本語翻訳  
・ローカルOllama優先の翻訳  
・Ollama失敗時の辞書翻訳 / 原文フォールバック  
・Markdown構造、URL、topic_id、数値の維持  

### 4.13 writers/markdown_writer.py

責務はMarkdown文字列生成のみである。
保存処理は行わない。
Exploration では Daily Report 節、Action Suggestions 節、Topic Summaries 節を先頭に追加できる。

### 4.14 writers/file_writer.py

責務はMarkdown文字列の保存のみである。
英語版 / 日本語版ともに同じ保存規則を扱う。

### 4.15 pipelines/rss_pipeline.py

責務は既存モジュールの接続と実行順制御のみである。
現在の主な流れは以下である。

・設定読込  
・複数RSS取得  
・正規化  
・必要に応じた補助要約生成  
・判定 / score 算出  
・必要に応じた重複排除  
・topic_id 付与  
・topic summary 生成  
・日次レポート生成  
・行動提案生成  
・Exploration / Monitoring 分離  
・Markdown生成  
・英語版保存  
・日本語翻訳  
・日本語版保存  
・必要に応じた履歴保存  
・処理ログ出力  
・Exploration Markdown を戻り値として返す  

### 4.16 gui_app.py

責務はローカルGUI入口のみである。

## 5. データフロー

現在のパイプラインは概ね以下の流れである。

load_config → setup_logging → fetch → normalize → summarize(optional) → classify/score → deduplicate(optional) → assign_topics → summarize_topics → build_daily_report → build_action_suggestions → split → markdown → save(english) → translate(japanese) → save(japanese) → save(history) → output

入口は以下の2系統である。

・CLI: `app.py` → `run_rss_pipeline()`  
・GUI: `gui_app.py` → `run_rss_pipeline()`  

## 6. 出力仕様

### Exploration

・全記事  
・CLI標準出力対象  
・保存対象  
・先頭に Daily Report 節を追加可能  
・その後に Action Suggestions 節を追加可能  
・その後に Topic Summaries 節を追加可能  
・保存ファイル  
  - `collected_articles.md`  
  - `collected_articles_ja.md`  
  - `collected_articles_YYYY-MM-DD.md`  
  - `collected_articles_ja_YYYY-MM-DD.md`  

### Monitoring

・一致記事のみ  
・保存対象  
・保存ファイル  
  - `monitored_articles.md`  
  - `monitored_articles_ja.md`  
  - `monitored_articles_YYYY-MM-DD.md`  
  - `monitored_articles_ja_YYYY-MM-DD.md`  

### Logging

・コンソール出力  
・設定に応じたファイル出力  
・ログフォーマット: 時刻 / レベル / モジュール名 / メッセージ  

### GUI

・実行中 / 成功 / 失敗表示  
・時刻付きの追記型結果表示  
・保存先表示  
・出力ファイルオープン導線  

## 7. 例外処理方針

現在の例外処理は最小構成である。

・各モジュールは自分の入力不正に対して最小限の例外を送出する  
・summary_generator は記事単位の失敗を握りつぶし、元記事のまま継続する  
・translator はOllama失敗時に辞書翻訳または原文で継続する  
・pipeline は致命エラーをログに記録して再送出する  
・CLI は例外を捕捉して標準エラーへ出す  
・GUI は例外を捕捉して画面へ表示する  

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

## 9. 将来拡張時の扱い

今後の拡張は既存責務を壊さず、新しい責務として追加することを前提とする。
候補は以下である。

・Web UI 追加  
・通知連携  
・週次レポート生成  
