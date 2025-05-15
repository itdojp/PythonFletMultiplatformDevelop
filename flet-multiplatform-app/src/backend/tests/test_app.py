"""アプリケーションのテスト"""

import pytest
from fastapi import status

from ..config import settings


class TestApp:
    """アプリケーションのテストクラス"""

    def test_root_endpoint(self, client):
        """ルートエンドポイントのテスト"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs_url" in data
        assert data["docs_url"] == f"{settings.API_V1_STR}/docs"

    def test_health_check(self, client):
        """ヘルスチェックエンドポイントのテスト"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}

    def test_docs_available(self, client):
        """APIドキュメントが利用可能かテスト"""
        response = client.get(f"{settings.API_V1_STR}/docs")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]

    def test_openapi_json_available(self, client):
        """OpenAPIスキーマが利用可能かテスト"""
        response = client.get(f"{settings.API_V1_STR}/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        assert "application/json" in response.headers["content-type"]
