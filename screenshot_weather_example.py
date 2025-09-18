#!/usr/bin/env python3
"""
スクリーンショットベースの天気情報機能の使用例
"""

from datetime import date
from config import AppConfig
from newsletter_generator import NewsletterGenerator

def generate_newsletter_with_screenshot():
    """
    スクリーンショットを使用してメルマガを生成する例
    """

    # 設定の読み込み
    config = AppConfig.from_env()

    # メルマガ生成器の初期化
    generator = NewsletterGenerator(config)

    # 生成パラメータ
    target_date = date(2025, 9, 17)
    screenshot_path = "/Users/takashikemmoku/Desktop/newsletter20250916/スクリーンショット 2025-09-17 22.49.35.png"

    print("📧 スクリーンショットベース天気情報でメルマガ生成開始")
    print(f"📅 対象日: {target_date}")
    print(f"📸 スクリーンショット: {screenshot_path}")
    print("-" * 60)

    try:
        # スクリーンショットを使用してメルマガ生成
        result = generator.generate_newsletter(
            target_date=target_date,
            weather_screenshot_path=screenshot_path
        )

        if result and result.get('content'):
            print("✅ メルマガ生成成功!")
            print(f"📊 文字数: {len(result['content'])}")
            print("\n--- 生成されたメルマガ ---")
            print(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])

            # 天気情報の詳細表示
            if result.get('weather_info'):
                weather = result['weather_info']
                print(f"\n--- 抽出された天気情報 ---")
                print(f"🌤️ 天気概況: {weather.天気概況}")
                print(f"🌅 登校時天気: {weather.登校時_天気}")
                print(f"🌡️ 登校時最高気温: {weather.登校時_最高気温}")
                print(f"🌡️ 登校時最低気温: {weather.登校時_最低気温}")
                print(f"🌇 授業終了時天気: {weather.授業終了時_天気}")
                print(f"🌡️ 授業終了時気温: {weather.授業終了時_気温}")
                print(f"💧 登校時湿度: {weather.登校時_湿度}")
                print(f"💨 登校時風速: {weather.登校時_風速風向}")
                print(f"☔ 登校時降水確率: {weather.登校時_降水確率}")

        else:
            print("❌ メルマガ生成に失敗しました")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_newsletter_with_screenshot()