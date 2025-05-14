"""Fletアプリケーションを定義するモジュール"""

import flet as ft
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

from .backend.schemas import UserResponse
from .config import settings


class LoginView(UserControl):
    """ログインビュー"""

    def __init__(self, page: Page, on_login_success=None):
        super().__init__()
        self.page = page
        self.on_login_success = on_login_success
        self.username = TextField(
            label="ユーザー名",
            autofocus=True,
            on_submit=self._login,
        )
        self.password = TextField(
            label="パスワード",
            password=True,
            can_reveal_password=True,
            on_submit=self._login,
        )
        self.error_text = Text(
            color=colors.RED_400,
            visible=False,
        )

    def _login(self, e):
        """ログイン処理"""
        # TODO: 実際のログイン処理を実装
        if self.username.value == "admin" and self.password.value == "admin":
            self.error_text.visible = False
            if self.on_login_success:
                self.on_login_success(
                    UserResponse(
                        id=1,
                        username="admin",
                        email="admin@example.com",
                        full_name="Administrator",
                        is_active=True,
                        is_superuser=True,
                        created_at="2024-01-01T00:00:00",
                        updated_at="2024-01-01T00:00:00",
                    )
                )
        else:
            self.error_text.value = "ユーザー名またはパスワードが正しくありません"
            self.error_text.visible = True
        self.update()

    def build(self):
        """ビューを構築する"""
        return Container(
            content=Column(
                controls=[
                    Text("ログイン", size=30, weight=ft.FontWeight.BOLD),
                    self.username,
                    self.password,
                    self.error_text,
                    ElevatedButton(
                        "ログイン",
                        on_click=self._login,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=20,
            alignment=ft.alignment.center,
        )


class MainView(UserControl):
    """メインビュー"""

    def __init__(self, page: Page, user: UserResponse):
        super().__init__()
        self.page = page
        self.user = user
        self.selected_index = 0
        self.rail = NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
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
        self.content = Container(
            content=Text("ダッシュボード", size=30),
            padding=20,
        )

    def _rail_changed(self, e):
        """ナビゲーションの変更を処理する"""
        self.selected_index = e.control.selected_index
        if self.selected_index == 0:
            self.content.content = Text("ダッシュボード", size=30)
        elif self.selected_index == 1:
            self.content.content = Column(
                controls=[
                    Text("プロフィール", size=30),
                    Text(f"ユーザー名: {self.user.username}"),
                    Text(f"メールアドレス: {self.user.email}"),
                    Text(f"氏名: {self.user.full_name}"),
                ],
                spacing=10,
            )
        elif self.selected_index == 2:
            self.content.content = Text("設定", size=30)
        self.update()

    def build(self):
        """ビューを構築する"""
        return Row(
            controls=[
                self.rail,
                ft.VerticalDivider(width=1),
                self.content,
            ],
            expand=True,
        )


def create_app(page: Page):
    """アプリケーションを作成する"""
    page.title = settings.PROJECT_NAME
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 800
    page.window_min_height = 600

    def _on_login_success(user: UserResponse):
        """ログイン成功時の処理"""
        page.clean()
        page.add(MainView(page, user))

    # ログインビューを表示
    page.add(LoginView(page, _on_login_success))

    return page
