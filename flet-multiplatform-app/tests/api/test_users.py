"""ユーザーAPIのテスト"""

import pytest
from fastapi import status
from httpx import AsyncClient

from src.backend.core.security import create_access_token
from src.backend.models.user import User
from src.backend.schemas.user import UserCreate

pytestmark = pytest.mark.asyncio


async def test_create_user(client: AsyncClient, test_user: User) -> None:
    """ユーザー作成のテスト"""
    # スーパーユーザーのトークンを取得
    access_token = create_access_token({"sub": test_user.username})
    headers = {"Authorization": f"Bearer {access_token}"}

    # テストユーザーをスーパーユーザーに更新
    test_user.is_superuser = True
    await test_user.save()

    # 新規ユーザーの作成
    user_in = UserCreate(
        email="newuser@example.com",
        username="newuser",
        password="newpassword",
        is_active=True,
        is_superuser=False,
    )
    response = await client.post(
        "/api/v1/users/",
        headers=headers,
        json=user_in.dict(),
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_in.email
    assert data["username"] == user_in.username
    assert "password" not in data


async def test_create_user_not_superuser(client: AsyncClient, test_user: User) -> None:
    """非スーパーユーザーによるユーザー作成失敗のテスト"""
    access_token = create_access_token({"sub": test_user.username})
    headers = {"Authorization": f"Bearer {access_token}"}

    user_in = UserCreate(
        email="newuser@example.com",
        username="newuser",
        password="newpassword",
        is_active=True,
        is_superuser=False,
    )
    response = await client.post(
        "/api/v1/users/",
        headers=headers,
        json=user_in.dict(),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_read_users(client: AsyncClient, test_user: User) -> None:
    """ユーザー一覧取得のテスト"""
    # スーパーユーザーのトークンを取得
    access_token = create_access_token({"sub": test_user.username})
    headers = {"Authorization": f"Bearer {access_token}"}

    # テストユーザーをスーパーユーザーに更新
    test_user.is_superuser = True
    await test_user.save()

    response = await client.get("/api/v1/users/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(user["username"] == test_user.username for user in data)


async def test_read_users_not_superuser(client: AsyncClient, test_user: User) -> None:
    """非スーパーユーザーによるユーザー一覧取得失敗のテスト"""
    access_token = create_access_token({"sub": test_user.username})
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.get("/api/v1/users/", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_read_user(client: AsyncClient, test_user: User) -> None:
    """特定ユーザー情報取得のテスト"""
    # スーパーユーザーのトークンを取得
    access_token = create_access_token({"sub": test_user.username})
    headers = {"Authorization": f"Bearer {access_token}"}

    # テストユーザーをスーパーユーザーに更新
    test_user.is_superuser = True
    await test_user.save()

    response = await client.get(f"/api/v1/users/{test_user.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


async def test_read_user_not_superuser(client: AsyncClient, test_user: User) -> None:
    """非スーパーユーザーによる特定ユーザー情報取得失敗のテスト"""
    access_token = create_access_token({"sub": test_user.username})
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.get(f"/api/v1/users/{test_user.id}", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
