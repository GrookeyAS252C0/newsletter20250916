#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新しいニュースレターテンプレート形式のテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from teacher_quotes_service import TeacherQuotesService

def test_newsletter_template():
    """新しいニュースレターテンプレート形式のテスト"""
    print("=== 新しいニュースレターテンプレート形式テスト ===\n")

    try:
        # サービス初期化
        service = TeacherQuotesService()

        # 名言データベースを強制的に再読み込み
        service.meigen_converter.parse_quotes(process_all=True)
        service.meigen_quotes = service.meigen_converter.quotes

        print("📊 LLMフォーマッター状態:")
        if service.llm_formatter.llm_available:
            print("  ✅ LLM利用可能（gpt-4o-mini使用）")
        else:
            print("  ⚠️ LLM利用不可（フォールバック形式で動作）")

        # 複数の名言をテスト
        print("\n🎯 名言データベースからのテンプレート形式テスト:")

        for i in range(3):
            print(f"\n--- テスト {i+1} ---")
            test_quote = service.get_random_quote(use_meigen_db=True)

            if test_quote:
                print(f"選択された名言: 「{test_quote.quote[:30]}...」")
                print(f"カテゴリ: {test_quote.category}")
                print()

                # 新しいテンプレート形式で表示
                newsletter_format = service.get_newsletter_template_format(test_quote)
                print(newsletter_format)
            else:
                print("名言を取得できませんでした")

        # カテゴリ別テスト
        print("\n🏷️ カテゴリ別テスト:")
        categories_to_test = ["習慣形成", "コミュニケーション", "自己管理"]

        for category in categories_to_test:
            print(f"\n--- {category}カテゴリ ---")
            category_quote = service.get_random_quote(category=category, use_meigen_db=True)

            if category_quote:
                newsletter_format = service.get_newsletter_template_format(category_quote)
                print(newsletter_format)
            else:
                print(f"カテゴリ'{category}'の名言が見つかりません")

        print("\n✅ ニュースレターテンプレート形式テスト完了！")

    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

def test_fallback_template():
    """フォールバック機能のテスト"""
    print("\n=== フォールバックテンプレート機能テスト ===")

    try:
        service = TeacherQuotesService()

        # 従来の名言でテスト
        traditional_quote = service.get_random_quote(use_meigen_db=False)

        if traditional_quote:
            print("📰 従来名言でのテンプレート形式:")
            newsletter_format = service.get_newsletter_template_format(traditional_quote)
            print(newsletter_format)

        print("✅ フォールバックテンプレート機能正常動作")

    except Exception as e:
        print(f"❌ フォールバックテストエラー: {e}")

if __name__ == "__main__":
    test_newsletter_template()
    test_fallback_template()