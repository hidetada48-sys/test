"""
Imagen 3 画像生成スクリプト
============================
Claude Codeが生成した image_prompts.json を読み込み、
Imagen 3で画像を生成してoutput/images/に保存する。

使い方：
  python3 generate_images.py
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types


# ========== 設定 ==========

# Google APIキー（aistudio.google.com/apikey で取得）
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyCMOhm4df677kqMVC-0uxAyWk9kE313JkM")

# 使用するモデル
IMAGE_MODEL = "imagen-4.0-generate-001"

# パス設定
BASE_DIR    = Path(__file__).parent
PROMPT_FILE = BASE_DIR / "output" / "image_prompts.json"
IMAGE_DIR   = BASE_DIR / "output" / "images"


# ========== メイン処理 ==========

def main():
    print("=" * 50)
    print("  Imagen 3 画像生成")
    print("=" * 50)

    # APIキーの確認
    if GOOGLE_API_KEY == "ここにGoogleのAPIキーを入力":
        print("\n❌ Google APIキーが設定されていません")
        print("  → https://aistudio.google.com/apikey でキーを取得")
        print("  → generate_images.py の GOOGLE_API_KEY に入力")
        sys.exit(1)

    # image_prompts.json の確認
    if not PROMPT_FILE.exists():
        print(f"\n❌ プロンプトファイルが見つかりません: {PROMPT_FILE}")
        print("  → 先にClaude Codeで記事を生成してください")
        sys.exit(1)

    # プロンプトの読み込み
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    print(f"\n📋 {len(prompts)}枚の画像を生成します")

    # 出力フォルダの作成
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    # Google Genaiクライアントの初期化
    client = genai.Client(api_key=GOOGLE_API_KEY)

    # タイムスタンプ（ファイル名に使う）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = []
    for i, item in enumerate(prompts, 1):
        img_type    = item.get("type", "body")
        prompt_en   = item.get("prompt_en", "")
        desc_ja     = item.get("description_ja", "")
        aspect      = item.get("aspect_ratio", "1:1")

        print(f"\n  [{i}/{len(prompts)}] {img_type}: {desc_ja[:40]}...")

        try:
            response = client.models.generate_images(
                model=IMAGE_MODEL,
                prompt=prompt_en,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=aspect,
                )
            )

            # 画像を保存
            file_name = f"image_{timestamp}_{i:02d}_{img_type}.png"
            file_path = IMAGE_DIR / file_name

            image_bytes = response.generated_images[0].image.image_bytes
            with open(file_path, "wb") as f:
                f.write(image_bytes)

            print(f"    ✅ 保存: {file_name}")
            results.append({"file": str(file_path), "type": img_type, "description": desc_ja})

        except Exception as e:
            print(f"    ❌ 失敗: {e}")
            results.append({"file": None, "type": img_type, "description": desc_ja, "error": str(e)})

    # 完了
    success = sum(1 for r in results if r["file"])
    print(f"\n✅ 完了: {success}/{len(prompts)}枚 生成成功")
    print(f"📁 保存先: {IMAGE_DIR}")


if __name__ == "__main__":
    main()
