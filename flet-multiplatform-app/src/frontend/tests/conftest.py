"""フロントエンドテストの設定モジュール"""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from flet import Page

from frontend.config.test_config import frontend_test_settings


@pytest.fixture(scope="function")
def test_page() -> Generator[Page, None, None]:
    """テスト用のFletページを作成するフィクスチャ。

    Yields:
        Page: テスト用のFletページ
    """
    os.environ["TESTING"] = "True"
    os.environ["TEST_FRONTEND_WINDOW_WIDTH"] = str(
        frontend_test_settings.TEST_WINDOW_WIDTH
    )
    os.environ["TEST_FRONTEND_WINDOW_HEIGHT"] = str(
        frontend_test_settings.TEST_WINDOW_HEIGHT
    )
    os.environ["TEST_FRONTEND_THEME_MODE"] = frontend_test_settings.TEST_THEME_MODE

    from frontend.flet_app import main

    page = Page()
    page.window_width = frontend_test_settings.TEST_WINDOW_WIDTH
    page.window_height = frontend_test_settings.TEST_WINDOW_HEIGHT
    page.theme_mode = frontend_test_settings.TEST_THEME_MODE

    yield page

    page.close()


@pytest_asyncio.fixture(scope="function")
async def test_api_client() -> AsyncGenerator[None, None]:
    """テスト用のAPIクライアントを作成するフィクスチャ。

    Yields:
        None: APIクライアントの準備が完了した状態
    """
    os.environ["TESTING"] = "True"
    os.environ["TEST_API_URL"] = frontend_test_settings.TEST_API_URL
    os.environ["TEST_API_TIMEOUT"] = str(frontend_test_settings.TEST_API_TIMEOUT)

    yield

    # APIクライアントのクリーンアップ
    os.environ.pop("TESTING", None)
    os.environ.pop("TEST_API_URL", None)
    os.environ.pop("TEST_API_TIMEOUT", None)
