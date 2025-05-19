"""ユーザー関連のテスト"""

import pytest
from fastapi import status

from ..schemas import UserCreate, UserResponse, UserUpdate


class TestUsers:
    """ユーザー関連のテストクラス"""

    def test_create_user(self, client, test_token):
        """ユーザー作成のテスト（管理者権限が必要）"""
        headers = {"Authorization": f"Bearer {test_token}"}
        user_data = {
            "email": "newuser2@example.com",
            "username": "newuser2",
            "password": "testpassword",
            "full_name": "New User 2",
            "is_active": True,
            "is_superuser": False,
        }

        # ユーザー作成
        response = client.post("/api/v1/users/", json=user_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED

        # レスポンスの検証
        created_user = UserResponse(**response.json())
        assert created_user.email == user_data["email"]
        assert created_user.username == user_data["username"]
        assert created_user.full_name == user_data["full_name"]
        assert created_user.is_active == user_data["is_active"]
        assert created_user.is_superuser == user_data["is_superuser"]

    def test_read_users(self, client, test_token):
        """ユーザー一覧取得のテスト（管理者権限が必要）"""
        headers = {"Authorization": f"Bearer {test_token}"}

        # ユーザー一覧を取得
        response = client.get("/api/v1/users/", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        # レスポンスの検証
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0

    def test_read_user(self, client, test_user, test_token):
        """ユーザー詳細取得のテスト"""
        headers = {"Authorization": f"Bearer {test_token}"}

        # ユーザー詳細を取得
        response = client.get(f"/api/v1/users/{test_user.id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        # レスポンスの検証
        user_data = UserResponse(**response.json())
        assert user_data.id == test_user.id
        assert user_data.email == test_user.email

        # 存在しないユーザーIDの場合は404
        response = client.get("/api/v1/users/9999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_user(self, client, test_user, test_token):
        """ユーザー情報更新のテスト"""
        headers = {"Authorization": f"Bearer {test_token}"}
        update_data = {
            "email": "updated@example.com",
            "full_name": "Updated User",
        }

        # ユーザー情報を更新
        response = client.put(
            f"/api/v1/users/{test_user.id}", json=update_data, headers=headers
        )
        assert response.status_code == status.HTTP_200_OK

        # レスポンスの検証
        updated_user = UserResponse(**response.json())
        assert updated_user.email == update_data["email"]
        assert updated_user.full_name == update_data["full_name"]

        # 自分以外のユーザーは更新できない
        response = client.put("/api/v1/users/9999", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_user(self, client, test_user, test_token):
        """ユーザー削除のテスト"""
        headers = {"Authorization": f"Bearer {test_token}"}

        # ユーザーを削除
        response = client.delete(f"/api/v1/users/{test_user.id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        # 削除されたユーザーは取得できない
        response = client.get(f"/api/v1/users/{test_user.id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # 自分以外のユーザーは削除できない
        response = client.delete("/api/v1/users/9999", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
