# Smart-Catch

## 1. プロジェクト概要

Smart-Catch は、公開されている RSS 情報を取得し、キーワード判定を行ったうえで Markdown 文字列を生成・保存する Python 製のローカル CLI アプリです。

現時点では MVP 段階であり、設定ファイルを入力として複数の RSS 情報源を順番に処理し、結果を標準出力へ表示しつつ Markdown ファイルとして保存する最小構成まで実装されています。

## 2. 現在できること

- JSON 設定ファイルを読み込む
- `sources.rss` に定義した複数 RSS を順番に取得する
- RSS 記事を内部で扱いやすい最小構造へ正規化する
- RSS `summary` に含まれる HTML タグを除去する
- `monitoring.keywords` を使って記事本文要約とタイトルに対するキーワード部分一致判定を行う
- `monitoring.keyword_weights` に応じて整数 `score` を調整する
- `deduplication.enabled` に応じて記事重複を除去する
- `logging` 設定に応じてコンソール / ファイルへログ出力する
- 判定結果を Markdown 文字列へ変換する
- Markdown を `output/exploration/collected_articles.md` と `output/monitoring/monitored_articles.md` に UTF-8 で保存する
- CLI から実行し、結果を標準出力へ表示する

## 3. 現在まだできないこと

- GUI / Web アプリとしての実行
- 高度な意味類似ベースの重複判定
- 高度な分類、ランキング、重み調整
- 自動テストの整備
- 高度なログローテーションや外部監視連携

## 4. システム構成

各モジュールの責務は以下のとおりです。

- `config_loader`: 設定読み込みのみ
- `logging_config`: ログ初期化のみ
- `fetcher`: 取得のみ
- `normalizer`: 構造統一のみ
- `summarizer`: 空 summary 記事への補助要約のみ
- `classifier`: 判定と score 算出のみ
- `deduplicator`: 機械的な重複排除のみ
- `writer`: Markdown 文字列生成のみ
- `file_writer`: ファイル保存のみ
- `pipeline`: 接続と実行順制御のみ
- `app.py`: CLI 入口のみ

現在の処理フローは次のとおりです。

1. `config/config.json` を読む
2. `logging` 設定でログを初期化する
3. RSS 設定一覧を取得する
4. 各 RSS を順番に fetch する
5. 取得結果を 1 つにまとめる
6. fetch 結果を normalize する
7. 必要に応じて空 summary 記事へ補助要約を行う
8. `monitoring.keywords` と `monitoring.keyword_weights` を使って classify / score 算出を行う
9. 必要に応じて重複排除を行う
10. Exploration / Monitoring を分離する
11. Markdown を保存する
12. CLI から標準出力へ表示する
13. 処理状況をログへ記録する

## 5. ディレクトリ構成

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
│   │   ├── file_writer.py
│   │   └── markdown_writer.py
│   └── pipelines/
│       └── rss_pipeline.py
├── requirements.txt
├── TASK_PLAN.md
├── ARCHITECTURE.md
└── PROJECT_CONTEXT.md
```

## 6. セットアップ手順

Python 仮想環境を使う前提です。

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

依存関係をインストールします。

```bash
pip install -r requirements.txt
```

現在の `requirements.txt` には以下が含まれます。

- `feedparser==6.0.12`
- `sgmllib3k==1.0.0`

次に `config/config.json` を確認し、実在する RSS URL を設定してください。ダミー URL では動作しません。

## 7. 実行方法

既定の設定ファイルを使う場合:

```bash
python app.py
```

設定ファイルパスを明示する場合:

```bash
python app.py config/config.json
```

引数を 2 個以上渡した場合は usage エラーで終了します。

## 8. `config.json` の役割と例

`config/config.json` は、RSS 取得対象とキーワード判定条件、出力先、ログ設定を与える設定ファイルです。現時点で実処理に使っている主な項目は以下です。

- `sources.rss`: RSS 情報源の一覧
- `name`: 情報源名
- `url`: RSS URL
- `max_items`: 取得件数上限
- `monitoring.keywords`: キーワード判定に使う文字列一覧
- `monitoring.keyword_weights`: score 重み設定
- `deduplication.enabled`: 重複排除の有効/無効
- `deduplication.mode`: `url_only` または `url_and_title`
- `output.exploration_dir`: Exploration の保存先ディレクトリ
- `output.monitoring_dir`: Monitoring の保存先ディレクトリ
- `logging.level`: ログレベル
- `logging.save_to_file`: ログファイル保存の有無
- `logging.log_dir`: ログディレクトリ

例:

```json
{
  "sources": {
    "rss": [
      {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "max_items": 10
      },
      {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "max_items": 10
      }
    ]
  },
  "monitoring": {
    "keywords": [
      "AI",
      "生成AI",
      "ChatGPT",
      "OpenAI",
      "Claude",
      "Claude Code",
      "Codex",
      "LLM"
    ],
    "keyword_weights": {
      "ChatGPT": 3,
      "OpenAI": 3,
      "Claude Code": 4,
      "Codex": 4,
      "LLM": 2
    }
  },
  "deduplication": {
    "enabled": false,
    "mode": "url_and_title"
  },
  "output": {
    "exploration_dir": "output/exploration",
    "monitoring_dir": "output/monitoring"
  },
  "logging": {
    "level": "INFO",
    "save_to_file": true,
    "log_dir": "logs"
  }
}
```

補足:

- `sources.rss` の全要素を順番に処理します
- `monitoring.keywords` はタイトルと summary に対する部分一致判定に使います
- `keyword_weights` 未設定の keyword は重み 1 です
- `deduplication.enabled=false` のときは従来どおり動きます
- `logging.save_to_file=false` のときはログファイルを保存しません

## 9. 出力例の概要

出力は Markdown 文字列として生成され、CLI 実行時には標準出力へ表示されます。あわせて Exploration / Monitoring の両方が保存されます。ログは標準エラー側に出ます。

構造は次の形式です。

```markdown
# Collected Articles

## 記事タイトル
- URL: https://example.com/article
- Source: RSS Source Name
- Published: 2026-03-19T00:00:00Z
- Matched: Yes
- Score: 5
- Matched Keywords: AI, OpenAI
### Summary
記事要約
```

ログ例:

```text
2026-03-20 07:00:00,000 INFO src.pipelines.rss_pipeline Pipeline started
2026-03-20 07:00:01,000 INFO src.pipelines.rss_pipeline RSS fetch completed: Hugging Face Blog (10 entries)
```

## 10. 現在の制約

- ローカル環境向けの CLI アプリです
- 入力は JSON 設定ファイルです
- Exploration は `output/exploration/collected_articles.md` に保存します
- Monitoring は `output/monitoring/monitored_articles.md` に保存します
- ログファイルは `logs/smart_catch.log` に保存します
- 複数 RSS を順番に処理します
- RSS `summary` の HTML タグ除去は行いますが、高度な整形は行いません
- score は最小ルールベースであり、学習的な最適化はしていません
- 重複排除は URL 完全一致と正規化タイトル一致のみです
- ログは標準ライブラリ logging の最小構成です
- 公開情報のみを前提としています

## 11. 今後の拡張候補

現時点で未実装ですが、今後の候補としては以下が考えられます。

- GUI / Web 化
- より高度な重複判定
- `summary` の空白整形や本文品質の改善
- 手動確認に加えた自動テスト整備
- 高度なログローテーションや外部監視連携

これらは README 執筆時点では実装されていません。

## 12. 注意事項

- `https://example.com/rss` のようなダミー URL では動作しません
- 実行には到達可能な実在 RSS URL が必要です
- RSS の `summary` に HTML が含まれる場合があります
- 現在は `summary` の HTML タグのみ除去し、内容の高度な整形までは行いません
- `deduplication.mode=url_and_title` では正規化タイトル一致も重複とみなします
- `logging.save_to_file=true` のときは `logs` ディレクトリ配下にログファイルを作成します
- 取得対象は公開情報に限定してください
