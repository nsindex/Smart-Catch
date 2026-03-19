# TASK_PLAN.md（初回版 v0.1）

## 1. 目的

本ドキュメントは、情報収集アプリのMVPを安全に実装するために、実装作業を小粒度タスクへ分解し、実行順序・依存関係・完了条件を固定するための計画書である。

---

## 2. タスク分解方針

本プロジェクトでは以下のルールでタスクを定義する。

・1タスク = 1変更目的  
・1タスク = 1主要責務  
・変更対象ファイルは最小限にする  
・依存追加は禁止（提案のみ）  
・各タスクに Done Criteria と Check Method を定義する  
・Codex への依頼は 1依頼 = 1タスク とする

---

## 3. タスク一覧

### Task T01

**Task Name**  
config loader の実装

**Purpose**  
`config/config.json` を読み込み、内部で利用可能な設定辞書を返す処理を追加する。

**Target Files**

- `src/config_loader.py`
    

**Do Not Touch**

- `app.py`
    
- `src/fetchers/`
    
- `src/normalizer.py`
    
- `src/classifier.py`
    
- `src/markdown_writer.py`
    
- `src/output_handler.py`
    

**Done Criteria**

- `config.json` を読み込める
    
- ファイル不存在時に安全な例外または明確なエラーになる
    
- JSON形式不正時に安全に停止できる
    

**Check Method**

- 正常な `config.json` で読込確認
    
- 不存在ファイルで異常系確認
    
- 不正JSONで異常系確認
    

**Priority**  
High

**Depends On**  
なし

**Risk**  
Low

**Requires Human Review**  
Yes

**Status**  
Todo

---

### Task T02

**Task Name**  
最小 fetcher の実装

**Purpose**  
公開情報源1種から最小限の情報を取得する処理を追加する。初回版では1種類に限定する。

**Target Files**

- `src/fetchers/<source_fetcher>.py`
    

**Do Not Touch**

- `src/config_loader.py`
    
- `src/normalizer.py`
    
- `src/classifier.py`
    
- `src/markdown_writer.py`
    
- `src/output_handler.py`
    
- `app.py`
    

**Done Criteria**

- 指定情報源からデータを取得できる
    
- 取得失敗時に安全に失敗する
    
- 生データを返せる
    

**Check Method**

- 正常取得確認
    
- 接続失敗または取得失敗の異常系確認
    

**Priority**  
High

**Depends On**  
T01

**Risk**  
Medium

**Requires Human Review**  
Yes

**Status**  
Todo

---

### Task T03

**Task Name**  
normalizer の実装

**Purpose**  
fetcher が返した生データを共通内部形式へ変換する。

**Target Files**

- `src/normalizer.py`
    

**Do Not Touch**

- `src/config_loader.py`
    
- `src/fetchers/`
    
- `src/classifier.py`
    
- `src/markdown_writer.py`
    
- `src/output_handler.py`
    
- `app.py`
    

**Done Criteria**

- 共通形式の最低項目（source, title, url, published_at など）へ整形できる
    
- 欠損値がある場合の扱いが定義される
    
- 副作用を持たない
    

**Check Method**

- 正常データ入力で整形確認
    
- 欠損データ入力で異常系または補正確認
    

**Priority**  
High

**Depends On**  
T02

**Risk**  
Low

**Requires Human Review**  
Yes

**Status**  
Todo

---

### Task T04

**Task Name**  
classifier の実装

**Purpose**  
正規化データを監視型結果と探索型結果に分類する。

**Target Files**

- `src/classifier.py`
    

**Do Not Touch**

- `src/config_loader.py`
    
- `src/fetchers/`
    
- `src/normalizer.py`
    
- `src/markdown_writer.py`
    
- `src/output_handler.py`
    
- `app.py`
    

**Done Criteria**

- 監視キーワード一致を判定できる
    
- 探索型候補として扱うデータを分離できる
    
- 副作用を持たない
    

**Check Method**

- 一致キーワードありのケース確認
    
- 一致キーワードなしのケース確認
    
- 空データ入力確認
    

**Priority**  
High

**Depends On**  
T01, T03

**Risk**  
Medium

**Requires Human Review**  
Yes

**Status**  
Todo

---

### Task T05

**Task Name**  
monitoring 用 Markdown 生成の実装

**Purpose**  
監視型結果を Markdown 文字列へ変換する処理を追加する。

**Target Files**

- `src/markdown_writer.py`
    

**Do Not Touch**

- `src/config_loader.py`
    
- `src/fetchers/`
    
- `src/normalizer.py`
    
- `src/classifier.py`
    
- `src/output_handler.py`
    
- `app.py`
    

**Done Criteria**

- 監視型結果一覧から Markdown を生成できる
    
- タイトル、URL、日時などの最低項目を含む
    
- 保存処理を持たない
    

**Check Method**

- 正常データで Markdown 生成確認
    
- 空データでの出力確認
    

**Priority**  
High

**Depends On**  
T04

**Risk**  
Low

**Requires Human Review**  
Yes

**Status**  
Todo

---

### Task T06

**Task Name**  
exploration 用 Markdown 生成の実装

**Purpose**  
探索型結果を Markdown 文字列へ変換する処理を追加する。

**Target Files**

- `src/markdown_writer.py`
    

**Do Not Touch**

- `src/config_loader.py`
    
- `src/fetchers/`
    
- `src/normalizer.py`
    
- `src/classifier.py`
    
- `src/output_handler.py`
    
- `app.py`
    

**Done Criteria**

- 探索型結果一覧から Markdown を生成できる
    
- 話題候補または関連項目が構造化されている
    
- 保存処理を持たない
    

**Check Method**

- 正常データで Markdown 生成確認
    
- 空データでの出力確認
    

**Priority**  
Medium

**Depends On**  
T04

**Risk**  
Low

**Requires Human Review**  
Yes

**Status**  
Todo

---

### Task T07

**Task Name**  
output handler の実装

**Purpose**  
生成された Markdown を指定ディレクトリへ保存する処理を追加する。

**Target Files**

- `src/output_handler.py`
    

**Do Not Touch**

- `src/config_loader.py`
    
- `src/fetchers/`
    
- `src/normalizer.py`
    
- `src/classifier.py`
    
- `src/markdown_writer.py`
    
- `app.py`
    

**Done Criteria**

- 保存先ディレクトリを扱える
    
- monitoring / exploration に分けて保存できる
    
- 保存失敗時に安全に停止できる
    

**Check Method**

- 正常保存確認
    
- 不正パスや書込失敗時の異常系確認
    

**Priority**  
High

**Depends On**  
T05, T06

**Risk**  
Medium

**Requires Human Review**  
Yes

**Status**  
Todo

---

### Task T08

**Task Name**  
logger の最小実装

**Purpose**  
実行開始、主要処理、エラー時の最小ログ出力を追加する。

**Target Files**

- `src/logger.py`
    

**Do Not Touch**

- `src/config_loader.py`
    
- `src/fetchers/`
    
- `src/normalizer.py`
    
- `src/classifier.py`
    
- `src/markdown_writer.py`
    
- `src/output_handler.py`
    
- `app.py`
    

**Done Criteria**

- INFO / ERROR の最小出力ができる
    
- 機密情報を出力しない
    
- ログファイルまたは標準出力の方針が明確である
    

**Check Method**

- 正常時ログ確認
    
- 異常時ログ確認
    
- 機密情報非出力確認
    

**Priority**  
Medium

**Depends On**  
なし

**Risk**  
Low

**Requires Human Review**  
Yes

**Status**  
Todo

---

### Task T09

**Task Name**  
app.py への最小接続

**Purpose**  
設定読込→取得→整形→分類→Markdown生成→保存の最小フローを `app.py` から実行できるようにする。

**Target Files**

- `app.py`
    

**Do Not Touch**

- 各モジュールの責務を変更しない
    
- 新規依存を追加しない
    

**Done Criteria**

- `app.py` 実行でMVPフローが一通り動く
    
- 主要例外を入口で整形して表示できる
    
- 各責務が `app.py` に混入していない
    

**Check Method**

- 正常実行確認
    
- 設定不備時の異常系確認
    
- 出力生成確認
    

**Priority**  
High

**Depends On**  
T01, T02, T03, T04, T05, T06, T07

**Risk**  
Medium

**Requires Human Review**  
Yes

**Status**  
Todo

---

## 4. 実装順序

初回版では以下の順で進める。

1. T01 config loader
    
2. T02 最小 fetcher
    
3. T03 normalizer
    
4. T04 classifier
    
5. T05 monitoring Markdown
    
6. T06 exploration Markdown
    
7. T07 output handler
    
8. T08 logger
    
9. T09 app.py 接続
    

---

## 5. AI実装ルール

- 1依頼 = 1タスク
    
- Proposal Mode → Apply Mode の2段階で進める
    
- 改善提案はその場で実装せず別タスク化する
    
- 依存追加は承認制
    
- 指定外ファイル変更は禁止
    
- 実装後は安全レビューSkillとテスト観点整理Skillを適用する
    

---

## 6. 状態管理ルール

使用する Status は以下とする。

- Todo
    
- Ready
    
- In Progress
    
- Review
    
- Done
    
- Blocked
    

初回版では全タスクを Todo で開始し、依存が満たされたものから Ready に更新する。

---

## 7. 状態

初回版（v0.1）  
MVP実装用の最小タスク計画として固定
