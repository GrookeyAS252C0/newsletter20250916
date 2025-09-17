#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM強化名言フォーマット機能のテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from teacher_quotes_service import TeacherQuotesService
from llm_quote_formatter import LLMQuoteFormatter

def test_enhanced_quote_formatting():
    """LLM強化名言フォーマット機能のテスト"""
    print("=== LLM強化名言フォーマット機能テスト ===\n")

    try:
        # サービス初期化
        service = TeacherQuotesService()

        # 名言データベースを強制的に再読み込み
        service.meigen_converter.parse_quotes(process_all=True)
        service.meigen_quotes = service.meigen_converter.quotes

        print("📊 LLMフォーマッター状態:")
        if service.llm_formatter.llm_available:
            print("  ✅ LLM利用可能（OpenAI API連携）")
        else:
            print("  ⚠️ LLM利用不可（フォールバック形式で動作）")

        # テスト用名言を取得
        print("\n🎲 テスト用名言選択:")
        test_quote = service.get_random_quote(use_meigen_db=True)
        if not test_quote:
            print("  ❌ テスト用名言が取得できませんでした")
            return

        print(f"  - 選択された名言: 「{test_quote.quote[:50]}...」")
        print(f"  - カテゴリ: {test_quote.category}")
        print(f"  - 発言者: {test_quote.teacher}")

        # 従来形式での表示
        print("\n📰 従来のメルマガ形式:")
        traditional_format = service.format_quote_for_newsletter(test_quote)
        print(traditional_format)

        # LLM強化形式での表示
        print("\n✨ LLM強化版（受験生・保護者向け）:")
        enhanced_format = service.get_enhanced_newsletter_format(test_quote)
        print(enhanced_format)

        # 詳細な解釈情報を表示
        if service.llm_formatter.llm_available:
            print("\n🔍 詳細な解釈情報:")
            formatted_quote = service.format_quote_for_parents(test_quote)
            print(f"  📅 イベント文脈: {formatted_quote.event_context}")
            print(f"  💭 教育的解釈: {formatted_quote.educational_interpretation}")

        # 複数カテゴリでのテスト
        print("\n🎯 カテゴリ別フォーマットテスト:")
        categories_to_test = ["習慣形成", "コミュニケーション", "自己管理"]

        for category in categories_to_test:
            category_quote = service.get_random_quote(category=category, use_meigen_db=True)
            if category_quote:
                print(f"\n--- {category}カテゴリ ---")
                enhanced = service.get_enhanced_newsletter_format(category_quote)
                # 最初の3行のみ表示（サンプル）
                lines = enhanced.split('\n')[:3]
                for line in lines:
                    print(line)
                print("...")

        print("\n✅ LLM強化フォーマットテスト完了！")

    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

def test_fallback_functionality():
    """フォールバック機能のテスト"""
    print("\n=== フォールバック機能テスト ===")

    try:
        # APIキーなしでフォーマッターを初期化
        fallback_formatter = LLMQuoteFormatter(api_key=None)
        service = TeacherQuotesService()

        # フォールバック処理をテスト
        test_quote = service.get_random_quote(use_meigen_db=True)
        if test_quote:
            fallback_result = fallback_formatter.format_quote_for_parents(test_quote)
            print("📝 フォールバック形式:")
            print(fallback_result.formatted_display)

        print("✅ フォールバック機能正常動作")

    except Exception as e:
        print(f"❌ フォールバックテストエラー: {e}")

if __name__ == "__main__":
    test_enhanced_quote_formatting()
    test_fallback_functionality()