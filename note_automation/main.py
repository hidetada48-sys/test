"""
note記事自動生成スクリプト
============================
使い方：
  1. input/ フォルダに3つのテキストファイルを用意する
  2. ANTHROPIC_API_KEY と GOOGLE_API_KEY を設定する
  3. python main.py を実行する
  4. output/ フォルダに記事と画像が生成される
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

import anthropic
import requests
from google import genai
from google.genai import types


# ========== 設定 ==========

# Anthropic APIキー（記事生成・調査用）
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "ここにAnthropicのAPIキーを入力")

# Google APIキー（Imagen 3 画像生成用）
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "ここにGoogleのAPIキーを入力")

# 使用するClaudeモデル
CLAUDE_MODEL = "claude-opus-4-6"

# 使用する画像生成モデル（Imagen 3）
IMAGE_MODEL = "imagen-3.0-generate-001"

# 入力・出力フォルダのパス
INPUT_DIR = Path(__file__).parent / "input"
OUTPUT_DIR = Path(__file__).parent / "output"
IMAGE_DIR = OUTPUT_DIR / "images"

# Web調査で取得する結果の件数
SEARCH_RESULTS_COUNT = 5


# ========== APIキーの確認 ==========

def check_api_keys():
    """APIキーが設定されているか確認する"""
    errors = []

    if ANTHROPIC_API_KEY == "ここにAnthropicのAPIキーを入力":
        errors.append(
            "Anthropic APIキー未設定\n"
            "  → https://console.anthropic.com/ でキーを取得\n"
            "  → main.py の ANTHROPIC_API_KEY に入力"
        )

    if GOOGLE_API_KEY == "ここにGoogleのAPIキーを入力":
        errors.append(
            "Google APIキー未設定\n"
            "  → https://aistudio.google.com/apikey でキーを取得\n"
            "  → main.py の GOOGLE_API_KEY に入力"
        )

    if errors:
        print("\n❌ APIキーが設定されていません：")
        for e in errors:
            print(f"\n  {e}")
        sys.exit(1)


# ========== ファイル読み込み ==========

def load_inputs() -> dict:
    """3つのインプットファイルを読み込む"""
    print("\n📂 インプットファイルを読み込み中...")

    files = {
        "selling_know_how": INPUT_DIR / "01_selling_know_how.txt",
        "theme":            INPUT_DIR / "02_theme.txt",
        "my_info":          INPUT_DIR / "03_my_info.txt",
    }

    inputs = {}
    for key, path in files.items():
        if not path.exists():
            print(f"❌ ファイルが見つかりません: {path}")
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            inputs[key] = f.read().strip()
        print(f"  ✅ {path.name} を読み込みました")

    return inputs


def extract_theme(raw_theme: str) -> str:
    """テーマファイルからコメント行を除いてテーマ文字列を抽出する"""
    lines = [
        line for line in raw_theme.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    return lines[0] if lines else raw_theme


# ========== Web調査 ==========

def research_theme(theme: str) -> str:
    """Jina AI SearchでテーマをWeb調査する（APIキー不要・無料枠）"""
    print(f"\n🔍 テーマを調査中: {theme[:50]}...")

    # Jina AI Search の エンドポイント
    # https://s.jina.ai/{クエリ} にGETするだけで検索結果が返ってくる
    query = f"{theme} 方法 コツ 実践"
    url = f"https://s.jina.ai/{requests.utils.quote(query)}"

    headers = {
        "Accept": "application/json",
        "X-Locale": "ja-JP",           # 日本語優先の結果を取得
        "X-No-Cache": "true",           # 最新情報を取得
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = []

        # Jina AIの検索結果からテキストを取り出す
        for item in data.get("data", [])[:SEARCH_RESULTS_COUNT]:
            title   = item.get("title", "")
            content = item.get("content", "")[:800]  # 長すぎる場合は800文字に切り詰める
            source  = item.get("url", "")
            results.append(f"【タイトル】{title}\n【内容】{content}\n【出典】{source}")

        if not results:
            print("❌ Web調査結果が0件でした。ネットワーク接続を確認してから再実行してください。")
            sys.exit(1)

        print(f"  ✅ {len(results)}件の調査結果を取得しました（Jina AI）")
        return "\n\n---\n\n".join(results)

    except requests.exceptions.RequestException as e:
        print(f"❌ Web調査でエラーが発生しました: {e}")
        print("  → ネットワーク接続を確認してから再実行してください。")
        sys.exit(1)


# ========== Claudeへの問い合わせ ==========

def call_claude(client: anthropic.Anthropic, prompt: str, step_name: str) -> str:
    """Claudeにプロンプトを送信して結果を受け取る"""
    print(f"\n🤖 Claude実行中: {step_name}...")

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    result = message.content[0].text
    print(f"  ✅ {step_name} 完了")
    return result


# ========== ステップ①：記事構成の作成 ==========

def create_structure(claude, inputs: dict, research: str) -> str:
    """インプットと調査結果から記事構成を作成する"""

    prompt = f"""あなたはnoteで多くの読者に読まれ購入される記事を作る専門家です。

以下の情報をもとに、note記事の構成（アウトライン）を作成してください。

## テーマ
{inputs['theme']}

## 売れる記事のノウハウ（必ず反映すること）
{inputs['selling_know_how']}

## 筆者の一次情報
{inputs['my_info']}

## Web調査結果
{research}

---

【出力形式】
JSON形式のみで出力してください（説明文は不要）：

{{
  "title": "記事タイトル（読者が思わずクリックしたくなるもの）",
  "subtitle": "サブタイトル（補足説明）",
  "target_reader": "想定読者（どんな人に向けた記事か）",
  "sections": [
    {{
      "heading": "見出し",
      "purpose": "このセクションの目的",
      "key_points": ["ポイント1", "ポイント2"]
    }}
  ],
  "cta": "記事の最後に促すアクション（フォロー・購入など）"
}}

売れる記事ノウハウを最大限に反映した構成にしてください。"""

    return call_claude(claude, prompt, "記事構成の作成")


# ========== ステップ②：本文の執筆 ==========

def write_article(claude, inputs: dict, research: str, structure: str) -> str:
    """記事構成をもとに本文を執筆する"""

    prompt = f"""あなたはnoteで人気の記事ライターです。
以下の構成と情報をもとに、note記事の本文を執筆してください。

## 記事構成
{structure}

## テーマ
{inputs['theme']}

## 売れる記事のノウハウ（必ず徹底的に反映すること）
{inputs['selling_know_how']}

## 筆者の一次情報（必ず記事に盛り込むこと）
{inputs['my_info']}

## Web調査結果（参考情報として活用）
{research}

---

【執筆ルール】
1. 売れる記事ノウハウを一つ残らず記事に反映すること
2. 筆者の一次情報を具体的なエピソードとして盛り込むこと
3. 読者が「自分のことだ」と感じられる書き出しにすること
4. 見出しは ## を使うこと
5. 記事の長さは2000〜4000文字を目安にすること
6. note向けの読みやすい文体（短い文・改行多め）にすること
7. 画像を入れるべき場所に以下の形式でタグを挿入すること：
   【画像挿入:サムネイル】画像の説明（記事冒頭のサムネイル）
   【画像挿入:本文】画像の説明（本文中）

【出力形式】
Markdown形式で本文全体を出力してください。"""

    return call_claude(claude, prompt, "記事本文の執筆")


# ========== ステップ③：画像プロンプトの抽出 ==========

def extract_image_instructions(claude, article: str, theme: str) -> list[dict]:
    """記事内の【画像挿入】タグを解析してImagen 3用プロンプトを生成する"""

    prompt = f"""以下のnote記事に含まれる【画像挿入】タグを分析し、
Imagen 3（Google）で生成するための英語プロンプトをJSON形式で返してください。

## 記事テーマ
{theme}

## 記事本文
{article}

---

【出力形式】
JSON配列のみで出力してください（説明文は不要）：

[
  {{
    "tag": "【画像挿入:サムネイル】...",
    "type": "thumbnail",
    "description_ja": "どんな画像か日本語で説明",
    "prompt_en": "Imagen 3向け英語プロンプト（写真調・高品質・日本語テキストなし）",
    "aspect_ratio": "16:9"
  }},
  {{
    "tag": "【画像挿入:本文】...",
    "type": "body",
    "description_ja": "どんな画像か日本語で説明",
    "prompt_en": "Imagen 3向け英語プロンプト（写真調・高品質・日本語テキストなし）",
    "aspect_ratio": "1:1"
  }}
]

重要：
- prompt_en は具体的で詳細な英語プロンプトにすること
- 画像内に日本語テキストを含めないこと（Imagen 3は日本語文字が苦手）
- サムネイルは横長（16:9）、本文画像は正方形（1:1）にすること"""

    result = call_claude(claude, prompt, "画像プロンプトの生成")

    # JSON部分のみを抽出してパース
    try:
        json_match = re.search(r'\[.*\]', result, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass

    print("  ⚠️ 画像プロンプトのJSON解析に失敗しました。空リストで続行します。")
    return []


# ========== ステップ④：Imagen 3で画像を生成 ==========

def generate_images(image_instructions: list[dict], timestamp: str) -> list[dict]:
    """Imagen 3を使って画像を生成し、ファイルに保存する"""

    if not image_instructions:
        print("\n⚠️ 画像プロンプトがないため画像生成をスキップします")
        return []

    print(f"\n🖼️  Imagen 3で画像を生成中（{len(image_instructions)}枚）...")
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    # Google Genai クライアントの初期化
    google_client = genai.Client(api_key=GOOGLE_API_KEY)

    results = []
    for i, instruction in enumerate(image_instructions, 1):
        img_type = instruction.get("type", "body")
        prompt_en = instruction.get("prompt_en", "")
        aspect_ratio = instruction.get("aspect_ratio", "1:1")
        desc_ja = instruction.get("description_ja", "")

        print(f"  [{i}/{len(image_instructions)}] {img_type}: {desc_ja[:40]}...")

        try:
            response = google_client.models.generate_images(
                model=IMAGE_MODEL,
                prompt=prompt_en,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=aspect_ratio,
                )
            )

            # 画像をファイルに保存
            file_name = f"image_{timestamp}_{i:02d}_{img_type}.png"
            file_path = IMAGE_DIR / file_name

            image_bytes = response.generated_images[0].image.image_bytes
            with open(file_path, "wb") as f:
                f.write(image_bytes)

            print(f"    ✅ 保存完了: {file_path.name}")

            results.append({
                "tag": instruction.get("tag", ""),
                "file_path": str(file_path),
                "file_name": file_name,
                "type": img_type,
                "description_ja": desc_ja,
            })

        except Exception as e:
            print(f"    ❌ 画像生成に失敗しました: {e}")
            results.append({
                "tag": instruction.get("tag", ""),
                "file_path": None,
                "file_name": None,
                "type": img_type,
                "description_ja": desc_ja,
                "error": str(e),
            })

    return results


# ========== ステップ⑤：記事に画像パスを埋め込む ==========

def embed_images_in_article(article: str, image_results: list[dict]) -> str:
    """記事の【画像挿入】タグを実際の画像参照に置き換える"""

    updated = article
    for img in image_results:
        tag = img.get("tag", "")
        if not tag or not img.get("file_name"):
            continue

        # 【画像挿入:○○】〜 の行をMarkdown画像形式に置き換える
        replacement = (
            f"![{img['description_ja']}](images/{img['file_name']})\n"
            f"*{img['description_ja']}*"
        )
        updated = updated.replace(tag, replacement)

    return updated


# ========== 出力の保存 ==========

def save_outputs(article: str, structure: str, image_results: list[dict], timestamp: str):
    """生成した内容をoutputフォルダに保存する"""
    print("\n💾 ファイルを保存中...")
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 記事本文を保存
    article_path = OUTPUT_DIR / f"article_{timestamp}.md"
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(article)
    print(f"  ✅ 記事本文: {article_path}")

    # 記事構成を保存（参考用）
    structure_path = OUTPUT_DIR / f"structure_{timestamp}.json"
    with open(structure_path, "w", encoding="utf-8") as f:
        f.write(structure)
    print(f"  ✅ 記事構成: {structure_path}")

    # 画像一覧を保存（参考用）
    if image_results:
        image_log_path = OUTPUT_DIR / f"image_log_{timestamp}.json"
        with open(image_log_path, "w", encoding="utf-8") as f:
            json.dump(image_results, f, ensure_ascii=False, indent=2)
        print(f"  ✅ 画像ログ: {image_log_path}")

    return article_path


# ========== メイン処理 ==========

def main():
    print("=" * 50)
    print("  note記事自動生成システム")
    print("=" * 50)

    # APIキーの確認
    check_api_keys()

    # 処理ごとに共通のタイムスタンプを使う
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Claudeクライアントの初期化
    claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # ① インプットファイルの読み込み
    inputs = load_inputs()
    theme = extract_theme(inputs["theme"])

    # ② Web調査
    research = research_theme(theme)

    # ③ 記事構成の作成
    structure = create_structure(claude, inputs, research)

    # ④ 本文の執筆
    article = write_article(claude, inputs, research, structure)

    # ⑤ 画像プロンプトの抽出
    image_instructions = extract_image_instructions(claude, article, theme)

    # ⑥ Imagen 3で画像を生成
    image_results = generate_images(image_instructions, timestamp)

    # ⑦ 記事に画像パスを埋め込む
    article_with_images = embed_images_in_article(article, image_results)

    # ⑧ ファイルの保存
    article_path = save_outputs(article_with_images, structure, image_results, timestamp)

    # 完了メッセージ
    success_count = sum(1 for r in image_results if r.get("file_path"))
    print("\n" + "=" * 50)
    print("  ✅ 完了！")
    print("=" * 50)
    print(f"\n📄 記事ファイル : {article_path}")
    print(f"🖼️  生成画像     : {IMAGE_DIR}/ ({success_count}枚)")
    print("\n次のステップ：")
    print("  1. output/article_*.md を開いて記事を確認する")
    print("  2. output/images/ の画像を確認する")
    print("  3. note.com に記事と画像を貼り付けて投稿する")


if __name__ == "__main__":
    main()
