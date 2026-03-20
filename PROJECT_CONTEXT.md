# PROJECT_CONTEXT.md

## 1. プロジェクト概要

本プロジェクトは、公開されている複数のRSSフィードから記事情報を取得し、
キーワードベースで判定を行い、結果をMarkdown形式で出力・保存する
ローカルCLI / ローカルGUIアプリケーションである。

処理はローカルで実行され、現在は外部APIやデータベースを使用しない。
Web化は未実装である。

---

## 2. 現在の機能範囲

現在の実装には以下が含まれる。

・複数RSSフィードからの記事取得  
・記事データの正規化（summaryのHTML除去を含む）  
・summary 空記事に対する補助要約生成（configで有効/無効切替可能）  
・キーワードベースの一致判定  
・keyword_weights を考慮した score 算出  
・設定で有効/無効を切り替えられる重複排除  
・Markdown文字列生成  
・CLI標準出力  
・Markdownファイル保存  
・Exploration / Monitoring 分離出力  
・config に従ったログ出力  
・pipeline を再利用するローカルGUI入口  
・GUI上での進行状態表示と出力ファイルオープン導線  

---

## 3. 入力仕様

入力は設定ファイル（JSON）によって与えられる。

主な項目は以下である。

・RSSソース一覧  
・キーワード一覧  
・キーワード重み設定（任意）  
・重複排除の有効/無効と mode  
・要約生成有効/無効  
・出力先設定  
・ログ設定  

CLI / GUI からは設定ファイルパスを指定可能であり、
未指定の場合は既定値 `config/config.json` を使用する。

---

## 4. 出力仕様

出力はMarkdown形式であり、以下の2系統を持つ。

### Exploration
・全記事を対象  
・CLI標準出力の対象  
・保存先: `output/exploration/collected_articles.md`

### Monitoring
・`matched == True` の記事のみを対象  
・保存先: `output/monitoring/monitored_articles.md`

### Logging
・コンソール出力  
・設定に応じたファイル出力  
・保存先: `logs/smart_catch.log`

### GUI
・実行中 / 成功 / 失敗表示  
・Exploration 保存先表示  
・Monitoring 保存先表示  
・時刻付きの追記型結果表示  
・出力ファイルオープン導線  

---

## 5. 処理フロー

現在の処理は以下のパイプラインで構成される。

1. 設定ファイル読込
2. ログ初期化
3. 複数RSS取得
4. 正規化
5. 必要に応じて空summary記事へ補助要約生成
6. キーワード判定と score 算出
7. 必要に応じて重複排除
8. Exploration / Monitoring 分離
9. Markdown生成
10. ファイル保存
11. CLI出力またはGUI結果表示
12. 処理ログ記録

すべての処理は同期的に実行される。

---

## 6. 設計方針

本プロジェクトは責務分離を重視した構成を採用している。

・fetcher：データ取得のみ  
・normalizer：データ整形のみ  
・summarizer：補助要約生成のみ  
・classifier：判定処理と score 算出のみ  
・deduplicator：機械的な重複排除のみ  
・writer：出力生成のみ  
・file_writer：保存のみ  
・logging_config：ログ初期化のみ  
・pipeline：処理順制御と接続のみ  
・CLI（app.py）：CLI入口のみ  
・GUI（gui_app.py）：ローカルGUI入口のみ  

---

## 7. 変更ポリシー

変更は以下の原則に従う。

・1タスク＝1責務に限定する  
・変更範囲は最小にする  
・既存モジュールの責務を侵さない  
・出力仕様を破壊しない  
・依存追加は明示承認時のみ許可する  

---

## 8. 現在の到達状態

本プロジェクトは以下の状態にある。

・複数RSSから取得可能  
・Markdown生成まで接続済み  
・Exploration 保存可能  
・Monitoring 保存可能  
・Monitoring 0件でも動作継続可能  
・summary 空記事に対して補助要約を試行可能  
・keyword_weights による score 調整可能  
・設定で切り替え可能な重複排除を追加済み  
・設定に応じたコンソール / ファイルログ出力が可能  
・CLI に加えてローカルGUI入口を利用可能  
・GUI で進行状態と結果サマリを確認可能  

つまり、最小実用レベルの情報収集パイプラインとして完成しており、
現在は拡張フェーズにある。

---

## 9. 今後の拡張方向

今後の拡張候補は以下である。

・Web UI 化  
