import importlib.util
import os
import sys
from pathlib import Path

import flet as ft


def main(page: ft.Page):
    page.title = "Flet マルチプラットフォーム開発ツール"
    page.theme_mode = ft.ThemeMode.SYSTEM

    # テーマ設定
    apply_app_theme(page)
    # ロゴとタイトル
    header = ft.Row(
        [
            ft.Container(
                content=ft.Text("F", size=40, weight=ft.FontWeight.BOLD),
                bgcolor="#E3F2FD",  # 薄い青色
                width=60,
                height=60,
                border_radius=30,
                alignment=ft.alignment.center,
            ),
            ft.Text(
                "Flet マルチプラットフォーム開発ツール",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )  # 利用可能なツールリスト
    tools_list = [
        {
            "name": "プラットフォーム別機能実装ヘルパー",
            "description": "各プラットフォーム（Android、iOS、Web、デスクトップ）向けの最適化されたUIコードを生成",
            "icon": "devices",
            "module_path": "platform_helper.main",
        },
        {
            "name": "デプロイメントチェックリスト生成ツール",
            "description": "各プラットフォーム向けのデプロイ前チェックリストを生成",
            "icon": "checklist",
            "module_path": "deployment_checklist.main",
        },
        {
            "name": "UIコンポーネントカタログ",
            "description": "Fletで利用可能な主要UIコンポーネントのサンプルコードとプロパティ集",
            "icon": "widgets",
            "module_path": "ui_component_catalog.main",
        },
        {
            "name": "レスポンシブビジュアライザー",
            "description": "異なる画面サイズでのレイアウト表示をプレビュー",
            "icon": "responsive",
            "module_path": "responsive_visualizer.main",
        },
    ]  # ツールを起動する関数

    def launch_tool(e, tool_info):
        # 新しいウィンドウでツールを起動
        module_path = tool_info["module_path"]
        try:
            # モジュールのフルパスを取得
            base_dir = os.path.dirname(os.path.abspath(__file__))

            print(f"Starting tool: {tool_info['name']}")
            # 開始処理を表示
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"{tool_info['name']}を起動中...")
            )
            page.snack_bar.open = True
            page.update()

            # プラットフォームに応じたコマンド実行
            module_path_str = os.path.join(base_dir, module_path.replace(".", os.sep))
            if os.name == "nt":  # Windows
                os.system(f'start cmd /c "python {module_path_str}.py && pause"')
            else:
                # Linux/Mac用のコマンド
                os.system(f"python3 {module_path_str}.py &")

        except Exception as ex:
            print(f"Error launching tool: {ex}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"ツール起動エラー: {str(ex)}")
            )
            page.snack_bar.open = True
            page.update()

    # ツールカードのリスト
    tools_cards = []
    for tool in tools_list:
        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(tool["icon"]),
                            title=ft.Text(tool["name"], weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(tool["description"]),
                        ),
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.ElevatedButton(
                                        text="起動",
                                        icon="launch",
                                        on_click=lambda e, t=tool: launch_tool(e, t),
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                            padding=ft.padding.only(right=10, bottom=10),
                        ),
                    ]
                ),
                width=550,
                padding=10,
            ),
            elevation=4,
        )
        tools_cards.append(card)

    # レイアウト
    page.add(
        ft.AppBar(
            title=ft.Text("Flet マルチプラットフォーム開発ツール"), center_title=True
        ),
        ft.Container(
            content=ft.Column(
                [
                    header,
                    ft.Container(height=20),
                    ft.Text("利用可能なツール", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "以下のツールからプロジェクト開発に必要なものを選択してください"
                    ),
                    ft.Container(height=10),
                    ft.Column(tools_cards, spacing=10),
                ]
            ),
            padding=20,
        ),
    )


def apply_app_theme(page: ft.Page):
    # 最新のFlet APIを使用してテーマを設定
    page.theme = ft.Theme(
        color_scheme_seed="blue",
        use_material3=True,
    )
    page.dark_theme = ft.Theme(
        color_scheme_seed="blue",
        use_material3=True,
    )


if __name__ == "__main__":
    ft.app(target=main)
