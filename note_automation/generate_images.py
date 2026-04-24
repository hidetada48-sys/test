"""
Gemini Nano Banana Pro 画像生成スクリプト
============================
Claude Codeが生成した image_prompts.json を読み込み、
Gemini Nano Banana Pro（gemini-3-pro-image-preview）で画像を生成してoutput/images/に保存する。

使い方：
  python3 generate_images.py
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# .envファイルからAPIキーを読み込む
load_dotenv(Path(__file__).parent / ".env")

# ========== 設定 ==========

# Google APIキー（note_automation/.env の GOOGLE_API_KEY に記載）
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# 使用するモデル（Gemini 3.1 Flash Image = Nano Banana 2）
IMAGE_MODEL = "gemini-3-pro-image-preview"

# パス設定
BASE_DIR   = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"


def find_current_output_dir() -> Path:
    """output/YYYY-MM-DD/ フォルダのうち image_prompts.json があるものを返す"""
    date_dirs = sorted(
        [d for d in OUTPUT_DIR.iterdir() if d.is_dir() and d.name[:4].isdigit()],
        reverse=True  # 新しい日付順
    )
    for d in date_dirs:
        if (d / "image_prompts.json").exists():
            return d
    raise FileNotFoundError(
        "image_prompts.json が見つかりません。先にClaude Codeで記事を生成してください。"
    )


# ========== メイン処理 ==========

def main():
    print("=" * 50)
    print("  Gemini Nano Banana Pro 画像生成")
    print("=" * 50)

    # APIキーの確認
    if GOOGLE_API_KEY == "ここにGoogleのAPIキーを入力":
        print("\n❌ Google APIキーが設定されていません")
        print("  → https://aistudio.google.com/apikey でキーを取得")
        print("  → note_automation/.env の GOOGLE_API_KEY に入力")
        sys.exit(1)

    # 現在の出力フォルダ（image_prompts.jsonがある最新の日付フォルダ）を取得
    try:
        current_dir = find_current_output_dir()
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        sys.exit(1)

    PROMPT_FILE = current_dir / "image_prompts.json"
    IMAGE_DIR   = current_dir / "images"

    print(f"\n📁 対象フォルダ: {current_dir.name}")

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
            # アスペクト比をプロンプトに含めて指定する
            prompt_with_aspect = f"{prompt_en} --ar {aspect}"

            # Gemini 3.1 Flash Image は generate_content で画像を生成する
            response = client.models.generate_content(
                model=IMAGE_MODEL,
                contents=prompt_with_aspect,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                )
            )

            # 画像を保存（レスポンスのpartsからINLINE_DATAを取り出す）
            file_name = f"image_{timestamp}_{i:02d}_{img_type}.png"
            file_path = IMAGE_DIR / file_name

            image_bytes = None
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_bytes = part.inline_data.data
                    break

            if image_bytes is None:
                raise ValueError("画像データがレスポンスに含まれていませんでした")

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
