# filepath: c:\work\PythonFletMultiplatformDevelopmentDocuments\tools\debug_test.py
import flet as ft


def main(page: ft.Page):
    page.title = "デバッグテスト"

    # シンプルな表示
    page.add(
        ft.Text("これはデバッグテストです", size=30, color="blue"),
        ft.ElevatedButton(
            "テストボタン", on_click=lambda e: print("ボタンがクリックされました")
        ),
    )

    # ログ出力
    print("デバッグテスト: ページが読み込まれました")


# Windowsアプリではなくブラウザで実行
if __name__ == "__main__":
    print("デバッグテスト: アプリケーション開始")
    ft.app(target=main, view=ft.WEB_BROWSER)
    print("デバッグテスト: アプリケーション終了")
