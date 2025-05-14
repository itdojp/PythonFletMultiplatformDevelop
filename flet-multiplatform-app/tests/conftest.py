import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base, get_db
from src.main import app

# テスト用のデータベースURL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/flet_dev_test"
)

# テスト用のエンジンとセッション
engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """イベントループのフィクスチャ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def test_db() -> AsyncGenerator[None, None]:
    """テストデータベースのセットアップとクリーンアップ"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session(test_db: None) -> AsyncGenerator[AsyncSession, None]:
    """データベースセッションのフィクスチャ"""
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """テストクライアントのフィクスチャ"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear() 