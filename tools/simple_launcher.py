# filepath: c:\work\PythonFletMultiplatformDevelopmentDocuments\tools\simple_launcher.py
import os
import sys

import flet as ft


def main(page: ft.Page):
    page.title = "Flet マルチプラットフォーム開発ツール"

    # シンプルツールリスト
    tools = [
        {
            "name": "シンプルテスト",
            "file": "simple_test.py",
            "description": "Fletの基本機能テスト",
        },
        {
            "name": "テンプレートジェネレータ(シンプル)",
            "file": "simple_template_generator.py",
            "description": "シンプルなテンプレート生成ツール",
        },
    ]

    def launch_tool(e, file_name):
        # シンプルなツール起動方法
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            tool_path = os.path.join(current_dir, file_name)

            # サブプロセスとして起動
            import subprocess

            subprocess.Popen([sys.executable, tool_path])

            page.snack_bar = ft.SnackBar(content=ft.Text(f"{file_name}を起動しました"))
            page.snack_bar.open = True
            page.update()
        except Exception as e:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"エラー: {str(e)}"))
            page.snack_bar.open = True
            page.update()

    # ツールカード生成
    tool_cards = []
    for tool in tools:
        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(tool["name"], size=20, weight="bold"),
                        ft.Text(tool["description"], size=14),
                        ft.ElevatedButton(
                            "起動",
                            on_click=lambda e, file=tool["file"]: launch_tool(e, file),
                        ),
                    ]
                ),
                padding=15,
            ),
            margin=10,
        )
        tool_cards.append(card)

    # レイアウト構築
    page.add(
        ft.Text("Fletマルチプラットフォーム開発ツール", size=30, weight="bold"),
        ft.Text("開発に役立つツール集", size=16),
        ft.Row(tool_cards, wrap=True),
    )


# Windowsアプリとして実行
if __name__ == "__main__":
    ft.app(target=main, view=None)
