# filepath: c:\work\PythonFletMultiplatformDevelopmentDocuments\tools\fixed_test.py
import flet as ft
from flet import Page, Text


def main(page: Page):
    page.title = "フレットテスト"

    # シンプルなテキスト表示
    page.add(
        Text("これはテストです", size=30, color="blue"),
        Text("正常に動作しています", color="green"),
    )

    # 色を使ったコンテナ
    container = ft.Container(
        content=Text("これはコンテナ内のテキストです"),
        padding=10,
        bgcolor="#E3F2FD",  # 文字列で色を指定
        border=ft.border.all(1, "#2196F3"),  # 文字列で色を指定
        border_radius=10,
    )
    page.add(container)


# ブラウザモードで実行
if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
