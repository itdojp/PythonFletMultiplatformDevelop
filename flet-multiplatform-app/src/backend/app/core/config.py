from typing import Any, List, Optional, Union

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Flet Multiplatform App"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here"  # 本番環境では環境変数から取得する
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8日間

    # PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "flet_app"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # CORS設定
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:8000",
        "http://localhost:8501",
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

# SQLAlchemy用のデータベースURIを設定
if settings.SQLALCHEMY_DATABASE_URI is None:
    settings.SQLALCHEMY_DATABASE_URI = "sqlite:///./sql_app.db"
    # PostgreSQLを使用する場合
    # settings.SQLALCHEMY_DATABASE_URI = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
