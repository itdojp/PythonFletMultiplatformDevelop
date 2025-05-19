import flet as ft


def main(page: ft.Page):
    page.title = "マイアプリ"

    # タイトル
    title = ft.Text("マイアプリ", size=30)

    # メインコンテンツ
    content = ft.Column(
        [
            ft.Text("ようこそ！", size=20),
            ft.ElevatedButton(
                "クリックしてください", on_click=lambda _: show_message()
            ),
        ]
    )

    def show_message():
        page.add(ft.Text("ボタンがクリックされました！"))
        page.update()

    # レイアウト
    page.add(title, content)


if __name__ == "__main__":
    ft.app(target=main)
