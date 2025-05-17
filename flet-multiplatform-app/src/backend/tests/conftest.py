"""
テスト用のフィクスチャを定義するモジュール
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.config import settings

from ..app import app
from ..config.database import Base, get_db
from ..models import User
from ..schemas import UserCreate
from ..utils.security import get_password_hash

# テスト用のデータベースURL
TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# テスト用のエンジンとセッションファクトリの作成
test_engine = create_async_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """テスト用のデータベースセッションを提供するフィクスチャ"""
    # テーブルを作成
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # テスト用のセッションを作成
    async with TestingSessionLocal() as session:
        yield session

    # テーブルを削除
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # エンジンを閉じる
    await test_engine.dispose()


@pytest.fixture(scope="function")
def client(db: AsyncSession) -> Generator[TestClient, None, None]:
    """テスト用のクライアントを提供するフィクスチャ"""

    # 依存関係のオーバーライド
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # 依存関係を元に戻す
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(db: AsyncSession) -> User:
    """テスト用のユーザーを作成するフィクスチャ"""
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword",
        full_name="Test User",
    )
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
