"""
日大一中先生名言サービス
"""

import os
import random
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from src.utils.logging_config import logger
from meigen_converter import MeigenConverter, Quote
from llm_quote_formatter import LLMQuoteFormatter, FormattedQuote


@dataclass
class TeacherQuote:
    """先生の名言データクラス"""
    quote: str
    teacher: str
    category: str
    background: str
    scene: str
    context: str
    educational_value: str
    date: str


class TeacherQuotesService:
    """日大一中先生名言サービス"""

    def __init__(self, quotes_file_path: str = "transcript_quotes_balanced_detailed.txt"):
        """
        初期化

        Args:
            quotes_file_path: 名言ファイルのパス
        """
        self.quotes_file_path = quotes_file_path
        self.quotes: List[TeacherQuote] = []
        self.meigen_converter = MeigenConverter()
        self.meigen_quotes: List[Quote] = []
        self.llm_formatter = LLMQuoteFormatter()
        self.load_quotes()
        self.load_meigen_quotes()
    
    def load_quotes(self) -> None:
        """名言ファイルを読み込み、パースする"""
        try:
            if not os.path.exists(self.quotes_file_path):
                logger.warning(f"名言ファイルが見つかりません: {self.quotes_file_path}")
                return
            
            with open(self.quotes_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 各名言を区切り文字で分割
            quote_sections = content.split('--------------------------------------------------')
            
            for section in quote_sections:
                quote = self._parse_quote_section(section.strip())
                if quote:
                    self.quotes.append(quote)
            
            logger.info(f"名言を{len(self.quotes)}件読み込みました")
            
        except Exception as e:
            logger.error(f"名言ファイルの読み込みに失敗しました: {e}")

    def load_meigen_quotes(self) -> None:
        """名言データベースから名言を読み込み"""
        try:
            self.meigen_quotes = self.meigen_converter.parse_quotes()
            logger.info(f"名言データベースから{len(self.meigen_quotes)}件の名言を読み込みました")
        except Exception as e:
            logger.error(f"名言データベースの読み込みに失敗しました: {e}")
            self.meigen_quotes = []
    
    def _parse_quote_section(self, section: str) -> Optional[TeacherQuote]:
        """名言セクションをパースしてTeacherQuoteオブジェクトを作成"""
        if not section or len(section.strip()) == 0:
            return None
        
        try:
            lines = section.split('\n')
            
            # 名言本文を抽出（「」内の文字列）
            quote_match = re.search(r'「(.+?)」', section)
            if not quote_match:
                return None
            quote_text = quote_match.group(1)
            
            # 発言者を抽出
            teacher_match = re.search(r'発言者:\s*(.+)', section)
            teacher = teacher_match.group(1).strip() if teacher_match else "不明"
            
            # カテゴリを抽出
            category_match = re.search(r'カテゴリ:\s*(.+)', section)
            category = category_match.group(1).strip() if category_match else "その他"
            
            # 詳細背景を抽出
            background_match = re.search(r'詳細背景:\s*(.+?)(?=発言場面:|$)', section, re.DOTALL)
            background = background_match.group(1).strip() if background_match else ""
            
            # 発言場面を抽出
            scene_match = re.search(r'発言場面:\s*(.+?)(?=前後の内容:|$)', section, re.DOTALL)
            scene = scene_match.group(1).strip() if scene_match else ""
            
            # 前後の内容を抽出
            context_match = re.search(r'前後の内容:\s*(.+?)(?=教育的価値:|$)', section, re.DOTALL)
            context = context_match.group(1).strip() if context_match else ""
            
            # 教育的価値を抽出
            educational_value_match = re.search(r'教育的価値:\s*(.+?)(?=日付:|$)', section, re.DOTALL)
            educational_value = educational_value_match.group(1).strip() if educational_value_match else ""
            
            # 日付を抽出
            date_match = re.search(r'日付:\s*(.+)', section)
            date = date_match.group(1).strip() if date_match else ""
            
            return TeacherQuote(
                quote=quote_text,
                teacher=teacher,
                category=category,
                background=background,
                scene=scene,
                context=context,
                educational_value=educational_value,
                date=date
            )
            
        except Exception as e:
            logger.error(f"名言の解析に失敗しました: {e}")
            return None
    
    def get_random_quote(self, category: Optional[str] = None, use_meigen_db: bool = False) -> Optional[TeacherQuote]:
        """
        ランダムに名言を取得

        Args:
            category: 特定のカテゴリから選択する場合
            use_meigen_db: 名言データベースから選択するかどうか

        Returns:
            TeacherQuote: 選択された名言
        """
        if use_meigen_db:
            return self._get_random_meigen_quote(category)

        if not self.quotes:
            return None

        if category:
            filtered_quotes = [q for q in self.quotes if q.category == category]
            if not filtered_quotes:
                logger.warning(f"カテゴリ'{category}'の名言が見つかりません")
                return None
            return random.choice(filtered_quotes)

        return random.choice(self.quotes)

    def _get_random_meigen_quote(self, category: Optional[str] = None) -> Optional[TeacherQuote]:
        """名言データベースからランダムに名言を取得"""
        if not self.meigen_quotes:
            return None

        unpublished_quotes = self.meigen_converter.get_unpublished_quotes()
        if not unpublished_quotes:
            logger.warning("未配信の名言がありません")
            return None

        if category:
            filtered_quotes = [q for q in unpublished_quotes if q.category == category]
            if not filtered_quotes:
                logger.warning(f"カテゴリ'{category}'の未配信名言が見つかりません")
                return None
            selected_quote = random.choice(filtered_quotes)
        else:
            selected_quote = random.choice(unpublished_quotes)

        return self._convert_meigen_to_teacher_quote(selected_quote)

    def _convert_meigen_to_teacher_quote(self, meigen_quote: Quote) -> TeacherQuote:
        """名言データベースの形式をTeacherQuote形式に変換"""
        return TeacherQuote(
            quote=meigen_quote.quote,
            teacher=meigen_quote.speaker_role,
            category=meigen_quote.category,
            background=meigen_quote.background,
            scene=meigen_quote.scene,
            context=f"{meigen_quote.scene}で語られた言葉。{meigen_quote.educational_value}",
            educational_value=meigen_quote.educational_value,
            date=meigen_quote.date
        )
    
    def get_available_categories(self, include_meigen_db: bool = True) -> List[str]:
        """利用可能なカテゴリ一覧を取得"""
        categories = set(quote.category for quote in self.quotes)

        if include_meigen_db and self.meigen_quotes:
            meigen_categories = set(quote.category for quote in self.meigen_quotes)
            categories.update(meigen_categories)

        return sorted(list(categories))
    
    def get_quotes_by_teacher(self, teacher_name: str) -> List[TeacherQuote]:
        """特定の先生の名言を取得"""
        return [q for q in self.quotes if teacher_name in q.teacher]
    
    def format_quote_for_newsletter(self, quote: TeacherQuote) -> str:
        """メルマガ用に名言をフォーマット"""
        if not quote:
            return "本日の名言は準備中です。"
        
        formatted_text = f"""💎 **今日の日大一名言**

「{quote.quote}」

**{quote.teacher}**

📝 *{quote.educational_value}*

---
"""
        return formatted_text
    
    def get_quote_count(self, include_meigen_db: bool = True) -> int:
        """登録されている名言の総数を取得"""
        total = len(self.quotes)
        if include_meigen_db:
            total += len(self.meigen_quotes)
        return total

    def get_meigen_stats(self) -> Dict:
        """名言データベースの統計情報を取得"""
        if not self.meigen_quotes:
            return {"error": "名言データベースが読み込まれていません"}

        unpublished = self.meigen_converter.get_unpublished_quotes()
        published_count = len(self.meigen_quotes) - len(unpublished)

        categories = {}
        for quote in self.meigen_quotes:
            if quote.category not in categories:
                categories[quote.category] = {"total": 0, "unpublished": 0}
            categories[quote.category]["total"] += 1

        for quote in unpublished:
            if quote.category in categories:
                categories[quote.category]["unpublished"] += 1

        return {
            "total_quotes": len(self.meigen_quotes),
            "published": published_count,
            "unpublished": len(unpublished),
            "categories": categories
        }

    def mark_meigen_as_published(self, quote_id: int, newsletter_number: int):
        """名言データベースの名言を配信済みとしてマーク"""
        self.meigen_converter.mark_as_published(quote_id, newsletter_number)

    def format_quote_for_parents(self, quote: TeacherQuote) -> FormattedQuote:
        """
        受験生・保護者向けに名言を魅力的にフォーマット

        Args:
            quote: フォーマットする名言

        Returns:
            FormattedQuote: LLMで解釈・フォーマットされた名言
        """
        return self.llm_formatter.format_quote_for_parents(quote)

    def get_enhanced_newsletter_format(self, quote: TeacherQuote) -> str:
        """
        従来のメルマガ形式に加えて、LLM強化版も提供

        Args:
            quote: フォーマットする名言

        Returns:
            str: 受験生・保護者向けフォーマット済みテキスト
        """
        if not quote:
            return "本日の名言は準備中です。"

        try:
            formatted_quote = self.format_quote_for_parents(quote)
            return formatted_quote.formatted_display
        except Exception as e:
            logger.error(f"LLM名言フォーマットエラー: {e}")
            # フォールバック：従来形式
            return self.format_quote_for_newsletter(quote)

    def get_newsletter_template_format(self, quote: TeacherQuote) -> str:
        """
        指定されたテンプレート形式で名言を表示

        Args:
            quote: フォーマットする名言

        Returns:
            str: 指定テンプレート形式の名言
        """
        if not quote:
            return """5. 日大一・今日の名言
-----
今年度の学校行事・広報イベントの中から、日大一に関係する人たちによる名言をご紹介します。
名言：本日の名言は準備中です
誰が？：
いつ？：
どんな文脈で？：
-----"""

        try:
            return self.llm_formatter.create_newsletter_template(quote)
        except Exception as e:
            logger.error(f"ニュースレターテンプレートフォーマットエラー: {e}")
            # フォールバック：基本テンプレート
            return f"""5. 日大一・今日の名言
-----
今年度の学校行事・広報イベントの中から、日大一に関係する人たちによる名言をご紹介します。
名言：{quote.quote}
誰が？：{quote.teacher}
いつ？：{quote.date}の{quote.scene}
どんな文脈で？：{quote.educational_value}
-----"""