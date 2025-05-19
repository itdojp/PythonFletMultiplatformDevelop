"""データベース接続モジュール。

このモジュールは、SQLAlchemyを使ったデータベース接続を管理します。
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import registry, sessionmaker

from backend.core.config import settings

# SQLAlchemy用のベースモデル
mapper_registry = registry()
Base = mapper_registry.generate_base()


# 非同期エンジンの作成
def get_engine():
    """データベースエンジンを取得"""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True,
    )
    return engine


# エンジンの初期化
engine = get_engine()

# 非同期セッションファクトリの作成
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """非同期データベースセッションを取得するジェネレータ関数

    Yields:
        AsyncSession: 非同期データベースセッション
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def init_db():
    """データベースの初期化"""
    # テーブルの作成
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
