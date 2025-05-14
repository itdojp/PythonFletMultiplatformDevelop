"""Fletアプリケーションのエントリーポイント"""

import flet as ft

from .app import create_app


def main(page: ft.Page):
    """メイン関数"""
    app = create_app(page)
    page.add(app)


if __name__ == "__main__":
    ft.app(target=main) 