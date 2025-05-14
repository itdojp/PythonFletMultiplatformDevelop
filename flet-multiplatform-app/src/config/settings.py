"""アプリケーションの設定を管理するモジュール"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# プロジェクトのルートディレクトリ
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """アプリケーションの設定クラス"""

    # 基本設定
    PROJECT_NAME: str = "Flet Multiplatform App"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # セキュリティ設定
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"

    # データベース設定
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "flet_dev")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """データベース接続URIを構築する"""
        if isinstance(v, str):
            return v

        # Docker Composeの環境変数からデータベース接続情報を取得
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            # postgresql:// を postgresql+asyncpg:// に置き換え
            return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # 環境変数が設定されていない場合はデフォルト値を使用
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            port=int(values.data.get("POSTGRES_PORT", 5432)),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )

    # CORS設定
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # ログ設定
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: Path = ROOT_DIR / "logs"
    LOG_FILE: str = "app.log"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    def __init__(self, **kwargs: Any) -> None:
        """初期化時にログディレクトリを作成"""
        super().__init__(**kwargs)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
