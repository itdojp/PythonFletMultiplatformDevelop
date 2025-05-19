"""データベース設定モジュール"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# settingsのimportは関数内で遅延実行


def get_engine_and_session():
    import os

    from backend.config.config import settings
    from backend.config.test_config import test_settings

    # 環境に応じた設定の選択
    current_settings = test_settings if os.getenv("TESTING") == "True" else settings
    engine = create_async_engine(
        current_settings.DATABASE_URL,
        echo=current_settings.DEBUG,
        future=True,
        pool_pre_ping=True,
    )
    AsyncSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    return engine, AsyncSessionLocal


# Get database engine and session
engine, AsyncSessionLocal = get_engine_and_session()


async def get_db() -> AsyncSession:
    """非同期データベースセッションを取得するジェネレータ関数。

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
