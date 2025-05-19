"""テスト用のデータベース初期化スクリプト"""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.config.database import Base, get_engine_and_session
from backend.config.test_config import test_settings
from backend.main import app


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """テスト用のデータベースセッションを提供するフィクスチャ。

    Yields:
        AsyncSession: テスト用のデータベースセッション
    """
    # テスト用のエンジンとセッションファクトリの作成
    test_engine, TestSessionLocal = get_engine_and_session()

    # テーブルを作成
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # テスト用のセッションを作成
    async with TestSessionLocal() as session:
        yield session

    # テーブルを削除
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # エンジンを閉じる
    await test_engine.dispose()


@pytest.fixture(scope="function")
def client(test_db: AsyncSession) -> Generator[TestClient, None, None]:
    """テスト用のクライアントを提供するフィクスチャ。

    Args:
        test_db: テスト用のデータベースセッション

    Yields:
        TestClient: テスト用のクライアント
    """

    # 依存関係のオーバーライド
    def override_get_db():
        return test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
