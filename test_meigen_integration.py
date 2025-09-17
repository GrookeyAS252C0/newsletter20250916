#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
名言データベース統合機能のテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from teacher_quotes_service import TeacherQuotesService

def test_meigen_integration():
    """名言データベース統合機能のテスト"""
    print("=== 名言データベース統合機能テスト ===\n")

    try:
        # サービス初期化
        service = TeacherQuotesService()

        # 名言データベースを強制的に再読み込み
        service.meigen_converter.parse_quotes(process_all=True)
        service.meigen_quotes = service.meigen_converter.quotes

        # 基本統計情報
        print("📊 統計情報:")
        total_quotes = service.get_quote_count(include_meigen_db=True)
        transcript_quotes = service.get_quote_count(include_meigen_db=False)
        print(f"  - 総名言数: {total_quotes}")
        print(f"  - 従来名言数: {transcript_quotes}")
        print(f"  - 名言DB数: {total_quotes - transcript_quotes}")

        # 名言データベースの統計
        meigen_stats = service.get_meigen_stats()
        if "error" not in meigen_stats:
            print(f"\n📈 名言データベース詳細:")
            print(f"  - 総数: {meigen_stats['total_quotes']}")
            print(f"  - 配信済み: {meigen_stats['published']}")
            print(f"  - 未配信: {meigen_stats['unpublished']}")

            print(f"\n📂 カテゴリ別統計:")
            for category, stats in meigen_stats['categories'].items():
                print(f"  - {category}: {stats['total']}件 (未配信: {stats['unpublished']}件)")

        # カテゴリ一覧
        print(f"\n🏷️ 利用可能カテゴリ:")
        categories = service.get_available_categories(include_meigen_db=True)
        for i, category in enumerate(categories, 1):
            print(f"  {i}. {category}")

        # 名言データベースからランダム選択テスト
        print(f"\n🎲 名言データベースからランダム名言:")
        random_meigen = service.get_random_quote(use_meigen_db=True)
        if random_meigen:
            print(f"  - 名言: 「{random_meigen.quote}」")
            print(f"  - 発言者: {random_meigen.teacher}")
            print(f"  - カテゴリ: {random_meigen.category}")
            print(f"  - 文脈: {random_meigen.context}")

        # 特定カテゴリからの選択テスト
        if categories:
            test_category = categories[0]
            print(f"\n🎯 カテゴリ'{test_category}'からの名言:")
            category_quote = service.get_random_quote(category=test_category, use_meigen_db=True)
            if category_quote:
                print(f"  - 名言: 「{category_quote.quote}」")
                print(f"  - 発言者: {category_quote.teacher}")
            else:
                print(f"  - カテゴリ'{test_category}'の未配信名言がありません")

        # メルマガ形式テスト
        print(f"\n📧 メルマガ形式変換テスト:")
        if random_meigen:
            newsletter_format = service.format_quote_for_newsletter(random_meigen)
            print(newsletter_format)

        print("✅ 統合テスト完了！")

    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_meigen_integration()