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
・分離層  
・出力生成層  
・保存層  
・実行制御層  
・CLI入口層  

---

## 3. 現在のディレクトリ構成

```text
Smart-Catch/
├── app.py
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

責務は設定ファイルの読込のみである。

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

### 4.8 writers/markdown_writer.py

責務はMarkdown文字列生成のみである。
保存処理は行わない。

### 4.9 writers/file_writer.py

責務はMarkdown文字列の保存のみである。

### 4.10 pipelines/rss_pipeline.py

責務は既存モジュールの接続と実行順制御のみである。
現在の主な流れは以下である。

・設定読込  
・複数RSS取得  
・正規化  
・必要に応じた補助要約生成  
・判定 / score 算出  
・必要に応じた重複排除  
・Exploration / Monitoring 分離  
・Markdown生成  
・保存  
・処理ログ出力  
・Exploration Markdown を戻り値として返す  

## 5. データフロー

現在のパイプラインは概ね以下の流れである。

load_config → setup_logging → fetch → normalize → summarize(optional) → classify/score → deduplicate(optional) → split → markdown → save

分離後の扱いは以下とする。

・Exploration = 全記事  
・Monitoring = matched == True  の記事  

## 6. 出力仕様

### Exploration

・全記事  
・CLI標準出力対象  
・保存対象  

### Monitoring

・一致記事のみ  
・保存対象  

### Logging

・コンソール出力  
・設定に応じたファイル出力  
・ログフォーマット: 時刻 / レベル / モジュール名 / メッセージ  

## 7. 例外処理方針

現在の例外処理は最小構成である。

・各モジュールは自分の入力不正に対して最小限の例外を送出する  
・summary_generator は記事単位の失敗を握りつぶし、元記事のまま継続する  
・deduplicator は設定無効時に何もしない  
・pipeline は必要最低限の接続確認のみ行う  
・pipeline は致命エラーをログに記録して再送出する  
・CLI は例外を捕捉して標準エラーへ出す  

回復処理、再試行、複雑なフォールバックは持たない。

## 8. 設計原則

・1モジュール1責務  
・変更範囲は最小  
・責務外処理を持ち込まない  
・writerは文字列生成のみ  
・保存処理は file_writer に限定する  
・ログ初期化は logging_config に限定する  
・pipelineは接続と順序制御に留める  
・依存追加は明示承認時のみ許可する  

## 9. 将来拡張時の扱い

今後の拡張は既存責務を壊さず、新しい責務として追加することを前提とする。
候補は以下である。

・GUI追加  
