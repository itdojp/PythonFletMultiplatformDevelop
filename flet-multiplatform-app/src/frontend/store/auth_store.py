"""認証状態管理ストア"""
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from flet import Page

from src.backend.schemas.user import UserResponse
from src.frontend.api.client import APIClient

@dataclass
class AuthStore:
    """認証状態管理クラス"""
    page: Page
    api_client: APIClient
    _current_user: Optional[UserResponse] = None
    _listeners: List[Callable[[], None]] = field(default_factory=list)

    @property
    def is_authenticated(self) -> bool:
        """認証状態の取得"""
        return self._current_user is not None

    @property
    def current_user(self) -> Optional[UserResponse]:
        """現在のユーザー情報の取得"""
        return self._current_user

    def add_listener(self, listener: Callable[[], None]) -> None:
        """状態変更リスナーの追加"""
        self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[], None]) -> None:
        """状態変更リスナーの削除"""
        self._listeners.remove(listener)

    def _notify_listeners(self) -> None:
        """リスナーへの通知"""
        for listener in self._listeners:
            listener()

    async def login(self, username: str, password: str) -> None:
        """ログイン"""
        await self.api_client.login(username, password)
        self._current_user = await self.api_client.get_current_user()
        self._notify_listeners()

    async def logout(self) -> None:
        """ログアウト"""
        self.api_client.access_token = None
        self._current_user = None
        self._notify_listeners()

    async def refresh_user(self) -> None:
        """ユーザー情報の更新"""
        if self.is_authenticated:
            self._current_user = await self.api_client.get_current_user()
            self._notify_listeners() 