from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import settings
from backend.app.db.base import Base

# データベースURLを取得
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

# SQLiteの場合はcheck_same_threadをFalseに設定
connect_args = {}
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# エンジンの作成
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args, pool_pre_ping=True
)

# セッションファクトリの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
