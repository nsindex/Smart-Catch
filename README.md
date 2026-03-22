# Smart-Catch

Smart-Catch は、複数のRSSフィードから記事を収集し、キーワード判定・トピック整理・日次レポート生成まで行うローカル実行型の情報整理ツールです。

英語版Markdownを標準出力・保存しつつ、日本語で読みやすい翻訳版Markdownも別ファイルとして保存できます。
翻訳はローカルOllamaを優先し、Ollamaが使えない場合でもフォールバックで処理を継続します。

---

## 1. 現在できること

・複数RSSフィードの記事取得  
・記事データの正規化  
・キーワードベースの一致判定とスコアリング  
・重複排除  
・topic_id 付与と topic summaries 生成  
・Daily Report / Action Suggestions 生成  
・Exploration / Monitoring の分離保存  
・英語版Markdown保存  
・日本語版Markdown保存  
・日付付き履歴保存  
・CLI / ローカルGUI / Windowsタスクスケジューラ実行  

---

## 2. 実行方法

CLI:

```powershell
python app.py config/config.json
```

GUI:

```powershell
python gui_app.py
```

Windowsタスクスケジューラ:

```bat
run_smart_catch.bat
run_smart_catch.bat config\config.json
```

---

## 3. 出力ファイル

Exploration:

- `output/exploration/collected_articles.md`
- `output/exploration/collected_articles_ja.md`

Monitoring:

- `output/monitoring/monitored_articles.md`
- `output/monitoring/monitored_articles_ja.md`

履歴保存が有効な場合:

- `collected_articles_YYYY-MM-DD.md`
- `collected_articles_ja_YYYY-MM-DD.md`
- `monitored_articles_YYYY-MM-DD.md`
- `monitored_articles_ja_YYYY-MM-DD.md`

英語版は原本として維持され、日本語版は閲覧用の別ファイルとして追加保存されます。

---

## 4. Exploration Markdown の内容

Exploration では以下を確認できます。

- `# Daily Report`
- `# Action Suggestions`
- `## Topic Summaries`
- `# Collected Articles`

Monitoring では一致記事のみを保存します。

---

## 5. 日本語版Markdownについて

日本語版Markdownは、英語版Markdownを保存した後に後段の翻訳レイヤーで生成します。
既存の収集・判定・保存の流れは変更せず、英語原本を保持したまま日本語閲覧版を追加します。

翻訳方式:

- ローカルOllamaを優先
- Ollama失敗時は辞書翻訳または原文でフォールバック
- URL、topic_001 形式のID、数値、Markdown構造は維持

そのため、Ollama未起動時でも英語版保存を含む処理全体は止まりません。

---

## 6. Ollama準備手順（任意）

翻訳品質を上げたい場合は、ローカルで Ollama を起動してください。

```powershell
ollama serve
ollama pull gemma3n:e4b
```

接続先は `http://localhost:11434/api/generate` を使用します。
外部クラウドAPIは使用しません。

---

## 7. config の主な項目

- `sources.rss`: RSSソース一覧
- `monitoring.keywords`: 監視キーワード
- `monitoring.keyword_weights`: キーワード重み
- `summary_generation.enabled`: 補助要約生成の有効 / 無効
- `deduplication.enabled`: 重複排除の有効 / 無効
- `deduplication.mode`: 重複判定方式
- `output.exploration_dir`: Exploration保存先
- `output.monitoring_dir`: Monitoring保存先
- `output.save_history`: 履歴保存の有効 / 無効
- `logging.level`: ログレベル
- `logging.save_to_file`: ログファイル保存の有効 / 無効

---

## 8. 自動実行（Windowsタスクスケジューラ）

Windows タスク スケジューラから定期実行する場合は `run_smart_catch.bat` を使います。
このバッチはプロジェクトルートへ移動し、`.venv\Scripts\python.exe` で既存の `app.py` をそのまま起動するため、作業ディレクトリ依存を減らしやすいです。

手動実行:

```bat
run_smart_catch.bat
run_smart_catch.bat config\config.json
```

タスクスケジューラ設定手順:

1. タスク スケジューラで新しいタスクを作成する
2. トリガーで毎朝など任意の実行時刻を設定する
3. 操作で「プログラムの開始」を選ぶ
4. プログラム/スクリプトに `run_smart_catch.bat` を指定する
5. 「開始 (オプション)」にはプロジェクトルートを指定する
6. 別の設定ファイルを使う場合は引数に `config\config.json` などを渡す

ログ確認:

- `logs/smart_catch.log`
- `logging.save_to_file=true` のときにファイル保存されます

---

## 9. 現在の制約

- 翻訳はローカルOllamaの状態に依存します
- Ollama未起動時はフォールバック翻訳になるため、日本語の自然さは低下する場合があります
- Web UI は未実装です
- 通知連携やDB保存は未実装です
