#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メルマガ配信管理システム

機能:
1. 名言の選択・配信管理
2. 配信スケジュール管理
3. 配信履歴の記録
4. 統計情報の表示
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from meigen_converter import MeigenConverter, Quote


class NewsletterManager:
    """メルマガ配信管理クラス"""

    def __init__(self, converter: MeigenConverter,
                 schedule_file: str = "newsletter_schedule.json"):
        self.converter = converter
        self.schedule_file = schedule_file
        self.schedule_data = self._load_schedule()

    def _load_schedule(self) -> Dict:
        """配信スケジュールの読み込み"""
        default_schedule = {
            "next_newsletter_number": 1,
            "schedule": [],
            "published_history": [],
            "settings": {
                "frequency": "weekly",  # weekly, biweekly, monthly
                "preferred_categories": ["習慣形成", "基礎力育成", "コミュニケーション"],
                "max_quotes_per_issue": 1
            }
        }

        if os.path.exists(self.schedule_file):
            try:
                with open(self.schedule_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default_schedule
        return default_schedule

    def _save_schedule(self):
        """配信スケジュールの保存"""
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(self.schedule_data, f, ensure_ascii=False, indent=2)

    def select_next_quote(self, preferred_category: str = None) -> Optional[Quote]:
        """次の配信用名言を選択"""
        unpublished = self.converter.get_unpublished_quotes()

        if not unpublished:
            return None

        # カテゴリ指定がある場合
        if preferred_category:
            category_quotes = [q for q in unpublished if q.category == preferred_category]
            if category_quotes:
                # 優先度順でソート
                category_quotes.sort(key=lambda x: (x.priority == '高', x.id))
                return category_quotes[0]

        # 優先度の高いものから選択
        high_priority = [q for q in unpublished if q.priority == '高']
        if high_priority:
            return min(high_priority, key=lambda x: x.id)

        # 通常の優先度から選択
        return min(unpublished, key=lambda x: x.id)

    def schedule_quote(self, quote: Quote, publish_date: str = None) -> Dict:
        """名言の配信スケジュール"""
        if publish_date is None:
            publish_date = datetime.now().strftime('%Y-%m-%d')

        newsletter_number = self.schedule_data["next_newsletter_number"]

        schedule_entry = {
            "newsletter_number": newsletter_number,
            "quote_id": quote.id,
            "publish_date": publish_date,
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }

        self.schedule_data["schedule"].append(schedule_entry)
        self.schedule_data["next_newsletter_number"] += 1
        self._save_schedule()

        return schedule_entry

    def publish_quote(self, quote_id: int, newsletter_number: int) -> bool:
        """名言を配信済みとしてマーク"""
        # 配信履歴に追加
        publish_entry = {
            "newsletter_number": newsletter_number,
            "quote_id": quote_id,
            "publish_date": datetime.now().strftime('%Y-%m-%d'),
            "published_at": datetime.now().isoformat()
        }

        self.schedule_data["published_history"].append(publish_entry)

        # スケジュールのステータス更新
        for entry in self.schedule_data["schedule"]:
            if (entry["quote_id"] == quote_id and
                    entry["newsletter_number"] == newsletter_number):
                entry["status"] = "published"
                entry["published_at"] = datetime.now().isoformat()
                break

        # コンバーターでもマーク
        self.converter.mark_as_published(quote_id, newsletter_number)

        self._save_schedule()
        return True

    def get_scheduled_quotes(self) -> List[Dict]:
        """スケジュール済みの名言を取得"""
        return [entry for entry in self.schedule_data["schedule"]
                if entry["status"] == "scheduled"]

    def get_published_history(self) -> List[Dict]:
        """配信履歴を取得"""
        return self.schedule_data["published_history"]

    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        all_quotes = self.converter.quotes
        total_quotes = len(all_quotes)
        published_count = len([q for q in all_quotes if q.published])
        unpublished_count = total_quotes - published_count

        category_stats = {}
        for quote in all_quotes:
            category = quote.category
            if category not in category_stats:
                category_stats[category] = {"total": 0, "published": 0}
            category_stats[category]["total"] += 1
            if quote.published:
                category_stats[category]["published"] += 1

        return {
            "total_quotes": total_quotes,
            "published_count": published_count,
            "unpublished_count": unpublished_count,
            "next_newsletter_number": self.schedule_data["next_newsletter_number"],
            "category_statistics": category_stats,
            "last_update": datetime.now().isoformat()
        }

    def generate_weekly_schedule(self, weeks: int = 4) -> List[Dict]:
        """週次配信スケジュールを生成"""
        schedule = []
        start_date = datetime.now()

        unpublished = self.converter.get_unpublished_quotes()
        preferred_categories = self.schedule_data["settings"]["preferred_categories"]

        for week in range(weeks):
            if not unpublished:
                break

            publish_date = start_date + timedelta(weeks=week)

            # 優先カテゴリから選択
            selected_quote = None
            for category in preferred_categories:
                category_quotes = [q for q in unpublished if q.category == category]
                if category_quotes:
                    selected_quote = min(category_quotes, key=lambda x: x.id)
                    break

            if not selected_quote and unpublished:
                selected_quote = min(unpublished, key=lambda x: x.id)

            if selected_quote:
                schedule_entry = self.schedule_quote(
                    selected_quote,
                    publish_date.strftime('%Y-%m-%d')
                )
                schedule.append(schedule_entry)
                unpublished.remove(selected_quote)

        return schedule

    def create_newsletter_content(self, quote_id: int) -> str:
        """メルマガ本文を生成"""
        quote = next((q for q in self.converter.quotes if q.id == quote_id), None)
        if not quote:
            return ""

        newsletter_content = f"""今週の教育名言

{self.converter.generate_newsletter_format(quote)}

---
配信日: {datetime.now().strftime('%Y年%m月%d日')}
名言ID: {quote.id}
カテゴリ: {quote.category}
"""
        return newsletter_content


def main():
    """使用例"""
    # システム初期化
    converter = MeigenConverter()
    converter.parse_quotes()

    manager = NewsletterManager(converter)

    print("=== メルマガ配信管理システム ===\n")

    # 統計情報表示
    stats = manager.get_statistics()
    print("【統計情報】")
    print(f"総名言数: {stats['total_quotes']}")
    print(f"配信済み: {stats['published_count']}")
    print(f"未配信: {stats['unpublished_count']}")
    print(f"次回配信号数: {stats['next_newsletter_number']}")

    # 次の名言を選択
    print("\n【次回配信予定】")
    next_quote = manager.select_next_quote()
    if next_quote:
        print(f"名言ID: {next_quote.id}")
        print(f"カテゴリ: {next_quote.category}")
        print(f"優先度: {next_quote.priority}")

        # メルマガ本文生成
        print("\n【メルマガ本文プレビュー】")
        content = manager.create_newsletter_content(next_quote.id)
        print(content)

        # スケジュール登録（例）
        schedule_entry = manager.schedule_quote(next_quote)
        print(f"\nスケジュール登録完了: 第{schedule_entry['newsletter_number']}号")

        # 配信済みとしてマーク（例 - 実際の配信後に実行）
        # manager.publish_quote(next_quote.id, schedule_entry['newsletter_number'])

    # 4週間分のスケジュール生成（例）
    print("\n【4週間配信スケジュール】")
    weekly_schedule = manager.generate_weekly_schedule(4)
    for entry in weekly_schedule:
        quote = next((q for q in converter.quotes if q.id == entry["quote_id"]), None)
        if quote:
            print(f"第{entry['newsletter_number']}号 ({entry['publish_date']}): {quote.category} - ID{quote.id}")


if __name__ == "__main__":
    main()