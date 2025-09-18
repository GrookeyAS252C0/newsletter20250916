#!/usr/bin/env python3
"""
スクリーンショットベースの天気情報解析機能のテストスクリプト
"""

import os
from datetime import date
from config import AppConfig
from weather_service import WeatherService

def test_screenshot_weather_analysis():
    """スクリーンショットから天気情報を解析するテスト"""

    # 設定の読み込み
    config = AppConfig.from_env()
    weather_service = WeatherService(config.openai_api_key)

    # スクリーンショットのパス
    screenshot_path = "/Users/takashikemmoku/Desktop/newsletter20250916/スクリーンショット 2025-09-17 22.49.35.png"
    target_date = date(2025, 9, 17)

    print(f"スクリーンショット解析テスト開始")
    print(f"対象ファイル: {screenshot_path}")
    print(f"対象日: {target_date}")
    print("-" * 50)

    # ファイルの存在確認
    if not os.path.exists(screenshot_path):
        print(f"エラー: ファイルが見つかりません: {screenshot_path}")
        return

    try:
        # スクリーンショット解析の実行
        weather_info = weather_service.analyze_weather_screenshot(screenshot_path, target_date)

        if weather_info:
            print("✅ 解析成功!")
            print(f"天気概況: {weather_info.天気概況}")
            print(f"登校時の天気: {weather_info.登校時_天気}")
            print(f"登校時の最高気温: {weather_info.登校時_最高気温}")
            print(f"登校時の最低気温: {weather_info.登校時_最低気温}")
            print(f"授業終了時の天気: {weather_info.授業終了時_天気}")
            print(f"授業終了時の気温: {weather_info.授業終了時_気温}")
            print(f"快適具合: {weather_info.快適具合}")

            # ハートウォーミングメッセージの生成テスト
            print("\n--- ハートウォーミングメッセージ ---")
            message = weather_service.generate_heartwarming_message(weather_info, target_date)
            print(message)

        else:
            print("❌ 解析に失敗しました")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_screenshot_weather_analysis()