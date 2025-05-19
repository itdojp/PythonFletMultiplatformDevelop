# filepath: c:\work\PythonFletMultiplatformDevelopmentDocuments\tools\test_colors.py
import flet as ft


def main(page: ft.Page):
    page.title = "カラーテスト"

    # カラーのテスト表示
    page.add(
        ft.Text("カラーテスト", size=30, weight=ft.FontWeight.BOLD),
        ft.Container(
            content=ft.Text("赤色のテキスト"), bgcolor="red", padding=10  # 文字列で指定
        ),
        ft.Container(
            content=ft.Text("青色のコンテナ"),
            bgcolor="blue",  # 文字列で指定
            padding=10,
        ),
    )


# Windowsアプリとして実行
if __name__ == "__main__":
    ft.app(target=main, view=None)
