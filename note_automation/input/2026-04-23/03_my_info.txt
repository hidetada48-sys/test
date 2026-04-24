# 一次情報まとめ：NotebookLM × Claude Code でAI画像生成ツールを選定した話

作成日：2026-04-23

---

## この記事の核心体験

「Claude CodeからNotebookLMを操作して、ブラウザを一度も開かずに30本のリサーチソースを収集し、LMのチャット経由で回答を受け取り、メモをmdファイルとして受け取る」というワークフローを初めて実践した。

---

## 時系列

### ① 背景：画像生成ツールが決まっていなかった

- note記事用の画像生成は `generate_images.py`（Gemini Nano Banana 2 = `gemini-3.1-flash-image-preview`）でやっていた
- ただしWindowsにもLinuxにも汎用化できておらず、`~/test/note_automation/` の中でしか動かない状態
- GPT Image 2（OpenAI）という新しいモデルが登場したという情報を入手
- どちらを本命にすべきか判断できていなかった

---

### ② notebooklm-py のセットアップ（2026-04-22〜23）

**きっかけ：** 大きな資料をClaudeのコンテキストに直接入れるとトークンを大量消費する問題を解決したかった。

**インストール：**
```bash
uv tool install notebooklm-py --with playwright
# → v0.3.4 インストール完了
# セッション保存先: /home/hidetada48/.notebooklm/browser_profile
```

**使えるようになった主要コマンド：**
```bash
notebooklm list                                               # ノートブック一覧
notebooklm ask -n [ID] "質問"                                 # 質問する
notebooklm source list -n [ID]                                # ソース一覧
notebooklm source add-research -n [ID] "検索ワード" --import-all  # 検索してソース追加
notebooklm create "タイトル"                                   # ノートブック作成
notebooklm note list -n [ID]                                  # メモ一覧
notebooklm note get -n [ID] [noteID]                          # メモ全文取得
notebooklm generate report -n [ID]                            # レポート生成
```

**動作確認：** 既存ノートブック「Claude Design」（a1a5ed5f・30ソース）に質問して動作確認。

---

### ③ GPT Image 2 vs Nano Banana Pro 比較調査（2026-04-23）

画像生成ツール選定の判断材料を集めるために、NotebookLMを使ったリサーチを実施。

**ステップ1：ノートブックを作る**
```bash
notebooklm create "GPT Image 2 vs NanoBanana Pro 比較調査"
# → ノートブックID: 34a78960
```

**ステップ2：ソースをパターンを変えた検索で追加する**

検索クエリに媒体名を含めることで約9割の精度で絞り込める、というコツを発見。

| クエリパターン | 媒体 |
|---|---|
| `"GPT Image 2" note記事` | note記事 |
| `"GPT Image 2" YouTube` | YouTube |
| `"GPT Image 2"` | 一般web |

→ 3回に分けて検索、合計30ソース追加。

**ステップ3：Claude CodeからLMに質問する**

ブラウザを開かずに、ターミナル上のClaude Codeから直接NotebookLMに質問。
LMは30本のソースを元に回答を生成し、Claude Codeのターミナルに返ってくる。

**ステップ4：LMにメモを作らせ、Claude Codeがmdで受け取る**

LMのチャット内で生成した回答をLMのメモ機能に保存させる。
その後、`notebooklm note get` でClaude Codeがmdとして受け取り、ローカルファイルに保存。

```
保存先：INBOX/GPT_Image2_vs_NanoBanana_Pro_比較.md
```

---

### ④ 調査結果：GPT Image 2の情報

- モデルID: `gpt-image-2`、SDK: OpenAI Python SDK
- 最大3840px、アスペクト比 3:1〜1:3 で自由指定可能
- 料金: Low $0.006 / Medium $0.053 / High $0.21（1枚あたり）
- Batch APIで50%割引あり
- Canva・Adobe・HubSpot など商用SaaSで採用済み

**断念した理由：** OpenAIの月額利用制限があり、安定した運用ができないと判断。

---

### ⑤ 結論：Gemini Nano Banana Proに決定（2026-04-23）

- `generate_images.py` のモデルを1行変更（Nano Banana 2 → Nano Banana Pro）
- `gemini-3.1-flash-image-preview` → `gemini-3-pro-image-preview`

**選んだ理由：**
- Google APIキーが既にある
- 月額制限がない（従量課金）
- APIの呼び出し方が全く同じ（コード変更が1行で済んだ）

---

### ⑥ 汎用化まで完了（2026-04-23）

NotebookLMリサーチの結果を受けて、その日のうちにシステムを整備。

- `~/dotfiles/claude/scripts/generate_image.py` として汎用スクリプト作成
- `~/dotfiles/claude/skills/generate-image/SKILL.md` でスキル化
- どのリポジトリからでも `/generate-image` または「画像生成して」で動くように
- GOOGLE_API_KEYを`~/.bashrc`に設定済み

---

## 発見・感動したこと

1. **ブラウザを一度も開かずにNotebookLMを操作できた**
   - 普段はブラウザでLMを開き、手でソースを追加し、手でチャットしていた
   - それが全部Claude Codeのターミナルから完結した

2. **「検索クエリに媒体名を含める」だけで媒体別収集ができた**
   - note記事だけ・YouTubeだけ・一般webだけを3回に分けて収集
   - 精度約9割で絞り込める

3. **LMで作ったメモがそのままClaude Codeのmdファイルになる**
   - LMのチャット内で生成した情報を `notebooklm note get` で取得
   - ブラウザのコピペ作業ゼロで、ローカルのINBOXに保存できた

4. **調査〜判断〜実装まで1日で完結した**
   - 朝：notebooklm-pyセットアップ
   - 昼：GPT Image 2 vs Gemini調査（NotebookLMで30ソース収集）
   - 夜：結論を出してGeminiに決定、汎用スクリプト化まで完了

---

## 登場ツール

| ツール | 役割 |
|---|---|
| notebooklm-py | Claude CodeからNotebookLMをCLI操作するPythonツール（v0.3.4） |
| NotebookLM | Googleの無料リサーチツール。ソースを登録して質問できる |
| generate_images.py | note記事用・汎用画像生成スクリプト（Gemini API使用） |
| Gemini Nano Banana Pro | `gemini-3-pro-image-preview`、高画質・写実的 |

---

## 既存ノートブック（主要なもの）

| ID | タイトル | ソース数 |
|---|---|---|
| a1a5ed5f | Claude Design | 30 |
| 34a78960 | GPT Image 2 vs NanoBanana Pro | 30 |
| cbb12da6 | 2026 X Algorithm Mastery | - |
| 55a40989 | Mastering Claude Skills | - |
| 770b419c | Claude Code: Advanced Automation | - |
