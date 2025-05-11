from flet import Page, Column, Text, ElevatedButton, Row

def home_screen(page: Page):
    page.title = "ホーム"
    page.vertical_alignment = "center"

    content = Column(
        controls=[
            Text("ようこそ！", size=32, weight="bold"),
            Text("このアプリケーションはマルチプラットフォーム対応です。", size=16),
            ElevatedButton("設定に移動", on_click=lambda e: page.go("/settings")),
            ElevatedButton("プロフィールに移動", on_click=lambda e: page.go("/profile")),
        ],
        alignment="center",
        spacing=20,
    )

    page.add(content)