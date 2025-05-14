"""アプリケーションの設定を管理するモジュール。

このモジュールは、アプリケーション全体で使用される設定を一元管理します。
環境変数や設定ファイルから設定を読み込み、型安全な方法でアクセスできるようにします。

主な機能:
- データベース接続設定の管理
- セキュリティ関連の設定
- アプリケーションの基本設定
- 環境変数からの設定値の読み込み

設定の優先順位:
1. 環境変数
2. .env ファイル
3. デフォルト値

例:
    ```python
    from config.settings import settings

    # 設定値の使用例
    db_url = settings.SQLALCHEMY_DATABASE_URI
    secret_key = settings.SECRET_KEY
    ```
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# プロジェクトのルートディレクトリ
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """アプリケーションの設定を管理するクラス。
    
    このクラスは、PydanticのBaseSettingsを継承しており、環境変数や.envファイルから
    設定を読み込むことができます。
    
    Attributes:
        PROJECT_NAME (str): アプリケーション名。デフォルトは"Flet Multiplatform App"。
        VERSION (str): アプリケーションバージョン。デフォルトは"0.1.0"。
        API_V1_STR (str): APIのベースパス。デフォルトは"/api/v1"。
        DEBUG (bool): デバッグモードの有効/無効。デフォルトはTrue。
        
        SECRET_KEY (str): 暗号化に使用されるシークレットキー。
           環境変数`SECRET_KEY`で上書き可能。
           
        ACCESS_TOKEN_EXPIRE_MINUTES (int): アクセストークンの有効期限（分）。
           デフォルトは11520分（8日間）。
           
        ALGORITHM (str): トークンの暗号化アルゴリズム。デフォルトは"HS256"。
        
        POSTGRES_SERVER (str): PostgreSQLサーバーのホスト名。
            環境変数`POSTGRES_SERVER`で上書き可能。デフォルトは"localhost"。
            
        POSTGRES_USER (str): PostgreSQLのユーザー名。
            環境変数`POSTGRES_USER`で上書き可能。デフォルトは"postgres"。
            
        POSTGRES_PASSWORD (str): PostgreSQLのパスワード。
            環境変数`POSTGRES_PASSWORD`で上書き可能。デフォルトは"postgres"。
            
        POSTGRES_DB (str): データベース名。
            環境変数`POSTGRES_DB`で上書き可能。デフォルトは"flet_dev"。
            
        POSTGRES_PORT (str): PostgreSQLのポート番号。
            環境変数`POSTGRES_PORT`で上書き可能。デフォルトは"5432"。
            
        SQLALCHEMY_DATABASE_URI (Optional[PostgresDsn]): SQLAlchemyのデータベースURI。
            自動的に構築されるか、環境変数`DATABASE_URL`で直接指定可能。
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
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
        """データベース接続URIを構築するバリデーター。
        
        Args:
            v: 検証する値。Noneの場合は自動構築される。
            values: 他のフィールドの値が含まれる辞書。
            
        Returns:
            構築されたデータベース接続URI。
            
        Note:
            1. すでに値が設定されている場合はそのまま返す。
            2. 環境変数`DATABASE_URL`が設定されている場合は、
               接頭辞を`postgresql+asyncpg://`に置き換えて返す。
            3. 上記のいずれでもない場合は、個別の接続情報からURIを構築する。
        """
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
