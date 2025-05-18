"""フロントエンドテスト用の設定モジュール"""

from typing import Any

from pydantic_settings import BaseSettings


class FrontendTestSettings(BaseSettings):
    """フロントエンドテスト用の設定クラス"""

    # テスト用のAPI設定
    TEST_API_URL: str = "http://localhost:8000/api/v1"
    TEST_API_TIMEOUT: int = 10

    # テスト用のUI設定
    TEST_WINDOW_WIDTH: int = 1200
    TEST_WINDOW_HEIGHT: int = 800
    TEST_THEME_MODE: str = "light"

    # テスト用の環境設定
    TEST_ENVIRONMENT: str = "test"
    TEST_DEBUG: bool = True

    class Config:
        env_prefix = "TEST_FRONTEND_"
        case_sensitive = True


frontend_test_settings = FrontendTestSettings()
