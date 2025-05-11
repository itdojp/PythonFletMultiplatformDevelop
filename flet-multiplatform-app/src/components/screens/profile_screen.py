from flet import Page, Column, Text, Container, Row, IconButton, icons

def profile_screen(page: Page):
    page.title = "プロフィール"
    page.vertical_alignment = "center"

    profile_info = Column(
        [
            Text("ユーザー名: 山田太郎", size=24, weight="bold"),
            Text("メール: yamada@example.com", size=16),
            Text("自己紹介: Python開発者。Fletを使用してマルチプラットフォームアプリを開発しています。", size=14),
        ],
        alignment="center",
        spacing=10,
    )

    edit_button = IconButton(icon=icons.EDIT, tooltip="プロフィールを編集", on_click=lambda e: edit_profile())
    
    page.add(
        Container(
            content=Column([profile_info, edit_button]),
            padding=20,
            bgcolor="white",
            border_radius=10,
            box_shadow="0 4px 10px rgba(0, 0, 0, 0.1)",
        )
    )

def edit_profile():
    # プロフィール編集のロジックをここに追加
    pass