# DECISIONS.md

本ドキュメントは、Smart-Catch における設計判断の理由を記録する。

---

## 記録ルール

・実装時に判断が必要だった場合のみ記録する
・日付・内容・理由・却下した選択肢を必ず書く
・過去の判断を変更する場合は上書きせず新規追記する

---

## 記録フォーマット

### YYYY-MM-DD: 判断タイトル
- 判断内容：
- 理由：
- 却下した選択肢：
- 影響範囲：

---

## 判断履歴

### 2026-04-01: Ollama未起動時のURLErrorをキャッシュしない設計
- 判断内容：urllib.error.URLError（接続拒否）はキャッシュせず、TimeoutError等はキャッシュする
- 理由：Ollamaを起動後に再試行できるようにするため。タイムアウトは再試行しても無駄なのでキャッシュする
- 却下した選択肢：全URLErrorをキャッシュする（起動後に再試行できなくなるため却下）
- 影響範囲：src/translators/markdown_translator.py、src/summarizers/summary_generator.py

### 2026-04-01: summary生成にOllama英語1文要約を採用
- 判断内容：summaryなし記事にOllamaで英語1文要約を生成し、失敗時は日本語テンプレートにフォールバック
- 理由：RSSフィードが英語ソースのため、英語summaryの方がkeyword_classifierとの親和性が高い
- 却下した選択肢：日本語で生成する（翻訳処理で二重に翻訳されるため却下）
- 影響範囲：src/summarizers/summary_generator.py

### 2026-04-01: ZennとQiitaをRSSソースに追加
- 判断内容：国内日本語技術情報源としてZenn・Qiitaを追加（max_items: 10）
- 理由：Hugging Face / OpenAIは英語のみ。日本語AI記事のカバレッジ向上のため
- 却下した選択肢：なし
- 影響範囲：config/config.json

---

## 今後の判断記録はここに追記する
