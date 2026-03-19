# Smart-Catch

## 1. プロジェクト概要

Smart-Catch は、公開されている RSS 情報を取得し、キーワード判定を行ったうえで Markdown 文字列として出力する Python 製のローカル CLI アプリです。

現時点では MVP 段階であり、設定ファイルを入力として 1 件の RSS 情報源を処理し、結果を標準出力へ表示する最小構成まで実装されています。

## 2. 現在できること

- JSON 設定ファイルを読み込む
- `sources.rss` の先頭 1 件を使って RSS を取得する
- RSS 記事を内部で扱いやすい最小構造へ正規化する
- `monitoring.keywords` を使って記事本文要約とタイトルに対するキーワード部分一致判定を行う
- 判定結果を Markdown 文字列へ変換する
- CLI から実行し、結果を標準出力へ表示する

## 3. 現在まだできないこと

- 複数 RSS 情報源の順次処理
- 取得結果のファイル保存
- Markdown の保存先制御
- RSS `summary` に含まれる HTML の除去
- GUI / Web アプリとしての実行
- 高度な分類、スコアリング、ランキング
- 自動テストの整備

## 4. システム構成

各モジュールの責務は以下のとおりです。

- `config_loader`: 設定読み込みのみ
- `fetcher`: 取得のみ
- `normalizer`: 構造統一のみ
- `classifier`: 判定のみ
- `writer`: Markdown 文字列生成のみ
- `pipeline`: 接続と実行順制御のみ
- `app.py`: CLI 入口のみ

現在の処理フローは次のとおりです。

1. `config/config.json` を読む
2. RSS 設定を取得する
3. RSS を fetch する
4. fetch 結果を normalize する
5. `monitoring.keywords` を使って classify する
6. classify 結果を Markdown に変換する
7. CLI から標準出力へ表示する

## 5. ディレクトリ構成

```text
Smart-Catch/
├── app.py
├── config/
│   └── config.json
├── src/
│   ├── config_loader.py
│   ├── fetchers/
│   │   └── rss_fetcher.py
│   ├── normalizers/
│   │   └── rss_normalizer.py
│   ├── classifiers/
│   │   └── keyword_classifier.py
│   ├── writers/
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

`config/config.json` は、RSS 取得対象とキーワード判定条件を与える設定ファイルです。現時点で実処理に使っている主な項目は以下です。

- `sources.rss`: RSS 情報源の一覧
- `name`: 情報源名
- `url`: RSS URL
- `max_items`: 取得件数上限
- `monitoring.keywords`: キーワード判定に使う文字列一覧

例:

```json
{
  "sources": {
    "rss": [
      {
        "name": "Googleニュース（日本）",
        "url": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja",
        "max_items": 20
      }
    ]
  },
  "monitoring": {
    "keywords": [
      "AI",
      "Claude Code",
      "OpenAI",
      "LLM",
      "自動化"
    ]
  }
}
```

補足:

- 初回版では `sources.rss` の先頭 1 件のみ処理します
- `monitoring.keywords` はタイトルと summary に対する部分一致判定に使います

## 9. 出力例の概要

出力はファイルではなく Markdown 文字列です。CLI 実行時には標準出力へ表示されます。

構造は次の形式です。

```markdown
# Collected Articles

## 記事タイトル
- URL: https://example.com/article
- Source: RSS Source Name
- Published: 2026-03-19T00:00:00Z
- Matched: Yes
- Matched Keywords: AI, OpenAI
### Summary
記事要約
```

各記事には以下の情報が含まれます。

- 記事タイトル
- URL
- 情報源名
- 公開日時
- キーワード一致有無
- 一致したキーワード
- summary

## 10. 現在の制約

- ローカル環境向けの CLI アプリです
- 入力は JSON 設定ファイルです
- 出力は Markdown 文字列であり、保存処理は未実装です
- 初回版は RSS 先頭 1 件のみ処理します
- 複数 RSS の処理は未実装です
- RSS `summary` に HTML が含まれていても除去しません
- 公開情報のみを前提としています

## 11. 今後の拡張候補

現時点で未実装ですが、今後の候補としては以下が考えられます。

- 複数 RSS 情報源の処理
- Markdown のファイル保存
- monitoring / exploration の出力分離
- summary の HTML 整形
- 手動確認に加えた自動テスト整備

これらは README 執筆時点では実装されていません。

## 12. 注意事項

- `https://example.com/rss` のようなダミー URL では動作しません
- 実行には到達可能な実在 RSS URL が必要です
- RSS の `summary` に HTML が含まれる場合があります
- 現時点ではファイル保存を行いません
- 現時点では単一 RSS のみを処理します
- 取得対象は公開情報に限定してください
