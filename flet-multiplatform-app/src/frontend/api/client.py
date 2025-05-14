"""APIクライアントの実装"""

import json
from typing import Any, Dict, Optional

import httpx
from flet import Page

from src.backend.schemas.user import UserCreate, UserResponse
from src.frontend.config import settings


class APIClient:
    """APIクライアントクラス"""

    def __init__(self, page: Page):
        self.page = page
        self.base_url = settings.API_BASE_URL
        self._access_token: Optional[str] = None
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
        )

    @property
    def access_token(self) -> Optional[str]:
        """アクセストークンの取得"""
        return self._access_token

    @access_token.setter
    def access_token(self, token: Optional[str]) -> None:
        """アクセストークンの設定"""
        self._access_token = token
        if token:
            self._client.headers["Authorization"] = f"Bearer {token}"
        else:
            self._client.headers.pop("Authorization", None)

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """ログイン"""
        response = await self._client.post(
            "/api/v1/auth/login",
            data={"username": username, "password": password},
        )
        response.raise_for_status()
        data = response.json()
        self.access_token = data["access_token"]
        return data

    async def get_current_user(self) -> UserResponse:
        """現在のユーザー情報を取得"""
        response = await self._client.get("/api/v1/auth/me")
        response.raise_for_status()
        return UserResponse(**response.json())

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """ユーザーを作成"""
        response = await self._client.post(
            "/api/v1/users/",
            json=user_data.dict(),
        )
        response.raise_for_status()
        return UserResponse(**response.json())

    async def get_users(self) -> list[UserResponse]:
        """ユーザー一覧を取得"""
        response = await self._client.get("/api/v1/users/")
        response.raise_for_status()
        return [UserResponse(**user) for user in response.json()]

    async def get_user(self, user_id: int) -> UserResponse:
        """特定のユーザー情報を取得"""
        response = await self._client.get(f"/api/v1/users/{user_id}")
        response.raise_for_status()
        return UserResponse(**response.json())

    async def close(self) -> None:
        """クライアントを閉じる"""
        await self._client.aclose()

    def __del__(self) -> None:
        """デストラクタ"""
        if hasattr(self, "_client"):
            self.page.loop.create_task(self.close())
