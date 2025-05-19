import json
import os
import re
from pathlib import Path

import flet as ft


# ユーティリティ関数: スネークケース変換
def snake_case(s):
    # スペースと特殊文字を削除
    s = re.sub(r"[^\w\s]", "", s)
    # キャメルケースをスネークケースに変換
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    # スペースをアンダースコアに置換し、小文字に変換
    return re.sub(r"\s+", "_", s).lower()


# テーマを設定
def apply_app_theme(page):
    page.theme = ft.Theme(
        color_scheme_seed="blue",
    )
    page.update()


# テンプレート変数の置換
def replace_template_vars(content, vars):
    for key, value in vars.items():
        content = content.replace("{{" + key + "}}", value)
    return content


# テンプレート定義の読み込み
def load_template_definitions():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    templates_path = os.path.join(current_dir, "template_definitions.json")

    try:
        with open(templates_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"テンプレート定義の読み込みエラー: {e}")
        # エラー時はダミーデータを返す
        return {
            "project_templates": [],
            "component_templates": [],
            "screen_templates": [],
        }


def main(page: ft.Page):
    page.title = "Flet テンプレートジェネレーター"
    page.theme_mode = ft.ThemeMode.SYSTEM

    # テーマ設定
    apply_app_theme(page)

    # 選択されたテンプレート情報
    selected_template = None
    selected_template_type = None
    selected_template_info = ft.Text()

    # カスタマイズオプションのコンテナ
    customize_container = ft.Container(
        content=ft.Column([ft.Text("テンプレートを選択してください", italic=True)]),
        padding=10,
        visible=False,
        border=ft.border.all(1, ft.colors.BLACK12),
        border_radius=10,
    )

    # テンプレート定義の読み込み
    templates = load_template_definitions()

    # 作業ディレクトリ
    working_dir = ft.TextField(
        label="出力ディレクトリ",
        value=os.path.expanduser("~"),
        width=500,
        hint_text="テンプレートファイルを生成するディレクトリ",
    )

    def select_dir(_):
        def result_handler(e: ft.FilePickerResultEvent):
            if e.path:
                working_dir.value = e.path
                page.update()

        file_picker = ft.FilePicker(on_result=result_handler)
        page.overlay.append(file_picker)
        page.update()
        file_picker.get_directory_path()

    browse_button = ft.ElevatedButton("参照", on_click=select_dir, icon="folder_open")

    # プロジェクト名
    project_name = ft.TextField(
        label="プロジェクト名", width=300, hint_text="作成するプロジェクト名"
    )

    # プロジェクト説明
    project_description = ft.TextField(
        label="プロジェクト説明",
        width=500,
        multiline=True,
        hint_text="プロジェクトの簡単な説明",
    )
    # テンプレートタイプのタブ切り替え
    template_tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="プロジェクトテンプレート",
                icon="folder_outlined",
                content=ft.Container(
                    content=create_project_templates_view(
                        templates["project_templates"]
                    ),
                    padding=10,
                ),
            ),
            ft.Tab(
                text="コンポーネントテンプレート",
                icon="widgets_outlined",
                content=ft.Container(
                    content=create_component_templates_view(
                        templates["component_templates"]
                    ),
                    padding=10,
                ),
            ),
            ft.Tab(
                text="画面テンプレート",
                icon="pages_outlined",
                content=ft.Container(
                    content=create_screen_templates_view(templates["screen_templates"]),
                    padding=10,
                ),
            ),
        ],
        expand=1,
    )

    # 選択されたテンプレート情報
    selected_template = None
    selected_template_type = None
    selected_template_info = ft.Text()

    # カスタマイズオプションのコンテナ
    customize_container = ft.Container(
        content=ft.Column([ft.Text("テンプレートを選択してください", italic=True)]),
        padding=10,
        visible=False,
        border=ft.border.all(1, ft.colors.BLACK12),
        border_radius=10,
    )

    # プロジェクトテンプレートビューの作成
    def create_project_templates_view(templates):
        template_cards = []

        for template in templates:
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                template["name"], size=16, weight=ft.FontWeight.BOLD
                            ),
                            ft.Text(
                                template["description"],
                                size=12,
                                color=ft.colors.BLACK54,
                            ),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "選択",
                                        on_click=lambda _, t=template: select_project_template(
                                            t
                                        ),
                                    )
                                ]
                            ),
                        ]
                    ),
                    padding=10,
                ),
                margin=5,
            )
            template_cards.append(card)

        return ft.Column(
            [
                ft.Text("プロジェクトテンプレートを選択", size=20),
                ft.Divider(),
                ft.ResponsiveRow(
                    [
                        ft.Column([card], col={"sm": 6, "md": 4, "xl": 3})
                        for card in template_cards
                    ]
                ),
            ]
        )

    # コンポーネントテンプレートビューの作成
    def create_component_templates_view(templates):
        template_cards = []

        for template in templates:
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                template["name"], size=16, weight=ft.FontWeight.BOLD
                            ),
                            ft.Text(
                                template["description"],
                                size=12,
                                color=ft.colors.BLACK54,
                            ),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "選択",
                                        on_click=lambda _, t=template: select_component_template(
                                            t
                                        ),
                                    )
                                ]
                            ),
                        ]
                    ),
                    padding=10,
                ),
                margin=5,
            )
            template_cards.append(card)

        return ft.Column(
            [
                ft.Text("コンポーネントテンプレートを選択", size=20),
                ft.Divider(),
                ft.ResponsiveRow(
                    [
                        ft.Column([card], col={"sm": 6, "md": 4, "xl": 3})
                        for card in template_cards
                    ]
                ),
            ]
        )

    # 画面テンプレートビューの作成
    def create_screen_templates_view(templates):
        template_cards = []

        for template in templates:
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                template["name"], size=16, weight=ft.FontWeight.BOLD
                            ),
                            ft.Text(
                                template["description"],
                                size=12,
                                color=ft.colors.BLACK54,
                            ),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "選択",
                                        on_click=lambda _, t=template: select_screen_template(
                                            t
                                        ),
                                    )
                                ]
                            ),
                        ]
                    ),
                    padding=10,
                ),
                margin=5,
            )
            template_cards.append(card)

        return ft.Column(
            [
                ft.Text("画面テンプレートを選択", size=20),
                ft.Divider(),
                ft.ResponsiveRow(
                    [
                        ft.Column([card], col={"sm": 6, "md": 4, "xl": 3})
                        for card in template_cards
                    ]
                ),
            ]
        )

    # プロジェクトテンプレートの選択
    def select_project_template(template):
        nonlocal selected_template, selected_template_type
        selected_template = template
        selected_template_type = "project"

        selected_template_info.value = (
            f"選択されたテンプレート: {template['name']}\n{template['description']}"
        )
        customize_container.visible = True

        update_customize_options("project", template)
        page.update()

    # コンポーネントテンプレートの選択
    def select_component_template(template):
        nonlocal selected_template, selected_template_type
        selected_template = template
        selected_template_type = "component"

        selected_template_info.value = (
            f"選択されたテンプレート: {template['name']}\n{template['description']}"
        )
        customize_container.visible = True

        update_customize_options("component", template)
        page.update()

    # 画面テンプレートの選択
    def select_screen_template(template):
        nonlocal selected_template, selected_template_type
        selected_template = template
        selected_template_type = "screen"

        selected_template_info.value = (
            f"選択されたテンプレート: {template['name']}\n{template['description']}"
        )
        customize_container.visible = True

        update_customize_options("screen", template)
        page.update()

    # カスタマイズオプションの更新
    def update_customize_options(template_type, template):
        customize_container.content.controls.clear()

        if template_type == "project":
            # プロジェクト名の入力欄
            customize_container.content.controls.append(
                ft.Column(
                    [
                        ft.Text(
                            "プロジェクトカスタマイズ",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Divider(),
                        ft.Text("プロジェクト名とディレクトリ名は必須です", size=12),
                        project_name,
                        project_description,
                        ft.CheckboxGroup(
                            options=[
                                ft.CheckboxOption("README.mdを作成", value=True),
                                ft.CheckboxOption("requirements.txtを作成", value=True),
                                ft.CheckboxOption("ディレクトリ構造を維持", value=True),
                            ]
                        ),
                    ]
                )
            )
        elif template_type == "component":
            # コンポーネント名の入力欄
            component_name = ft.TextField(
                label="コンポーネント名",
                width=300,
                hint_text="作成するコンポーネント名（PascalCase推奨）",
            )

            output_path = ft.TextField(
                label="出力パス",
                width=500,
                hint_text="components/custom/ など、相対パスを入力",
            )

            customize_container.content.controls.append(
                ft.Column(
                    [
                        ft.Text(
                            "コンポーネントカスタマイズ",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Divider(),
                        component_name,
                        output_path,
                    ]
                )
            )
        elif template_type == "screen":
            # 画面名の入力欄
            screen_name = ft.TextField(
                label="画面名", width=300, hint_text="作成する画面名（PascalCase推奨）"
            )

            output_path = ft.TextField(
                label="出力パス", width=500, hint_text="views/ など、相対パスを入力"
            )

            customize_container.content.controls.append(
                ft.Column(
                    [
                        ft.Text("画面カスタマイズ", size=16, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        screen_name,
                        output_path,
                    ]
                )
            )

    # テンプレート生成ボタン
    generate_button = ft.ElevatedButton(
        "テンプレート生成", icon="create", on_click=lambda _: generate_template()
    )

    # テンプレート生成処理
    def generate_template():
        if not selected_template:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("テンプレートを選択してください"), action="閉じる"
            )
            page.snack_bar.open = True
            page.update()
            return

        if not working_dir.value or not os.path.isdir(working_dir.value):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("有効な出力ディレクトリを選択してください"),
                action="閉じる",
            )
            page.snack_bar.open = True
            page.update()
            return

        if selected_template_type == "project":
            generate_project_template()
        elif selected_template_type == "component":
            generate_component_template()
        elif selected_template_type == "screen":
            generate_screen_template()

    # プロジェクトテンプレート生成
    def generate_project_template():
        if not project_name.value:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("プロジェクト名を入力してください"), action="閉じる"
            )
            page.snack_bar.open = True
            page.update()
            return

        # プロジェクトディレクトリのパス
        project_dir = os.path.join(working_dir.value, project_name.value)

        # ディレクトリが既に存在するか確認
        if os.path.exists(project_dir):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"ディレクトリ {project_dir} は既に存在します"),
                action="閉じる",
            )
            page.snack_bar.open = True
            page.update()
            return

        # プロジェクトディレクトリを作成
        os.makedirs(project_dir, exist_ok=True)

        # テンプレート変数
        template_vars = {
            "app_name": project_name.value,
            "app_description": project_description.value
            or "Fletを使用したアプリケーション",
        }

        # ファイルを生成
        for file_info in selected_template["structure"]:
            file_path = os.path.join(project_dir, file_info["path"])

            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # テンプレート変数を置換
            content = replace_template_vars(file_info["content"], template_vars)

            # ファイルに書き込み
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"プロジェクトテンプレートが生成されました: {project_dir}"),
            action="閉じる",
        )
        page.snack_bar.open = True
        page.update()

    # コンポーネントテンプレート生成
    def generate_component_template():
        component_name = customize_container.content.controls[0].controls[2].value
        output_path = customize_container.content.controls[0].controls[3].value

        if not component_name:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("コンポーネント名を入力してください"), action="閉じる"
            )
            page.snack_bar.open = True
            page.update()
            return

        # 出力ディレクトリ
        if output_path:
            output_dir = os.path.join(working_dir.value, output_path)
        else:
            output_dir = os.path.join(working_dir.value, "components")

        # ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)

        # ファイル名（スネークケース）
        file_name = snake_case(component_name) + ".py"
        file_path = os.path.join(output_dir, file_name)

        # テンプレート変数
        template_vars = {
            "component_name": component_name,
            "component_description": selected_template["description"],
        }

        # テンプレート変数を置換
        content = replace_template_vars(selected_template["content"], template_vars)

        # クラス名を置換（カスタマイズによる名前変更）
        class_pattern = r"class\s+\w+"
        content = re.sub(class_pattern, f"class {component_name}", content)

        # ファイルに書き込み
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"コンポーネントテンプレートが生成されました: {file_path}"),
            action="閉じる",
        )
        page.snack_bar.open = True
        page.update()

    # 画面テンプレート生成
    def generate_screen_template():
        screen_name = customize_container.content.controls[0].controls[2].value
        output_path = customize_container.content.controls[0].controls[3].value

        if not screen_name:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("画面名を入力してください"), action="閉じる"
            )
            page.snack_bar.open = True
            page.update()
            return

        # 出力ディレクトリ
        if output_path:
            output_dir = os.path.join(working_dir.value, output_path)
        else:
            output_dir = os.path.join(working_dir.value, "views")

        # ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)

        # ファイル名（スネークケース）
        file_name = snake_case(screen_name) + ".py"
        file_path = os.path.join(output_dir, file_name)

        # テンプレート変数
        template_vars = {
            "screen_name": screen_name,
            "screen_description": selected_template["description"],
        }

        # テンプレート変数を置換
        content = replace_template_vars(selected_template["content"], template_vars)

        # クラス名を置換（カスタマイズによる名前変更）
        class_pattern = r"class\s+\w+"
        content = re.sub(class_pattern, f"class {screen_name}", content)

        # ファイルに書き込み
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"画面テンプレートが生成されました: {file_path}"),
            action="閉じる",
        )
        page.snack_bar.open = True
        page.update()

    # レイアウト構築
    page.add(
        ft.Text("Flet テンプレートジェネレーター", size=30, weight=ft.FontWeight.BOLD),
        ft.Row([working_dir, browse_button]),
        template_tabs,
        selected_template_info,
        customize_container,
        generate_button,
    )


if __name__ == "__main__":
    # ブラウザで実行（デバッグ用）
    ft.app(target=main, view=ft.WEB_BROWSER)
