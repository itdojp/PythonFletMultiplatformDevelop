import flet as ft
import platform
import json
import os
from pathlib import Path

def main(page: ft.Page):
    page.title = "Flet プラットフォーム別機能実装ヘルパー"
    page.theme_mode = ft.ThemeMode.SYSTEM
    
    # テーマ設定
    apply_app_theme(page)
    
    # プラットフォーム検出情報
    current_os = platform.system()
    os_info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor()
    }
    
    # プラットフォーム別機能リスト
    # 実際のアプリで使えるサンプルコード
    platform_features = load_platform_features()
    
    # コード生成機能
    def generate_code():
        feature = feature_dropdown.value
        if not feature:
            page.snack_bar = ft.SnackBar(content=ft.Text("機能を選択してください"))
            page.snack_bar.open = True
            page.update()
            return
            
        # 選択された機能のコードを取得
        feature_data = next((f for f in platform_features if f["name"] == feature), None)
        if not feature_data:
            return
            
        # プラットフォーム検出と条件分岐のコードを生成
        code = "import flet as ft\nimport platform\n\n"
        code += "def detect_platform():\n"
        code += "    system = platform.system()\n"
        code += "    if system == 'Windows':\n"
        code += "        return 'windows'\n"
        code += "    elif system == 'Darwin':\n"
        code += "        return 'macos'\n"
        code += "    elif system == 'Linux':\n"
        code += "        # モバイルLinux(Android)と通常のLinuxを区別\n"
        code += "        try:\n"
        code += "            with open('/system/build.prop', 'r') as f:\n"
        code += "                return 'android'\n"
        code += "        except (FileNotFoundError, PermissionError):\n"
        code += "            return 'linux'\n"
        code += "    elif system == 'Java':\n"
        code += "        # WebブラウザのJava環境の場合はWeb\n"
        code += "        return 'web'\n"
        code += "    return 'unknown'\n\n"
        
        code += f"def {feature_data['function_name']}(page: ft.Page):\n"
        code += "    platform_type = detect_platform()\n\n"
        code += "    # プラットフォーム別の実装\n"
        code += "    if platform_type == 'android':\n"
        code += f"        {feature_data['android'].strip().replace(chr(10), chr(10) + '        ')}\n\n"
        code += "    elif platform_type == 'ios' or platform_type == 'macos':\n"
        code += f"        {feature_data['ios'].strip().replace(chr(10), chr(10) + '        ')}\n\n"
        code += "    elif platform_type == 'web':\n"
        code += f"        {feature_data['web'].strip().replace(chr(10), chr(10) + '        ')}\n\n"
        code += "    else:  # desktop (Windows/Linux)\n"
        code += f"        {feature_data['desktop'].strip().replace(chr(10), chr(10) + '        ')}\n"
        
        # コードをテキストエリアに表示
        code_preview.value = code
        page.update()
    
    # 機能のドロップダウン
    feature_dropdown = ft.Dropdown(
        label="実装したい機能を選択",
        options=[ft.dropdown.Option(feature["name"]) for feature in platform_features],
        width=500,
        on_change=lambda _: generate_code()
    )
    
    # コードプレビュー
    code_preview = ft.TextField(
        label="生成されたコード",
        multiline=True,
        min_lines=20,
        max_lines=30,
        read_only=True,
        width=900
    )
    
    # コードのコピー機能
    def copy_to_clipboard(_):
        page.set_clipboard(code_preview.value)
        page.snack_bar = ft.SnackBar(content=ft.Text("コードをクリップボードにコピーしました"))
        page.snack_bar.open = True
        page.update()
    
    copy_button = ft.ElevatedButton(
        text="コードをコピー",
        icon="copy",
        on_click=copy_to_clipboard
    )
    
    # ファイルとして保存する機能
    def save_to_file(_):
        file_dialog = ft.FilePicker()
        page.overlay.append(file_dialog)
        
        def save_result(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    with open(e.path, "w", encoding="utf-8") as f:
                        f.write(code_preview.value)
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"コードを {e.path} に保存しました"))
                    page.snack_bar.open = True
                except Exception as ex:
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"保存エラー: {str(ex)}"))
                    page.snack_bar.open = True
            page.update()
        
        file_dialog.on_result = save_result
        file_dialog.save_file(
            allowed_extensions=["py"],
            initial_filename="platform_feature.py"
        )
    
    save_button = ft.ElevatedButton(
        text="ファイルに保存",
        icon="save",
        on_click=save_to_file
    )
    
    # レイアウト
    page.add(
        ft.AppBar(title=ft.Text("Flet プラットフォーム別機能実装ヘルパー"), center_title=True),
        ft.Container(
            content=ft.Column([
                ft.Text("現在の環境情報", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"OS: {os_info['system']} {os_info['release']}"),
                        ft.Text(f"バージョン: {os_info['version']}"),
                        ft.Text(f"マシン: {os_info['machine']}"),
                        ft.Text(f"プロセッサ: {os_info['processor']}")
                    ]),
                    padding=10,
                    border=ft.border.all(1, "#B3E5FC"),  # 薄い青色の境界線
                    border_radius=10
                ),
                ft.Container(height=20),
                ft.Text("プラットフォーム別機能の実装", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("以下から実装したい機能を選択すると、プラットフォーム別の条件分岐を含むコードが生成されます。"),
                feature_dropdown,
                ft.Container(height=20),
                code_preview,
                ft.Row([copy_button, save_button], spacing=10)
            ]),
            padding=20
        )
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

def load_platform_features():
    """プラットフォーム別機能のサンプルコードを読み込む"""
    features_file = Path(__file__).parent / "platform_features.json"
    
    # ファイルが存在しない場合はデフォルトのサンプルを作成
    if not features_file.exists():
        default_features = [
            {
                "name": "ナビゲーションUI",
                "function_name": "create_navigation_ui",
                "description": "プラットフォームに適したナビゲーションUIを作成",
                "android": "# Androidスタイルのボトムナビゲーション\nreturn ft.NavigationBar(\n    destinations=[\n        ft.NavigationDestination(icon=\"home\", label=\"ホーム\"),\n        ft.NavigationDestination(icon=\"search\", label=\"検索\"),\n        ft.NavigationDestination(icon=\"person\", label=\"プロフィール\")\n    ],\n    selected_index=0\n)",
                "ios": "# iOSスタイルのタブバー\nreturn ft.Tabs(\n    selected_index=0,\n    tabs=[\n        ft.Tab(text=\"ホーム\", icon=\"home\"),\n        ft.Tab(text=\"検索\", icon=\"search\"),\n        ft.Tab(text=\"プロフィール\", icon=\"person\")\n    ]\n)",
                "web": "# Webスタイルのサイドナビゲーション\nreturn ft.NavigationRail(\n    selected_index=0,\n    label_type=ft.NavigationRailLabelType.ALL,\n    destinations=[\n        ft.NavigationRailDestination(icon=\"home\", label=\"ホーム\"),\n        ft.NavigationRailDestination(icon=\"search\", label=\"検索\"),\n        ft.NavigationRailDestination(icon=\"person\", label=\"プロフィール\")\n    ],\n)",
                "desktop": "# デスクトップスタイルのサイドナビゲーション\nreturn ft.NavigationRail(\n    selected_index=0,\n    extended=True,\n    label_type=ft.NavigationRailLabelType.ALL,\n    destinations=[\n        ft.NavigationRailDestination(icon=\"home\", label=\"ホーム\"),\n        ft.NavigationRailDestination(icon=\"search\", label=\"検索\"),\n        ft.NavigationRailDestination(icon=\"person\", label=\"プロフィール\")\n    ],\n)"
            },
            {
                "name": "ダイアログ表示",
                "function_name": "show_platform_dialog",
                "description": "プラットフォームに適したダイアログを表示",
                "android": "# Androidスタイルのダイアログ\npage.dialog = ft.AlertDialog(\n    title=ft.Text(\"確認\"),\n    content=ft.Text(\"この操作を続行しますか？\"),\n    actions=[\n        ft.TextButton(\"キャンセル\", on_click=lambda _: page.close_dialog()),\n        ft.TextButton(\"OK\", on_click=lambda _: page.close_dialog())\n    ],\n    actions_alignment=ft.MainAxisAlignment.END\n)\npage.dialog.open = True\npage.update()",
                "ios": "# iOSスタイルのダイアログ\npage.dialog = ft.AlertDialog(\n    title=ft.Text(\"確認\"),\n    content=ft.Text(\"この操作を続行しますか？\"),\n    actions=[\n        ft.TextButton(\"キャンセル\", on_click=lambda _: page.close_dialog()),\n        ft.TextButton(\"OK\", on_click=lambda _: page.close_dialog())\n    ],\n    actions_alignment=ft.MainAxisAlignment.CENTER\n)\npage.dialog.open = True\npage.update()",
                "web": "# Webスタイルのモーダルダイアログ\npage.dialog = ft.AlertDialog(\n    modal=True,\n    title=ft.Text(\"確認\"),\n    content=ft.Text(\"この操作を続行しますか？\"),\n    actions=[\n        ft.TextButton(\"キャンセル\", on_click=lambda _: page.close_dialog()),\n        ft.TextButton(\"OK\", on_click=lambda _: page.close_dialog())\n    ],\n)\npage.dialog.open = True\npage.update()",
                "desktop": "# デスクトップスタイルのダイアログ\npage.dialog = ft.AlertDialog(\n    title=ft.Text(\"確認\"),\n    content=ft.Text(\"この操作を続行しますか？\"),\n    actions=[\n        ft.TextButton(\"キャンセル\", on_click=lambda _: page.close_dialog()),\n        ft.TextButton(\"OK\", on_click=lambda _: page.close_dialog())\n    ],\n)\npage.dialog.open = True\npage.update()"
            },
            {
                "name": "プラットフォーム別ボタンスタイル",
                "function_name": "create_platform_button",
                "description": "プラットフォームのデザインガイドラインに沿ったボタンスタイル",
                "android": "# Androidのマテリアルデザインボタン\nreturn ft.ElevatedButton(\n    text=\"アクション\",\n    style=ft.ButtonStyle(\n        shape=ft.RoundedRectangleBorder(radius=8),\n        elevation=4\n    )\n)",
                "ios": "# iOSスタイルの丸みを帯びたボタン\nreturn ft.ElevatedButton(\n    text=\"アクション\",\n    style=ft.ButtonStyle(\n        shape=ft.RoundedRectangleBorder(radius=20),\n        elevation=0,\n        color=\"#2196F3\"\n    )\n)",
                "web": "# Web風のフラットボタン\nreturn ft.ElevatedButton(\n    text=\"アクション\",\n    style=ft.ButtonStyle(\n        shape=ft.RoundedRectangleBorder(radius=4),\n        elevation=1\n    )\n)",
                "desktop": "# デスクトップ風のボタン\nreturn ft.ElevatedButton(\n    text=\"アクション\",\n    style=ft.ButtonStyle(\n        shape=ft.RoundedRectangleBorder(radius=4),\n        elevation=2\n    )\n)"
            },
            {
                "name": "ファイルピッカー実装",
                "function_name": "show_file_picker",
                "description": "各プラットフォームに最適化されたファイル選択UI",
                "android": "# Androidのファイルピッカー\nfile_picker = ft.FilePicker()\npage.overlay.append(file_picker)\n\ndef on_files_selected(e):\n    if e.files:\n        # 選択されたファイルを処理\n        selected_file = e.files[0]\n        print(f\"選択されたファイル: {selected_file.name}, サイズ: {selected_file.size}バイト\")\n\nfile_picker.on_result = on_files_selected\nfile_picker.pick_files(\n    allow_multiple=False,\n    allowed_extensions=[\"jpg\", \"png\", \"pdf\"]\n)",
                "ios": "# iOSのファイルピッカー\nfile_picker = ft.FilePicker()\npage.overlay.append(file_picker)\n\ndef on_files_selected(e):\n    if e.files:\n        # 選択されたファイルを処理\n        selected_file = e.files[0]\n        print(f\"選択されたファイル: {selected_file.name}, サイズ: {selected_file.size}バイト\")\n\nfile_picker.on_result = on_files_selected\nfile_picker.pick_files(\n    allow_multiple=False,\n    allowed_extensions=[\"jpg\", \"png\", \"pdf\"]\n)",
                "web": "# Webのファイルピッカー\nfile_picker = ft.FilePicker()\npage.overlay.append(file_picker)\n\ndef on_files_selected(e):\n    if e.files:\n        # 選択されたファイルを処理\n        selected_file = e.files[0]\n        print(f\"選択されたファイル: {selected_file.name}, サイズ: {selected_file.size}バイト\")\n\nfile_picker.on_result = on_files_selected\nfile_picker.pick_files(\n    allow_multiple=False,\n    allowed_extensions=[\"jpg\", \"png\", \"pdf\"]\n)",
                "desktop": "# デスクトップのファイルピッカー\nfile_picker = ft.FilePicker()\npage.overlay.append(file_picker)\n\ndef on_files_selected(e):\n    if e.files:\n        # 選択されたファイルを処理\n        selected_file = e.files[0]\n        print(f\"選択されたファイル: {selected_file.name}, サイズ: {selected_file.size}バイト\")\n\nfile_picker.on_result = on_files_selected\nfile_picker.pick_files(\n    allow_multiple=False,\n    allowed_extensions=[\"jpg\", \"png\", \"pdf\"]\n)"
            },
            {
                "name": "プラットフォーム別テーマ適用",
                "function_name": "apply_platform_theme",
                "description": "各プラットフォームに最適化されたテーマを適用",
                "android": "# Androidマテリアルテーマ\npage.theme = ft.Theme(\n    color_scheme_seed=\"blue\",\n    use_material3=True\n)",
                "ios": "# iOSライクなテーマ\npage.theme = ft.Theme(\n    color_scheme_seed=\"cyan\",\n    use_material3=True\n)",
                "web": "# Webモダンテーマ\npage.theme = ft.Theme(\n    color_scheme_seed=\"indigo\",\n    use_material3=True\n)",
                "desktop": "# デスクトップテーマ\npage.theme = ft.Theme(\n    color_scheme_seed=\"blue\",\n    use_material3=True\n)"
            }
        ]
        
        # ディレクトリがなければ作成
        features_file.parent.mkdir(parents=True, exist_ok=True)
        
        # デフォルト機能をJSONファイルに保存
        with open(features_file, "w", encoding="utf-8") as f:
            json.dump(default_features, f, ensure_ascii=False, indent=2)
    
    # 機能を読み込む
    with open(features_file, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    ft.app(target=main)
