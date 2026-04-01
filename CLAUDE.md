# Smart-Catch プロジェクト

## プロジェクト概要
- RSSフィードを収集・スコアリング・日本語化して出力するモニタリングツール
- 実行: python app.py
- 仮想環境: .venv（有効化: .\.venv\Scripts\Activate.ps1）
- 設定ファイル: config/config.json（RSSソース・キーワード・スコア設定）

## アーキテクチャ
- src/pipelines/rss_pipeline.py がメインパイプライン
- src/summarizers/summary_generator.py：summaryなし記事をOllamaで要約生成
- src/translators/markdown_translator.py：英語MD→日本語MD（Ollama使用）
- 翻訳フォールバック順：Ollama → TERM_MAP/PHRASE_MAP辞書
- Ollama: localhost:11434、モデル: gemma3n:e4b

## 開発ルール
- 変更前に必ず .bak バックアップを作成
- 変更後は diff で確認してから報告
- 破壊的・不可逆操作の前に必ず確認停止

## セッション終了前チェックリスト
- [ ] python app.py を実行して動作確認したか
- [ ] git status で未コミットファイルがないか確認したか
- [ ] .bak ファイルが .gitignore に含まれているか

## .gitignore に追加済み
- *.bak

## ディレクトリ構成

```
Smart-Catch/
├── app.py                    # CLI エントリポイント
├── gui_app.py                # GUI エントリポイント（Tkinter）
├── run_smart_catch.bat       # Windows 実行バッチ
├── test_config.py
├── requirements.txt
├── config/
│   └── config.json           # RSSソース・キーワード・スコア設定
├── src/
│   ├── config_loader.py
│   ├── logging_config.py
│   ├── output_handler.py
│   ├── pipelines/
│   │   └── rss_pipeline.py           # メインパイプライン
│   ├── fetchers/
│   │   └── rss_fetcher.py            # RSS取得
│   ├── normalizers/
│   │   └── rss_normalizer.py         # 正規化
│   ├── classifiers/
│   │   └── keyword_classifier.py     # キーワード判定・スコアリング
│   ├── deduplicators/
│   │   └── article_deduplicator.py   # 重複排除
│   ├── summarizers/
│   │   └── summary_generator.py      # Ollama要約生成
│   ├── topic_extractors/
│   │   └── topic_extractor.py        # topic_id付与
│   ├── topic_summarizers/
│   │   └── topic_summarizer.py       # トピック要約生成
│   ├── report_generators/
│   │   └── daily_report_generator.py # 日次レポート生成
│   ├── action_generators/
│   │   └── action_generator.py       # 行動提案生成
│   ├── translators/
│   │   └── markdown_translator.py    # 英語MD→日本語MD翻訳
│   └── writers/
│       ├── markdown_writer.py        # Markdown構築
│       └── file_writer.py            # ファイル保存
├── output/
│   ├── exploration/                  # 全記事（英語・日本語）
│   └── monitoring/                   # キーワード一致記事（英語・日本語）
└── logs/
```
