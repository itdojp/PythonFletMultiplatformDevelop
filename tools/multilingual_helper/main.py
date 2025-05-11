import flet as ft
import json
import os
import re
from pathlib import Path
import shutil

def main(page: ft.Page):
    page.title = "Flet 多言語対応ヘルパー"
    page.theme_mode = ft.ThemeMode.SYSTEM
    
    # テーマ設定
    apply_app_theme(page)
    
    # 作業ディレクトリ
    working_dir = ft.TextField(
        label="プロジェクトディレクトリ",
        value=os.path.expanduser("~"),
        width=600,
        hint_text="翻訳ファイルを生成するプロジェクトディレクトリ"
    )
    
    # 翻訳ファイルの出力ディレクトリ
    def select_dir(_):
        def result_handler(e: ft.FilePickerResultEvent):
            if e.path:
                working_dir.value = e.path
                page.update()
        
        file_picker = ft.FilePicker(on_result=result_handler)
        page.overlay.append(file_picker)
        page.update()
        file_picker.get_directory_path()
    
    browse_button = ft.ElevatedButton("参照", on_click=select_dir, icon=ft.icons.FOLDER_OPEN)
    
    # 言語リスト
    language_data = load_language_templates()
    available_languages = [lang["locale"] for lang in language_data]
    
    selected_languages = []
    
    language_checkboxes = []
    for lang in language_data:
        checkbox = ft.Checkbox(
            label=f"{lang['language']} ({lang['locale']})",
            value=lang["locale"] == "ja",  # デフォルトで日本語を選択
        )
        language_checkboxes.append(checkbox)
    
    # 新しい翻訳キーの追加セクション
    translation_category = ft.Dropdown(
        label="カテゴリ",
        options=[
            ft.dropdown.Option("common"),
            ft.dropdown.Option("errors"),
            ft.dropdown.Option("auth"),
            ft.dropdown.Option("navigation"),
            ft.dropdown.Option("new"),
        ],
        width=200
    )
    
    new_category = ft.TextField(
        label="新しいカテゴリ名",
        width=200,
        visible=False
    )
    
    def on_category_change(e):
        new_category.visible = translation_category.value == "new"
        page.update()
    
    translation_category.on_change = on_category_change
    
    translation_key = ft.TextField(
        label="翻訳キー",
        width=200,
        hint_text="例: submit_button"
    )
    
    # 各言語の翻訳入力フィールド
    translation_fields = {}
    translations_container = ft.Column(spacing=10)
    
    def update_translation_fields():
        translations_container.controls.clear()
        translation_fields.clear()
        
        selected_langs = [
            lang for i, lang in enumerate(language_data) 
            if language_checkboxes[i].value
        ]
        
        for lang in selected_langs:
            field = ft.TextField(
                label=f"{lang['language']} ({lang['locale']})",
                width=400,
                hint_text=f"{lang['locale']}での翻訳テキスト"
            )
            translation_fields[lang["locale"]] = field
            translations_container.controls.append(field)
        
        page.update()
    
    # 言語選択に変更があったとき
    for checkbox in language_checkboxes:
        checkbox.on_change = lambda _: update_translation_fields()
    
    # 初期表示
    update_translation_fields()
    
    # 翻訳の追加ボタン
    def add_translation(_):
        if not translation_key.value:
            page.snack_bar = ft.SnackBar(content=ft.Text("翻訳キーを入力してください"))
            page.snack_bar.open = True
            page.update()
            return
        
        # カテゴリの確定
        category = new_category.value if translation_category.value == "new" else translation_category.value
        
        if not category:
            page.snack_bar = ft.SnackBar(content=ft.Text("カテゴリを選択または入力してください"))
            page.snack_bar.open = True
            page.update()
            return
        
        # 翻訳データの収集
        translations = {}
        for locale, field in translation_fields.items():
            translations[locale] = field.value
        
        # 翻訳リストに追加
        key = translation_key.value
        if key not in all_translations:
            all_translations[key] = {"category": category, "translations": translations}
        
        # フィールドのクリア
        translation_key.value = ""
        for field in translation_fields.values():
            field.value = ""
        
        # 翻訳リストを更新
        update_translations_list()
        
        page.snack_bar = ft.SnackBar(content=ft.Text(f"翻訳「{key}」が追加されました"))
        page.snack_bar.open = True
        page.update()
    
    add_button = ft.ElevatedButton("翻訳を追加", on_click=add_translation, icon=ft.icons.ADD)
    
    # 追加された翻訳リスト
    all_translations = {}
    translations_list = ft.ListView(spacing=2, height=200)
    
    # 翻訳リストの更新
    def update_translations_list():
        translations_list.controls.clear()
        
        for key, data in all_translations.items():
            category = data["category"]
            translations = data["translations"]
            
            # 最初の翻訳を表示用に取得
            sample_translation = next(iter(translations.values()), "")
            
            translations_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.icons.TRANSLATE),
                    title=ft.Text(key),
                    subtitle=ft.Text(f"[{category}] {sample_translation}"),
                    trailing=ft.IconButton(
                        icon=ft.icons.DELETE,
                        tooltip="削除",
                        on_click=lambda e, k=key: remove_translation(k)
                    )
                )
            )
        
        page.update()
    
    # 翻訳の削除
    def remove_translation(key):
        if key in all_translations:
            del all_translations[key]
            update_translations_list()
            
            page.snack_bar = ft.SnackBar(content=ft.Text(f"翻訳「{key}」が削除されました"))
            page.snack_bar.open = True
            page.update()
    
    # RTL (右から左)プレビュー
    rtl_preview = ft.Container(
        content=ft.Column([
            ft.Text("RTLレイアウトプレビュー", weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("قائمة المستخدم", text_align=ft.TextAlign.RIGHT),
                        ft.TextField(
                            text_align=ft.TextAlign.RIGHT,
                            label="اسم المستخدم",
                            width=200
                        ),
                        ft.TextField(
                            text_align=ft.TextAlign.RIGHT,
                            label="كلمة المرور",
                            password=True,
                            width=200
                        ),
                        ft.Row([
                            ft.ElevatedButton("إلغاء"),
                            ft.ElevatedButton("تسجيل الدخول", bgcolor=ft.colors.PRIMARY)
                        ], alignment=ft.MainAxisAlignment.END)
                    ]),
                    width=300,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=8,
                    padding=10,
                    alignment=ft.alignment.center_right
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        ]),
        visible=False
    )
    
    # RTLプレビューの切り替え
    def toggle_rtl_preview(e):
        rtl_preview.visible = not rtl_preview.visible
        page.update()
    
    rtl_button = ft.TextButton(
        "RTLプレビューを表示",
        on_click=toggle_rtl_preview,
        icon=ft.icons.FORMAT_TEXTDIRECTION_R_TO_L
    )
    
    # 翻訳ファイルの生成
    def generate_translation_files(e):
        if not working_dir.value:
            page.snack_bar = ft.SnackBar(content=ft.Text("プロジェクトディレクトリを選択してください"))
            page.snack_bar.open = True
            page.update()
            return
        
        if not all_translations:
            page.snack_bar = ft.SnackBar(content=ft.Text("翻訳が追加されていません"))
            page.snack_bar.open = True
            page.update()
            return
        
        # 選択された言語を取得
        selected_langs = [
            lang for i, lang in enumerate(language_data) 
            if language_checkboxes[i].value
        ]
        
        if not selected_langs:
            page.snack_bar = ft.SnackBar(content=ft.Text("少なくとも1つの言語を選択してください"))
            page.snack_bar.open = True
            page.update()
            return
        
        # 翻訳ディレクトリを作成
        translations_dir = Path(working_dir.value) / "translations"
        translations_dir.mkdir(exist_ok=True, parents=True)
        
        # コード生成用にカテゴリ別に翻訳をグループ化
        categorized_translations = {}
        for key, data in all_translations.items():
            category = data["category"]
            if category not in categorized_translations:
                categorized_translations[category] = {}
            
            categorized_translations[category][key] = data["translations"]
        
        # 各言語の翻訳ファイルを生成
        for lang in selected_langs:
            locale = lang["locale"]
            lang_file = translations_dir / f"{locale}.json"
            
            # 各言語の翻訳を抽出
            translations = {}
            for category, keys in categorized_translations.items():
                if category not in translations:
                    translations[category] = {}
                
                for key, values in keys.items():
                    if locale in values and values[locale]:
                        translations[category][key] = values[locale]
                    else:
                        # 翻訳がない場合は英語または最初に利用可能な翻訳を使用
                        translations[category][key] = values.get("en", next(iter(values.values()), key))
            
            # JSONファイルとして保存
            with open(lang_file, "w", encoding="utf-8") as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
        
        # Pythonのユーティリティコードを生成
        utils_file = translations_dir / "i18n.py"
        
        # 翻訳ユーティリティのコードテンプレート
        code = """
# i18n.py - Flet 多言語対応ユーティリティ
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class I18n:
    def __init__(self, default_locale: str = "en"):
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.available_locales = []
        self._load_translations()
    
    def _load_translations(self):
        """すべての利用可能な翻訳を読み込む"""
        translations_dir = Path(__file__).parent
        
        # 利用可能な翻訳ファイルをスキャン
        for file in translations_dir.glob("*.json"):
            locale = file.stem
            self.available_locales.append(locale)
            
            with open(file, "r", encoding="utf-8") as f:
                self.translations[locale] = json.load(f)
    
    def set_locale(self, locale: str) -> bool:
        """現在のロケールを設定する"""
        if locale in self.available_locales:
            self.current_locale = locale
            return True
        return False
    
    def get(self, key: str, params: Optional[Dict[str, str]] = None) -> str:
        """翻訳テキストを取得する。形式: 'category.key'"""
        if not key or "." not in key:
            return key
        
        category, text_key = key.split(".", 1)
        
        # 現在のロケールで翻訳を取得、なければデフォルトロケールを使用
        translations = self.translations.get(self.current_locale, {})
        category_dict = translations.get(category, {})
        text = category_dict.get(text_key)
        
        if text is None:
            # 現在のロケールで見つからない場合、デフォルトロケールで試す
            fallback = self.translations.get(self.default_locale, {})
            fallback_category = fallback.get(category, {})
            text = fallback_category.get(text_key, key)
        
        # パラメータの置換
        if params and text:
            for param_key, param_value in params.items():
                text = text.replace("{" + param_key + "}", str(param_value))
        
        return text
    
    def get_direction(self) -> str:
        """現在のロケールの文字方向（LTR/RTL）を取得"""
        # RTLの言語リスト
        rtl_locales = ["ar", "he", "fa", "ur"]
        return "rtl" if self.current_locale in rtl_locales else "ltr"
    
    @property
    def locale(self) -> str:
        """現在のロケールを取得"""
        return self.current_locale

# シングルトンインスタンス
_i18n = None

def get_i18n(default_locale: str = "en") -> I18n:
    """I18nインスタンスを取得（初回呼び出し時に初期化）"""
    global _i18n
    if _i18n is None:
        _i18n = I18n(default_locale)
    return _i18n

# 使用例:
# i18n = get_i18n("ja")
# text = i18n.get("common.save")
# formatted_text = i18n.get("errors.min_length", {"field": "名前", "min": "3"})
"""
        
        with open(utils_file, "w", encoding="utf-8") as f:
            f.write(code.strip())
        
        # サンプルコードを生成
        sample_file = translations_dir / "sample_usage.py"
        
        sample_code = """
# Flet多言語対応のサンプルコード
import flet as ft
from i18n import get_i18n

def main(page: ft.Page):
    page.title = "Flet多言語化サンプル"
    
    # 翻訳インスタンスを初期化（デフォルトは日本語）
    i18n = get_i18n("ja")
    
    # 言語選択ドロップダウン
    language_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("ja", "日本語"),
            ft.dropdown.Option("en", "English"),
            ft.dropdown.Option("zh", "中文"),
            ft.dropdown.Option("ar", "العربية")
        ],
        value=i18n.locale,
        width=200
    )
    
    # 各UIコンポーネントの参照を保持
    ui_components = {}
    
    def create_ui():
        # サンプルUIの作成
        return ft.Column([
            ft.Text(i18n.get("navigation.dashboard"), size=30, weight=ft.FontWeight.BOLD),
            
            ft.TextField(
                label=i18n.get("auth.email"),
                hint_text="example@example.com"
            ),
            
            ft.TextField(
                label=i18n.get("auth.password"),
                password=True
            ),
            
            ft.Row([
                ft.Checkbox(label=i18n.get("auth.remember_me")),
                ft.TextButton(i18n.get("auth.forgot_password"))
            ]),
            
            ft.Row([
                ft.ElevatedButton(i18n.get("common.cancel")),
                ft.ElevatedButton(
                    i18n.get("auth.login"),
                    bgcolor=ft.colors.PRIMARY
                )
            ], alignment=ft.MainAxisAlignment.END),
            
            # エラーメッセージの例
            ft.Container(
                content=ft.Text(
                    i18n.get("errors.min_length", {"field": i18n.get("auth.password"), "min": "8"})
                ),
                bgcolor=ft.colors.RED_100,
                padding=10,
                border_radius=5,
                visible=True
            )
        ])
    
    # UI更新関数
    def update_ui():
        # 文字方向の設定
        page.rtl = i18n.get_direction() == "rtl"
        
        # 新しいUIを作成し直す
        page.controls = [
            ft.AppBar(title=ft.Text("Flet I18n Demo")),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("言語選択:"),
                        language_dropdown
                    ]),
                    ft.Divider(),
                    create_ui()
                ]),
                padding=20
            )
        ]
        page.update()
    
    # 言語変更時の処理
    def on_language_change(e):
        i18n.set_locale(language_dropdown.value)
        update_ui()
    
    language_dropdown.on_change = on_language_change
    
    # 初期UI表示
    update_ui()

ft.app(target=main)
"""
        
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write(sample_code.strip())
        
        # 生成完了メッセージ
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"{len(selected_langs)}言語の翻訳ファイルが生成されました"),
            action="OK"
        )
        page.snack_bar.open = True
        page.update()
    
    generate_button = ft.ElevatedButton(
        "翻訳ファイルを生成",
        on_click=generate_translation_files,
        icon=ft.icons.FILE_DOWNLOAD,
        bgcolor=ft.colors.PRIMARY
    )
    
    # レイアウト
    page.add(
        ft.AppBar(
            title=ft.Text("Flet 多言語対応ヘルパー"),
            center_title=True,
            bgcolor=ft.colors.SURFACE_VARIANT
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("プロジェクト設定", weight=ft.FontWeight.BOLD, size=16),
                ft.Row([
                    working_dir,
                    browse_button
                ]),
                
                ft.Divider(),
                
                ft.Text("対応言語の選択", weight=ft.FontWeight.BOLD, size=16),
                ft.Row([
                    ft.Column(
                        controls=language_checkboxes[:len(language_checkboxes)//2],
                        spacing=5
                    ),
                    ft.Column(
                        controls=language_checkboxes[len(language_checkboxes)//2:],
                        spacing=5
                    ),
                ]),
                
                ft.Divider(),
                
                ft.Text("翻訳の追加", weight=ft.FontWeight.BOLD, size=16),
                ft.Row([
                    translation_category,
                    new_category,
                    translation_key
                ]),
                translations_container,
                add_button,
                
                ft.Divider(),
                
                ft.Text("追加された翻訳", weight=ft.FontWeight.BOLD, size=16),
                translations_list,
                
                rtl_button,
                rtl_preview,
                
                ft.Divider(),
                
                ft.Container(
                    content=generate_button,
                    alignment=ft.alignment.center
                )
            ]),
            padding=20,
            expand=True
        )
    )

def load_language_templates():
    """言語テンプレートを読み込む"""
    template_file = Path(__file__).parent / "language_templates.json"
    try:
        with open(template_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"言語テンプレートの読み込みエラー: {e}")
        return []

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
