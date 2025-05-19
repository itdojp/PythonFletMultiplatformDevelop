"""テストデータ生成器モジュール"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from faker import Faker

from ..schemas import ItemCreate, UserCreate


class DataGenerator:
    """テストデータ生成器クラス"""

    def __init__(self):
        """初期化"""
        self.faker = Faker()
        self._user_count = 0
        self._item_count = 0

    def generate_user_data(
        self, count: int = 1, is_superuser: bool = False, invalid: bool = False
    ) -> List[UserCreate]:
        """ユーザーのテストデータを生成

        Args:
            count (int): 生成するユーザー数
            is_superuser (bool): スーパーユーザーかどうか
            invalid (bool): 無効なデータを生成するかどうか

        Returns:
            List[UserCreate]: 生成されたユーザーのデータ
        """
        users = []
        for _ in range(count):
            if invalid:
                users.append(
                    UserCreate(
                        email=self.faker.email(),
                        username=(
                            "" if random.random() < 0.5 else self.faker.user_name()
                        ),
                        password=(
                            "short" if random.random() < 0.5 else self.faker.password()
                        ),
                        full_name=self.faker.name(),
                    )
                )
            else:
                self._user_count += 1
                users.append(
                    UserCreate(
                        email=f"user{self._user_count}@example.com",
                        username=f"user{self._user_count}",
                        password="password123",
                        full_name=self.faker.name(),
                        is_superuser=is_superuser,
                    )
                )
        return users

    def generate_item_data(
        self, count: int = 1, owner_id: Optional[int] = None, invalid: bool = False
    ) -> List[ItemCreate]:
        """アイテムのテストデータを生成

        Args:
            count (int): 生成するアイテム数
            owner_id (Optional[int]): アイテムの所有者のID
            invalid (bool): 無効なデータを生成するかどうか

        Returns:
            List[ItemCreate]: 生成されたアイテムのデータ
        """
        items = []
        for _ in range(count):
            if invalid:
                items.append(
                    ItemCreate(
                        title="" if random.random() < 0.5 else self.faker.sentence(),
                        description=self.faker.text(),
                        price=(
                            random.uniform(-100.0, 0.0)
                            if random.random() < 0.5
                            else 0.0
                        ),
                    )
                )
            else:
                self._item_count += 1
                items.append(
                    ItemCreate(
                        title=f"Item {self._item_count}",
                        description=self.faker.text(),
                        price=round(random.uniform(100.0, 1000.0), 2),
                        owner_id=owner_id,
                    )
                )
        return items

    def generate_auth_data(
        self, count: int = 1, invalid: bool = False
    ) -> List[Dict[str, str]]:
        """認証用のテストデータを生成

        Args:
            count (int): 生成する認証情報数
            invalid (bool): 無効なデータを生成するかどうか

        Returns:
            List[Dict[str, str]]: 生成された認証情報
        """
        auth_data = []
        for _ in range(count):
            if invalid:
                auth_data.append(
                    {
                        "email": self.faker.email(),
                        "password": "wrongpassword",
                    }
                )
            else:
                auth_data.append(
                    {
                        "email": f"user{self._user_count}@example.com",
                        "password": "password123",
                    }
                )
        return auth_data

    def generate_dates(
        self, count: int = 1, past_days: int = 30, future_days: int = 30
    ) -> List[datetime]:
        """日付データを生成

        Args:
            count (int): 生成する日付数
            past_days (int): 過去の日数範囲
            future_days (int): 未来の日数範囲

        Returns:
            List[datetime]: 生成された日付
        """
        dates = []
        for _ in range(count):
            days = random.randint(-past_days, future_days)
            dates.append(datetime.utcnow() + timedelta(days=days))
        return dates
