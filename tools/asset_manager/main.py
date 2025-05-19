import hashlib
import io
import json
import os
import re
import shutil
from pathlib import Path

import flet as ft
from PIL import Image, ImageOps


def main(page: ft.Page):
    page.title = "Flet アセット管理ツール"
    page.theme_mode = ft.ThemeMode.SYSTEM

    # テーマ設定
    apply_app_theme(page)

    # 作業ディレクトリ
    working_dir = ft.TextField(
        label="プロジェクトディレクトリ",
        value=os.path.expanduser("~"),
        width=500,
        hint_text="プロジェクトのルートディレクトリ",
    )

    def select_dir(_):
        def result_handler(e: ft.FilePickerResultEvent):
            if e.path:
                working_dir.value = e.path
                update_asset_scanner()
                page.update()

        file_picker = ft.FilePicker(on_result=result_handler)
        page.overlay.append(file_picker)
        page.update()
        file_picker.get_directory_path()

    browse_button = ft.ElevatedButton(
        "参照", on_click=select_dir, icon=ft.icons.FOLDER_OPEN
    )

    # プラットフォーム定義を読み込む
    platform_data = load_platform_definitions()

    # プラットフォーム選択
    platforms = [p["name"] for p in platform_data]
    platform_selector = ft.Dropdown(
        label="アセット生成プラットフォーム",
        options=[ft.dropdown.Option(p) for p in platforms],
        width=300,
        hint_text="アセットを生成するプラットフォーム",
    )

    # アセットタイプの選択
    asset_types = ["アイコン", "画像", "フォント"]

    asset_type_selector = ft.Dropdown(
        label="アセットタイプ",
        options=[ft.dropdown.Option(t) for t in asset_types],
        width=200,
        value="アイコン",
    )

    # 選択したアセットの情報を表示
    selected_asset_info = ft.Text()

    # アイコン/画像のプレビュー
    asset_preview = ft.Image(
        width=150, height=150, fit=ft.ImageFit.CONTAIN, border_radius=10
    )

    # アセットのスキャン結果
    asset_list = ft.ListView(spacing=2, height=200)

    # アセットパス（画像）
    asset_path = None

    # スキャン対象の拡張子
    asset_extensions = {
        "アイコン": ["png", "jpg", "jpeg", "svg"],
        "画像": ["png", "jpg", "jpeg", "webp", "gif"],
        "フォント": ["ttf", "otf", "woff", "woff2"],
    }

    # アセットパスを設定する
    def set_asset_path(path):
        nonlocal asset_path
        asset_path = path

        if is_image_file(path):
            try:
                # プレビュー表示
                with open(path, "rb") as f:
                    image_bytes = f.read()

                asset_preview.src_base64 = bytes_to_base64(image_bytes)
                asset_preview.visible = True

                # 画像情報の表示
                try:
                    with Image.open(path) as img:
                        width, height = img.size
                        format_name = img.format
                        mode = img.mode

                        info_text = f"ファイル: {os.path.basename(path)}\n"
                        info_text += f"サイズ: {width}x{height}px\n"
                        info_text += f"形式: {format_name}\n"
                        info_text += f"モード: {mode}\n"
                        info_text += (
                            f"ファイルサイズ: {os.path.getsize(path) // 1024} KB"
                        )

                        selected_asset_info.value = info_text
                except Exception as e:
                    selected_asset_info.value = f"画像情報の取得エラー: {str(e)}"
            except Exception as e:
                asset_preview.src_base64 = None
                selected_asset_info.value = f"プレビューエラー: {str(e)}"
        else:
            asset_preview.src_base64 = None
            asset_preview.visible = False
            selected_asset_info.value = f"選択: {os.path.basename(path)}"

        page.update()

    # アセットスキャナーを更新
    def update_asset_scanner():
        asset_list.controls.clear()

        if not working_dir.value or not os.path.exists(working_dir.value):
            return

        # 選択されたアセットタイプの拡張子を取得
        extensions = asset_extensions.get(asset_type_selector.value, [])
        if not extensions:
            return

        # ディレクトリ内のアセットをスキャン
        project_dir = Path(working_dir.value)
        assets_found = []

        for ext in extensions:
            for file_path in project_dir.glob(f"**/*.{ext}"):
                if ".git" not in str(file_path) and "node_modules" not in str(
                    file_path
                ):
                    assets_found.append(str(file_path))

        # 結果をリストに表示
        for asset in assets_found:
            rel_path = os.path.relpath(asset, working_dir.value)

            asset_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(
                        ft.icons.IMAGE
                        if is_image_file(asset)
                        else ft.icons.FONT_DOWNLOAD
                    ),
                    title=ft.Text(os.path.basename(asset)),
                    subtitle=ft.Text(rel_path),
                    on_click=lambda _, a=asset: set_asset_path(a),
                )
            )

        selected_asset_info.value = f"{len(assets_found)} 個のアセットが見つかりました"
        page.update()

    # アセットタイプが変更されたときの処理
    def on_asset_type_change(_):
        update_asset_scanner()

    asset_type_selector.on_change = on_asset_type_change

    # 出力オプション
    output_options = ft.Column(
        [
            ft.Text("出力オプション", weight=ft.FontWeight.BOLD),
            ft.Checkbox(label="すべてのサイズを生成", value=True),
            ft.Checkbox(label="ダークモード用のアセットも生成", value=False),
        ]
    )

    # アセット生成ボタン
    def generate_assets(_):
        if not asset_path:
            page.snack_bar = ft.SnackBar(content=ft.Text("アセットを選択してください"))
            page.snack_bar.open = True
            page.update()
            return

        if not platform_selector.value:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("プラットフォームを選択してください")
            )
            page.snack_bar.open = True
            page.update()
            return

        # 選択されたプラットフォームのデータを取得
        platform = next(
            (p for p in platform_data if p["name"] == platform_selector.value), None
        )
        if not platform:
            return

        # アセットの種類に基づいて処理を分岐
        if asset_type_selector.value in ["アイコン", "画像"]:
            if not is_image_file(asset_path):
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("選択されたファイルは画像ではありません")
                )
                page.snack_bar.open = True
                page.update()
                return

            # 画像の処理
            process_image_asset(platform, asset_path)
        elif asset_type_selector.value == "フォント":
            # フォントの処理
            process_font_asset(asset_path)

    # 画像アセットの処理
    def process_image_asset(platform, src_path):
        try:
            # プロジェクトディレクトリ
            project_dir = Path(working_dir.value)

            # 元のファイル名と拡張子
            orig_filename = os.path.basename(src_path)
            name, ext = os.path.splitext(orig_filename)
            ext = ext.lstrip(".")

            # プラットフォーム別のディレクトリ構造を取得
            dir_structure = platform["directory_structure"]
            base_dir_template = list(dir_structure.values())[0]

            # アセットタイプ
            asset_type = (
                "icons" if asset_type_selector.value == "アイコン" else "images"
            )

            # サイズ情報の取得
            sizes = (
                platform["icon_sizes"]
                if asset_type_selector.value == "アイコン"
                else platform["screenshot_sizes"]
            )

            # 生成されたファイルカウント
            generated_count = 0

            with Image.open(src_path) as img:
                # アルファチャンネルを保持して変換
                if img.mode != "RGBA" and "A" not in img.mode:
                    img = img.convert("RGBA")

                # 各サイズに対して処理
                for size_info in sizes:
                    # サイズ情報に基づいてファイル名を構築
                    if "scale" in size_info:
                        # アイコンスタイル
                        output_size = size_info["size"]
                        scale = size_info["scale"]
                        resolution = size_info["name"]

                        # ディレクトリパス
                        dir_path = base_dir_template.format(
                            asset_type=asset_type,
                            resolution=resolution,
                            filename=name,
                            scale=scale,
                            size=output_size,
                            extension=ext,
                        )

                        # パターンに応じてパスを分解
                        if "{resolution}" in base_dir_template:
                            # Android スタイル
                            dir_path = os.path.dirname(dir_path)
                            filename = f"{name}.{ext}"
                            output_path = os.path.join(project_dir, dir_path, filename)
                        elif "@{scale}x" in base_dir_template:
                            # iOS スタイル
                            dir_path = os.path.dirname(dir_path)
                            filename = f"{name}@{int(scale)}x.{ext}"
                            output_path = os.path.join(project_dir, dir_path, filename)
                        elif "{size}x{size}" in base_dir_template:
                            # デスクトップスタイル
                            size_dir = f"{output_size}x{output_size}"
                            dir_path = base_dir_template.split("{size}x{size}")[0]
                            dir_path = os.path.join(project_dir, dir_path, size_dir)
                            filename = f"{name}.{ext}"
                            output_path = os.path.join(dir_path, filename)
                        else:
                            # Web スタイル
                            dir_path = os.path.dirname(dir_path)
                            filename = f"{name}-{output_size}.{ext}"
                            output_path = os.path.join(project_dir, dir_path, filename)

                        # ディレクトリを作成
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)

                        # 画像をリサイズして保存
                        resized_img = img.resize(
                            (output_size, output_size), Image.LANCZOS
                        )
                        resized_img.save(output_path)
                        generated_count += 1

                    else:
                        # スクリーンショットスタイル
                        width = size_info["width"]
                        height = size_info["height"]
                        screen_type = size_info["name"]

                        # アスペクト比を維持してリサイズ
                        original_width, original_height = img.size
                        aspect_ratio = original_width / original_height

                        if aspect_ratio > (width / height):
                            # 元画像が横長
                            new_width = width
                            new_height = int(width / aspect_ratio)
                        else:
                            # 元画像が縦長
                            new_height = height
                            new_width = int(height * aspect_ratio)

                        # ディレクトリパス
                        dir_path = os.path.join(
                            project_dir,
                            f"assets/{platform['name'].lower()}/screenshots/{screen_type}",
                        )
                        os.makedirs(dir_path, exist_ok=True)

                        # 画像をリサイズして保存
                        filename = f"{name}_{screen_type}.{ext}"
                        output_path = os.path.join(dir_path, filename)

                        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                        resized_img.save(output_path)
                        generated_count += 1

            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"{generated_count}個のアセットが生成されました")
            )
            page.snack_bar.open = True
            page.update()

        except Exception as e:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"アセット生成エラー: {str(e)}")
            )
            page.snack_bar.open = True
            page.update()

    # フォントアセットの処理
    def process_font_asset(src_path):
        try:
            # プロジェクトディレクトリ
            project_dir = Path(working_dir.value)

            # フォントディレクトリを作成
            font_dir = project_dir / "assets" / "fonts"
            font_dir.mkdir(parents=True, exist_ok=True)

            # フォントファイルをコピー
            font_name = os.path.basename(src_path)
            dest_path = font_dir / font_name

            shutil.copy2(src_path, dest_path)

            # pubspec.yamlにフォント設定を追加するための情報を提供
            pubspec_info = f"""
# pubspec.yaml に以下を追加してください:
fonts:
  - family: {os.path.splitext(font_name)[0]}
    fonts:
      - asset: assets/fonts/{font_name}
"""

            # ダイアログでフォント設定情報を表示
            page.dialog = ft.AlertDialog(
                title=ft.Text("フォント設定"),
                content=ft.Column(
                    [
                        ft.Text("フォントファイルがコピーされました:"),
                        ft.Text(str(dest_path)),
                        ft.Divider(),
                        ft.Text("pubspec.yaml設定:", weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Text(pubspec_info),
                            bgcolor=ft.colors.SURFACE_VARIANT,
                            padding=10,
                            border_radius=5,
                        ),
                    ]
                ),
                actions=[
                    ft.TextButton("閉じる", on_click=lambda _: page.close_dialog())
                ],
            )
            page.dialog.open = True
            page.update()

        except Exception as e:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"フォント処理エラー: {str(e)}")
            )
            page.snack_bar.open = True
            page.update()

    generate_button = ft.ElevatedButton(
        "アセットを生成",
        on_click=generate_assets,
        icon=ft.icons.IMAGE,
        bgcolor=ft.colors.PRIMARY,
    )

    # アセット名の検証と正規化のツール
    asset_name_input = ft.TextField(
        label="アセット名", width=400, hint_text="アセット名を入力して標準化"
    )

    def normalize_asset_name(_):
        name = asset_name_input.value
        if not name:
            return

        # 標準化ルール
        # 1. スペースをアンダースコアに置換
        # 2. 小文字に変換
        # 3. アルファベット、数字、アンダースコア、ハイフン以外の文字を削除
        normalized = re.sub(r"[^\w\-]", "", name.lower().replace(" ", "_"))

        asset_name_input.value = normalized
        page.update()

    normalize_button = ft.ElevatedButton(
        "名前を標準化", on_click=normalize_asset_name, icon=ft.icons.AUTORENEW
    )

    # アセット使用状況スキャンボタン
    def scan_asset_usage(_):
        if not working_dir.value or not os.path.exists(working_dir.value):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("有効なプロジェクトディレクトリを指定してください")
            )
            page.snack_bar.open = True
            page.update()
            return

        project_dir = Path(working_dir.value)

        # アセットディレクトリを特定
        asset_dirs = []
        for potential_dir in ["assets", "src/assets", "public/assets"]:
            if (project_dir / potential_dir).exists():
                asset_dirs.append(project_dir / potential_dir)

        if not asset_dirs:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("アセットディレクトリが見つかりません")
            )
            page.snack_bar.open = True
            page.update()
            return

        # アセットファイルの収集
        all_assets = []
        for asset_dir in asset_dirs:
            for ext in [
                "png",
                "jpg",
                "jpeg",
                "svg",
                "gif",
                "webp",
                "ttf",
                "otf",
                "woff",
                "woff2",
            ]:
                all_assets.extend(asset_dir.glob(f"**/*.{ext}"))

        if not all_assets:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("アセットファイルが見つかりません")
            )
            page.snack_bar.open = True
            page.update()
            return

        # コードファイルをスキャン
        code_files = []
        for ext in ["py", "dart", "js", "jsx", "ts", "tsx", "html", "css", "scss"]:
            code_files.extend(project_dir.glob(f"**/*.{ext}"))

        # 使用状況の確認
        asset_usage = {}

        for asset in all_assets:
            rel_path = asset.relative_to(project_dir)
            asset_name = asset.name
            asset_usage[str(rel_path)] = {
                "name": asset_name,
                "path": str(rel_path),
                "used": False,
                "references": [],
            }

        for code_file in code_files:
            if ".git" in str(code_file) or "node_modules" in str(code_file):
                continue

            try:
                with open(code_file, "r", encoding="utf-8") as f:
                    content = f.read()

                    for asset_path, asset_info in asset_usage.items():
                        asset_name = asset_info["name"]

                        # ファイル名と相対パスの両方で検索
                        if (
                            asset_name in content
                            or asset_path.replace("\\", "/") in content
                        ):
                            asset_info["used"] = True
                            asset_info["references"].append(
                                str(code_file.relative_to(project_dir))
                            )
            except Exception:
                # エンコーディングエラーなどをスキップ
                continue

        # 未使用アセットと使用済みアセットを集計
        unused_assets = [info for info in asset_usage.values() if not info["used"]]
        used_assets = [info for info in asset_usage.values() if info["used"]]

        # 結果の表示
        page.dialog = ft.AlertDialog(
            title=ft.Text("アセット使用状況"),
            content=ft.Column(
                [
                    ft.Text(f"合計アセット数: {len(asset_usage)}"),
                    ft.Text(
                        f"使用済みアセット: {len(used_assets)}", color=ft.colors.GREEN
                    ),
                    ft.Text(
                        f"未使用アセット: {len(unused_assets)}",
                        color=ft.colors.RED if unused_assets else ft.colors.GREEN,
                    ),
                    ft.Divider(),
                    (
                        ft.Text("未使用アセット:", weight=ft.FontWeight.BOLD)
                        if unused_assets
                        else ft.Text(
                            "すべてのアセットが使用されています！",
                            color=ft.colors.GREEN,
                        )
                    ),
                    ft.ListView(
                        controls=[
                            ft.Text(f"- {info['path']}") for info in unused_assets
                        ],
                        height=200 if unused_assets else 0,
                    ),
                ]
            ),
            actions=[ft.TextButton("閉じる", on_click=lambda _: page.close_dialog())],
        )
        page.dialog.open = True
        page.update()

    scan_usage_button = ft.ElevatedButton(
        "アセット使用状況をスキャン",
        on_click=scan_asset_usage,
        icon=ft.icons.FIND_IN_PAGE,
    )

    # レイアウト
    page.add(
        ft.AppBar(
            title=ft.Text("Flet アセット管理ツール"),
            center_title=True,
            bgcolor=ft.colors.SURFACE_VARIANT,
        ),
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("プロジェクト設定", weight=ft.FontWeight.BOLD, size=16),
                    ft.Row([working_dir, browse_button]),
                    ft.Divider(),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        "アセットスキャン",
                                        weight=ft.FontWeight.BOLD,
                                        size=16,
                                    ),
                                    ft.Row([asset_type_selector, scan_usage_button]),
                                    asset_list,
                                ],
                                expand=True,
                            ),
                            ft.VerticalDivider(width=1),
                            ft.Column(
                                [
                                    ft.Text(
                                        "アセットプレビュー",
                                        weight=ft.FontWeight.BOLD,
                                        size=16,
                                    ),
                                    ft.Container(
                                        content=asset_preview,
                                        padding=10,
                                        border=ft.border.all(
                                            1, ft.colors.OUTLINE_VARIANT
                                        ),
                                        border_radius=10,
                                        width=170,
                                        height=170,
                                        alignment=ft.alignment.center,
                                    ),
                                    selected_asset_info,
                                ],
                                expand=True,
                            ),
                        ]
                    ),
                    ft.Divider(),
                    ft.Text("アセット生成", weight=ft.FontWeight.BOLD, size=16),
                    ft.Row([platform_selector, generate_button]),
                    output_options,
                    ft.Divider(),
                    ft.Text("アセット名の正規化", weight=ft.FontWeight.BOLD, size=16),
                    ft.Row([asset_name_input, normalize_button]),
                ]
            ),
            padding=20,
            expand=True,
        ),
    )

    # アセットプレビューの初期状態
    asset_preview.visible = False

    # 初期スキャン
    update_asset_scanner()


def load_platform_definitions():
    """プラットフォーム定義を読み込む"""
    platform_file = Path(__file__).parent / "platform_assets.json"
    try:
        with open(platform_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"プラットフォーム定義の読み込みエラー: {e}")
        return []


def is_image_file(path):
    """ファイルが画像かどうかを判断する"""
    ext = os.path.splitext(path)[1].lower()
    return ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]


def bytes_to_base64(data):
    """バイトデータをbase64に変換する"""
    import base64

    return base64.b64encode(data).decode("utf-8")


def apply_app_theme(page: ft.Page):
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
