"""テスト用の設定モジュール"""

from typing import Any

from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    """テスト用の設定クラス"""

    # テスト用のデータベース設定
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    TEST_DATABASE_ECHO: bool = False

    # テスト用のセキュリティ設定
    TEST_SECRET_KEY: str = "test-secret-key"
    TEST_ALGORITHM: str = "HS256"
    TEST_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # テスト用の環境設定
    TEST_ENVIRONMENT: str = "test"
    TEST_DEBUG: bool = True

    class Config:
        env_prefix = "TEST_"
        case_sensitive = True


test_settings = TestSettings()
