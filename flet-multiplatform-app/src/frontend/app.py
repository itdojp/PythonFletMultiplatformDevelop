"""フロントエンドアプリケーション"""

from typing import Optional

from flet import (
    AppBar,
    Column,
    Container,
    ElevatedButton,
    Icon,
    IconButton,
    NavigationRail,
    NavigationRailDestination,
    Page,
    Row,
    Text,
    TextField,
    UserControl,
    colors,
    icons,
)

from src.frontend.api.client import APIClient
from src.frontend.store.auth_store import AuthStore
from src.frontend.utils.async_utils import (
    AsyncError,
    LoadingManager,
    handle_async_errors,
    with_loading,
)


class LoginView(UserControl):
    """ログインビュー"""

    def __init__(self, auth_store: AuthStore, loading_manager: LoadingManager):
        super().__init__()
        self.auth_store = auth_store
        self.loading_manager = loading_manager
        self.username_field = TextField(label="ユーザー名", autofocus=True)
        self.password_field = TextField(label="パスワード", password=True)
        self.error_text = Text(color=colors.RED, visible=False)

    def build(self):
        return Container(
            content=Column(
                controls=[
                    Text("ログイン", size=30, weight="bold"),
                    self.username_field,
                    self.password_field,
                    self.error_text,
                    ElevatedButton(
                        "ログイン",
                        on_click=self._login,
                    ),
                ],
                horizontal_alignment="center",
                spacing=20,
            ),
            padding=20,
            alignment="center",
        )

    @with_loading(loading_manager)
    @handle_async_errors("ログインに失敗しました")
    async def _login(self, e):
        username = self.username_field.value
        password = self.password_field.value

        if not username or not password:
            self.error_text.value = "ユーザー名とパスワードを入力してください"
            self.error_text.visible = True
            self.update()
            return

        try:
            await self.auth_store.login(username, password)
            self.error_text.visible = False
            self.update()
        except AsyncError as e:
            self.error_text.value = str(e)
            self.error_text.visible = True
            self.update()


class MainView(UserControl):
    """メインビュー"""

    def __init__(self, auth_store: AuthStore, loading_manager: LoadingManager):
        super().__init__()
        self.auth_store = auth_store
        self.loading_manager = loading_manager
        self.navigation_rail = NavigationRail(
            selected_index=0,
            label_type="all",
            destinations=[
                NavigationRailDestination(
                    icon=icons.DASHBOARD_OUTLINED,
                    selected_icon=icons.DASHBOARD,
                    label="ダッシュボード",
                ),
                NavigationRailDestination(
                    icon=icons.PERSON_OUTLINE,
                    selected_icon=icons.PERSON,
                    label="プロフィール",
                ),
                NavigationRailDestination(
                    icon=icons.SETTINGS_OUTLINED,
                    selected_icon=icons.SETTINGS,
                    label="設定",
                ),
            ],
            on_change=self._rail_changed,
        )
        self.content = Column(
            controls=[
                Text("ダッシュボード", size=30, weight="bold"),
            ],
            expand=True,
        )

    def build(self):
        return Row(
            controls=[
                self.navigation_rail,
                Container(
                    content=self.content,
                    expand=True,
                    padding=20,
                ),
            ],
            expand=True,
        )

    def _rail_changed(self, e):
        index = e.control.selected_index
        if index == 0:
            self.content.controls = [Text("ダッシュボード", size=30, weight="bold")]
        elif index == 1:
            self.content.controls = [Text("プロフィール", size=30, weight="bold")]
        elif index == 2:
            self.content.controls = [Text("設定", size=30, weight="bold")]
        self.update()


def create_app(page: Page):
    """アプリケーションの作成"""
    # ページの設定
    page.title = "Flet Multiplatform App"
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 800
    page.window_min_height = 600
    page.theme_mode = "light"
    page.padding = 0

    # コンポーネントの初期化
    api_client = APIClient(page)
    auth_store = AuthStore(page, api_client)
    loading_manager = LoadingManager(page)

    # 認証状態に応じてビューを切り替え
    def on_auth_state_changed():
        if auth_store.is_authenticated:
            page.controls = [MainView(auth_store, loading_manager)]
        else:
            page.controls = [LoginView(auth_store, loading_manager)]
        page.update()

    # 認証状態の変更を監視
    auth_store.add_listener(on_auth_state_changed)

    # 初期ビューの設定
    on_auth_state_changed()
