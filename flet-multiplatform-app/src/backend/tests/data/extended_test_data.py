"""拡張テストデータモジュール"""

from datetime import datetime, timedelta
from typing import Dict, List

from ..schemas import ItemCreate, UserCreate


class ExtendedTestData:
    """拡張テストデータクラス"""

    @staticmethod
    def get_extended_user_data() -> Dict[str, List[UserCreate]]:
        """拡張ユーザーデータを取得"""
        return {
            "valid_users": [
                UserCreate(
                    email="user1@example.com",
                    username="user1",
                    password="password123",
                    full_name="User One",
                ),
                UserCreate(
                    email="user2@example.com",
                    username="user2",
                    password="password123",
                    full_name="User Two",
                ),
                UserCreate(
                    email="user3@example.com",
                    username="user3",
                    password="password123",
                    full_name="User Three",
                ),
            ],
            "invalid_users": [
                UserCreate(
                    email="invalid@example.com",
                    username="invalid",
                    password="short",
                    full_name="Invalid User",
                ),
                UserCreate(
                    email="invalid@example.com",
                    username="",
                    password="password123",
                    full_name="Invalid User",
                ),
                UserCreate(
                    email="invalid@example.com",
                    username="user1",
                    password="password123",
                    full_name="Duplicate User",
                ),
            ],
        }

    @staticmethod
    def get_extended_item_data() -> Dict[str, List[ItemCreate]]:
        """拡張アイテムデータを取得"""
        return {
            "valid_items": [
                ItemCreate(
                    title="Item 1",
                    description="Description for item 1",
                    price=100.0,
                ),
                ItemCreate(
                    title="Item 2",
                    description="Description for item 2",
                    price=200.0,
                ),
                ItemCreate(
                    title="Item 3",
                    description="Description for item 3",
                    price=300.0,
                ),
            ],
            "invalid_items": [
                ItemCreate(
                    title="",
                    description="Invalid item",
                    price=0.0,
                ),
                ItemCreate(
                    title="Too Long Title" * 20,
                    description="Invalid item",
                    price=-100.0,
                ),
                ItemCreate(
                    title="Item 1",
                    description="Duplicate item",
                    price=100.0,
                ),
            ],
        }

    @staticmethod
    def get_extended_auth_data() -> Dict[str, Dict[str, str]]:
        """拡張認証データを取得"""
        return {
            "valid_credentials": [
                {
                    "email": "user1@example.com",
                    "password": "password123",
                },
                {
                    "email": "user2@example.com",
                    "password": "password123",
                },
            ],
            "invalid_credentials": [
                {
                    "email": "user1@example.com",
                    "password": "wrongpassword",
                },
                {
                    "email": "nonexistent@example.com",
                    "password": "password123",
                },
            ],
        }

    @staticmethod
    def get_extended_dates() -> Dict[str, datetime]:
        """拡張日付データを取得"""
        now = datetime.utcnow()
        return {
            "now": now,
            "past": now - timedelta(days=1),
            "future": now + timedelta(days=1),
            "past_week": now - timedelta(days=7),
            "future_week": now + timedelta(days=7),
            "past_month": now - timedelta(days=30),
            "future_month": now + timedelta(days=30),
        }
