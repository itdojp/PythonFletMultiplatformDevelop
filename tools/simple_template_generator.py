# filepath: c:\work\PythonFletMultiplatformDevelopmentDocuments\tools\simple_template_generator.py
import flet as ft
from flet import Page, Text, ElevatedButton

def main(page: Page):
    page.title = "簡易テンプレートジェネレーター"
    
    def button_clicked(e):
        page.add(Text("テンプレート生成ボタンがクリックされました！"))
        page.update()
    
    page.add(
        Text("シンプルテンプレートジェネレーター", size=30),
        ElevatedButton("テンプレート生成", on_click=button_clicked)
    )

# simple_test.pyと同様の実行コード
ft.app(target=main, view=ft.WEB_BROWSER)
