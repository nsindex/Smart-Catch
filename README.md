# Smart-Catch

Smart-Catch は、複数のRSSフィードから記事を収集し、キーワード判定・トピック整理・日次レポート生成まで行うローカル実行型の情報整理ツールです。

英語版Markdownを標準出力・保存しつつ、日本語で読みやすい翻訳版Markdownも別ファイルとして保存できます。
翻訳はローカルOllamaを優先し、Ollamaが使えない場合でもフォールバックで処理を継続します。

---

## 1. 現在できること

・複数RSSフィードの記事取得  
・記事データの正規化  
・キーワードベースの一致判定とスコアリング  
・ソース別の日付フィルタ（max_age_days）  
・ソース別の最低スコアフィルタ（min_score）  
・セッションをまたいだ重複排除（seen_articles.db）  
・セッション内重複排除（URL＋タイトル）  
・topic_id 付与と topic summaries 生成  
・Daily Report / Action Suggestions 生成  
・Exploration / Monitoring の分離保存  
・英語版Markdown保存  
・日本語版Markdown保存（Monitoring: Ollama翻訳 / Exploration: 軽量翻訳）  
・Ollamaによる日本語要約生成  
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

Windowsタスクスケジューラ（GUIを起動）:

```bat
run_smart_catch.bat
```

---

## 3. 出力ファイル

Exploration（全記事）:

- `output/exploration/collected_articles.md`
- `output/exploration/collected_articles_ja.md`

Monitoring（キーワード一致記事）:

- `output/monitoring/archive/monitored_articles.md`
- `output/monitoring/archive/monitored_articles_ja.md`

履歴保存が有効な場合（`output.save_history: true`）:

| ファイル | 保存先 |
|---------|--------|
| `collected_articles_YYYY-MM-DD.md` | `output/exploration/` |
| `collected_articles_ja_YYYY-MM-DD.md` | `output/exploration/` |
| `monitored_articles_YYYY-MM-DD.md` | `output/monitoring/archive/` |
| `monitored_articles_ja_YYYY-MM-DD.md` | `output/monitoring/` |

日付付き日本語版（`monitored_articles_ja_YYYY-MM-DD.md`）のみ `output/monitoring/` 直下に保存されます。他のモニタリングファイルは `archive/` サブフォルダに格納されます。

英語版は原本として維持され、日本語版は閲覧用の別ファイルとして追加保存されます。

---

## 4. Exploration Markdown の内容

Exploration では以下を確認できます。

- `# Daily Report`
- `# Action Suggestions`
- `## Topic Summaries`
- `# Collected Articles`
- 各 article ブロックのメタ情報（`topic_id`, URL, Source, Published, Matched, Score, Matched Keywords, Summary）

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

## 6. GUIの機能

### メインタブ

- 設定ファイルの選択と実行
- パイプライン実行はワーカースレッドで動作するためGUIが固まりません
- 実行ログをリアルタイム表示

### Ollama自動検知・自動起動

GUI起動時に `localhost:11434` への接続を確認し、Ollamaが起動していない場合は自動起動を試みます。
実行ボタン押下時にも起動状態を確認し、未起動の場合は警告を表示します。

### キーワード管理タブ

`monitoring.keywords` の一覧表示・追加・削除・保存が GUI から行えます。
設定ファイルを選択し直した際は、キーワードリストが自動的に再読み込みされます。
保存はアトミック書き込み（tmp → rename）で行い、書き込み中断による破損を防いでいます。

---

## 7. Ollama準備手順（任意）

翻訳品質を上げたい場合は、ローカルで Ollama を起動してください。

```powershell
ollama serve
ollama pull gemma3n:e4b
```

接続先は `http://localhost:11434/api/generate` を使用します。
外部クラウドAPIは使用しません。

GUIを使用する場合、起動時に自動で検知・起動を試みるため、手動での `ollama serve` は不要な場合があります。

---

## 8. config の主な項目

- `sources.rss`: RSSソース一覧
- `sources.rss[].max_age_days`: ソースごとの記事の最大経過日数（この日数より古い記事を除外）
- `sources.rss[].min_score`: ソースごとの最低スコア閾値（任意）
- `monitoring.keywords`: 監視キーワード
- `monitoring.keyword_weights`: キーワード重み
- `summary_generation.enabled`: 補助要約生成の有効 / 無効
- `deduplication.enabled`: 重複排除の有効 / 無効
- `deduplication.mode`: 重複判定方式（`url_and_title` など）
- `output.exploration_dir`: Exploration保存先
- `output.monitoring_dir`: Monitoring保存先
- `output.save_history`: 履歴保存の有効 / 無効
- `logging.level`: ログレベル
- `logging.save_to_file`: ログファイル保存の有効 / 無効

---

## 9. 自動実行（Windowsタスクスケジューラ）

Windows タスク スケジューラから定期実行する場合は `run_smart_catch.bat` を使います。
このバッチはプロジェクトルートへ移動し、仮想環境を有効化した上で GUI（`gui_app.py`）を起動します。

手動実行:

```bat
run_smart_catch.bat
```

タスクスケジューラ設定手順:

1. タスク スケジューラで新しいタスクを作成する
2. トリガーで毎朝など任意の実行時刻を設定する
3. 操作で「プログラムの開始」を選ぶ
4. プログラム/スクリプトに `run_smart_catch.bat` の絶対パスを指定する
5. 「開始 (オプション)」の設定は不要（バッチ内でディレクトリ移動します）

ログ確認:

- `logs/smart_catch.log`
- `logging.save_to_file=true` のときにファイル保存されます

---

## 10. 現在の制約

- 翻訳・要約はローカルOllamaの状態に依存します
- Ollama未起動時はフォールバック翻訳になるため、日本語の自然さは低下する場合があります
- seen_articles.db（実行間重複排除用SQLite）は `output/seen_articles.db`（`output.base_dir` 配下）に自動生成されます。キーワードを大幅変更した場合は削除してリセットしてください
- Web UI は未実装です
- 通知連携・記事蓄積DBは未実装です（seen_articles.db は重複排除専用で記事全文は保存しません）
