"""テスト用の設定ファイル"""

import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator

# src ディレクトリを Python パスに追加
sys.path.append(str(Path(__file__).parent.parent / "src"))

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.backend.app import app
from src.backend.core.security import get_password_hash
from src.backend.db.base import Base
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.user import UserCreate

# テスト用のデータベースURL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# テスト用のエンジンとセッション
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """イベントループのフィクスチャ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """テスト用データベースのフィクスチャ"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="module")
def client(test_db: AsyncSession) -> Generator:
    """テストクライアントのフィクスチャ"""

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="module")
async def test_user(test_db: AsyncSession) -> User:
    """テストユーザーのフィクスチャ"""
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword",
        is_active=True,
        is_superuser=False,
    )
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user
