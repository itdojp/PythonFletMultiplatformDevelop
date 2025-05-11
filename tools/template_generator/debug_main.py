# filepath: c:\work\PythonFletMultiplatformDevelopmentDocuments\tools\template_generator\debug_main.py
import flet as ft

def main(page: ft.Page):
    page.title = "テンプレートジェネレーターデバッグ"
    
    # シンプルな表示
    page.add(
        ft.Text("テンプレートジェネレーターデバッグモード", size=30, weight=ft.FontWeight.BOLD),
        ft.Text("ランチャーの問題を修正中です。しばらくお待ちください。")
    )

# ウィンドウアプリとして実行
ft.app(target=main, view=None)
