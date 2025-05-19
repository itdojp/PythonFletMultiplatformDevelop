"""アプリケーション設定モジュール。

このモジュールは、アプリケーションの設定を管理します。
"""

import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, field_validator
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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS設定
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """コンマ区切りの文字列をリストに変換する。

        Args:
            v: 変換対象の値

        Returns:
            変換後の値

        Raises:
            ValueError: 値が無効な場合
        """
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
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """データベース接続URIを構築する。

        Args:
            v: 入力値
            values: 他のフィールドの値

        Returns:
            データベース接続URI
        """
        if isinstance(v, str):
            return v

        # テスト環境の場合
        if os.getenv("TESTING") == "True":
            return "sqlite+aiosqlite:///:memory:"

        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            path=f"/{values.data.get('POSTGRES_DB') or ''}",
        )

    # 最初の管理者ユーザー設定
    FIRST_SUPERUSER_EMAIL: EmailStr = os.getenv(
        "FIRST_SUPERUSER_EMAIL", "admin@example.com"
    )
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "admin")

    # テストやJWTで利用される追加設定
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    SQLALCHEMY_DATABASE_URI: Optional[str] = os.getenv("SQLALCHEMY_DATABASE_URI", None)

    # Pydantic v2では、Configクラスの代わりにmodel_configを使用します


settings = Settings()
