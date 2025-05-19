"""アプリケーション設定モジュール。

このモジュールは、アプリケーションの設定を一元管理します。
"""

import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定クラス。

    このクラスは、アプリケーションの設定を管理します。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # アプリケーション設定
    PROJECT_NAME: str = "Flet Multiplatform App"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # セキュリティ設定
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8日間
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # CORS設定
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """コンマ区切りの文字列をリストに変換する。"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # データベース設定
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "flet_app")

    # データベースURL
    DATABASE_URL: Optional[str] = None
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """データベース接続URIを構築する。"""
        if isinstance(v, str):
            return v

        # テスト環境の場合
        if os.getenv("TESTING") == "True":
            return "sqlite+aiosqlite:///:memory:"

        # PostgreSQL接続の場合
        user = values.data.get("POSTGRES_USER", "")
        password = values.data.get("POSTGRES_PASSWORD", "")
        server = values.data.get("POSTGRES_SERVER", "")
        db = values.data.get("POSTGRES_DB", "")

        if user and server and db:
            return f"postgresql+asyncpg://{user}:{password}@{server}/{db}"

        return None

    # 管理者ユーザー設定
    FIRST_SUPERUSER_EMAIL: EmailStr = os.getenv(
        "FIRST_SUPERUSER_EMAIL", "admin@example.com"
    )
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "admin")


# 設定インスタンスのシングルトン作成
settings = Settings()
