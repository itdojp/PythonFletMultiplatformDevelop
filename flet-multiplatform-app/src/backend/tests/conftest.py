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
from backend.config.test_config import test_settings

from ..app import app
from ..config.database import Base, get_db
from ..models import User
from ..schemas import UserCreate
from ..utils.security import get_password_hash
from .data.data_generator import DataGenerator
from .data.extended_data import ExtendedData
from .data.test_data import TestData
from .mocks.test_mocks import TestMocks
from .utils.test_utils import TestUtils

# テスト用のデータベースURL
TEST_SQLALCHEMY_DATABASE_URL = test_settings.TEST_DATABASE_URL

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
    """テスト用のデータベースセッションを提供するフィクスチャ。

    Yields:
        AsyncSession: テスト用のデータベースセッション
    """
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
    """テスト用のクライアントを提供するフィクスチャ。認証ヘッダー付きのクライアントを提供します。

    Args:
        db: テスト用のデータベースセッション

    Yields:
        TestClient: テスト用のクライアント
    """

    # 依存関係のオーバーライド
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # 依存関係を元に戻す
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(db: AsyncSession) -> User:
    """テスト用のユーザーを作成するフィクスチャ"""
    generator = DataGenerator()
    user_data = generator.generate_user_data(1)[0]
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
