"""拡張テストデータモジュール"""

from datetime import datetime, timedelta
from random import choice, randint
from typing import Dict, List, Optional

from ..data.data_generator import DataGenerator
from ..schemas import ItemCreate, UserCreate


class ExtendedData:
    """拡張テストデータクラス"""

    @staticmethod
    def generate_extended_user_data(
        count: int = 1,
        is_superuser: bool = False,
        invalid: bool = False,
        with_items: bool = False,
        item_count: int = 3,
    ) -> List[Dict[str, Any]]:
        """拡張ユーザーのデータを生成

        Args:
            count (int): ユーザー数
            is_superuser (bool): スーパーユーザーかどうか
            invalid (bool): 無効なデータかどうか
            with_items (bool): アイテムを含めるかどうか
            item_count (int): アイテム数

        Returns:
            List[Dict[str, Any]]: ユーザーのデータ
        """
        generator = DataGenerator()
        users = generator.generate_user_data(count, is_superuser, invalid)

        if with_items:
            for user in users:
                items = generator.generate_item_data(
                    count=item_count, owner_id=1, invalid=invalid  # テスト用の仮のID
                )
                user.items = items

        return [
            {
                "email": user.email,
                "username": user.username,
                "password": user.password,
                "full_name": user.full_name,
                "is_superuser": user.is_superuser,
                "items": [item.dict() for item in getattr(user, "items", [])],
            }
            for user in users
        ]

    @staticmethod
    def generate_extended_item_data(
        count: int = 1,
        owner_id: Optional[int] = None,
        invalid: bool = False,
        with_history: bool = False,
        history_count: int = 3,
    ) -> List[Dict[str, Any]]:
        """拡張アイテムのデータを生成

        Args:
            count (int): アイテム数
            owner_id (Optional[int]): 所有者のID
            invalid (bool): 無効なデータかどうか
            with_history (bool): 履歴を含めるかどうか
            history_count (int): 履歴数

        Returns:
            List[Dict[str, Any]]: アイテムのデータ
        """
        generator = DataGenerator()
        items = generator.generate_item_data(count, owner_id, invalid)

        if with_history:
            for item in items:
                item.history = [
                    {
                        "date": generator.generate_dates(1)[0],
                        "price": round(item.price * (1 + randint(-10, 10) / 100), 2),
                        "description": f"Price update {i + 1}",
                    }
                    for i in range(history_count)
                ]

        return [
            {
                "title": item.title,
                "description": item.description,
                "price": item.price,
                "owner_id": item.owner_id,
                "history": getattr(item, "history", []),
            }
            for item in items
        ]

    @staticmethod
    def generate_extended_auth_data(
        count: int = 1, invalid: bool = False, with_refresh: bool = False
    ) -> List[Dict[str, str]]:
        """拡張認証データを生成

        Args:
            count (int): 認証情報数
            invalid (bool): 無効なデータかどうか
            with_refresh (bool): リフレッシュトークンを含めるかどうか

        Returns:
            List[Dict[str, str]]: 認証情報
        """
        generator = DataGenerator()
        auth_data = generator.generate_auth_data(count, invalid)

        if with_refresh:
            for data in auth_data:
                data["refresh_token"] = f"refresh_{data['email']}"

        return auth_data

    @staticmethod
    def generate_extended_date_data(
        count: int = 1,
        past_days: int = 30,
        future_days: int = 30,
        with_timezone: bool = False,
    ) -> List[Dict[str, Any]]:
        """拡張日付データを生成

        Args:
            count (int): 日付数
            past_days (int): 過去の日数範囲
            future_days (int): 未来の日数範囲
            with_timezone (bool): タイムゾーン情報を含めるかどうか

        Returns:
            List[Dict[str, Any]]: 日付データ
        """
        generator = DataGenerator()
        dates = generator.generate_dates(count, past_days, future_days)

        if with_timezone:
            timezones = [
                "Asia/Tokyo",
                "America/New_York",
                "Europe/London",
                "Australia/Sydney",
            ]
            for date in dates:
                date.tzinfo = choice(timezones)

        return [
            {
                "date": date,
                "timestamp": date.timestamp(),
                "iso_format": date.isoformat(),
                "timezone": getattr(date, "tzinfo", "UTC"),
            }
            for date in dates
        ]
