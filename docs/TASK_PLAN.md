# TASK_PLAN（更新版 v2.2）

## 1. 目的

本ドキュメントは、Smart-Catch の開発タスクを
**T単位（機能単位）で管理**し、CODEX が 1タスク単位で実装・確認・ドキュメント同期まで進められる状態を作ることを目的とする。

本ドキュメントにおける「タスク」とは、`Txx` 形式のIDを持つ項目のみを指す。
細かい実装手順はここでは分解しすぎず、各タスクの完了条件と停止条件を明確にする。

---

## 2. 現在の開発フェーズ

・MVP完成済み
・複数RSS対応済み
・Markdown保存対応済み
・Monitoring / Exploration 分離完了
・補助要約生成追加済み
・スコアリング改善済み
・重複排除追加済み
・ログ機構追加済み
・ローカルGUI改善済み
・自動実行対応済み
・トピック抽出 / 要約基盤追加済み
・日次レポート生成追加済み
・行動提案追加済み
・トピック精度改善完了済み
・日本語翻訳版Markdown出力追加済み
・ローカルLLM翻訳レイヤー追加済み
・Ollama要約生成追加済み
・Zenn / Qiita RSSソース追加済み
・現在は安定運用フェーズにある

---

## 3. 完了済みタスク（DONE）

### T01 設定読込
Status: DONE

### T02 RSS取得
Status: DONE

### T03 正規化
Status: DONE

### T04 キーワード判定
Status: DONE

### T05 Markdown生成
Status: DONE

### T06 パイプライン接続
Status: DONE

### T07 CLI実装
Status: DONE

### T08 E2E動作確認
Status: DONE

### T09 Markdown保存機能
Status: DONE

### T10 複数RSS対応
Status: DONE

### T11 Monitoring / Exploration 分離
Status: DONE

### T12 LLM Summary生成
Status: DONE

### T13 スコアリング改善
Status: DONE

### T14 重複排除
Status: DONE

### T15 ログ機構
Status: DONE

### T16 GUI / Web化（T16-A / T16-B ローカルGUI）
Status: DONE

### T17 自動実行（Windowsタスクスケジューラ対応）
Status: DONE

### T18 設定バリデーション
Status: DONE

### T19 トピック抽出（topic_id付与）
Status: DONE

### T20 トピック要約（内部データ生成）
Status: DONE

### T21 トピック表示（Markdown反映）
Status: DONE

### T22 日次レポート生成
Status: DONE

### T23 行動提案
Status: DONE

### T24 自動化運用強化（履歴保存）
Status: DONE

### T25 精度改善（ノイズ除去）
Status: DONE

### T26 強語除外
Status: DONE

### T27 条件強化
Status: DONE

### T28 keyword一致強化
Status: DONE

### T29 トピック分割方式への変更（結合型 → 分割型）
Status: DONE

### T30 Summary分析型への改善
Status: DONE

### T31 ノイズ語除去の改善
Status: DONE

### T32 Summary精度改善（日時・形式ノイズ除去）
Status: DONE

### T33 日本語翻訳版Markdown出力
Status: DONE

### T34 ローカルLLM翻訳レイヤー
Status: DONE

### T35 Markdown article 出力への topic_id 追加
Status: DONE

### T36 Ollamaによる要約生成・翻訳リクエスト安定化
Status: DONE

目的
・summaryなし記事にOllama英語1文要約を追加
・翻訳リクエストにtemperature=0・stopトークンを追加し出力を安定化
・URLErrorキャッシュ戦略をタイムアウトと接続拒否で分離

### T37 ZennとQiitaのRSSソース追加
Status: DONE

目的
・国内日本語技術記事のカバレッジ向上

---

## 4. 次タスク（NEXT）

なし（次タスク待ち）

---

## 5. 保留タスク（BACKLOG）

なし

---

## 6. 予定タスク（TODO）

なし

---

## 7. タスク実行ルール

・1タスク = 1機能単位で扱う
・CODEX は T単位で実装・確認・必要な資料更新まで行う
・人間は T完了時のみ確認と承認を行う
・停止条件に触れた場合は自走せず停止して報告する
・NEXTが無い場合は新規実装禁止

---

## 8. 現在の到達点

・複数RSS取得可能（Hugging Face / OpenAI / Zenn / Qiita）
・正規化 / 判定 / Markdown生成可能
・CLI実行可能
・ローカルGUI実行可能
・exploration 保存可能
・monitoring 保存可能
・英語版Markdown保存可能
・日本語版Markdown保存可能
・日付付き履歴保存可能
・topic 分割型ロジックを導入済み
・Daily Report / Action Suggestions / Topic Summaries を表示可能
・ローカルOllama優先の翻訳レイヤーを導入済み
・Ollama失敗時もフォールバックで継続可能
・Ollama要約生成追加済み（失敗時はテンプレートフォールバック）
・現在は安定運用フェーズにある
