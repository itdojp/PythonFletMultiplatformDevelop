"""認証関連のテスト"""

import pytest
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas import Token, UserCreate, UserResponse


class TestAuth:
    """認証関連のテストクラス"""

    @pytest.mark.asyncio
    async def test_register_user(self, client, db):
        """ユーザー登録のテスト"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "testpassword",
            "full_name": "New User",
        }

        # ユーザー登録
        response = client.post(
            "/api/v1/auth/register",
            json=user_data
        )
        assert response.status_code == status.HTTP_201_CREATED

        # レスポンスの検証
        created_user = UserResponse(**response.json())
        assert created_user.email == user_data["email"]
        assert created_user.username == user_data["username"]
        assert created_user.full_name == user_data["full_name"]
        assert created_user.is_active is True
        assert created_user.is_superuser is False

        # 同じメールアドレスでの登録はできない
        response = client.post(
            "/api/v1/auth/register",
            json=user_data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_login(self, client, test_user):
        """ログインのテスト"""
        # 正しい認証情報でログイン
        form_data = {
            "username": "test@example.com",
            "password": "testpassword",
        }
        response = client.post(
            "/api/v1/auth/login",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == status.HTTP_200_OK

        # トークンの検証
        token_data = Token(**response.json())
        assert token_data.token_type == "bearer"
        assert hasattr(token_data, "access_token")

        # 間違ったパスワードでのログインは失敗
        form_data["password"] = "wrongpassword"
        response = client.post(
            "/api/v1/auth/login",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_read_users_me(self, client, test_user, test_token):
        """現在のユーザー情報取得のテスト"""
        # 認証ヘッダーを設定
        headers = {"Authorization": f"Bearer {test_token}"}

        # ユーザー情報を取得
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        # レスポンスの検証
        user_data = UserResponse(**response.json())
        assert user_data.email == test_user.email
        assert user_data.username == test_user.username

        # 無効なトークンでのアクセスは失敗
        headers["Authorization"] = "Bearer invalidtoken"
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
