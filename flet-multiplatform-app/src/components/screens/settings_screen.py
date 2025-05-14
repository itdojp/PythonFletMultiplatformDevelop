from flet import AppBar, Column, ElevatedButton, IconButton, Page, Text, icons


def settings_screen(page: Page):
    page.title = "設定"
    page.vertical_alignment = "center"

    settings_content = Column(
        controls=[
            Text("設定画面", size=24, weight="bold"),
            Text("ここでアプリの設定を変更できます。", size=16),
            ElevatedButton("保存", on_click=lambda e: save_settings()),
            ElevatedButton("キャンセル", on_click=lambda e: cancel_settings()),
        ],
        alignment="center",
        spacing=20,
    )

    page.add(settings_content)


def save_settings():
    # 設定を保存するロジックをここに追加
    print("設定が保存されました。")


def cancel_settings():
    # 設定をキャンセルするロジックをここに追加
    print("設定がキャンセルされました。")
