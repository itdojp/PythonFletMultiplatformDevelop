# filepath: c:\work\PythonFletMultiplatformDevelopmentDocuments\tools\debug_launcher.py
import flet as ft
from flet import Page, Text, ElevatedButton

def main(page: Page):
    page.title = "デバッグランチャー"
    
    def button_clicked(e):
        page.add(Text("ボタンがクリックされました！"))
        page.update()
    
    page.add(
        Text("Fletランチャーデバッグモード", size=30),
        ElevatedButton("クリック", on_click=button_clicked)
    )

# simple_test.pyと同様の実行コード
ft.app(target=main, view=ft.WEB_BROWSER)
