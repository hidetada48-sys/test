# note記事自動生成システム

## フォルダ構成

```
note_automation/
├── input/
│   ├── 01_selling_know_how.txt   ← 売れる記事ノウハウ
│   ├── 02_theme.txt              ← 書きたいテーマ
│   └── 03_my_info.txt            ← あなたの一次情報
├── output/                       ← 生成結果（自動作成）
│   ├── article_日時.md           ← 完成した記事本文
│   ├── structure_日時.json       ← 記事構成（参考用）
│   ├── image_log_日時.json       ← 画像ログ（参考用）
│   └── images/                  ← 生成された画像
│       ├── image_日時_01_thumbnail.png
│       └── image_日時_02_body.png
├── main.py
├── requirements.txt
└── README.md
```

---

## セットアップ手順

### ステップ1：Anthropic APIキーを取得する（記事生成用）

1. https://console.anthropic.com/ にアクセス
2. アカウントを作成（無料）
3. 「API Keys」→「Create Key」でキーを発行
4. `sk-ant-...` から始まるキーをコピー

### ステップ2：Google APIキーを取得する（画像生成用）

1. https://aistudio.google.com/apikey にアクセス
2. Googleアカウントでログイン
3. 「Create API key」でキーを発行
4. キーをコピー

### ステップ3：main.py にAPIキーを設定する

`main.py` を開いて以下の2箇所を編集：

```python
ANTHROPIC_API_KEY = "sk-ant-ここに貼り付ける"
GOOGLE_API_KEY    = "AIza...ここに貼り付ける"
```

### ステップ4：ライブラリをインストールする

**Windows（コマンドプロンプト）：**
```
pip install -r requirements.txt
```

**Linux / Chromebook（ターミナル）：**
```
pip3 install -r requirements.txt
```

---

## 使い方

### ① インプットファイルを用意する

`input/` フォルダの3つのファイルを編集する：

| ファイル | 内容 |
|---------|------|
| `01_selling_know_how.txt` | 売れる記事の書き方・ノウハウ・参考記事 |
| `02_theme.txt` | 書きたいテーマ（1行） |
| `03_my_info.txt` | あなた自身の体験・データ・知識 |

### ② スクリプトを実行する

**Windows：**
```
python main.py
```

**Linux / Chromebook：**
```
python3 main.py
```

### ③ 実行の流れ

```
📂 インプット読み込み
  ↓
🔍 Web調査（DuckDuckGo）※失敗時はエラー停止
  ↓
🤖 記事構成の作成（Claude）
  ↓
🤖 本文の執筆（Claude）
  ↓
🤖 画像プロンプトの生成（Claude）
  ↓
🖼️  画像の生成（Imagen 3）
  ↓
💾 ファイルの保存
```

### ④ 出力を確認する

- `output/article_日時.md` → 記事本文（画像埋め込み済み）
- `output/images/` → 生成された画像ファイル

---

## よくある質問

**Q: 画像生成だけ失敗した場合は？**
A: 記事本文は保存されます。Google APIキーを確認してから再実行してください。

**Q: Web調査がエラーになった場合は？**
A: エラーで停止します。ネットワーク接続を確認してから再実行してください。
Web調査は記事品質に直結するため、必須処理としています。

**Q: 記事を修正したい場合は？**
A: `output/article_日時.md` をテキストエディタで開いて編集してください。
