"""データベースの設定を管理するモジュール"""

import logging
from typing import AsyncGenerator, Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine import Engine

from .settings import settings

logger = logging.getLogger(__name__)

# 非同期エンジンの作成
try:
    engine = create_async_engine(
        str(settings.SQLALCHEMY_DATABASE_URI),
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True,  # 接続が有効かどうかを確認する
        pool_recycle=3600,  # 1時間で接続をリサイクル
    )
    logger.info(f"Database connection created: {settings.SQLALCHEMY_DATABASE_URI}")
except Exception as e:
    logger.error(f"Error creating database engine: {e}")
    raise

# 非同期セッションファクトリの作成
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """データベースセッションを取得する依存性注入関数"""
    session = AsyncSessionLocal()
    try:
        logger.debug("Yielding database session")
        yield session
        await session.commit()
        logger.debug("Database session committed")
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        await session.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await session.rollback()
        raise
    finally:
        logger.debug("Closing database session")
        await session.close()
