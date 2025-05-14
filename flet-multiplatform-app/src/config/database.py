"""データベースの設定を管理するモジュール"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .settings import settings

# 非同期エンジンの作成
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=settings.DEBUG,
    future=True,
)

# 非同期セッションファクトリの作成
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """データベースセッションを取得する依存性注入関数"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close() 