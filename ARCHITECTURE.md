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
│   ├── classifiers/
│   │   └── keyword_classifier.py
│   ├── writers/
│   │   ├── markdown_writer.py
│   │   └── file_writer.py
│   └── pipelines/
│       └── rss_pipeline.py
├── TASK_PLAN.md
├── ARCHITECTURE.md
└── PROJECT_CONTEXT.md
```

## 4. モジュール責務

### 4.1 config_loader.py

責務は以下の2点に限定する。

・設定ファイル（JSON）の読込  
・実行前に必要な最小限の設定妥当性確認  

---

#### 詳細

config_loader.py は、アプリケーションの実行前段階において
設定を安全に読み込むための入口モジュールである。

このモジュールが扱う処理は、以下に限定する。

・JSONファイルの読込  
・ルート構造の確認（dictであること）  
・必須キーの存在確認  
・主要設定値の型チェック  

---

#### 制約（重要）

以下の処理は責務に含めない。

・値の妥当性チェック（範囲、フォーマットなど）  
・URLの到達確認  
・外部通信を伴う検証  
・設定値の補完（デフォルト値の注入）  
・設定の変換や正規化  
・他モジュールとの結合ロジック  

---

#### 設計意図

本モジュールのバリデーションは、
「実行前に確実に検出できる構造的な不正の排除」に限定する。

これにより、

・実行時エラーの削減  
・CLI / GUI の既存エラー処理の活用  
・pipeline 層への責務流入防止  

を実現する。

---

#### 将来拡張

バリデーション処理が以下のように拡張された場合は、
責務分離を行い専用モジュールへ分割する。

・詳細な値検証が増加した場合  
・設定補完処理が必要になった場合  
・設定変換やマージ処理が追加された場合  

分離先例:
・config_validator.py  
・config_transformer.py  

その際、config_loader.py は再び「読込責務」に限定する。

### 4.2 logging_config.py

責務は logging 設定に従ったログ初期化のみである。
現在は以下を扱う。

・コンソールハンドラ設定  
・必要に応じたファイルハンドラ設定  
・ログレベル設定  
・最小フォーマット設定  

### 4.3 fetchers/rss_fetcher.py

責務はRSSの取得と浅い記事情報抽出のみである。

### 4.4 summarizers/summary_generator.py

責務は summary が空の記事に対する補助要約生成のみである。
既存 summary は変更しない。
失敗時は元記事をそのまま返す。

### 4.5 normalizers/rss_normalizer.py

責務は取得済み記事データの正規化のみである。
現在は以下を含む。

・キー名の統一  
・欠損値の吸収  
・summary のHTMLタグ除去  
・HTMLエンティティ復元  

### 4.6 classifiers/keyword_classifier.py

責務はキーワード一致判定と score 算出のみである。
現在は以下を付与する。

・matched  
・matched_keywords  
・score  

score は以下の最小ルールで算出する。

・title 一致: keyword_weight × 2  
・summary 一致: keyword_weight × 1  
・同一 keyword が title / summary の両方に一致した場合は両方加点  
・weight 未設定 keyword は 1  

### 4.7 deduplicators/article_deduplicator.py

責務は機械的に判定できる記事重複の除去のみである。
現在は以下を扱う。

・URL 完全一致  
・正規化タイトル一致  
・残存優先順位: score → summary 長 → 先着  

### 4.8 topic_extractors/topic_extractor.py

責務は記事への `topic_id` 付与のみである。
現在は以下を扱う。

・`matched_keywords` の共通性によるトピック判定  
・`title` / `summary` の語共通による補助判定  
・`topic_001` 形式の topic_id 採番  

### 4.9 topic_summarizers/topic_summarizer.py

責務は `topic_id` ごとの要約データ生成のみである。
現在は以下を扱う。

・topic ごとの article_count 集計  
・matched_keywords 優先の top_keywords 抽出  
・最小限の stopwords 除外  
・短い topic summary 生成  

### 4.10 report_generators/daily_report_generator.py

責務は日次レポート内部データの生成のみである。
現在は以下を扱う。

・topic_count 集計  
・主要 topic の抽出  
・注目記事の抽出  
・定型文ベースの report summary 生成  

### 4.11 writers/markdown_writer.py

責務はMarkdown文字列生成のみである。
保存処理は行わない。
Exploration では Daily Report 節と Topic Summaries 節を先頭に追加できる。

### 4.12 writers/file_writer.py

責務はMarkdown文字列の保存のみである。

### 4.13 pipelines/rss_pipeline.py

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
・Exploration / Monitoring 分離  
・Markdown生成  
・保存  
・処理ログ出力  
・Exploration Markdown を戻り値として返す  

### 4.14 gui_app.py

責務はローカルGUI入口のみである。
現在は以下を扱う。

・config パス入力  
・既存 pipeline 呼び出し  
・Run ボタンの多重実行防止  
・実行中 / 成功 / 失敗表示  
・時刻付きの追記型結果表示  
・Exploration / Monitoring 保存先表示  
・保存済み出力ファイルを開く導線  

## 5. データフロー

現在のパイプラインは概ね以下の流れである。

load_config → setup_logging → fetch → normalize → summarize(optional) → classify/score → deduplicate(optional) → assign_topics → summarize_topics → build_daily_report → split → markdown → save

入口は以下の2系統である。

・CLI: `app.py` → `run_rss_pipeline()`  
・GUI: `gui_app.py` → `run_rss_pipeline()`  

分離後の扱いは以下とする。

・Exploration = 全記事  
・Monitoring = matched == True の記事  

## 6. 出力仕様

### Exploration

・全記事  
・CLI標準出力対象  
・保存対象  
・先頭に Daily Report 節を追加可能  
・その後に Topic Summaries 節を追加可能  

### Monitoring

・一致記事のみ  
・保存対象  

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
・deduplicator は設定無効時に何もしない  
・pipeline は必要最低限の接続確認のみ行う  
・pipeline は致命エラーをログに記録して再送出する  
・CLI は例外を捕捉して標準エラーへ出す  
・GUI は例外を捕捉して画面へ表示する  

回復処理、再試行、複雑なフォールバックは持たない。

## 8. 設計原則

・1モジュール1責務  
・変更範囲は最小  
・責務外処理を持ち込まない  
・writerは文字列生成のみ  
・保存処理は file_writer に限定する  
・ログ初期化は logging_config に限定する  
・pipelineは接続と順序制御に留める  
・GUI は pipeline 再利用のみで処理本体を持たない  
・依存追加は明示承認時のみ許可する  

## 9. 将来拡張時の扱い

今後の拡張は既存責務を壊さず、新しい責務として追加することを前提とする。
候補は以下である。

・Web UI 追加  



