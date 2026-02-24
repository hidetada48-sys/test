# note記事自動生成システム

## 仕組み

```
あなた
  ↓ inputに3ファイルを用意して「note記事を生成して」と言うだけ

Claude Code（APIキー不要）
  ├── Jina AI MCP でWeb調査
  ├── 記事構成を作成
  ├── 本文を執筆
  └── 画像プロンプトを生成（image_prompts.json）

generate_images.py（Google APIキーのみ必要）
  └── Imagen 3で画像を自動生成
```

---

## フォルダ構成

```
note_automation/
├── CLAUDE.md              ← Claude Codeへの作業指示書
├── generate_images.py     ← 画像生成スクリプト
├── input/
│   ├── 01_selling_know_how.txt  ← 売れる記事ノウハウ
│   ├── 02_theme.txt             ← 書きたいテーマ
│   └── 03_my_info.txt           ← あなたの一次情報
├── output/                ← 生成結果（自動作成）
│   ├── article_日時.md    ← 完成した記事
│   ├── image_prompts.json ← 画像プロンプト
│   └── images/            ← 生成された画像
├── requirements.txt
└── README.md
```

---

## セットアップ

### 必要なAPIキーはGoogle（画像生成）のみ

1. https://aistudio.google.com/apikey にアクセス
2. Googleアカウントでログイン
3. 「Create API key」でキーを発行
4. `generate_images.py` の以下の行に入力：

```python
GOOGLE_API_KEY = "AIza...ここに貼り付ける"
```

### ライブラリのインストール

**Windows：**
```
pip install -r requirements.txt
```

**Linux / Chromebook：**
```
pip3 install -r requirements.txt
```

---

## 使い方

### ① inputファイルを用意する

| ファイル | 内容 |
|---------|------|
| `01_selling_know_how.txt` | 売れる記事ノウハウ・参考情報 |
| `02_theme.txt` | 書きたいテーマ（1行） |
| `03_my_info.txt` | あなたの体験・データ・知識 |

### ② Claude Codeに話しかける

```
note記事を生成して
```

それだけでOKです。あとはClaude Codeが自動で進めます。

---

## よくある質問

**Q: Web調査が失敗した場合は？**
A: エラーで停止します。ネットワーク接続を確認して再実行してください。

**Q: 画像生成だけ失敗した場合は？**
A: 記事本文は保存されます。Google APIキーを確認して `python3 generate_images.py` を再実行してください。

**Q: 記事を修正したい場合は？**
A: `output/article_日時.md` をテキストエディタで開いて編集してください。
