import flet as ft


def main(page: ft.Page):
    page.title = "Flet Test App"

    # ボタン作成
    def button_clicked(e):
        page.add(ft.Text(f"ボタンがクリックされました！"))
        page.update()

    # UIを構築
    page.add(
        ft.Text("テストアプリケーション", size=30),
        ft.ElevatedButton("クリック", on_click=button_clicked),
    )


if __name__ == "__main__":
    # 通常のモードで実行
    ft.app(target=main)
