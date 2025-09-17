#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
名言データベースをメルマガ形式に変換するツール

機能:
1. meigen_db_20250916.txtから名言を抽出
2. メルマガ形式（名言・属性・文脈）に変換
3. 掲載管理機能（重複防止）
4. 増分処理対応
"""

import re
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class Quote:
    """名言データクラス"""
    id: int
    quote: str
    speaker: str
    speaker_role: str
    category: str
    background: str
    scene: str
    educational_value: str
    date: str
    published: bool = False
    publish_date: Optional[str] = None
    newsletter_number: Optional[int] = None
    priority: str = "中"


class MeigenConverter:
    """名言変換・管理クラス"""

    def __init__(self, data_file: str = "meigen_db_20250916.txt",
                 meta_file: str = "meigen_meta.json"):
        self.data_file = data_file
        self.meta_file = meta_file
        self.quotes: List[Quote] = []
        self.meta_data = self._load_meta_data()

    def _load_meta_data(self) -> Dict:
        """メタデータの読み込み"""
        default_meta = {
            "last_processed_id": 0,
            "total_quotes": 0,
            "last_update": None,
            "published_count": 0
        }

        if os.path.exists(self.meta_file):
            try:
                with open(self.meta_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default_meta
        return default_meta

    def _save_meta_data(self):
        """メタデータの保存"""
        with open(self.meta_file, 'w', encoding='utf-8') as f:
            json.dump(self.meta_data, f, ensure_ascii=False, indent=2)

    def parse_quotes(self, process_all: bool = False) -> List[Quote]:
        """名言データの解析"""
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"データファイルが見つかりません: {self.data_file}")

        with open(self.data_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # セクションごとに分割
        sections = content.split('--------------------------------------------------')
        matches = []

        for section in sections:
            if not section.strip():
                continue
            match = self._parse_section(section)
            if match:
                matches.append(match)

        # 増分処理の判定
        start_id = 0 if process_all else self.meta_data["last_processed_id"]

        for match in matches:
            quote_id = int(match[0])

            # 増分処理：既に処理済みのIDはスキップ
            if quote_id <= start_id:
                continue

            # 発言者属性の解析
            speaker_attrs = self._parse_speaker_attributes(match[3])
            speaker_role = self._determine_speaker_role(match[2], speaker_attrs)

            quote = Quote(
                id=quote_id,
                quote=match[1].strip(),
                speaker=match[2].strip(),
                speaker_role=speaker_role,
                category=match[4].strip(),
                background=match[5].strip(),
                scene=match[6].strip(),
                educational_value=match[7].strip(),
                date=match[8].strip(),
                priority=self._determine_priority(match[4].strip())
            )

            self.quotes.append(quote)

        # メタデータ更新
        if self.quotes:
            self.meta_data["last_processed_id"] = max(q.id for q in self.quotes)
            self.meta_data["total_quotes"] = self.meta_data["last_processed_id"]
            self.meta_data["last_update"] = datetime.now().isoformat()
            self._save_meta_data()

        return self.quotes

    def _parse_section(self, section: str) -> Optional[Tuple]:
        """セクションをパースしてタプルを返す"""
        # 番号と名言を抽出
        quote_match = re.search(r'(\d+)\.\s*「(.+?)」', section, re.DOTALL)
        if not quote_match:
            return None

        quote_id = quote_match.group(1)
        quote_text = quote_match.group(2).strip()

        # 発言者を抽出
        speaker_match = re.search(r'発言者:\s*(.+)', section)
        speaker = speaker_match.group(1).strip() if speaker_match else "不明"

        # 発言者属性を抽出
        attr_start = section.find('発言者属性:')
        attr_end = section.find('カテゴリ:')
        attr_text = ""
        if attr_start != -1 and attr_end != -1:
            attr_text = section[attr_start+5:attr_end].strip()

        # カテゴリを抽出
        category_match = re.search(r'カテゴリ:\s*(.+)', section)
        category = category_match.group(1).strip() if category_match else "その他"

        # 詳細背景を抽出
        background_match = re.search(r'詳細背景:\s*(.+?)(?=発言場面:|$)', section, re.DOTALL)
        background = background_match.group(1).strip() if background_match else ""

        # 発言場面を抽出
        scene_match = re.search(r'発言場面:\s*(.+?)(?=前後の内容:|$)', section, re.DOTALL)
        scene = scene_match.group(1).strip() if scene_match else ""

        # 教育的価値を抽出
        educational_value_match = re.search(r'教育的価値:\s*(.+?)(?=日付:|$)', section, re.DOTALL)
        educational_value = educational_value_match.group(1).strip() if educational_value_match else ""

        # 日付を抽出
        date_match = re.search(r'日付:\s*(.+)', section)
        date = date_match.group(1).strip() if date_match else ""

        return (quote_id, quote_text, speaker, attr_text, category, background, scene, educational_value, date)

    def _parse_speaker_attributes(self, attr_text: str) -> Dict[str, str]:
        """発言者属性の解析"""
        attrs = {}
        lines = attr_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                attrs[key.strip()] = value.strip()
        return attrs

    def _determine_speaker_role(self, speaker: str, attrs: Dict[str, str]) -> str:
        """発言者の属性を決定"""
        # 学生の場合
        if '生徒' in speaker or any('生徒' in v for v in attrs.values()):
            role_parts = []
            if '学年担当' in attrs:
                role_parts.append(attrs['学年担当'])
            if '役職' in attrs:
                role_parts.append(attrs['役職'])
            if 'バレーボール部' in str(attrs.values()) or '水泳部' in str(attrs.values()):
                if 'バレーボール部' in str(attrs.values()):
                    role_parts.append('バレーボール部所属')
                elif '水泳部' in str(attrs.values()):
                    role_parts.append('水泳部所属')
            return '、'.join(role_parts) if role_parts else '生徒'

        # 教員の場合
        role_parts = []
        if '役職' in attrs:
            role_parts.append(attrs['役職'])
        if '所属部署' in attrs:
            role_parts.append(attrs['所属部署'])
        if '担当科目' in attrs:
            role_parts.append(f"{attrs['担当科目']}担当")
        if '学年担当' in attrs:
            role_parts.append(attrs['学年担当'])

        if role_parts:
            return '、'.join(role_parts) + 'の先生'
        else:
            return '先生'

    def _determine_priority(self, category: str) -> str:
        """カテゴリに基づく優先度の決定"""
        high_priority = ['習慣形成', '基礎力育成', 'コミュニケーション']
        if category in high_priority:
            return '高'
        return '中'

    def get_unpublished_quotes(self) -> List[Quote]:
        """未掲載の名言を取得"""
        return [q for q in self.quotes if not q.published]

    def get_quotes_by_category(self, category: str) -> List[Quote]:
        """カテゴリ別の名言を取得"""
        return [q for q in self.quotes if q.category == category]

    def get_quotes_by_priority(self, priority: str) -> List[Quote]:
        """優先度別の名言を取得"""
        return [q for q in self.quotes if q.priority == priority]

    def mark_as_published(self, quote_id: int, newsletter_number: int):
        """名言を掲載済みとしてマーク"""
        for quote in self.quotes:
            if quote.id == quote_id:
                quote.published = True
                quote.publish_date = datetime.now().strftime('%Y-%m-%d')
                quote.newsletter_number = newsletter_number
                self.meta_data["published_count"] += 1
                self._save_meta_data()
                break

    def generate_newsletter_format(self, quote: Quote) -> str:
        """メルマガ形式に変換"""
        # 文脈の生成（背景と教育的価値を組み合わせ）
        context = f"{quote.scene}で語られた言葉。{quote.educational_value}"

        template = f"""**名言**: 「{quote.quote}」

**誰が**: {quote.speaker_role}

**文脈**: {context}"""

        return template

    def export_quotes(self, quotes: List[Quote], filename: str = None):
        """名言データをJSONで出力"""
        if filename is None:
            filename = f"quotes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        data = {
            "export_date": datetime.now().isoformat(),
            "total_count": len(quotes),
            "quotes": [asdict(q) for q in quotes]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filename


def main():
    """メイン関数 - 使用例"""
    converter = MeigenConverter()

    # 新規データの解析
    print("名言データを解析中...")
    quotes = converter.parse_quotes()
    print(f"新規名言数: {len(quotes)}")

    # 未掲載の名言を取得
    unpublished = converter.get_unpublished_quotes()
    print(f"未掲載名言数: {len(unpublished)}")

    # 最初の未掲載名言をメルマガ形式で出力
    if unpublished:
        first_quote = unpublished[0]
        print("\n=== メルマガ形式サンプル ===")
        print(converter.generate_newsletter_format(first_quote))

        # 掲載済みとしてマーク（例）
        # converter.mark_as_published(first_quote.id, 1)

    # データをJSONでエクスポート
    if quotes:
        export_file = converter.export_quotes(quotes)
        print(f"\nデータをエクスポートしました: {export_file}")


if __name__ == "__main__":
    main()