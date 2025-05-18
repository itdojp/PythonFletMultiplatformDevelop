"""ログインページのテスト"""

import pytest
from flet import Page

from frontend.pages.login import LoginPage


class TestLoginPage:
    """ログインページのテストクラス"""

    @pytest.mark.asyncio
    async def test_login_page_initial_state(self, test_page: Page):
        """ログインページの初期状態のテスト"""
        login_page = LoginPage(test_page)
        await login_page.init_page()

        # フォームの初期状態を確認
        assert login_page.email.value == ""
        assert login_page.password.value == ""
        assert login_page.error_message.value == ""
        assert login_page.loading.value is False

    @pytest.mark.asyncio
    async def test_login_success(self, test_page: Page, test_api_client):
        """ログイン成功のテスト"""
        login_page = LoginPage(test_page)
        await login_page.init_page()

        # テスト用のログイン情報
        login_page.email.value = "test@example.com"
        login_page.password.value = "testpassword"

        # ログインボタンをクリック
        await login_page.login_button.click_async()

        # ローディング状態を確認
        assert login_page.loading.value is True

        # APIレスポンスを待つ
        await asyncio.sleep(1)  # APIレスポンスの待ち時間

        # ローディング状態が解除されていることを確認
        assert login_page.loading.value is False

        # エラーメッセージがないことを確認
        assert login_page.error_message.value == ""

    @pytest.mark.asyncio
    async def test_login_failure(self, test_page: Page, test_api_client):
        """ログイン失敗のテスト"""
        login_page = LoginPage(test_page)
        await login_page.init_page()

        # テスト用のログイン情報（不正なパスワード）
        login_page.email.value = "test@example.com"
        login_page.password.value = "wrongpassword"

        # ログインボタンをクリック
        await login_page.login_button.click_async()

        # ローディング状態を確認
        assert login_page.loading.value is True

        # APIレスポンスを待つ
        await asyncio.sleep(1)  # APIレスポンスの待ち時間

        # ローディング状態が解除されていることを確認
        assert login_page.loading.value is False

        # エラーメッセージが表示されていることを確認
        assert login_page.error_message.value != ""
