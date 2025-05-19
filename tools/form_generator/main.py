import datetime
import inspect
import json
import os
import re
from pathlib import Path

import flet as ft


def main(page: ft.Page):
    page.title = "Flet フォームジェネレーター"
    page.theme_mode = ft.ThemeMode.SYSTEM

    # テーマ設定
    apply_app_theme(page)

    # 作業ディレクトリ
    working_dir = ft.TextField(
        label="プロジェクトディレクトリ",
        value=os.path.expanduser("~"),
        width=500,
        hint_text="フォームコードを生成するプロジェクトディレクトリ",
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

    browse_button = ft.ElevatedButton(
        "参照", on_click=select_dir, icon=ft.icons.FOLDER_OPEN
    )

    # フォームフィールド定義の読み込み
    form_fields = load_form_fields()

    # フォームテンプレートの読み込み
    form_templates = load_form_templates()

    # メイン操作タブ
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="テンプレート",
                icon=ft.icons.TEMPLATE_OUTLINED,
                content=ft.Container(
                    content=create_templates_view(form_templates), padding=10
                ),
            ),
            ft.Tab(
                text="カスタムフォーム",
                icon=ft.icons.CREATE_OUTLINED,
                content=ft.Container(
                    content=create_custom_form_builder(form_fields), padding=10
                ),
            ),
            ft.Tab(
                text="フォーム設定",
                icon=ft.icons.SETTINGS_OUTLINED,
                content=ft.Container(content=create_form_settings_view(), padding=10),
            ),
            ft.Tab(
                text="プレビュー",
                icon=ft.icons.VISIBILITY_OUTLINED,
                content=ft.Container(content=create_preview_view(), padding=10),
            ),
        ],
        expand=1,
    )

    # フォーム名とファイル名の設定
    form_name = ft.TextField(
        label="フォーム名",
        value="MyForm",
        width=300,
        hint_text="生成するフォームクラス名",
    )

    output_file = ft.TextField(
        label="出力ファイル名",
        width=300,
        hint_text="生成コードの出力ファイル名（.pyは自動追加）",
    )

    def update_output_file(_):
        if form_name.value:
            output_file.value = snake_case(form_name.value)
            page.update()

    form_name.on_change = update_output_file

    # コード生成ボタン
    generate_button = ft.ElevatedButton(
        "フォームコード生成",
        icon=ft.icons.CODE,
        on_click=lambda _: generate_form_code(),
    )

    # 選択されたテンプレート
    selected_template = None

    # カスタムフォームのフィールド
    custom_form_fields = []

    # フォームスタイル設定
    form_settings = {
        "layout": "column",
        "spacing": 10,
        "padding": 20,
        "submit_text": "送信",
        "cancel_text": "キャンセル",
        "show_cancel": True,
        "validation_mode": "onSubmit",
        "responsive": True,
    }

    # プレビュー用のコンテナ
    preview_container = ft.Container(
        content=ft.Text(
            "フォームを選択または作成すると、ここにプレビューが表示されます。"
        ),
        padding=20,
        border=ft.border.all(1, ft.colors.BLACK12),
        border_radius=10,
        bgcolor=ft.colors.BLACK3,
        width=600,
        height=400,
    )

    # テンプレートビューの作成
    def create_templates_view(templates):
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
                                f"フィールド数: {len(template['fields'])}",
                                size=12,
                                color=ft.colors.BLACK54,
                            ),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "選択",
                                        on_click=lambda _, t=template: select_template(
                                            t
                                        ),
                                    ),
                                    ft.OutlinedButton(
                                        "プレビュー",
                                        on_click=lambda _, t=template: preview_template(
                                            t
                                        ),
                                    ),
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
                ft.Text("テンプレートを選択", size=20),
                ft.Divider(),
                ft.ResponsiveRow(
                    [
                        ft.Column([card], col={"sm": 6, "md": 4, "xl": 3})
                        for card in template_cards
                    ]
                ),
            ]
        )

    # カスタムフォームビルダーの作成
    def create_custom_form_builder(field_definitions):
        field_types = [field["type"] for field in field_definitions]
        field_type_dropdown = ft.Dropdown(
            label="フィールドタイプ",
            options=[ft.dropdown.Option(t) for t in field_types],
            width=200,
        )

        field_name = ft.TextField(
            label="フィールド名", width=200, hint_text="例: username"
        )

        field_label = ft.TextField(
            label="ラベル", width=200, hint_text="例: ユーザー名"
        )

        field_required = ft.Checkbox(label="必須フィールド")

        add_field_button = ft.ElevatedButton(
            "フィールド追加",
            icon=ft.icons.ADD,
            on_click=lambda _: add_custom_field(
                field_type_dropdown.value,
                field_name.value,
                field_label.value,
                field_required.value,
            ),
        )

        custom_fields_list = ft.ListView(spacing=2, height=300, width=500)

        return ft.Column(
            [
                ft.Text("カスタムフォーム作成", size=20),
                ft.Divider(),
                ft.Row([field_type_dropdown, field_name, field_label]),
                field_required,
                add_field_button,
                ft.Text("追加されたフィールド", size=16),
                custom_fields_list,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "プレビュー",
                            icon=ft.icons.VISIBILITY,
                            on_click=lambda _: preview_custom_form(),
                        ),
                        ft.FilledTonalButton(
                            "クリア",
                            icon=ft.icons.CLEAR_ALL,
                            on_click=lambda _: clear_custom_fields(),
                        ),
                    ]
                ),
            ]
        )

    # フォーム設定ビューの作成
    def create_form_settings_view():
        layout_options = ft.RadioGroup(
            content=ft.Row(
                [
                    ft.Radio(value="column", label="縦並び"),
                    ft.Radio(value="row_wrap", label="横並び（折り返し）"),
                ]
            ),
            value=form_settings["layout"],
        )

        spacing_slider = ft.Slider(
            min=0,
            max=50,
            divisions=10,
            value=form_settings["spacing"],
            label="{value}px",
        )

        padding_slider = ft.Slider(
            min=0,
            max=50,
            divisions=10,
            value=form_settings["padding"],
            label="{value}px",
        )

        submit_text = ft.TextField(
            label="送信ボタンテキスト", value=form_settings["submit_text"]
        )

        cancel_text = ft.TextField(
            label="キャンセルボタンテキスト", value=form_settings["cancel_text"]
        )

        show_cancel = ft.Checkbox(
            label="キャンセルボタンを表示", value=form_settings["show_cancel"]
        )

        validation_mode = ft.Dropdown(
            label="バリデーションモード",
            options=[
                ft.dropdown.Option("onSubmit", "送信時のみ"),
                ft.dropdown.Option("onChange", "値変更時"),
                ft.dropdown.Option("onBlur", "フォーカス喪失時"),
            ],
            value=form_settings["validation_mode"],
        )

        responsive = ft.Checkbox(
            label="レスポンシブレイアウト", value=form_settings["responsive"]
        )

        def update_settings(_):
            form_settings["layout"] = layout_options.value
            form_settings["spacing"] = spacing_slider.value
            form_settings["padding"] = padding_slider.value
            form_settings["submit_text"] = submit_text.value
            form_settings["cancel_text"] = cancel_text.value
            form_settings["show_cancel"] = show_cancel.value
            form_settings["validation_mode"] = validation_mode.value
            form_settings["responsive"] = responsive.value

            # 設定を反映してプレビュー更新
            if selected_template:
                preview_template(selected_template)
            elif custom_form_fields:
                preview_custom_form()

        layout_options.on_change = update_settings
        spacing_slider.on_change = update_settings
        padding_slider.on_change = update_settings
        submit_text.on_change = update_settings
        cancel_text.on_change = update_settings
        show_cancel.on_change = update_settings
        validation_mode.on_change = update_settings
        responsive.on_change = update_settings

        return ft.Column(
            [
                ft.Text("フォーム設定", size=20),
                ft.Divider(),
                ft.Text("レイアウト"),
                layout_options,
                ft.Text("間隔"),
                spacing_slider,
                ft.Text("内側の余白"),
                padding_slider,
                ft.Row([submit_text, cancel_text]),
                show_cancel,
                validation_mode,
                responsive,
                ft.ElevatedButton("設定を適用", on_click=update_settings),
            ]
        )

    # プレビュービューの作成
    def create_preview_view():
        return ft.Column(
            [ft.Text("フォームプレビュー", size=20), ft.Divider(), preview_container]
        )

    # テンプレートの選択
    def select_template(template):
        nonlocal selected_template
        selected_template = template

        # フォーム名を更新
        form_name.value = pascal_case(template["name"])
        update_output_file(None)

        # プレビュー更新
        preview_template(template)

        # タブをプレビューに切り替え
        tabs.selected_index = 3
        page.update()

        # 成功メッセージ
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"テンプレート「{template['name']}」が選択されました"),
            action="閉じる",
        )
        page.snack_bar.open = True
        page.update()

    # テンプレートのプレビュー
    def preview_template(template):
        form_controls = create_form_preview_controls(template["fields"])

        preview_form = ft.Column(
            controls=[
                ft.Text(template["name"], size=20, weight=ft.FontWeight.BOLD),
                ft.Text("フォームプレビュー", size=14, color=ft.colors.BLACK54),
                create_form_layout(form_controls),
                ft.Row(
                    [
                        ft.ElevatedButton(form_settings["submit_text"]),
                        ft.OutlinedButton(
                            form_settings["cancel_text"],
                            visible=form_settings["show_cancel"],
                        ),
                    ]
                ),
            ],
            spacing=10,
        )

        preview_container.content = preview_form
        page.update()

    # カスタムフィールドの追加
    def add_custom_field(field_type, name, label, required):
        if not field_type or not name or not label:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("フィールドタイプ、フィールド名、ラベルは必須です"),
                action="閉じる",
            )
            page.snack_bar.open = True
            page.update()
            return

        # フィールド定義を検索
        field_def = next((f for f in form_fields if f["type"] == field_type), None)
        if not field_def:
            return

        # フィールド追加
        new_field = {
            "type": field_type,
            "name": snake_case(name),
            "label": label,
            "required": required,
            "validators": ["required"] if required else [],
        }

        custom_form_fields.append(new_field)
        update_custom_fields_list()

        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"フィールド「{label}」が追加されました"), action="閉じる"
        )
        page.snack_bar.open = True
        page.update()

    # カスタムフィールドリストの更新
    def update_custom_fields_list():
        custom_fields_list = tabs.tabs[1].content.content.controls[6]
        custom_fields_list.controls.clear()

        for i, field in enumerate(custom_form_fields):
            field_item = ft.Row(
                [
                    ft.Text(f"{i+1}. {field['label']} ({field['type']})", width=300),
                    ft.Text("必須" if field.get("required") else "任意", width=60),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        tooltip="削除",
                        on_click=lambda _, idx=i: remove_custom_field(idx),
                    ),
                ]
            )
            custom_fields_list.controls.append(field_item)

        page.update()

    # カスタムフィールドの削除
    def remove_custom_field(index):
        if 0 <= index < len(custom_form_fields):
            removed = custom_form_fields.pop(index)
            update_custom_fields_list()

            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"フィールド「{removed['label']}」が削除されました"),
                action="閉じる",
            )
            page.snack_bar.open = True
            page.update()

    # カスタムフィールドのクリア
    def clear_custom_fields():
        custom_form_fields.clear()
        update_custom_fields_list()

        page.snack_bar = ft.SnackBar(
            content=ft.Text("すべてのフィールドがクリアされました"), action="閉じる"
        )
        page.snack_bar.open = True
        page.update()

    # カスタムフォームのプレビュー
    def preview_custom_form():
        if not custom_form_fields:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("フォームにフィールドが追加されていません"),
                action="閉じる",
            )
            page.snack_bar.open = True
            page.update()
            return

        form_controls = create_form_preview_controls(custom_form_fields)

        preview_form = ft.Column(
            controls=[
                ft.Text("カスタムフォーム", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("フォームプレビュー", size=14, color=ft.colors.BLACK54),
                create_form_layout(form_controls),
                ft.Row(
                    [
                        ft.ElevatedButton(form_settings["submit_text"]),
                        ft.OutlinedButton(
                            form_settings["cancel_text"],
                            visible=form_settings["show_cancel"],
                        ),
                    ]
                ),
            ],
            spacing=10,
        )

        preview_container.content = preview_form

        # タブをプレビューに切り替え
        tabs.selected_index = 3
        page.update()

    # フォームプレビューコントロールの生成
    def create_form_preview_controls(fields):
        controls = []

        for field in fields:
            field_type = field["type"]
            label = field.get("label", "")

            if field_type == "text":
                control = ft.TextField(
                    label=label,
                    hint_text=field.get("hint_text", ""),
                    password=field.get("password", False),
                    multiline=field.get("multiline", False),
                )

            elif field_type == "dropdown":
                options = []
                for option in field.get("options", []):
                    if isinstance(option, dict):
                        options.append(
                            ft.dropdown.Option(option["value"], option["text"])
                        )
                    else:
                        options.append(ft.dropdown.Option(option))

                control = ft.Dropdown(
                    label=label, options=options, hint_text=field.get("hint_text", "")
                )

            elif field_type == "checkbox":
                control = ft.Checkbox(label=label, value=field.get("value", False))

            elif field_type == "radio":
                control = ft.RadioGroup(
                    content=ft.Column(
                        [
                            ft.Radio(value="option1", label="オプション1"),
                            ft.Radio(value="option2", label="オプション2"),
                            ft.Radio(value="option3", label="オプション3"),
                        ]
                    )
                )

            elif field_type == "switch":
                control = ft.Switch(label=label, value=field.get("value", False))

            elif field_type == "slider":
                control = ft.Column(
                    [
                        ft.Text(label),
                        ft.Slider(
                            min=field.get("min", 0),
                            max=field.get("max", 100),
                            divisions=field.get("divisions", 10),
                            value=field.get("value", 50),
                            label="{value}",
                        ),
                    ]
                )

            elif field_type == "date":
                control = ft.Column(
                    [
                        ft.Text(label),
                        ft.ElevatedButton("日付を選択", icon=ft.icons.CALENDAR_TODAY),
                    ]
                )

            elif field_type == "time":
                control = ft.Column(
                    [
                        ft.Text(label),
                        ft.ElevatedButton("時刻を選択", icon=ft.icons.ACCESS_TIME),
                    ]
                )

            elif field_type == "file":
                control = ft.Column(
                    [
                        ft.Text(label),
                        ft.ElevatedButton("ファイルを選択", icon=ft.icons.UPLOAD_FILE),
                    ]
                )

            else:
                # 不明なフィールドタイプの場合はテキストフィールドとして表示
                control = ft.TextField(label=label)

            controls.append(control)

        return controls

    # 選択されたレイアウトに基づいてフォームコントロールを配置
    def create_form_layout(controls):
        if form_settings["layout"] == "column":
            return ft.Column(
                controls=controls, spacing=form_settings["spacing"], width=500
            )
        else:  # row_wrap
            if form_settings["responsive"]:
                rows = []
                for control in controls:
                    rows.append(ft.Column([control], col={"sm": 12, "md": 6, "lg": 4}))
                return ft.ResponsiveRow(rows)
            else:
                return ft.Row(
                    controls=controls, spacing=form_settings["spacing"], wrap=True
                )

    # フォームコード生成
    def generate_form_code():
        if not selected_template and not custom_form_fields:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    "テンプレートを選択するか、カスタムフォームにフィールドを追加してください"
                ),
                action="閉じる",
            )
            page.snack_bar.open = True
            page.update()
            return

        if not working_dir.value or not os.path.isdir(working_dir.value):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("有効なプロジェクトディレクトリを選択してください"),
                action="閉じる",
            )
            page.snack_bar.open = True
            page.update()
            return

        if not form_name.value or not output_file.value:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("フォーム名と出力ファイル名を入力してください"),
                action="閉じる",
            )
            page.snack_bar.open = True
            page.update()
            return

        # 使用するフィールド定義
        fields = (
            selected_template["fields"] if selected_template else custom_form_fields
        )

        # コード生成
        code = generate_code(form_name.value, fields, form_settings)

        # 出力ファイルパス
        output_path = os.path.join(working_dir.value, f"{output_file.value}.py")

        # ファイルに保存
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(code)

        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"フォームコードが生成されました: {output_path}"),
            action="閉じる",
        )
        page.snack_bar.open = True
        page.update()

    # レイアウト構築
    page.add(
        ft.Text("Flet フォームジェネレーター", size=30, weight=ft.FontWeight.BOLD),
        ft.Row([working_dir, browse_button]),
        ft.Row([form_name, output_file]),
        tabs,
        generate_button,
    )


# コード生成関数
def generate_code(form_name, fields, settings):
    # インポート
    imports = ["import flet as ft", "import datetime", "import re"]

    # フォームクラス
    class_definition = f"class {form_name}(ft.UserControl):"

    # 初期化メソッド
    init_method = [
        "    def __init__(self, on_submit=None, on_cancel=None):",
        "        super().__init__()",
        "        self.on_submit = on_submit",
        "        self.on_cancel = on_cancel",
        "        self.fields = {}",
        "        self.error_text = ft.Text(color=ft.colors.RED)",
    ]

    # フィールド初期化
    field_init = ["        # フィールドの初期化"]
    for field in fields:
        field_type = field["type"]
        field_name = field["name"]

        if field_type == "text":
            field_init.append(f"        self.{field_name} = ft.TextField(")
            field_init.append(f"            label=\"{field.get('label', '')}\",")
            if field.get("hint_text"):
                field_init.append(
                    f"            hint_text=\"{field.get('hint_text')}\","
                )
            if field.get("password"):
                field_init.append(f"            password={field.get('password')},")
            if field.get("multiline"):
                field_init.append(f"            multiline={field.get('multiline')},")
            if field.get("max_length"):
                field_init.append(f"            max_length={field.get('max_length')},")
            field_init.append("        )")

        elif field_type == "dropdown":
            field_init.append(f"        self.{field_name} = ft.Dropdown(")
            field_init.append(f"            label=\"{field.get('label', '')}\",")
            if field.get("hint_text"):
                field_init.append(
                    f"            hint_text=\"{field.get('hint_text')}\","
                )

            options = field.get("options", [])
            if options:
                field_init.append("            options=[")
                for option in options:
                    if isinstance(option, dict):
                        field_init.append(
                            f"                ft.dropdown.Option(\"{option['value']}\", \"{option['text']}\"),"
                        )
                    else:
                        field_init.append(
                            f'                ft.dropdown.Option("{option}"),'
                        )
                field_init.append("            ],")

            field_init.append("        )")

        elif field_type == "checkbox":
            field_init.append(f"        self.{field_name} = ft.Checkbox(")
            field_init.append(f"            label=\"{field.get('label', '')}\",")
            if "value" in field:
                field_init.append(f"            value={field.get('value')},")
            field_init.append("        )")

        elif field_type == "radio":
            field_init.append(f"        self.{field_name} = ft.RadioGroup(")
            field_init.append("            content=ft.Column([")
            if field.get("content"):
                field_init.append(f"                {field.get('content')}")
            else:
                field_init.append(
                    '                ft.Radio(value="option1", label="オプション1"),'
                )
                field_init.append(
                    '                ft.Radio(value="option2", label="オプション2"),'
                )
            field_init.append("            ]),")
            if "value" in field:
                field_init.append(f"            value=\"{field.get('value')}\",")
            field_init.append("        )")

        elif field_type == "switch":
            field_init.append(f"        self.{field_name} = ft.Switch(")
            field_init.append(f"            label=\"{field.get('label', '')}\",")
            if "value" in field:
                field_init.append(f"            value={field.get('value')},")
            field_init.append("        )")

        elif field_type == "slider":
            field_init.append(f"        self.{field_name} = ft.Slider(")
            if "min" in field:
                field_init.append(f"            min={field.get('min')},")
            if "max" in field:
                field_init.append(f"            max={field.get('max')},")
            if "divisions" in field:
                field_init.append(f"            divisions={field.get('divisions')},")
            if "value" in field:
                field_init.append(f"            value={field.get('value')},")
            field_init.append('            label="{value}",')
            field_init.append("        )")

        elif field_type == "date":
            field_init.append(
                f"        self.{field_name}_text = ft.Text(\"{field.get('label', '')}\")"
            )
            field_init.append(f"        self.{field_name} = ft.ElevatedButton(")
            field_init.append(f'            "日付を選択",')
            field_init.append(f"            icon=ft.icons.CALENDAR_TODAY,")
            field_init.append(f"            on_click=self.{field_name}_picker")
            field_init.append("        )")
            field_init.append(f"        self.{field_name}_value = None")

        elif field_type == "time":
            field_init.append(
                f"        self.{field_name}_text = ft.Text(\"{field.get('label', '')}\")"
            )
            field_init.append(f"        self.{field_name} = ft.ElevatedButton(")
            field_init.append(f'            "時刻を選択",')
            field_init.append(f"            icon=ft.icons.ACCESS_TIME,")
            field_init.append(f"            on_click=self.{field_name}_picker")
            field_init.append("        )")
            field_init.append(f"        self.{field_name}_value = None")

        elif field_type == "file":
            field_init.append(
                f"        self.{field_name}_text = ft.Text(\"{field.get('label', '')}\")"
            )
            field_init.append(f"        self.{field_name} = ft.ElevatedButton(")
            field_init.append(f'            "ファイルを選択",')
            field_init.append(f"            icon=ft.icons.UPLOAD_FILE,")
            field_init.append(f"            on_click=self.{field_name}_picker")
            field_init.append("        )")
            field_init.append(f"        self.{field_name}_value = None")

    # フォームボタン
    buttons_init = [
        "        # フォームボタン",
        f"        self.submit_button = ft.ElevatedButton(\"{settings['submit_text']}\", on_click=self.handle_submit)",
    ]

    if settings["show_cancel"]:
        buttons_init.append(
            f"        self.cancel_button = ft.OutlinedButton(\"{settings['cancel_text']}\", on_click=self.handle_cancel)"
        )

    # フィールド登録とマッピング
    register_fields = ["        # フィールドの登録"]
    for field in fields:
        field_name = field["name"]
        register_fields.append(
            f'        self.fields["{field_name}"] = self.{field_name}'
        )

    # 日付・時刻・ファイルピッカーメソッド
    picker_methods = []
    for field in fields:
        if field["type"] == "date":
            picker_methods.extend(
                [
                    f"    def {field['name']}_picker(self, e):",
                    f"        def on_result(e):",
                    f"            if e.date:",
                    f"                self.{field['name']}_value = e.date",
                    f"                self.{field['name']}.text = e.date.strftime(\"%Y-%m-%d\")",
                    f"                self.update()",
                    f"        date_picker = ft.DatePicker(on_change=on_result)",
                    f"        self.page.overlay.append(date_picker)",
                    f"        self.page.update()",
                    f"        date_picker.pick_date()",
                    "",
                ]
            )
        elif field["type"] == "time":
            picker_methods.extend(
                [
                    f"    def {field['name']}_picker(self, e):",
                    f"        def on_result(e):",
                    f"            if e.time:",
                    f"                self.{field['name']}_value = e.time",
                    f"                self.{field['name']}.text = e.time.strftime(\"%H:%M\")",
                    f"                self.update()",
                    f"        time_picker = ft.TimePicker(on_change=on_result)",
                    f"        self.page.overlay.append(time_picker)",
                    f"        self.page.update()",
                    f"        time_picker.pick_time()",
                    "",
                ]
            )
        elif field["type"] == "file":
            picker_methods.extend(
                [
                    f"    def {field['name']}_picker(self, e):",
                    f"        def on_result(e):",
                    f"            if e.files and len(e.files) > 0:",
                    f"                self.{field['name']}_value = e.files[0].path",
                    f"                self.{field['name']}.text = e.files[0].name",
                    f"                self.update()",
                    f"        file_picker = ft.FilePicker(on_result=on_result)",
                    f"        self.page.overlay.append(file_picker)",
                    f"        self.page.update()",
                    f"        file_picker.pick_files()",
                    "",
                ]
            )

    # バリデーションメソッド
    validate_method = [
        "    def validate(self):",
        '        """フォームのバリデーションを行う"""',
        "        is_valid = True",
        "        errors = []",
        "",
    ]

    for field in fields:
        if field.get("validators"):
            field_name = field["name"]
            field_label = field.get("label", field_name)

            validate_method.append(f"        # {field_label}のバリデーション")

            for validator in field.get("validators", []):
                if isinstance(validator, str) and validator == "required":
                    if field["type"] in ["text", "dropdown"]:
                        validate_method.append(
                            f"        if not self.{field_name}.value:"
                        )
                        validate_method.append(
                            f'            errors.append(f"{field_label}は必須です")'
                        )
                        validate_method.append(f"            is_valid = False")
                    elif field["type"] in ["date", "time", "file"]:
                        validate_method.append(
                            f"        if not self.{field_name}_value:"
                        )
                        validate_method.append(
                            f'            errors.append(f"{field_label}は必須です")'
                        )
                        validate_method.append(f"            is_valid = False")

                elif isinstance(validator, str) and validator.startswith("min_length:"):
                    min_val = validator.split(":")[1].strip()
                    validate_method.append(
                        f"        if self.{field_name}.value and len(self.{field_name}.value) < {min_val}:"
                    )
                    validate_method.append(
                        f'            errors.append(f"{field_label}は{min_val}文字以上で入力してください")'
                    )
                    validate_method.append(f"            is_valid = False")

                elif isinstance(validator, str) and validator == "email":
                    validate_method.append(
                        f"        if self.{field_name}.value and not re.match(r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$', self.{field_name}.value):"
                    )
                    validate_method.append(
                        f'            errors.append("有効なメールアドレスを入力してください")'
                    )
                    validate_method.append(f"            is_valid = False")

                elif isinstance(validator, str) and validator.startswith("match:"):
                    other_field = validator.split(":")[1].strip()
                    validate_method.append(
                        f"        if self.{field_name}.value != self.{other_field}.value:"
                    )
                    validate_method.append(
                        f'            errors.append(f"{field_label}が一致しません")'
                    )
                    validate_method.append(f"            is_valid = False")

            validate_method.append("")

    validate_method.extend(
        [
            "        if not is_valid:",
            '            self.error_text.value = "\\n".join(errors)',
            "        else:",
            '            self.error_text.value = ""',
            "        self.update()",
            "        return is_valid",
            "",
        ]
    )

    # 送信・キャンセルハンドラ
    handler_methods = [
        "    def handle_submit(self, e):",
        '        """フォーム送信処理"""',
        "        if self.validate():",
        "            data = {}",
    ]

    for field in fields:
        field_name = field["name"]
        if field["type"] in ["date", "time", "file"]:
            handler_methods.append(
                f'            data["{field_name}"] = self.{field_name}_value'
            )
        else:
            handler_methods.append(
                f'            data["{field_name}"] = self.{field_name}.value'
            )

    handler_methods.extend(
        [
            "",
            "            if self.on_submit:",
            "                self.on_submit(data)",
            "",
            "    def handle_cancel(self, e):",
            '        """キャンセル処理"""',
            "        if self.on_cancel:",
            "            self.on_cancel()",
            "",
        ]
    )

    # ビルドメソッド
    build_method = ["    def build(self):"]

    # レイアウト設定
    if settings["layout"] == "column":
        build_method.append("        return ft.Column(")
        build_method.append("            controls=[")
    else:  # row_wrap
        if settings["responsive"]:
            build_method.append("        row_controls = []")
            for field in fields:
                field_name = field["name"]
                if field["type"] in ["date", "time", "file"]:
                    build_method.append(
                        f'        row_controls.append(ft.Column([self.{field_name}_text, self.{field_name}], col={{"sm": 12, "md": 6, "lg": 4}}))'
                    )
                else:
                    build_method.append(
                        f'        row_controls.append(ft.Column([self.{field_name}], col={{"sm": 12, "md": 6, "lg": 4}}))'
                    )

            build_method.append("        return ft.Column(")
            build_method.append("            controls=[")
            build_method.append("                ft.ResponsiveRow(row_controls),")
        else:
            build_method.append("        return ft.Column(")
            build_method.append("            controls=[")
            build_method.append("                ft.Row(")
            build_method.append("                    [")

    # フィールドの配置
    if settings["layout"] == "column":
        for field in fields:
            field_name = field["name"]
            if field["type"] in ["date", "time", "file"]:
                build_method.append(
                    f"                ft.Column([self.{field_name}_text, self.{field_name}]),"
                )
            else:
                build_method.append(f"                self.{field_name},")
    elif not settings["responsive"] and settings["layout"] == "row_wrap":
        for field in fields:
            field_name = field["name"]
            if field["type"] in ["date", "time", "file"]:
                build_method.append(
                    f"                        ft.Column([self.{field_name}_text, self.{field_name}]),"
                )
            else:
                build_method.append(f"                        self.{field_name},")

        build_method.append("                    ],")
        build_method.append(f"                    wrap=True,")
        build_method.append(f"                    spacing={settings['spacing']},")
        build_method.append("                ),")

    # エラーテキストとボタン
    build_method.append("                self.error_text,")
    build_method.append("                ft.Row(")
    build_method.append("                    controls=[")
    build_method.append("                        self.submit_button,")

    if settings["show_cancel"]:
        build_method.append("                        self.cancel_button,")

    build_method.append("                    ],")
    build_method.append("                ),")
    build_method.append("            ],")
    build_method.append(f"            spacing={settings['spacing']},")
    build_method.append(f"            padding={settings['padding']},")
    build_method.append("        )")

    # サンプル使用コード
    example_code = [
        "",
        "# サンプル使用法",
        "def main(page: ft.Page):",
        '    page.title = "フォームサンプル"',
        "",
        "    def on_form_submit(data):",
        '        page.snack_bar = ft.SnackBar(content=ft.Text(f"送信データ: {data}"))',
        "        page.snack_bar.open = True",
        "        page.update()",
        "",
        "    def on_form_cancel():",
        '        page.snack_bar = ft.SnackBar(content=ft.Text("キャンセルされました"))',
        "        page.snack_bar.open = True",
        "        page.update()",
        "",
        f"    form = {form_name}(on_submit=on_form_submit, on_cancel=on_form_cancel)",
        "",
        "    page.add(",
        '        ft.Text("フォームサンプル", size=30, weight=ft.FontWeight.BOLD),',
        "        form",
        "    )",
        "",
        'if __name__ == "__main__":',
        "    ft.app(target=main)",
    ]

    # コード全体を組み立て
    full_code = []
    full_code.extend(imports)
    full_code.append("")
    full_code.append(class_definition)
    full_code.extend(init_method)
    full_code.extend(field_init)
    full_code.extend(buttons_init)
    full_code.extend(register_fields)
    full_code.append("")
    full_code.extend(picker_methods)
    full_code.extend(validate_method)
    full_code.extend(handler_methods)
    full_code.extend(build_method)
    full_code.extend(example_code)

    return "\n".join(full_code)


# フォームフィールド定義を読み込む
def load_form_fields():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fields_path = os.path.join(current_dir, "form_fields.json")

    with open(fields_path, "r", encoding="utf-8") as f:
        return json.load(f)


# フォームテンプレートを読み込む
def load_form_templates():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    templates_path = os.path.join(current_dir, "form_templates.json")

    with open(templates_path, "r", encoding="utf-8") as f:
        return json.load(f)


# テーマを設定
def apply_app_theme(page):
    page.theme = ft.Theme(
        color_scheme_seed=ft.colors.BLUE,
        visual_density=ft.ThemeVisualDensity.COMFORTABLE,
    )
    page.update()


# ユーティリティ関数: PascalCase変換
def pascal_case(s):
    # スペースと特殊文字を削除し、各単語の先頭を大文字に
    s = re.sub(r"[^\w\s]", "", s)
    return "".join(word.capitalize() for word in s.split())


# ユーティリティ関数: snake_case変換
def snake_case(s):
    # スペースと特殊文字を削除
    s = re.sub(r"[^\w\s]", "", s)
    # キャメルケースをスネークケースに変換
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    # スペースをアンダースコアに置換し、小文字に変換
    return re.sub(r"\s+", "_", s).lower()


if __name__ == "__main__":
    ft.app(target=main)
