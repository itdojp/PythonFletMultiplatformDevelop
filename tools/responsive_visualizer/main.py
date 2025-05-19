import json
import os
import platform
import re
from pathlib import Path

import flet as ft

# 一般的なデバイスの画面サイズ定義
DEVICE_PRESETS = [
    {"name": "モバイル (小)", "width": 320, "height": 568, "icon": ft.icons.SMARTPHONE},
    {
        "name": "モバイル (標準)",
        "width": 375,
        "height": 667,
        "icon": ft.icons.SMARTPHONE,
    },
    {"name": "モバイル (大)", "width": 425, "height": 812, "icon": ft.icons.SMARTPHONE},
    {"name": "タブレット", "width": 768, "height": 1024, "icon": ft.icons.TABLET},
    {"name": "ノートPC", "width": 1024, "height": 768, "icon": ft.icons.LAPTOP},
    {
        "name": "デスクトップ",
        "width": 1440,
        "height": 900,
        "icon": ft.icons.DESKTOP_WINDOWS,
    },
    {"name": "カスタム", "width": 0, "height": 0, "icon": ft.icons.ASPECT_RATIO},
]


def main(page: ft.Page):
    page.title = "Fletレスポンシブビジュアライザー"
    page.theme_mode = ft.ThemeMode.SYSTEM

    # テーマ設定
    apply_app_theme(page)

    # Fletのサンプルレイアウト定義
    # これらはプレビュー用のサンプルレイアウトで、実行中に変更可能
    sample_layouts = {
        "基本レイアウト": {
            "code": """ft.Column([
    ft.Text("Fletレスポンシブレイアウト", size=30, weight=ft.FontWeight.BOLD),
    ft.Text("画面幅: {width}px、高さ: {height}px"),
    ft.Row([
        ft.Container(
            content=ft.Text("サイドナビ"),
            bgcolor=ft.colors.BLUE_100,
            padding=10,
            expand=1
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("メインコンテンツ"),
                ft.Row([
                    ft.Card(
                        content=ft.Container(
                            content=ft.Text("カード1"),
                            padding=10
                        ),
                        width=150,
                        height=100
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Text("カード2"),
                            padding=10
                        ),
                        width=150,
                        height=100
                    )
                ]),
                ft.TextField(label="入力フィールド")
            ]),
            bgcolor=ft.colors.BLUE_50,
            padding=10,
            expand=3
        )
    ], expand=True)
])""",
            "responsive_rules": """# レスポンシブ対応ルール
if width < 600:  # モバイル向け
    layout_row.direction = "column"  # 縦方向に配置
    for card in cards:
        card.width = None  # 幅自動調整
        card.expand = True
else:  # デスクトップ向け
    layout_row.direction = "row"  # 横方向に配置
    for card in cards:
        card.width = 150  # 固定幅
        card.expand = False""",
        },
        "アダプティブナビゲーション": {
            "code": """ft.Column([
    ft.Text("アダプティブナビゲーション", size=30, weight=ft.FontWeight.BOLD),
    ft.Text("画面幅: {width}px、高さ: {height}px"),
    ft.Row([
        # サイドナビゲーション (デスクトップ向け)
        ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(icon=ft.icons.HOME_OUTLINED, label="ホーム"),
                ft.NavigationRailDestination(icon=ft.icons.SEARCH_OUTLINED, label="検索"),
                ft.NavigationRailDestination(icon=ft.icons.SETTINGS_OUTLINED, label="設定")
            ],
        ),
        ft.VerticalDivider(width=1),
        # メインコンテンツ
        ft.Column([
            ft.Container(
                content=ft.Text("メインコンテンツエリア"),
                bgcolor=ft.colors.SURFACE_VARIANT,
                padding=20,
                border_radius=10,
                expand=True,
                alignment=ft.alignment.center
            )
        ], expand=True)
    ], expand=True),
    # ボトムナビゲーション (モバイル向け)
    ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.HOME_OUTLINED, label="ホーム"),
            ft.NavigationDestination(icon=ft.icons.SEARCH_OUTLINED, label="検索"),
            ft.NavigationDestination(icon=ft.icons.SETTINGS_OUTLINED, label="設定")
        ],
        selected_index=0
    )
])""",
            "responsive_rules": """# レスポンシブ対応ルール
if width < 600:  # モバイル向け
    side_nav.visible = False  # サイドナビを非表示
    nav_divider.visible = False  # 区切り線も非表示
    bottom_nav.visible = True  # ボトムナビを表示
else:  # デスクトップ向け
    side_nav.visible = True  # サイドナビを表示
    nav_divider.visible = True  # 区切り線も表示
    bottom_nav.visible = False  # ボトムナビを非表示""",
        },
        "グリッドレイアウト": {
            "code": """ft.Column([
    ft.Text("レスポンシブグリッドレイアウト", size=30, weight=ft.FontWeight.BOLD),
    ft.Text("画面幅: {width}px、高さ: {height}px"),
    ft.GridView(
        runs_count=runs_count,
        max_extent=150,
        child_aspect_ratio=1.0,
        spacing=10,
        run_spacing=10,
        controls=[
            ft.Container(
                content=ft.Text(f"アイテム {i}"),
                alignment=ft.alignment.center,
                bgcolor=ft.colors.BLUE_100,
                border_radius=10
            ) for i in range(1, 13)
        ],
        expand=True
    )
])""",
            "responsive_rules": """# レスポンシブ対応ルール
# 画面幅に基づいて列数を動的に調整
if width < 600:  # モバイル
    runs_count = 2
elif width < 1024:  # タブレット
    runs_count = 4
else:  # デスクトップ
    runs_count = 6""",
        },
    }

    # 現在のレイアウトとサイズ設定
    current_device = DEVICE_PRESETS[1]  # デフォルトはモバイル (標準)
    current_layout = list(sample_layouts.keys())[0]  # 最初のレイアウト
    is_portrait = True  # 縦向きがデフォルト
    custom_width = ft.TextField(value="375", width=100, label="幅 (px)")
    custom_height = ft.TextField(value="667", width=100, label="高さ (px)")

    # コード編集フィールド
    code_editor = ft.TextField(
        value=sample_layouts[current_layout]["code"],
        multiline=True,
        min_lines=10,
        max_lines=15,
        label="レイアウトコード",
        border=ft.InputBorder.OUTLINE,
    )

    # レスポンシブルール編集フィールド
    rules_editor = ft.TextField(
        value=sample_layouts[current_layout]["responsive_rules"],
        multiline=True,
        min_lines=5,
        max_lines=10,
        label="レスポンシブルール",
        border=ft.InputBorder.OUTLINE,
    )

    # プレビューコンテナ
    preview_container = ft.Container(
        content=ft.Container(
            content=ft.Text("プレビューを更新してください"),
            alignment=ft.alignment.center,
        ),
        bgcolor=ft.colors.BACKGROUND,
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=5,
        width=current_device["width"],
        height=current_device["height"],
        padding=10,
        alignment=ft.alignment.center,
        scale=0.8,  # プレビューエリアに収まるようにスケール
    )

    # プレビューエリア (スクロール可能なコンテナ内に配置)
    preview_area = ft.Container(
        content=ft.Column(
            [ft.Container(content=preview_container, alignment=ft.alignment.center)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True,
        padding=20,
        bgcolor=ft.colors.SURFACE_VARIANT,
        border_radius=10,
    )

    # デバイスプリセット選択ドロップダウン
    def on_device_changed(e):
        nonlocal current_device
        selected_device = next(
            (d for d in DEVICE_PRESETS if d["name"] == e.control.value),
            DEVICE_PRESETS[0],
        )
        current_device = selected_device

        # カスタムの場合は入力フィールドを有効に
        custom_width.disabled = selected_device["name"] != "カスタム"
        custom_height.disabled = selected_device["name"] != "カスタム"

        if selected_device["name"] != "カスタム":
            update_preview_size()

        page.update()

    device_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(device["name"]) for device in DEVICE_PRESETS],
        value=current_device["name"],
        on_change=on_device_changed,
        width=200,
    )

    # 向き切り替えボタン
    def toggle_orientation(e):
        nonlocal is_portrait
        is_portrait = not is_portrait
        update_preview_size()

    orientation_button = ft.IconButton(
        icon=ft.icons.SCREEN_ROTATION,
        tooltip="向きを切り替え",
        on_click=toggle_orientation,
    )

    # サンプルレイアウト選択ドロップダウン
    def on_layout_changed(e):
        nonlocal current_layout
        current_layout = e.control.value
        code_editor.value = sample_layouts[current_layout]["code"]
        rules_editor.value = sample_layouts[current_layout]["responsive_rules"]
        page.update()

    layout_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(layout) for layout in sample_layouts.keys()],
        value=current_layout,
        on_change=on_layout_changed,
        width=200,
    )

    # カスタムサイズ適用ボタン
    def apply_custom_size(e):
        try:
            width = int(custom_width.value)
            height = int(custom_height.value)
            if width > 0 and height > 0:
                current_device["width"] = width
                current_device["height"] = height
                update_preview_size()
        except ValueError:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("有効な数値を入力してください")
            )
            page.snack_bar.open = True
            page.update()

    custom_size_button = ft.ElevatedButton(
        text="サイズ適用", on_click=apply_custom_size
    )

    # プレビューサイズを更新する関数
    def update_preview_size():
        width = current_device["width"]
        height = current_device["height"]

        # 向きに応じて幅と高さを入れ替え
        if not is_portrait:
            width, height = height, width

        preview_container.width = width
        preview_container.height = height

        # スケールファクターを計算 (大きすぎる場合は縮小)
        available_width = page.window_width * 0.5  # 画面の半分の幅
        available_height = page.window_height * 0.6  # 画面の60%の高さ

        width_scale = min(1, available_width / width)
        height_scale = min(1, available_height / height)
        scale = min(width_scale, height_scale)

        preview_container.scale = max(
            0.3, scale * 0.9
        )  # 最低でも0.3、余裕を持って0.9倍

        # サイズ表示を更新
        update_preview()
        page.update()

    # プレビューを更新する関数
    def update_preview(e=None):
        width = preview_container.width
        height = preview_container.height

        try:
            # コードに現在のサイズを挿入
            layout_code = code_editor.value.format(width=width, height=height)

            # 変数を準備 (レスポンシブルールで使用)
            layout_vars = {
                "width": width,
                "height": height,
                "runs_count": 2,  # デフォルト値
            }

            # レスポンシブルールを評価
            if rules_editor.value:
                # ルールをコメント行から解析
                rule_lines = [
                    line.strip()
                    for line in rules_editor.value.split("\n")
                    if not line.strip().startswith("#")
                ]
                rule_code = "\n".join(rule_lines)

                # 安全に実行するため、限定された変数のみで評価
                exec(rule_code, {}, layout_vars)

            # Pythonコードをフレットコントロールに変換
            # 注意: 実際のアプリでは安全でないため、サンプルレイアウトの評価のみに限定
            control = eval(
                layout_code, {"ft": ft, "runs_count": layout_vars.get("runs_count", 2)}
            )

            preview_container.content = control

        except Exception as e:
            preview_container.content = ft.Text(f"エラー: {str(e)}", color="red")

        page.update()

    # プレビュー更新ボタン
    update_button = ft.ElevatedButton(
        text="プレビュー更新", icon=ft.icons.REFRESH, on_click=update_preview
    )

    # レイアウト
    page.add(
        ft.AppBar(
            title=ft.Text("Fletレスポンシブビジュアライザー"),
            center_title=True,
            bgcolor=ft.colors.SURFACE_VARIANT,
        ),
        ft.Row(
            [
                # 左側コントロールパネル
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("デバイス設定", weight=ft.FontWeight.BOLD, size=16),
                            ft.Row([device_dropdown, orientation_button]),
                            ft.Row([custom_width, custom_height, custom_size_button]),
                            ft.Divider(),
                            ft.Text(
                                "レイアウト設定", weight=ft.FontWeight.BOLD, size=16
                            ),
                            layout_dropdown,
                            code_editor,
                            ft.Text(
                                "レスポンシブルール", weight=ft.FontWeight.BOLD, size=16
                            ),
                            ft.Text(
                                "サイズに応じた調整ロジック (Python構文):", size=12
                            ),
                            rules_editor,
                            update_button,
                        ]
                    ),
                    width=450,
                    padding=20,
                    border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
                    border_radius=10,
                ),
                # 右側プレビューエリア
                preview_area,
            ],
            expand=True,
        ),
    )

    # 初期化
    custom_width.disabled = current_device["name"] != "カスタム"
    custom_height.disabled = current_device["name"] != "カスタム"
    update_preview_size()

    # ウィンドウサイズ変更時にプレビューサイズを調整
    def page_resize(e):
        update_preview_size()

    page.on_resize = page_resize


def apply_app_theme(page):
    """アプリにテーマを適用する"""
    page.theme = ft.Theme(
        color_scheme_seed=ft.colors.BLUE,
        use_material3=True,
    )

    # ダークモードの場合は背景色を調整
    if page.theme_mode == ft.ThemeMode.DARK:
        page.bgcolor = ft.colors.SURFACE_VARIANT

    page.update()


if __name__ == "__main__":
    ft.app(target=main)
