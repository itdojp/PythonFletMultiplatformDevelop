import flet as ft
from flet import Page, Text

def main(page: Page):
    page.title = "フレットテスト"
    page.add(Text("これはテストです"))

# 明示的にブラウザで起動
ft.app(target=main, view=ft.WEB_BROWSER)
