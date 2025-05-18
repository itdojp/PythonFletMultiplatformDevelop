"""テスト用のデータ定義モジュール"""

from datetime import datetime, timedelta
from typing import Dict, List

from ..schemas import ItemCreate, UserCreate


class TestData:
    """テスト用のデータクラス"""

    @staticmethod
    def get_test_user_data() -> Dict[str, List[UserCreate]]:
        """テスト用のユーザーデータを取得"""
        return {
            "valid_users": [
                UserCreate(
                    email="test@example.com",
                    username="testuser",
                    password="testpassword",
                    full_name="Test User",
                ),
                UserCreate(
                    email="admin@example.com",
                    username="adminuser",
                    password="adminpassword",
                    full_name="Admin User",
                    is_superuser=True,
                ),
            ],
            "invalid_users": [
                UserCreate(
                    email="invalid@example.com",
                    username="",  # 空のユーザー名
                    password="short",  # 短いパスワード
                    full_name="Invalid User",
                ),
                UserCreate(
                    email="invalid@example.com",
                    username="duplicate",
                    password="testpassword",
                    full_name="Duplicate User",
                ),
            ],
        }

    @staticmethod
    def get_test_item_data() -> Dict[str, List[ItemCreate]]:
        """テスト用のアイテムデータを取得"""
        return {
            "valid_items": [
                ItemCreate(
                    title="Test Item 1",
                    description="This is a test item",
                    price=100.0,
                ),
                ItemCreate(
                    title="Test Item 2",
                    description="Another test item",
                    price=200.0,
                ),
            ],
            "invalid_items": [
                ItemCreate(
                    title="",  # 空のタイトル
                    description="Invalid item",
                    price=0.0,
                ),
                ItemCreate(
                    title="Too Long Title" * 10,
                    description="Invalid item",
                    price=-100.0,  # 負の価格
                ),
            ],
        }

    @staticmethod
    def get_test_auth_data() -> Dict[str, Dict[str, str]]:
        """テスト用の認証データを取得"""
        return {
            "valid_credentials": {
                "email": "test@example.com",
                "password": "testpassword",
            },
            "invalid_credentials": {
                "email": "test@example.com",
                "password": "wrongpassword",
            },
        }

    @staticmethod
    def get_test_dates() -> Dict[str, datetime]:
        """テスト用の日付データを取得"""
        now = datetime.utcnow()
        return {
            "now": now,
            "past": now - timedelta(days=1),
            "future": now + timedelta(days=1),
        }
