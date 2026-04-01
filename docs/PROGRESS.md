# PROGRESS.md

## 現在の状況
👉 現在のフェーズ：安定運用中

## 直近の作業内容
- 日付：2026-04-01
- 作業内容：翻訳修正・RSS追加・ドキュメント整備
- 結果：正常動作確認済み

## 完了済み
- 翻訳の対話モード防止（temperature=0・stopトークン追加）
- Ollama未起動時のキャッシュ問題修正
- Hugging Face記事の要約をOllama生成に改善
- ZennとQiitaのRSSフィード追加
- Ollamaスタートアップ自動起動登録
- CLAUDE.md作成・ディレクトリ構成追記
- docs/フォルダ整備（Template構成に移行）

## 次にやること
- GUIにキーワード管理タブを追加
- Qiitaノイズ対策（min_score設定）
- 翻訳混在の軽微な修正（TERM_MAP処理順）

## 既知の問題
- Ollama未起動時は要約が定型文にフォールバック
- 翻訳でTERM_MAPが部分一致上書きするため混在が残る
