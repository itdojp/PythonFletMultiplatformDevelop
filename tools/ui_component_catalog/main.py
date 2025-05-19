import json
import os
import platform
from pathlib import Path

import flet as ft
import pyperclip


def main(page: ft.Page):
    page.title = "Fletコンポーネントカタログ"
    page.theme_mode = ft.ThemeMode.SYSTEM

    # テーマ設定
    apply_app_theme(page)

    # コンポーネントデータの読み込み
    components_data = []
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(
            os.path.join(script_dir, "components.json"), "r", encoding="utf-8"
        ) as file:
            components_data = json.load(file)
    except Exception as e:
        print(f"コンポーネントデータの読み込みエラー: {e}")

    # カテゴリごとにコンポーネントを分類
    categorized_components = {}
    for component in components_data:
        category = component.get("category", "その他")
        if category not in categorized_components:
            categorized_components[category] = []
        categorized_components[category].append(component)

    # 検索フィールド
    search_field = ft.TextField(
        label="コンポーネントを検索",
        hint_text="名前またはプロパティで検索...",
        prefix_icon=ft.icons.SEARCH,
        on_change=lambda e: filter_components(e.control.value),
        expand=True,
    )

    # コンポーネント一覧を表示する関数
    def create_component_card(component):
        # コードをクリップボードにコピーする関数
        def copy_code_to_clipboard(e, code):
            pyperclip.copy(code)
            page.snack_bar = ft.SnackBar(
                content=ft.Text("コードをクリップボードにコピーしました"),
                action="閉じる",
            )
            page.snack_bar.open = True
            page.update()

        # プロパティリスト
        properties_chips = ft.Row(
            wrap=True,
            scroll="auto",
            controls=[ft.Chip(label=prop) for prop in component.get("properties", [])],
        )

        # コードサンプル
        code_sample = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("サンプルコード:", weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.icons.COPY,
                                tooltip="コードをコピー",
                                on_click=lambda e, c=component[
                                    "code"
                                ]: copy_code_to_clipboard(e, c),
                            ),
                        ]
                    ),
                    ft.Container(
                        content=ft.Text(component["code"], selectable=True),
                        bgcolor=ft.colors.BLACK,
                        padding=10,
                        border_radius=5,
                        color=ft.colors.WHITE,
                    ),
                ]
            ),
            padding=10,
        )

        # コンポーネントのプレビュー（一部のコンポーネントのみ）
        preview_container = ft.Container(
            content=ft.Text("プレビューは現在実装中です"), visible=False
        )

        # カードの作成
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text(
                                component["name"], size=20, weight=ft.FontWeight.BOLD
                            ),
                            subtitle=ft.Text(component["description"]),
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("プロパティ:", weight=ft.FontWeight.BOLD),
                                    properties_chips,
                                ]
                            ),
                            padding=ft.padding.only(left=15, right=15, bottom=10),
                        ),
                        code_sample,
                        preview_container,
                    ]
                ),
                width=600,
                padding=15,
            ),
            elevation=3,
            margin=10,
        )

    # コンポーネント表示用のコンテナ
    components_view = ft.Column(scroll="auto", spacing=10)

    # タブの作成
    tabs = []
    tab_content = {}

    # カテゴリごとにタブを作成
    for category, components in categorized_components.items():
        # カテゴリ内のコンポーネントカードのリスト
        component_cards = ft.Column(
            controls=[create_component_card(component) for component in components],
            scroll="auto",
            spacing=10,
        )

        # タブを作成
        tab = ft.Tab(text=category, content=component_cards)
        tabs.append(tab)
        tab_content[category] = component_cards

    # すべてのタブを含むTabsコントロール
    categories_tabs = ft.Tabs(
        selected_index=0, animation_duration=300, tabs=tabs, expand=True
    )

    # コンポーネント検索フィルタリング関数
    def filter_components(search_text):
        if not search_text:
            # 検索テキストがない場合は全て表示
            categories_tabs.visible = True
            components_view.visible = False
            page.update()
            return

        # 検索テキストがある場合は検索結果のみ表示
        categories_tabs.visible = False
        components_view.visible = True

        # コンポーネントをフィルタリング
        components_view.controls.clear()
        search_text = search_text.lower()

        for component in components_data:
            # 名前、説明、プロパティで検索
            if (
                search_text in component["name"].lower()
                or search_text in component["description"].lower()
                or any(
                    search_text in prop.lower()
                    for prop in component.get("properties", [])
                )
            ):
                components_view.controls.append(create_component_card(component))

        page.update()

    # ヘッダー
    header = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Fletコンポーネントカタログ",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.PRIMARY,
                        ),
                        ft.Spacer(),
                        ft.Row(
                            [
                                ft.Icon(ft.icons.WEB_ASSET),
                                ft.Text("Flet バージョン: 0.13.0", italic=True),
                            ]
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    "Fletで利用可能なUIコンポーネントとそのサンプルコード集", size=16
                ),
            ]
        ),
        padding=10,
        margin=ft.margin.only(bottom=10),
    )

    # ページのメインレイアウト
    page.add(
        ft.AppBar(
            title=ft.Text("Fletコンポーネントカタログ"),
            center_title=True,
            bgcolor=ft.colors.SURFACE_VARIANT,
        ),
        ft.Container(
            content=ft.Column(
                [
                    header,
                    search_field,
                    ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
                    ft.Container(height=20),
                    ft.Container(content=categories_tabs, expand=True),
                    components_view,
                ]
            ),
            expand=True,
            padding=20,
        ),
    )

    # 初期状態設定
    components_view.visible = False
    page.update()


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
