# Python Flet - 多言語対応（i18n/l10n）ガイド

このガイドでは、Python Fletアプリケーションで多言語対応（国際化：i18n、地域化：l10n）を実装するための方法について解説します。様々な言語や地域のユーザーに対応するアプリケーションを効率的に開発するための戦略と実装テクニックを学びましょう。

## 目次

1. [多言語対応の基本原則](#多言語対応の基本原則)
2. [翻訳リソースの管理](#翻訳リソースの管理)
3. [言語の検出と切り替え](#言語の検出と切り替え)
4. [翻訳の適用](#翻訳の適用)
5. [日付・時刻・数値のフォーマット](#日付時刻数値のフォーマット)
6. [RTL（右から左）言語対応](#rtl右から左言語対応)
7. [翻訳管理ワークフロー](#翻訳管理ワークフロー)
8. [実装例とパターン](#実装例とパターン)

## 多言語対応の基本原則

国際化と地域化の基本的な考え方:

### 国際化(i18n)と地域化(l10n)の違い
- **国際化(i18n)**: アプリケーションが様々な言語や地域に適応できるように設計すること
- **地域化(l10n)**: 特定の言語や地域向けのコンテンツやフォーマットに適応すること

### 多言語対応の重要性
- [ ] より広いユーザー層へのアクセス
- [ ] 地域ごとの法的要件への対応
- [ ] ユーザーエクスペリエンスの向上
- [ ] マーケット拡大の機会

### 実装の基本原則
- [ ] テキストをコードから分離する
- [ ] 翻訳リソースを外部ファイルで管理する
- [ ] 動的に言語を切り替える機能を提供する
- [ ] 日付、時刻、数値などのフォーマットを地域に合わせる
- [ ] レイアウトが様々な言語の長さに対応できるようにする
- [ ] RTL（右から左）言語のサポートを考慮する

## 翻訳リソースの管理

効率的な翻訳リソース管理の方法:

### 翻訳ファイル形式

```python
# /app/i18n/locales/ja.json
{
  "app": {
    "title": "マイアプリ",
    "welcome": "ようこそ、{name}さん！"
  },
  "auth": {
    "login": "ログイン",
    "logout": "ログアウト",
    "username": "ユーザー名",
    "password": "パスワード",
    "errors": {
      "invalid_credentials": "ユーザー名またはパスワードが正しくありません"
    }
  },
  "common": {
    "cancel": "キャンセル",
    "save": "保存",
    "delete": "削除",
    "edit": "編集"
  },
  "home": {
    "title": "ホーム",
    "description": "これはホームページです"
  }
}

# /app/i18n/locales/en.json
{
  "app": {
    "title": "My App",
    "welcome": "Welcome, {name}!"
  },
  "auth": {
    "login": "Login",
    "logout": "Logout",
    "username": "Username",
    "password": "Password",
    "errors": {
      "invalid_credentials": "Username or password is incorrect"
    }
  },
  "common": {
    "cancel": "Cancel",
    "save": "Save",
    "delete": "Delete",
    "edit": "Edit"
  },
  "home": {
    "title": "Home",
    "description": "This is the home page"
  }
}
```

### 翻訳マネージャーの実装

```python
# /app/i18n/translation_manager.py
import json
import os
import re
from typing import Dict, Any, Optional, List, Set

class TranslationManager:
    def __init__(self, locales_dir: str, default_locale: str = "en"):
        self.locales_dir = locales_dir
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.available_locales: Set[str] = set()

        # 翻訳ファイルを読み込む
        self._load_translations()

    def _load_translations(self):
        """翻訳ファイルを読み込む"""
        if not os.path.exists(self.locales_dir):
            raise FileNotFoundError(f"Locales directory not found: {self.locales_dir}")

        # 利用可能な言語を探す
        for filename in os.listdir(self.locales_dir):
            if filename.endswith(".json"):
                locale = filename.split(".")[0]
                filepath = os.path.join(self.locales_dir, filename)

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        self.translations[locale] = json.load(f)
                        self.available_locales.add(locale)
                except Exception as e:
                    print(f"Error loading translation file {filepath}: {e}")

        # デフォルト言語が利用可能でない場合はエラー
        if self.default_locale not in self.available_locales:
            if len(self.available_locales) > 0:
                self.default_locale = next(iter(self.available_locales))
            else:
                raise ValueError("No translation files found")

        self.current_locale = self.default_locale

    def get_available_locales(self) -> List[str]:
        """利用可能な言語コードのリストを取得"""
        return list(self.available_locales)

    def set_locale(self, locale: str) -> bool:
        """現在の言語を設定"""
        if locale in self.available_locales:
            self.current_locale = locale
            return True
        return False

    def get_current_locale(self) -> str:
        """現在の言語コードを取得"""
        return self.current_locale

    def translate(self, key: str, params: Optional[Dict[str, Any]] = None) -> str:
        """キーに対応する翻訳を取得"""
        params = params or {}

        # ネストしたキーをパース（例: "app.title"）
        parts = key.split(".")

        # 現在の言語で翻訳を検索
        translation = self._get_nested_translation(self.current_locale, parts)

        # 見つからない場合はデフォルト言語で検索
        if translation is None and self.current_locale != self.default_locale:
            translation = self._get_nested_translation(self.default_locale, parts)

        # それでも見つからない場合はキーをそのまま返す
        if translation is None:
            translation = key

        # パラメータを置換
        if params and isinstance(translation, str):
            for param_key, param_value in params.items():
                placeholder = "{" + param_key + "}"
                translation = translation.replace(placeholder, str(param_value))

        return translation

    def _get_nested_translation(self, locale: str, key_parts: List[str]) -> Optional[str]:
        """ネストした翻訳データから値を取得"""
        if locale not in self.translations:
            return None

        current = self.translations[locale]

        for part in key_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        if not isinstance(current, str):
            return None

        return current

    def reload_translations(self):
        """翻訳を再読み込み"""
        self._load_translations()

# 単一インスタンスとして使用
translation_manager = TranslationManager(os.path.join(os.path.dirname(__file__), "locales"))

# 翻訳関数のショートカット
def t(key: str, params: Optional[Dict[str, Any]] = None) -> str:
    """翻訳を取得する短縮関数"""
    return translation_manager.translate(key, params)
```

### 複数形・性別対応

```python
# /app/i18n/locales/en.json の一部
{
  "items": {
    "count": {
      "zero": "No items",
      "one": "1 item",
      "other": "{count} items"
    }
  },
  "messages": {
    "unread": {
      "zero": "You have no unread messages",
      "one": "You have 1 unread message",
      "other": "You have {count} unread messages"
    }
  }
}

# /app/i18n/locales/ja.json の一部
{
  "items": {
    "count": {
      "zero": "アイテムはありません",
      "one": "1つのアイテム",
      "other": "{count}つのアイテム"
    }
  },
  "messages": {
    "unread": {
      "zero": "未読メッセージはありません",
      "one": "1件の未読メッセージがあります",
      "other": "{count}件の未読メッセージがあります"
    }
  }
}

# 複数形対応機能の追加
# /app/i18n/translation_manager.py に追加

def translate_plural(self, key: str, count: int, params: Optional[Dict[str, Any]] = None) -> str:
    """複数形に対応した翻訳を取得"""
    params = params or {}
    params["count"] = count

    # 複数形カテゴリを決定
    category = self._get_plural_category(count, self.current_locale)

    # 複数形キーを構築（例: "items.count.one"）
    plural_key = f"{key}.{category}"

    # 翻訳を取得
    translation = self.translate(plural_key, params)

    # 該当する複数形カテゴリが見つからない場合は "other" を使用
    if translation == plural_key:
        translation = self.translate(f"{key}.other", params)

    return translation

def _get_plural_category(self, count: int, locale: str) -> str:
    """言語に基づいて複数形カテゴリを取得"""
    # 簡易版：実際のアプリではより完全なプルーラルルールを実装する
    if count == 0:
        return "zero"
    elif count == 1:
        return "one"
    else:
        return "other"

# ショートカット関数
def tp(key: str, count: int, params: Optional[Dict[str, Any]] = None) -> str:
    """複数形翻訳を取得する短縮関数"""
    return translation_manager.translate_plural(key, count, params)
```

## 言語の検出と切り替え

言語設定の管理と言語切り替えの実装:

### システム言語の検出

```python
# /app/i18n/locale_detector.py
import locale
import os
import platform
from typing import Optional

class LocaleDetector:
    @staticmethod
    def detect_system_locale() -> str:
        """システムのロケールを検出"""
        system = platform.system()
        detected_locale = "en"  # デフォルト

        try:
            if system == "Windows":
                # Windowsの場合
                import ctypes
                windll = ctypes.windll.kernel32
                windll.GetUserDefaultUILanguage()
                detected_locale = locale.windows_locale[windll.GetUserDefaultUILanguage()]
            else:
                # macOS, Linuxの場合
                detected_locale = locale.getdefaultlocale()[0]

            # 言語コード部分のみを取得（例: "ja_JP" -> "ja"）
            if detected_locale and "_" in detected_locale:
                detected_locale = detected_locale.split("_")[0]
        except Exception as e:
            print(f"Error detecting system locale: {e}")

        return detected_locale

    @staticmethod
    def detect_browser_locale(page) -> Optional[str]:
        """ブラウザの言語を検出（Web版のみ）"""
        if page.platform == "web":
            # JavaScriptを使用してブラウザの言語を取得
            js_code = """
            (function() {
                // ブラウザの言語設定
                return navigator.language || navigator.userLanguage || "en";
            })();
            """

            try:
                browser_locale = page.eval_js(js_code)

                # 言語コード部分のみを取得（例: "ja-JP" -> "ja"）
                if browser_locale and ("-" in browser_locale):
                    browser_locale = browser_locale.split("-")[0]

                return browser_locale
            except Exception as e:
                print(f"Error detecting browser locale: {e}")

        return None

    @staticmethod
    def detect_best_locale(page, available_locales):
        """最適な言語を検出"""
        # 優先順位：
        # 1. ブラウザの言語（Web版の場合）
        # 2. システムの言語
        # 3. デフォルト（"en"）

        # ブラウザの言語を検出（Web版のみ）
        browser_locale = LocaleDetector.detect_browser_locale(page)
        if browser_locale in available_locales:
            return browser_locale

        # システムの言語を検出
        system_locale = LocaleDetector.detect_system_locale()
        if system_locale in available_locales:
            return system_locale

        # デフォルト言語
        return "en"
```

### 言語設定の保存と読み込み

```python
# /app/i18n/locale_storage.py
from app.core.storage.storage_service import StorageService

class LocaleStorage:
    def __init__(self, storage: StorageService):
        self.storage = storage
        self.key = "app_locale"

    def save_locale(self, locale: str) -> bool:
        """言語設定を保存"""
        return self.storage.set(self.key, locale)

    def load_locale(self) -> str:
        """保存された言語設定を読み込み"""
        return self.storage.get(self.key) or ""

    def clear_locale(self) -> bool:
        """言語設定を削除"""
        return self.storage.delete(self.key)
```

### 言語切り替えUI

```python
# /app/presentation/widgets/language_selector.py
import flet as ft
from app.i18n.translation_manager import translation_manager
from app.i18n.locale_storage import LocaleStorage

class LanguageSelector(ft.UserControl):
    def __init__(self, locale_storage: LocaleStorage, on_locale_change=None):
        super().__init__()
        self.locale_storage = locale_storage
        self.on_locale_change = on_locale_change

        # 言語名のマッピング
        self.language_names = {
            "en": "English",
            "ja": "日本語",
            "fr": "Français",
            "es": "Español",
            "zh": "中文",
            "ko": "한국어",
            "ar": "العربية",
            # 他の言語を追加
        }

    def build(self):
        """UIを構築"""
        # 利用可能な言語を取得
        available_locales = translation_manager.get_available_locales()
        current_locale = translation_manager.get_current_locale()

        # ドロップダウンオプションを作成
        options = [
            ft.dropdown.Option(
                locale,
                self.language_names.get(locale, locale)
            )
            for locale in available_locales
        ]

        self.locale_dropdown = ft.Dropdown(
            options=options,
            value=current_locale,
            on_change=self._on_locale_selected,
            width=150
        )

        return ft.Container(
            content=self.locale_dropdown,
            padding=ft.padding.only(right=10)
        )

    def _on_locale_selected(self, e):
        """言語選択時の処理"""
        selected_locale = self.locale_dropdown.value

        # 言語を設定
        if translation_manager.set_locale(selected_locale):
            # 設定を保存
            self.locale_storage.save_locale(selected_locale)

            # 変更コールバックを呼び出し
            if self.on_locale_change:
                self.on_locale_change(selected_locale)
```

## 翻訳の適用

アプリケーション全体に翻訳を適用する方法:

### 翻訳コンテキスト

```python
# /app/i18n/translation_context.py
import flet as ft
from typing import Dict, Any, Optional, Callable
from app.i18n.translation_manager import translation_manager, t, tp
from app.i18n.locale_storage import LocaleStorage
from app.i18n.locale_detector import LocaleDetector

class TranslationContext:
    def __init__(self, page: ft.Page, locale_storage: LocaleStorage):
        self.page = page
        self.locale_storage = locale_storage
        self.listeners: Dict[str, Callable[[str], None]] = {}
        self.listener_id_counter = 0

    def initialize(self):
        """初期化処理"""
        # 保存された言語設定を読み込み
        saved_locale = self.locale_storage.load_locale()

        if saved_locale and saved_locale in translation_manager.get_available_locales():
            # 保存された言語を設定
            translation_manager.set_locale(saved_locale)
        else:
            # 最適な言語を検出して設定
            best_locale = LocaleDetector.detect_best_locale(
                self.page,
                translation_manager.get_available_locales()
            )
            translation_manager.set_locale(best_locale)
            self.locale_storage.save_locale(best_locale)

    def add_listener(self, callback: Callable[[str], None]) -> str:
        """言語変更リスナーを追加"""
        listener_id = str(self.listener_id_counter)
        self.listener_id_counter += 1
        self.listeners[listener_id] = callback
        return listener_id

    def remove_listener(self, listener_id: str):
        """言語変更リスナーを削除"""
        if listener_id in self.listeners:
            del self.listeners[listener_id]

    def set_locale(self, locale: str) -> bool:
        """言語を設定し、リスナーに通知"""
        if translation_manager.set_locale(locale):
            # 設定を保存
            self.locale_storage.save_locale(locale)

            # リスナーに通知
            for callback in self.listeners.values():
                callback(locale)

            return True

        return False

    def get_current_locale(self) -> str:
        """現在の言語を取得"""
        return translation_manager.get_current_locale()

    def translate(self, key: str, params: Optional[Dict[str, Any]] = None) -> str:
        """翻訳を取得"""
        return t(key, params)

    def translate_plural(self, key: str, count: int, params: Optional[Dict[str, Any]] = None) -> str:
        """複数形対応の翻訳を取得"""
        return tp(key, count, params)

# グローバルコンテキスト（アプリ初期化時に設定）
translation_context = None

def init_translation_context(page: ft.Page, locale_storage: LocaleStorage):
    """翻訳コンテキストを初期化"""
    global translation_context
    translation_context = TranslationContext(page, locale_storage)
    translation_context.initialize()
    return translation_context
```

### 翻訳可能なコンポーネント

```python
# /app/presentation/widgets/translatable.py
import flet as ft
from typing import Dict, Any, Optional, List
from app.i18n.translation_context import translation_context

class TranslatableText(ft.UserControl):
    def __init__(
        self,
        key: str,
        params: Optional[Dict[str, Any]] = None,
        style: Optional[Dict[str, Any]] = None,
        update_on_locale_change: bool = True
    ):
        super().__init__()
        self.key = key
        self.params = params or {}
        self.style = style or {}
        self.update_on_locale_change = update_on_locale_change
        self.listener_id = None

    def build(self):
        """UIを構築"""
        # 翻訳テキストを取得
        translated_text = translation_context.translate(self.key, self.params)

        # スタイルを適用
        text = ft.Text(translated_text)

        for prop, value in self.style.items():
            if hasattr(text, prop):
                setattr(text, prop, value)

        self.text_control = text
        return text

    def did_mount(self):
        """マウント時の処理"""
        if self.update_on_locale_change:
            # 言語変更リスナーを登録
            self.listener_id = translation_context.add_listener(self._on_locale_change)

    def will_unmount(self):
        """アンマウント時の処理"""
        if self.listener_id:
            # リスナーを削除
            translation_context.remove_listener(self.listener_id)

    def _on_locale_change(self, locale: str):
        """言語変更時の処理"""
        if self.text_control:
            # テキストを更新
            self.text_control.value = translation_context.translate(self.key, self.params)
            self.update()

class TranslatablePluralText(TranslatableText):
    def __init__(
        self,
        key: str,
        count: int,
        params: Optional[Dict[str, Any]] = None,
        style: Optional[Dict[str, Any]] = None,
        update_on_locale_change: bool = True
    ):
        super().__init__(key, params, style, update_on_locale_change)
        self.count = count

    def build(self):
        """UIを構築"""
        # 複数形対応の翻訳テキストを取得
        translated_text = translation_context.translate_plural(self.key, self.count, self.params)

        # スタイルを適用
        text = ft.Text(translated_text)

        for prop, value in self.style.items():
            if hasattr(text, prop):
                setattr(text, prop, value)

        self.text_control = text
        return text

    def _on_locale_change(self, locale: str):
        """言語変更時の処理"""
        if self.text_control:
            # テキストを更新
            self.text_control.value = translation_context.translate_plural(
                self.key, self.count, self.params
            )
            self.update()
```

### 翻訳のホットリロード

```python
# /app/i18n/translation_manager.py に追加

def reload_all_translatable_components(page: ft.Page):
    """アプリ内の全ての翻訳可能コンポーネントを更新"""
    def _update_controls(controls: List[ft.Control]):
        if not controls:
            return

        for control in controls:
            # TranslatableTextコンポーネントの場合
            if hasattr(control, "_on_locale_change"):
                control._on_locale_change(self.current_locale)

            # 子コントロールを再帰的に更新
            if hasattr(control, "controls") and control.controls:
                _update_controls(control.controls)
            elif hasattr(control, "content") and control.content:
                if isinstance(control.content, list):
                    _update_controls(control.content)
                else:
                    _update_controls([control.content])

    # ページの全てのビューを更新
    for view in page.views:
        _update_controls(view.controls)

    page.update()
```

## 日付・時刻・数値のフォーマット

地域に合わせたフォーマット:

### フォーマッターの実装

```python
# /app/i18n/formatters.py
import locale
import datetime
from typing import Optional, Union
from babel.dates import format_date, format_time, format_datetime
from babel.numbers import format_number, format_decimal, format_percent, format_currency

class LocaleFormatter:
    def __init__(self, locale_code: str):
        self.locale_code = locale_code

    def set_locale(self, locale_code: str):
        """ロケールを設定"""
        self.locale_code = locale_code

    def format_date(
        self,
        date: Union[datetime.date, datetime.datetime, str],
        format: str = "medium"
    ) -> str:
        """日付をフォーマット"""
        if isinstance(date, str):
            try:
                date = datetime.datetime.fromisoformat(date)
            except ValueError:
                return date

        return format_date(date, format=format, locale=self.locale_code)

    def format_time(
        self,
        time: Union[datetime.time, datetime.datetime, str],
        format: str = "medium"
    ) -> str:
        """時刻をフォーマット"""
        if isinstance(time, str):
            try:
                time = datetime.datetime.fromisoformat(time)
            except ValueError:
                return time

        return format_time(time, format=format, locale=self.locale_code)

    def format_datetime(
        self,
        dt: Union[datetime.datetime, str],
        format: str = "medium"
    ) -> str:
        """日時をフォーマット"""
        if isinstance(dt, str):
            try:
                dt = datetime.datetime.fromisoformat(dt)
            except ValueError:
                return dt

        return format_datetime(dt, format=format, locale=self.locale_code)

    def format_number(self, number: Union[int, float, str], format: str = "#,##0.##") -> str:
        """数値をフォーマット"""
        if isinstance(number, str):
            try:
                number = float(number)
            except ValueError:
                return number

        return format_decimal(number, format=format, locale=self.locale_code)

    def format_percent(self, number: Union[float, str], format: str = "#,##0%") -> str:
        """パーセントをフォーマット"""
        if isinstance(number, str):
            try:
                number = float(number)
            except ValueError:
                return number

        return format_percent(number, format=format, locale=self.locale_code)

    def format_currency(
        self,
        number: Union[int, float, str],
        currency: str,
        format: Optional[str] = None
    ) -> str:
        """通貨をフォーマット"""
        if isinstance(number, str):
            try:
                number = float(number)
            except ValueError:
                return number

        return format_currency(number, currency, format=format, locale=self.locale_code)

# 翻訳コンテキストに連動したフォーマッター
class TranslationContextFormatter:
    def __init__(self, translation_context):
        self.translation_context = translation_context
        self.formatter = LocaleFormatter(translation_context.get_current_locale())

        # 言語変更時にフォーマッターを更新
        self.translation_context.add_listener(self._on_locale_change)

    def _on_locale_change(self, locale: str):
        """言語変更時の処理"""
        self.formatter.set_locale(locale)

    # LocaleFormatterの各メソッドの委譲
    def format_date(self, date, format="medium"):
        return self.formatter.format_date(date, format)

    def format_time(self, time, format="medium"):
        return self.formatter.format_time(time, format)

    def format_datetime(self, dt, format="medium"):
        return self.formatter.format_datetime(dt, format)

    def format_number(self, number, format="#,##0.##"):
        return self.formatter.format_number(number, format)

    def format_percent(self, number, format="#,##0%"):
        return self.formatter.format_percent(number, format)

    def format_currency(self, number, currency, format=None):
        return self.formatter.format_currency(number, currency, format)

# グローバルフォーマッター（翻訳コンテキスト初期化後に設定）
formatter = None

def init_formatter(translation_context):
    """フォーマッターを初期化"""
    global formatter
    formatter = TranslationContextFormatter(translation_context)
    return formatter
```

### フォーマット可能なコンポーネント

```python
# /app/presentation/widgets/formattable.py
import flet as ft
from typing import Optional, Union, Dict, Any
import datetime
from app.i18n.formatters import formatter

class FormattableDate(ft.UserControl):
    def __init__(
        self,
        date: Union[datetime.date, datetime.datetime, str],
        format: str = "medium",
        style: Optional[Dict[str, Any]] = None,
        update_on_locale_change: bool = True
    ):
        super().__init__()
        self.date = date
        self.format = format
        self.style = style or {}
        self.update_on_locale_change = update_on_locale_change

    def build(self):
        """UIを構築"""
        # 日付をフォーマット
        formatted_date = formatter.format_date(self.date, self.format)

        # スタイルを適用
        text = ft.Text(formatted_date)

        for prop, value in self.style.items():
            if hasattr(text, prop):
                setattr(text, prop, value)

        self.text_control = text
        return text

    def did_mount(self):
        """マウント時の処理"""
        if self.update_on_locale_change:
            # 言語変更時の更新処理を追加
            pass

class FormattableCurrency(ft.UserControl):
    def __init__(
        self,
        amount: Union[int, float, str],
        currency: str,
        format: Optional[str] = None,
        style: Optional[Dict[str, Any]] = None,
        update_on_locale_change: bool = True
    ):
        super().__init__()
        self.amount = amount
        self.currency = currency
        self.format = format
        self.style = style or {}
        self.update_on_locale_change = update_on_locale_change

    def build(self):
        """UIを構築"""
        # 金額をフォーマット
        formatted_amount = formatter.format_currency(self.amount, self.currency, self.format)

        # スタイルを適用
        text = ft.Text(formatted_amount)

        for prop, value in self.style.items():
            if hasattr(text, prop):
                setattr(text, prop, value)

        self.text_control = text
        return text

    def did_mount(self):
        """マウント時の処理"""
        if self.update_on_locale_change:
            # 言語変更時の更新処理を追加
            pass
```

## RTL（右から左）言語対応

RTL言語をサポートするためのレイアウト調整:

### RTL対応のレイアウト

```python
# /app/i18n/direction_manager.py
from typing import List, Set

class DirectionManager:
    def __init__(self):
        # RTL（右から左）言語のリスト
        self.rtl_locales: Set[str] = {
            "ar",  # アラビア語
            "he",  # ヘブライ語
            "fa",  # ペルシャ語
            "ur",  # ウルドゥー語
            # その他のRTL言語
        }

    def is_rtl(self, locale: str) -> bool:
        """RTL言語かどうかを判定"""
        if not locale:
            return False

        # 言語コード部分のみを取得（例: "ar-EG" -> "ar"）
        if "-" in locale:
            locale = locale.split("-")[0]

        return locale in self.rtl_locales

    def get_text_direction(self, locale: str) -> str:
        """テキスト方向を取得"""
        return "rtl" if self.is_rtl(locale) else "ltr"

    def get_flex_direction(self, locale: str, base_direction: str = "row") -> str:
        """RTL対応のFlex方向を取得"""
        if not self.is_rtl(locale):
            return base_direction

        # RTL言語の場合は方向を反転
        if base_direction == "row":
            return "row-reverse"
        elif base_direction == "row-reverse":
            return "row"

        return base_direction

    def get_padding(self, locale: str, left: int = 0, right: int = 0) -> tuple:
        """RTL対応のパディングを取得"""
        if not self.is_rtl(locale):
            return (left, right)

        # RTL言語の場合は左右を入れ替え
        return (right, left)

    def get_margin(self, locale: str, left: int = 0, right: int = 0) -> tuple:
        """RTL対応のマージンを取得"""
        if not self.is_rtl(locale):
            return (left, right)

        # RTL言語の場合は左右を入れ替え
        return (right, left)

    def get_alignment(self, locale: str, ltr_alignment: str) -> str:
        """RTL対応の配置を取得"""
        if not self.is_rtl(locale):
            return ltr_alignment

        # RTL言語の場合は左右を入れ替え
        alignment_map = {
            ft.MainAxisAlignment.START: ft.MainAxisAlignment.END,
            ft.MainAxisAlignment.END: ft.MainAxisAlignment.START,
            ft.CrossAxisAlignment.START: ft.CrossAxisAlignment.END,
            ft.CrossAxisAlignment.END: ft.CrossAxisAlignment.START,
            ft.TextAlign.LEFT: ft.TextAlign.RIGHT,
            ft.TextAlign.RIGHT: ft.TextAlign.LEFT,
        }

        return alignment_map.get(ltr_alignment, ltr_alignment)

# グローバルインスタンス
direction_manager = DirectionManager()

# 翻訳コンテキストと連携
class TranslationAwareDirectionManager:
    def __init__(self, translation_context):
        self.translation_context = translation_context
        self.direction_manager = direction_manager

    def is_rtl(self) -> bool:
        """現在の言語がRTLかどうかを判定"""
        return self.direction_manager.is_rtl(
            self.translation_context.get_current_locale()
        )

    def get_text_direction(self) -> str:
        """現在の言語のテキスト方向を取得"""
        return self.direction_manager.get_text_direction(
            self.translation_context.get_current_locale()
        )

    def get_flex_direction(self, base_direction: str = "row") -> str:
        """現在の言語に対応したFlex方向を取得"""
        return self.direction_manager.get_flex_direction(
            self.translation_context.get_current_locale(),
            base_direction
        )

    def get_padding(self, left: int = 0, right: int = 0) -> tuple:
        """現在の言語に対応したパディングを取得"""
        return self.direction_manager.get_padding(
            self.translation_context.get_current_locale(),
            left,
            right
        )

    def get_margin(self, left: int = 0, right: int = 0) -> tuple:
        """現在の言語に対応したマージンを取得"""
        return self.direction_manager.get_margin(
            self.translation_context.get_current_locale(),
            left,
            right
        )

    def get_alignment(self, ltr_alignment: str) -> str:
        """現在の言語に対応した配置を取得"""
        return self.direction_manager.get_alignment(
            self.translation_context.get_current_locale(),
            ltr_alignment
        )

# グローバル変数（翻訳コンテキスト初期化後に設定）
rtl_manager = None

def init_rtl_manager(translation_context):
    """RTLマネージャーを初期化"""
    global rtl_manager
    rtl_manager = TranslationAwareDirectionManager(translation_context)
    return rtl_manager
```

### RTL対応のコンポーネント

```python
# /app/presentation/widgets/rtl_aware.py
import flet as ft
from typing import List, Optional
from app.i18n.direction_manager import rtl_manager

class RTLAwareRow(ft.UserControl):
    def __init__(
        self,
        controls: Optional[List[ft.Control]] = None,
        spacing: int = 0,
        alignment: str = ft.MainAxisAlignment.START,
        vertical_alignment: str = ft.CrossAxisAlignment.CENTER,
        expand: bool = False,
        update_on_locale_change: bool = True
    ):
        super().__init__()
        self.original_controls = controls or []
        self.spacing = spacing
        self.original_alignment = alignment
        self.vertical_alignment = vertical_alignment
        self.expand = expand
        self.update_on_locale_change = update_on_locale_change
        self.row = None

    def build(self):
        """UIを構築"""
        # RTL対応の方向と配置を取得
        flex_direction = rtl_manager.get_flex_direction("row")
        alignment = rtl_manager.get_alignment(self.original_alignment)

        # 子コントロールをRTL対応に調整
        controls = list(self.original_controls)
        if rtl_manager.is_rtl():
            controls.reverse()

        # Rowコンポーネントを作成
        self.row = ft.Row(
            controls=controls,
            spacing=self.spacing,
            alignment=alignment,
            vertical_alignment=self.vertical_alignment,
            expand=self.expand
        )

        return self.row

    def did_mount(self):
        """マウント時の処理"""
        if self.update_on_locale_change:
            # 言語変更時の更新処理を追加
            pass

class RTLAwareContainer(ft.UserControl):
    def __init__(
        self,
        content: Optional[ft.Control] = None,
        padding: Optional[int] = None,
        padding_left: int = 0,
        padding_right: int = 0,
        alignment: str = None,
        update_on_locale_change: bool = True
    ):
        super().__init__()
        self.content = content
        self.base_padding = padding
        self.padding_left = padding_left
        self.padding_right = padding_right
        self.original_alignment = alignment
        self.update_on_locale_change = update_on_locale_change
        self.container = None

    def build(self):
        """UIを構築"""
        # RTL対応のパディングを取得
        padding = self.base_padding

        if self.padding_left > 0 or self.padding_right > 0:
            left, right = rtl_manager.get_padding(self.padding_left, self.padding_right)
            padding = ft.padding.only(left=left, right=right)

        # RTL対応の配置を取得
        alignment = self.original_alignment
        if alignment and rtl_manager.is_rtl():
            alignment = rtl_manager.get_alignment(alignment)

        # Containerコンポーネントを作成
        self.container = ft.Container(
            content=self.content,
            padding=padding,
            alignment=alignment
        )

        return self.container

    def did_mount(self):
        """マウント時の処理"""
        if self.update_on_locale_change:
            # 言語変更時の更新処理を追加
            pass
```

## 翻訳管理ワークフロー

効率的な翻訳管理と更新:

### 翻訳の抽出と読み込み

```python
# /scripts/extract_translations.py
import os
import json
import re
from typing import Set, Dict, Any

def extract_translation_keys(directory: str) -> Set[str]:
    """ソースコードから翻訳キーを抽出"""
    translation_keys = set()

    # 翻訳関数の正規表現パターン
    patterns = [
        r't\(["\']([^"\']+)["\']',  # t("key") または t('key')
        r'translate\(["\']([^"\']+)["\']',  # translate("key") または translate('key')
        r'translate_plural\(["\']([^"\']+)["\']',  # translate_plural("key") または translate_plural('key')
        r'tp\(["\']([^"\']+)["\']',  # tp("key") または tp('key')
        r'TranslatableText\(["\']([^"\']+)["\']',  # TranslatableText("key") または TranslatableText('key')
        r'key=["\']([^"\']+)["\']'  # key="key" または key='key'（TranslatableTextコンポーネント内）
    ]

    # ディレクトリ内のPythonファイルを検索
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                        # 各パターンでキーを抽出
                        for pattern in patterns:
                            matches = re.findall(pattern, content)
                            translation_keys.update(matches)
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")

    return translation_keys

def load_translations(file_path: str) -> Dict[str, Any]:
    """翻訳ファイルを読み込む"""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading translation file {file_path}: {e}")

    return {}

def save_translations(file_path: str, translations: Dict[str, Any]):
    """翻訳ファイルを保存"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(translations, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving translation file {file_path}: {e}")

def update_translations(keys: Set[str], translations: Dict[str, Any]) -> Dict[str, Any]:
    """キーに基づいて翻訳辞書を更新"""
    nested_keys = {}

    # ネストしたキー構造を構築
    for key in keys:
        parts = key.split(".")
        current = nested_keys

        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                # 最後の部分はキーとして設定
                if part not in current:
                    current[part] = key  # 元のキーを値として設定
            else:
                # 中間部分は辞書として設定
                if part not in current:
                    current[part] = {}
                current = current[part]

    # 既存の翻訳を保持しながら新しいキーを追加
    def update_dict(src, dest):
        for key, value in src.items():
            if isinstance(value, dict):
                if key not in dest:
                    dest[key] = {}
                elif not isinstance(dest[key], dict):
                    # キーが既に存在するが辞書でない場合は辞書に変換
                    dest[key] = {}

                update_dict(value, dest[key])
            else:
                # 翻訳キーが既に存在する場合はスキップ
                if key not in dest:
                    dest[key] = ""  # 新しいキーの翻訳は空文字列

    # 既存の翻訳にネストしたキーを追加
    update_dict(nested_keys, translations)

    return translations

def main():
    # ソースディレクトリ
    src_directory = "app"

    # 翻訳ファイルディレクトリ
    locales_directory = os.path.join("app", "i18n", "locales")

    # 翻訳キーを抽出
    translation_keys = extract_translation_keys(src_directory)
    print(f"Found {len(translation_keys)} translation keys")

    # 言語ファイルを取得
    locale_files = [f for f in os.listdir(locales_directory) if f.endswith(".json")]

    if not locale_files:
        # 初期言語ファイルを作成
        default_locales = ["en.json", "ja.json"]

        for locale_file in default_locales:
            file_path = os.path.join(locales_directory, locale_file)
            translations = update_translations(translation_keys, {})
            save_translations(file_path, translations)
            print(f"Created new translation file: {locale_file}")
    else:
        # 既存の言語ファイルを更新
        for locale_file in locale_files:
            file_path = os.path.join(locales_directory, locale_file)
            translations = load_translations(file_path)
            updated_translations = update_translations(translation_keys, translations)
            save_translations(file_path, updated_translations)
            print(f"Updated translation file: {locale_file}")

if __name__ == "__main__":
    main()
```

### 翻訳の状況確認

```python
# /scripts/check_translations.py
import os
import json
from typing import Dict, Any, Set, List

def load_translations(file_path: str) -> Dict[str, Any]:
    """翻訳ファイルを読み込む"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading translation file {file_path}: {e}")
        return {}

def flatten_translations(translations: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
    """ネストした翻訳辞書をフラットな形式に変換"""
    result = {}

    for key, value in translations.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            # 再帰的に処理
            nested = flatten_translations(value, full_key)
            result.update(nested)
        else:
            result[full_key] = value

    return result

def check_translations(reference_locale: str, locales_directory: str) -> Dict[str, Dict[str, Any]]:
    """各言語ファイルの翻訳状況をチェック"""
    # リファレンス言語ファイルを読み込む
    reference_file = os.path.join(locales_directory, f"{reference_locale}.json")
    reference_translations = load_translations(reference_file)
    flattened_reference = flatten_translations(reference_translations)

    # 結果を格納する辞書
    results = {}

    # 各言語ファイルをチェック
    for filename in os.listdir(locales_directory):
        if filename.endswith(".json") and filename != f"{reference_locale}.json":
            locale = filename[:-5]  # .jsonを除去
            file_path = os.path.join(locales_directory, filename)

            # 翻訳ファイルを読み込む
            translations = load_translations(file_path)
            flattened = flatten_translations(translations)

            # 統計情報を計算
            total_keys = len(flattened_reference)
            translated_keys = 0
            missing_keys = []

            for key, value in flattened_reference.items():
                if key in flattened and flattened[key] and flattened[key] != value:
                    translated_keys += 1
                else:
                    missing_keys.append(key)

            # 完了率を計算
            completion_rate = (translated_keys / total_keys) * 100 if total_keys > 0 else 0

            # 結果を格納
            results[locale] = {
                "total_keys": total_keys,
                "translated_keys": translated_keys,
                "missing_keys": missing_keys,
                "completion_rate": completion_rate
            }

    return results

def print_results(results: Dict[str, Dict[str, Any]]):
    """結果を表示"""
    print("\n翻訳の状況:")
    print("-" * 60)
    print(f"{'言語':10} | {'完了率':8} | {'翻訳済み':8} / {'合計':8}")
    print("-" * 60)

    # 完了率でソート
    sorted_results = sorted(
        results.items(),
        key=lambda x: x[1]["completion_rate"],
        reverse=True
    )

    for locale, result in sorted_results:
        completion_rate = result["completion_rate"]
        translated_keys = result["translated_keys"]
        total_keys = result["total_keys"]

        print(f"{locale:10} | {completion_rate:7.1f}% | {translated_keys:8} / {total_keys:8}")

    print("\n未翻訳のキー:")
    print("-" * 60)

    for locale, result in sorted_results:
        if result["missing_keys"]:
            print(f"\n{locale}:")
            for key in result["missing_keys"]:
                print(f"  - {key}")

def main():
    # 翻訳ファイルディレクトリ
    locales_directory = os.path.join("app", "i18n", "locales")

    # リファレンス言語（基準となる言語）
    reference_locale = "en"

    # 翻訳状況をチェック
    results = check_translations(reference_locale, locales_directory)

    # 結果を表示
    print_results(results)

if __name__ == "__main__":
    main()
```

## 実装例とパターン

実際のアプリケーションでの多言語対応実装例:

### アプリ初期化

```python
# /main.py
import flet as ft
import os
from app.core.storage.storage_factory import StorageFactory
from app.i18n.translation_context import init_translation_context
from app.i18n.formatters import init_formatter
from app.i18n.direction_manager import init_rtl_manager
from app.i18n.locale_storage import LocaleStorage
from app.presentation.widgets.language_selector import LanguageSelector

def main(page: ft.Page):
    # ストレージサービスを初期化
    storage = StorageFactory.get_storage(page)

    # 言語設定ストレージを初期化
    locale_storage = LocaleStorage(storage)

    # 翻訳コンテキストを初期化
    translation_context = init_translation_context(page, locale_storage)

    # フォーマッターを初期化
    formatter = init_formatter(translation_context)

    # RTLマネージャーを初期化
    rtl_manager = init_rtl_manager(translation_context)

    # 言語切り替え処理
    def on_locale_change(locale):
        # アプリ全体を更新
        page.update()

    # 言語切り替えUIを作成
    language_selector = LanguageSelector(locale_storage, on_locale_change)

    # アプリケーションのUIを構築
    from app.presentation.app import App
    app = App(page)

    # 言語切り替えUIをアプリバーに追加
    app.app_bar.actions.append(language_selector)

    # ページにアプリを追加
    page.add(app)

ft.app(target=main)
```

### 多言語対応のページ例

```python
# /app/presentation/pages/settings_page.py
import flet as ft
from app.i18n.translation_context import translation_context as tc, t
from app.i18n.formatters import formatter
from app.i18n.direction_manager import rtl_manager
from app.presentation.widgets.translatable import TranslatableText, TranslatablePluralText
from app.presentation.widgets.rtl_aware import RTLAwareContainer, RTLAwareRow
from datetime import datetime

class SettingsPage(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.notification_count = 3

    def build(self):
        """UIを構築"""
        # RTL対応のフレックス方向
        flex_direction = rtl_manager.get_flex_direction()

        # RTL対応のパディング
        left_padding, right_padding = rtl_manager.get_padding(10, 20)

        # RTL対応のテキスト配置
        text_align = "left" if not rtl_manager.is_rtl() else "right"

        # 翻訳テキスト
        title = TranslatableText(
            "settings.title",
            style={"size": 24, "weight": ft.FontWeight.BOLD, "text_align": text_align}
        )

        description = TranslatableText(
            "settings.description",
            style={"size": 16, "text_align": text_align}
        )

        # 複数形対応の翻訳テキスト
        notification_text = TranslatablePluralText(
            "settings.notifications.count",
            self.notification_count,
            {"count": self.notification_count},
            style={"size": 14, "color": ft.colors.BLUE}
        )

        # フォーマットされた日付
        current_date = datetime.now()
        formatted_date = formatter.format_date(current_date)
        date_text = ft.Text(f"{t('settings.last_updated')}: {formatted_date}")

        # 通貨のフォーマット
        price = 1299.99
        currency_code = "USD"
        formatted_price = formatter.format_currency(price, currency_code)
        price_text = ft.Text(f"{t('settings.subscription.price')}: {formatted_price}")

        # RTL対応のレイアウト
        language_row = RTLAwareRow(
            controls=[
                ft.Text(t("settings.language")),
                ft.Dropdown(
                    options=[
                        ft.dropdown.Option("en", "English"),
                        ft.dropdown.Option("ja", "日本語"),
                        ft.dropdown.Option("ar", "العربية")
                    ],
                    value=tc.get_current_locale(),
                    on_change=self._on_language_change
                )
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # 設定項目
        settings_container = RTLAwareContainer(
            content=ft.Column([
                language_row,
                ft.Divider(),
                RTLAwareRow(
                    controls=[
                        ft.Text(t("settings.theme")),
                        ft.RadioGroup(
                            content=ft.Row([
                                ft.Radio(value="light", label=t("settings.theme.light")),
                                ft.Radio(value="dark", label=t("settings.theme.dark"))
                            ])
                        )
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                RTLAwareRow(
                    controls=[
                        ft.Text(t("settings.notifications")),
                        ft.Switch(value=True)
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                notification_text
            ]),
            padding=10,
            padding_left=left_padding,
            padding_right=right_padding
        )

        # ボタンを含むフッター
        footer = RTLAwareRow(
            controls=[
                ft.ElevatedButton(
                    text=t("common.cancel"),
                    on_click=self._on_cancel
                ),
                ft.ElevatedButton(
                    text=t("common.save"),
                    on_click=self._on_save
                )
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.END
        )

        return ft.Column([
            title,
            description,
            ft.Divider(),
            settings_container,
            date_text,
            price_text,
            footer
        ], spacing=20, expand=True)

    def _on_language_change(self, e):
        """言語変更時の処理"""
        # 言語を設定
        tc.set_locale(e.control.value)

    def _on_cancel(self, e):
        """キャンセルボタン押下時の処理"""
        # 前の画面に戻る
        self.page.go("/")

    def _on_save(self, e):
        """保存ボタン押下時の処理"""
        # 設定を保存
        self.page.snack_bar = ft.SnackBar(content=ft.Text(t("settings.saved")))
        self.page.snack_bar.open = True
        self.page.update()

        # 前の画面に戻る
        self.page.go("/")
```

### 翻訳されたエラーメッセージの表示

```python
# /app/presentation/widgets/error_message.py
import flet as ft
from app.i18n.translation_context import t
from app.data.api.api_client import ApiException

class ErrorMessage(ft.UserControl):
    def __init__(self, error, visible=True):
        super().__init__()
        self.error = error
        self.visible = visible

    def build(self):
        """UIを構築"""
        # エラーメッセージの取得
        message = self._get_localized_error_message()

        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.ERROR_OUTLINE, color=ft.colors.RED_500),
                ft.Text(message, color=ft.colors.RED_700)
            ], spacing=5),
            visible=self.visible,
            padding=10,
            border_radius=5,
            bgcolor=ft.colors.RED_50
        )

    def _get_localized_error_message(self):
        """ローカライズされたエラーメッセージを取得"""
        if isinstance(self.error, ApiException):
            # APIエラーの場合
            status_code = self.error.status_code

            # ステータスコードに対応するエラーキーを作成
            error_key = f"errors.api.{status_code}"

            # 翻訳されたエラーメッセージを取得
            translated = t(error_key)

            # 翻訳が見つからない場合はデフォルトメッセージを使用
            if translated == error_key:
                return t("errors.api.default", {"message": self.error.message})

            return translated
        elif isinstance(self.error, str):
            # 文字列の場合はそのまま翻訳
            if self.error.startswith("errors."):
                return t(self.error)
            else:
                return self.error
        else:
            # その他のエラーの場合はデフォルトメッセージ
            return t("errors.unknown")
```

このガイドに従って多言語対応を実装することで、グローバルなユーザーに対応したアプリケーションを効率的に開発できます。言語や地域に関わらず、一貫した高品質のユーザーエクスペリエンスを提供するために、適切な国際化と地域化の戦略を取り入れましょう。特に、テキストの外部化、自動的な言語検出、RTL言語のサポート、適切な日付・時刻・数値フォーマットの実装が重要です。
