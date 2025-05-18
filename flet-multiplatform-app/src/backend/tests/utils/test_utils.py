"""テスト用のユーティリティ関数モジュール"""

import asyncio
from typing import Any, Dict, List, Optional

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Item, User
from ..schemas import ItemCreate, UserCreate
from ..utils.security import get_password_hash


class TestUtils:
    """テスト用のユーティリティクラス"""

    @staticmethod
    async def create_test_user(
        db: AsyncSession,
        user_data: UserCreate,
        is_superuser: bool = False
    ) -> User:
        """テスト用のユーザーを作成"""
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            is_active=True,
            is_superuser=is_superuser,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def create_test_item(
        db: AsyncSession,
        item_data: ItemCreate,
        owner_id: int
    ) -> Item:
        """テスト用のアイテムを作成"""
        item = Item(
            title=item_data.title,
            description=item_data.description,
            price=item_data.price,
            owner_id=owner_id,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def get_test_token(
        client: TestClient,
        email: str,
        password: str
    ) -> Optional[str]:
        """テスト用のアクセストークンを取得"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": email,
                "password": password,
            },
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        return None

    @staticmethod
    def get_test_headers(token: str) -> Dict[str, str]:
        """テスト用の認証ヘッダーを取得"""
        return {
            "Authorization": f"Bearer {token}",
        }

    @staticmethod
    async def cleanup_test_data(db: AsyncSession):
        """テストデータのクリーンアップ"""
        await db.execute("DELETE FROM item")
        await db.execute("DELETE FROM user")
        await db.commit()
