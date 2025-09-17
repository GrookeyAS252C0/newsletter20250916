#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLMを活用した名言フォーマットサービス
受験生・保護者向けに魅力的で落ち着いたトーンで名言を解釈・表示
"""

import os
import json
import logging
from typing import Dict, Optional, TYPE_CHECKING
from dataclasses import dataclass
from openai import OpenAI

# .envファイルから環境変数を読み込み
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenvがインストールされていない場合は警告
    logging.warning("python-dotenvがインストールされていません。.envファイルが読み込まれない可能性があります。")

if TYPE_CHECKING:
    from teacher_quotes_service import TeacherQuote

logger = logging.getLogger(__name__)

@dataclass
class FormattedQuote:
    """フォーマット済み名言データクラス"""
    original_quote: str
    event_context: str
    educational_interpretation: str
    formatted_display: str

class LLMQuoteFormatter:
    """LLM活用名言フォーマットサービス"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: OpenAI APIキー（未指定の場合は環境変数から取得）
        """
        # APIキーの取得と検証
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')

        # API keyが`OPENAI_API_KEY=`で始まっている場合は修正
        if self.api_key and self.api_key.startswith('OPENAI_API_KEY='):
            self.api_key = self.api_key.split('=', 1)[1]

        if not self.api_key or not self.api_key.startswith('sk-'):
            logger.warning("OpenAI APIキーが設定されていないか、形式が正しくありません")
            self.llm_available = False
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.llm_available = True
                logger.info("OpenAI APIクライアント初期化完了")
            except Exception as e:
                logger.error(f"OpenAI APIクライアント初期化エラー: {e}")
                self.llm_available = False
                self.client = None

    def format_quote_for_parents(self, quote: 'TeacherQuote') -> FormattedQuote:
        """
        名言を受験生・保護者向けに魅力的にフォーマット

        Args:
            quote: 元の名言データ

        Returns:
            FormattedQuote: フォーマット済み名言
        """
        if not self.llm_available:
            return self._fallback_format(quote)

        try:
            # イベント文脈の解釈
            event_context = self._interpret_event_context(quote)

            # 教育的意義の解釈
            educational_interpretation = self._interpret_educational_value(quote)

            # 最終的な表示フォーマット作成
            formatted_display = self._create_formatted_display(
                quote, event_context, educational_interpretation
            )

            return FormattedQuote(
                original_quote=quote.quote,
                event_context=event_context,
                educational_interpretation=educational_interpretation,
                formatted_display=formatted_display
            )

        except Exception as e:
            logger.error(f"LLM処理エラー: {e}")
            return self._fallback_format(quote)

    def _interpret_event_context(self, quote: 'TeacherQuote') -> str:
        """イベント文脈を受験生・保護者向けに解釈"""
        prompt = f"""
以下の教育現場での発言について、どのようなイベント・場面で語られたものかを、受験生と保護者にとって分かりやすく、落ち着いたトーンで説明してください。

発言: 「{quote.quote}」
発言者: {quote.teacher}
場面: {quote.scene}
背景: {quote.background}

要件:
- 50文字以内で簡潔に
- 学校の魅力が伝わる表現
- 創作せず、提供された情報のみを使用
- 「〜で」で終わる形式

例: 「学校説明会での教育方針説明で」「授業中の生徒指導で」
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.3
            )

            result = response.choices[0].message.content.strip()
            return result if result.endswith('で') else f"{result}で"

        except Exception as e:
            logger.error(f"イベント文脈解釈エラー: {e}")
            return f"{quote.scene}で"

    def _interpret_educational_value(self, quote: 'TeacherQuote') -> str:
        """教育的価値を受験生・保護者向けに解釈"""
        prompt = f"""
以下の教育現場での発言の教育的価値を、受験生の保護者の視点で落ち着いたトーンで解釈してください。

発言: 「{quote.quote}」
発言者: {quote.teacher}
カテゴリ: {quote.category}
教育的価値: {quote.educational_value}

要件:
- 100文字以内
- 保護者が共感できる表現
- 子どもの成長への期待を込めて
- 創作せず、提供された情報をベースに
- 敬語を使用した丁寧な文体

例: 「お子様の自立心を育む大切な指導として、日常の小さな習慣から確実な成長を促す教育方針が表れています。」
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"教育的価値解釈エラー: {e}")
            return quote.educational_value

    def _create_formatted_display(self, quote: 'TeacherQuote',
                                 event_context: str,
                                 educational_interpretation: str) -> str:
        """最終的な表示フォーマットを作成"""
        template = f"""📖 **日大一中の教育現場から**

**「{quote.quote}」**

🎯 **発言の場面**
{event_context}

👨‍🏫 **お話しされた方**
{quote.teacher}

💭 **この言葉に込められた想い**
{educational_interpretation}

---
*日大一中の先生方が大切にされている教育観をお届けしています*"""

        return template

    def create_newsletter_template(self, quote: 'TeacherQuote') -> str:
        """
        指定されたテンプレート形式で名言を表示

        Args:
            quote: フォーマットする名言

        Returns:
            str: 指定テンプレート形式の名言
        """
        if not self.llm_available:
            return self._create_newsletter_template_fallback(quote)

        try:
            # いつ？を解釈
            when_context = self._interpret_when_context(quote)

            # どんな文脈で？を解釈
            context_interpretation = self._interpret_detailed_context(quote)

            template = f"""5. 日大一・今日の名言
-----
今年度の学校行事・広報イベントの中から、日大一に関係する人たちによる名言をご紹介します。
名言：{quote.quote}
誰が？：{quote.teacher}
いつ？：{when_context}
どんな文脈で？：{context_interpretation}
-----"""

            return template

        except Exception as e:
            logger.error(f"ニュースレターテンプレート作成エラー: {e}")
            return self._create_newsletter_template_fallback(quote)

    def _interpret_when_context(self, quote: 'TeacherQuote') -> str:
        """「いつ？」の文脈を解釈"""
        prompt = f"""
以下の教育現場での発言について、「いつ？」という質問に答える形で、どのようなイベント・場面で発言されたかを簡潔に説明してください。

発言: 「{quote.quote}」
発言者: {quote.teacher}
場面: {quote.scene}
背景: {quote.background}

要件:
- 25文字以内で簡潔に
- 具体的な日付は避け、イベントや場面を重視
- 読者にとって分かりやすい表現
- 創作せず、提供された情報のみを使用

例: 「学校説明会にて」「修学旅行の事前指導で」「イングリッシュキャンプの振り返りで」
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"いつ文脈解釈エラー: {e}")
            return f"{quote.scene}"

    def _interpret_detailed_context(self, quote: 'TeacherQuote') -> str:
        """「どんな文脈で？」を詳細に解釈"""
        prompt = f"""
以下の教育現場での発言について、「どんな文脈で？」という質問に答える形で、この発言から読み取れる学校の教育環境や雰囲気を受験生・保護者に伝わるように詳しく説明してください。

発言: 「{quote.quote}」
カテゴリ: {quote.category}
場面: {quote.scene}
背景: {quote.background}
教育的価値: {quote.educational_value}

要件:
- 120文字以内で詳細な説明
- この発言から分かる学校の教育環境、先生と生徒の関係性、学校の雰囲気を含める
- 受験生・保護者がこの学校の魅力を感じられる表現
- 創作は一切せず、提供された情報から類推できる内容のみ
- 落ち着いた丁寧な文体
- 学校選びの参考になる具体的な情報

例: 「文化祭に向けた準備の中で語られた言葉で、生徒一人ひとりの努力を大切にし、主体的な取り組みを支援する学校の教育姿勢が表れています。先生方が生徒の成長を温かく見守る環境があることが伝わります」
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"詳細文脈解釈エラー: {e}")
            # フォールバック：データベースの情報を組み合わせて学校の雰囲気を伝える
            context_parts = []

            # 場面の説明
            if quote.scene:
                context_parts.append(f"{quote.scene}で語られた言葉です")

            # 背景情報から学校の教育姿勢を読み取る
            if quote.background:
                context_parts.append(f"{quote.background}")

            # 教育的価値から受験生・保護者への意義を説明
            if quote.educational_value:
                educational_part = quote.educational_value
                if "重要" in educational_part or "大切" in educational_part:
                    context_parts.append(f"先生方が生徒の成長を大切に考える教育環境が表れており、{educational_part}")
                elif "実践的" in educational_part or "具体的" in educational_part:
                    context_parts.append(f"生徒に寄り添った実践的な指導を行う学校の姿勢が見え、{educational_part}")
                else:
                    context_parts.append(f"この発言からは、{educational_part}")

            fallback_context = "。".join(context_parts)
            # 文字数制限内に調整
            if len(fallback_context) > 120:
                fallback_context = f"{quote.scene}で語られた言葉で、{quote.educational_value}"

            return fallback_context

    def _create_newsletter_template_fallback(self, quote: 'TeacherQuote') -> str:
        """LLM利用不可時のフォールバック"""
        when_context = quote.scene

        # 詳細な文脈説明を作成
        context_parts = []

        # 場面の説明
        if quote.scene:
            context_parts.append(f"{quote.scene}で語られた言葉です")

        # 背景情報から学校の教育姿勢を読み取る
        if quote.background:
            context_parts.append(f"{quote.background}")

        # 教育的価値から受験生・保護者への意義を説明
        if quote.educational_value:
            educational_part = quote.educational_value
            if "重要" in educational_part or "大切" in educational_part:
                context_parts.append(f"先生方が生徒の成長を大切に考える教育環境が表れており、{educational_part}")
            elif "実践的" in educational_part or "具体的" in educational_part:
                context_parts.append(f"生徒に寄り添った実践的な指導を行う学校の姿勢が見え、{educational_part}")
            else:
                context_parts.append(f"この発言からは、{educational_part}")

        context_interpretation = "。".join(context_parts)
        # 文字数制限内に調整
        if len(context_interpretation) > 120:
            context_interpretation = f"{quote.scene}で語られた言葉で、{quote.educational_value}"

        template = f"""5. 日大一・今日の名言
-----
今年度の学校行事・広報イベントの中から、日大一に関係する人たちによる名言をご紹介します。
名言：{quote.quote}
誰が？：{quote.teacher}
いつ？：{when_context}
どんな文脈で？：{context_interpretation}
-----"""

        return template

    def _fallback_format(self, quote: 'TeacherQuote') -> FormattedQuote:
        """LLM利用不可時のフォールバック"""
        event_context = f"{quote.scene}で"
        educational_interpretation = quote.educational_value

        formatted_display = f"""📖 **日大一中の教育現場から**

**「{quote.quote}」**

🎯 **発言の場面**
{event_context}

👨‍🏫 **お話しされた方**
{quote.teacher}

💭 **この言葉に込められた想い**
{educational_interpretation}

---
*日大一中の先生方が大切にされている教育観をお届けしています*"""

        return FormattedQuote(
            original_quote=quote.quote,
            event_context=event_context,
            educational_interpretation=educational_interpretation,
            formatted_display=formatted_display
        )