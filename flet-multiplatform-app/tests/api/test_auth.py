"""認証APIのテスト"""

import pytest
from fastapi import status
from httpx import AsyncClient

from src.backend.core.security import create_access_token
from src.backend.models.user import User

pytestmark = pytest.mark.asyncio


async def test_login_success(client: AsyncClient, test_user: User) -> None:
    """ログイン成功のテスト"""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.username,
            "password": "testpassword",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_invalid_username(client: AsyncClient) -> None:
    """無効なユーザー名でのログイン失敗のテスト"""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "invaliduser",
            "password": "testpassword",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_login_invalid_password(client: AsyncClient, test_user: User) -> None:
    """無効なパスワードでのログイン失敗のテスト"""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.username,
            "password": "invalidpassword",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_current_user(client: AsyncClient, test_user: User) -> None:
    """現在のユーザー情報取得のテスト"""
    access_token = create_access_token({"sub": test_user.username})
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


async def test_get_current_user_invalid_token(client: AsyncClient) -> None:
    """無効なトークンでのユーザー情報取得失敗のテスト"""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
