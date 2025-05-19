# Python Flet - プラットフォーム共通コード管理ガイド

> **対象Fletバージョン**: 0.19.0以上
>
> **最終更新日**: 2025年5月10日
>
> **注意**: Fletは活発に開発が進んでいるフレームワークです。最新の情報は[Flet公式ドキュメント](https://flet.dev/docs/)を参照してください。

このガイドでは、Python Fletを使用したマルチプラットフォーム開発において、効率的にコードを共有し、プラットフォーム固有の実装を管理するための戦略と手法を解説します。

> **関連ガイド**:
> - [マルチプラットフォームアーキテクチャ設計ガイド](./architecture-design-guide.md) - アプリ全体のアーキテクチャと依存性注入の設計
> - [UI/UXデザインガイドライン](./ui-ux-design-guidelines.md) - レスポンシブデザインとアダプティブUIの実装
> - [マルチプラットフォーム開発の流れ](./python-flet-multiplatform-guide.md) - 開発プロセス全体の概要

## 目次

1. [プラットフォーム共通コードの原則](#プラットフォーム共通コードの原則)
2. [プラットフォーム検出と分岐](#プラットフォーム検出と分岐)
3. [抽象化とインターフェース設計](#抽象化とインターフェース設計)
4. [プラットフォーム固有機能の実装](#プラットフォーム固有機能の実装)
5. [レスポンシブ設計とアダプティブUI](#レスポンシブ設計とアダプティブui)
6. [アセットとリソース管理](#アセットとリソース管理)
7. [デバイス機能へのアクセス](#デバイス機能へのアクセス)
8. [パフォーマンス最適化](#パフォーマンス最適化)
9. [実装例とパターン](#実装例とパターン)

## プラットフォーム共通コードの原則

マルチプラットフォーム開発における重要な原則:

### DRY原則(Don't Repeat Yourself)
- [ ] ビジネスロジックを共通コードとして一度だけ実装する
- [ ] データモデルとビジネスルールを全プラットフォームで共有する
- [ ] ユーティリティ関数とヘルパーを共通化する

### 共有コードと固有コードの境界設計
- [ ] 共有可能なコアコンポーネントを特定
- [ ] プラットフォーム固有のコードを明確に分離
- [ ] インターフェース経由で共通コードと固有コードを連携

### コードの整理原則
- [ ] 機能別にコードを整理する
- [ ] 共通コードとプラットフォーム固有コードを別フォルダに分離
- [ ] 依存関係を明確に管理する

## プラットフォーム検出と分岐

Fletでのプラットフォーム検出と条件分岐の実装方法:

### プラットフォーム検出

Fletでは、`page.platform`プロパティを使用して現在実行中のプラットフォームを検出できます:

```python
def main(page: ft.Page):
    platform = page.platform
    print(f"Running on platform: {platform}")

    # プラットフォームに基づいた処理
    if platform == "android" or platform == "ios":
        # モバイル向け処理
        pass
    elif platform == "windows" or platform == "macos" or platform == "linux":
        # デスクトップ向け処理
        pass
    else:
        # Web向け処理
        pass
```

### プラットフォーム分岐パターン

#### 条件分岐によるインライン実装

単純なケースでは直接条件分岐で処理:

```python
def create_action_button(page: ft.Page, text, on_click):
    if page.platform == "android":
        # Androidスタイルのボタン
        return ft.ElevatedButton(
            text=text,
            on_click=on_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_500
            )
        )
    elif page.platform == "ios":
        # iOSスタイルのボタン
        return ft.ElevatedButton(
            text=text,
            on_click=on_click,
            style=ft.ButtonStyle(
                shape=ft.StadiumBorder(),
                color=ft.colors.BLUE_500,
                bgcolor=ft.colors.WHITE,
                side=ft.BorderSide(1, ft.colors.BLUE_500)
            )
        )
    else:
        # Web/デスクトップ向けボタン
        return ft.ElevatedButton(
            text=text,
            on_click=on_click
        )
```

#### ファクトリーパターンによる実装分離

複雑なケースではファクトリーを使った実装:

```python
# /app/platform/button_factory.py
import flet as ft

class ButtonFactory:
    @staticmethod
    def create_primary_button(platform, text, on_click):
        if platform == "android":
            return AndroidButtonFactory.create_primary_button(text, on_click)
        elif platform == "ios":
            return IOSButtonFactory.create_primary_button(text, on_click)
        else:
            return WebButtonFactory.create_primary_button(text, on_click)

class AndroidButtonFactory:
    @staticmethod
    def create_primary_button(text, on_click):
        return ft.ElevatedButton(
            text=text,
            on_click=on_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_500
            )
        )

class IOSButtonFactory:
    @staticmethod
    def create_primary_button(text, on_click):
        return ft.ElevatedButton(
            text=text,
            on_click=on_click,
            style=ft.ButtonStyle(
                shape=ft.StadiumBorder(),
                color=ft.colors.BLUE_500,
                bgcolor=ft.colors.WHITE,
                side=ft.BorderSide(1, ft.colors.BLUE_500)
            )
        )

class WebButtonFactory:
    @staticmethod
    def create_primary_button(text, on_click):
        return ft.ElevatedButton(
            text=text,
            on_click=on_click
        )

# 使用例
def main(page: ft.Page):
    action_button = ButtonFactory.create_primary_button(
        page.platform, "Click Me", on_click=lambda e: print("Clicked")
    )
    page.add(action_button)
```

### プラットフォーム分岐のベストプラクティス

- [ ] 細かい分岐を避け、大きな機能単位で分ける
- [ ] デザインシステムを通じて抽象化レベルを上げる
- [ ] 過度の分岐は避け、可能な限り共通コードを使用する
- [ ] ビジネスロジックにはプラットフォーム分岐を入れない（UI層のみ）

## 抽象化とインターフェース設計

効果的なコード共有のための抽象化戦略:

### 抽象クラスとインターフェース

```python
# /app/platform/storage/storage_interface.py
from abc import ABC, abstractmethod

class StorageInterface(ABC):
    @abstractmethod
    def save(self, key: str, value: str) -> bool:
        """データを保存する"""
        pass

    @abstractmethod
    def load(self, key: str) -> str:
        """データを読み込む"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """データを削除する"""
        pass

# プラットフォーム固有の実装
# /app/platform/storage/web_storage.py
from app.platform.storage.storage_interface import StorageInterface
import json

class WebStorage(StorageInterface):
    """Web版のストレージ実装（localStorage使用）"""
    def __init__(self, page):
        self.page = page

    def save(self, key: str, value: str) -> bool:
        try:
            # JavaScriptのlocalStorageを使用
            js_code = f"localStorage.setItem('{key}', '{value}')"
            self.page.eval_js(js_code)
            return True
        except Exception as e:
            print(f"WebStorage save error: {e}")
            return False

    def load(self, key: str) -> str:
        try:
            js_code = f"localStorage.getItem('{key}')"
            result = self.page.eval_js(js_code)
            return result if result is not None else ""
        except Exception as e:
            print(f"WebStorage load error: {e}")
            return ""

    def delete(self, key: str) -> bool:
        try:
            js_code = f"localStorage.removeItem('{key}')"
            self.page.eval_js(js_code)
            return True
        except Exception as e:
            print(f"WebStorage delete error: {e}")
            return False

# /app/platform/storage/mobile_storage.py
from app.platform.storage.storage_interface import StorageInterface
import os
import json

class MobileStorage(StorageInterface):
    """モバイル版のストレージ実装（ファイル使用）"""
    def __init__(self, page):
        self.page = page
        self.storage_dir = os.path.join(os.path.expanduser("~"), ".my_app")
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_file_path(self, key):
        return os.path.join(self.storage_dir, f"{key}.dat")

    def save(self, key: str, value: str) -> bool:
        try:
            with open(self._get_file_path(key), "w") as f:
                f.write(value)
            return True
        except Exception as e:
            print(f"MobileStorage save error: {e}")
            return False

    def load(self, key: str) -> str:
        try:
            file_path = self._get_file_path(key)
            if not os.path.exists(file_path):
                return ""
            with open(file_path, "r") as f:
                return f.read()
        except Exception as e:
            print(f"MobileStorage load error: {e}")
            return ""

    def delete(self, key: str) -> bool:
        try:
            file_path = self._get_file_path(key)
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"MobileStorage delete error: {e}")
            return False

# ファクトリークラスでプラットフォーム固有実装を提供
# /app/platform/storage/storage_factory.py
from app.platform.storage.storage_interface import StorageInterface
from app.platform.storage.web_storage import WebStorage
from app.platform.storage.mobile_storage import MobileStorage

class StorageFactory:
    @staticmethod
    def get_storage(page) -> StorageInterface:
        platform = page.platform
        if platform == "android" or platform == "ios":
            return MobileStorage(page)
        else:
            return WebStorage(page)

# 使用例
def main(page: ft.Page):
    storage = StorageFactory.get_storage(page)

    # プラットフォームに関係なく同じインターフェースで使用
    storage.save("user_settings", json.dumps({"theme": "dark"}))
    settings = json.loads(storage.load("user_settings") or "{}")

    # UIの構築
    # ...
```

### 依存性注入による柔軟な構成

```python
# /app/core/di/service_locator.py
class ServiceLocator:
    _services = {}

    @classmethod
    def register(cls, interface_name, implementation):
        cls._services[interface_name] = implementation

    @classmethod
    def get(cls, interface_name):
        return cls._services.get(interface_name)

# アプリの初期化時にプラットフォームに応じた実装を登録
def setup_platform_services(page):
    from app.platform.storage.storage_factory import StorageFactory
    from app.platform.notification.notification_factory import NotificationFactory

    # プラットフォーム固有のサービスを登録
    ServiceLocator.register("storage", StorageFactory.get_storage(page))
    ServiceLocator.register("notification", NotificationFactory.get_notification(page))

# 使用例
class SettingsController:
    def __init__(self):
        # 必要なサービスを取得
        self.storage = ServiceLocator.get("storage")

    def save_settings(self, settings):
        return self.storage.save("settings", json.dumps(settings))

    def load_settings(self):
        settings_json = self.storage.load("settings")
        return json.loads(settings_json) if settings_json else {}
```

### 抽象化と状態管理の連携

「アーキテクチャ設計ガイド」で説明されている状態管理の概念は、プラットフォーム固有の実装と密接に関連しています。各プラットフォームの特性を活かしながら一貫した状態管理を実現するためには、以下のような連携が効果的です：

1. **プラットフォーム固有の永続化**: データの永続化はプラットフォームごとに異なる実装（AndroidのSharedPreferences、iOSのUserDefaults、WebのlocalStorage）を使用しますが、抽象インターフェースを通して統一的に扱えます。

2. **状態の同期**: グローバル状態オブジェクトとプラットフォーム固有の実装を連携させることで、状態変更を永続化したり、ネイティブ機能と同期させたりできます。

```python
# グローバル状態とプラットフォーム固有実装の連携例
class AppStateWithPlatformSync:
    def __init__(self, page):
        self.platform = page.platform
        # プラットフォーム固有のストレージを取得
        self.storage = ServiceLocator.get("storage")
        self.theme_mode = self._load_setting("theme_mode", "light")
        self._listeners = []

    def _load_setting(self, key, default_value):
        # プラットフォーム固有のストレージから設定を読み込む
        stored_value = self.storage.load(key)
        return stored_value if stored_value else default_value

    def _save_setting(self, key, value):
        # プラットフォーム固有のストレージに設定を保存
        self.storage.save(key, value)

    def add_listener(self, listener):
        self._listeners.append(listener)

    def remove_listener(self, listener):
        self._listeners.remove(listener)

    def notify_listeners(self):
        for listener in self._listeners:
            listener()

    def set_theme_mode(self, mode):
        self.theme_mode = mode
        # プラットフォーム固有のストレージに保存
        self._save_setting("theme_mode", mode)
        # リスナーに通知
        self.notify_listeners()
```

この例では、抽象化されたストレージインターフェースを使って、アプリの状態をプラットフォーム固有の方法で永続化しています。これにより、各プラットフォームで最適な実装を使いながら、アプリケーションコードはプラットフォームの違いを意識せずに状態を管理できます。

## プラットフォーム固有機能の実装

各プラットフォームで異なる機能の実装方法:

### 抽象機能インターフェースとプラグイン

```python
# /app/platform/camera/camera_interface.py
from abc import ABC, abstractmethod
from typing import Callable, Optional

class CameraInterface(ABC):
    @abstractmethod
    def take_photo(self, on_capture: Callable[[str], None]) -> bool:
        """写真を撮影する"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """カメラが利用可能かチェック"""
        pass

# プラットフォーム固有の実装
# /app/platform/camera/android_camera.py
from app.platform.camera.camera_interface import CameraInterface
import subprocess
import tempfile
import os

class AndroidCamera(CameraInterface):
    def __init__(self, page):
        self.page = page

    def is_available(self) -> bool:
        # 実際のアプリではFlutterのメソッドチャネルを通じて
        # ネイティブコードでチェックする必要があります
        return True

    def take_photo(self, on_capture: Callable[[str], None]) -> bool:
        # Androidのカメラ機能を呼び出す擬似コード
        # 実際にはFlutterのメソッドチャネルを使用して
        # Android APIを呼び出す必要があります
        try:
            # このコードは実際には動作しませんが、
            # Flutter/Androidネイティブコードとの連携概念を示しています
            temp_file = os.path.join(tempfile.gettempdir(), "camera_photo.jpg")

            # 擬似コード: ネイティブカメラAPIを呼び出す
            # result = self.page.invoke_method("takePhoto", {"save_path": temp_file})

            # 実際には上記の代わりにFletの機能を使ってFlutterのカメラプラグインを呼び出す

            # 成功したと仮定
            if os.path.exists(temp_file):
                on_capture(temp_file)
                return True
            return False
        except Exception as e:
            print(f"Camera error: {e}")
            return False

# /app/platform/camera/web_camera.py
from app.platform.camera.camera_interface import CameraInterface
import tempfile
import os
import base64

class WebCamera(CameraInterface):
    def __init__(self, page):
        self.page = page

    def is_available(self) -> bool:
        # WebブラウザでMediaDevicesをチェック
        js_code = """
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            return true;
        } else {
            return false;
        }
        """
        return self.page.eval_js(js_code) == True

    def take_photo(self, on_capture: Callable[[str], None]) -> bool:
        # Web用のカメラアクセスコード
        js_code = """
        // この例ではブラウザにカメラUIを表示し写真を撮影
        // カメラからの画像をBase64エンコードして返す擬似コード
        try {
            // カメラにアクセス
            navigator.mediaDevices.getUserMedia({video: true})
                .then(function(stream) {
                    // 処理を実装
                    // 実際にはここでカメラのUIを表示し、写真を撮影、
                    // Base64エンコードされた画像を返す処理を実装

                    // 仮の成功レスポンス
                    return "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD...";
                });
            return true;
        } catch (e) {
            console.error("Camera error:", e);
            return false;
        }
        """
        try:
            # 実際には上記のコードを実行し、結果のBase64データを取得
            # base64_data = self.page.eval_js(js_code)

            # テスト用の擬似レスポンス
            base64_data = "仮のBase64データ"

            # Base64データをファイルに保存
            if base64_data and base64_data.startswith("data:image/jpeg;base64,"):
                # Base64部分を抽出
                base64_str = base64_data.replace("data:image/jpeg;base64,", "")

                # 一時ファイルに保存
                temp_file = os.path.join(tempfile.gettempdir(), "web_camera_photo.jpg")
                with open(temp_file, "wb") as f:
                    f.write(base64.b64decode(base64_str))

                on_capture(temp_file)
                return True
            return False
        except Exception as e:
            print(f"Web camera error: {e}")
            return False

# ファクトリークラス
# /app/platform/camera/camera_factory.py
from app.platform.camera.camera_interface import CameraInterface
from app.platform.camera.android_camera import AndroidCamera
from app.platform.camera.ios_camera import IOSCamera  # 別途実装
from app.platform.camera.web_camera import WebCamera
from app.platform.camera.desktop_camera import DesktopCamera  # 別途実装

class CameraFactory:
    @staticmethod
    def get_camera(page) -> CameraInterface:
        platform = page.platform
        if platform == "android":
            return AndroidCamera(page)
        elif platform == "ios":
            return IOSCamera(page)
        elif platform in ["windows", "macos", "linux"]:
            return DesktopCamera(page)
        else:
            return WebCamera(page)
```

### プラットフォーム検出および機能チェック

```python
# /app/core/platform/platform_info.py
class PlatformInfo:
    def __init__(self, page):
        self.page = page
        self.platform = page.platform

    def is_mobile(self):
        return self.platform in ["android", "ios"]

    def is_desktop(self):
        return self.platform in ["windows", "macos", "linux"]

    def is_web(self):
        return not (self.is_mobile() or self.is_desktop())

    def has_feature(self, feature_name):
        # 機能の利用可能性チェック
        features = {
            "camera": self._has_camera,
            "gps": self._has_gps,
            "notification": self._has_notification,
            "biometric": self._has_biometric,
        }

        checker = features.get(feature_name)
        if checker:
            return checker()
        return False

    def _has_camera(self):
        # カメラ機能チェック
        if self.is_web():
            js_code = "!!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)"
            return self.page.eval_js(js_code) == True
        return self.is_mobile()  # モバイルデバイスならカメラありと仮定

    def _has_gps(self):
        # GPS機能チェック
        if self.is_web():
            js_code = "!!(navigator.geolocation)"
            return self.page.eval_js(js_code) == True
        return self.is_mobile()  # モバイルデバイスならGPSありと仮定

    def _has_notification(self):
        # 通知機能チェック
        if self.is_web():
            js_code = "!!(window.Notification)"
            return self.page.eval_js(js_code) == True
        return True  # その他のプラットフォームでは通知可能と仮定

    def _has_biometric(self):
        # 生体認証チェック
        return self.is_mobile()  # 単純化: モバイルのみ対応と仮定

# 使用例
def main(page: ft.Page):
    platform_info = PlatformInfo(page)

    # 機能によってUIを調整
    if platform_info.has_feature("camera"):
        page.add(ft.ElevatedButton("写真を撮る", on_click=take_photo))

    if platform_info.is_mobile():
        # モバイル向け特殊UIを表示
        pass
```

## レスポンシブ設計とアダプティブUI

プラットフォームに適応したUIの実装:

### レスポンシブレイアウト

```python
# /app/presentation/responsive/responsive_layout.py
import flet as ft

class ResponsiveLayout:
    # 画面サイズの境界値
    MOBILE_BREAKPOINT = 600
    TABLET_BREAKPOINT = 960

    def __init__(self, page: ft.Page):
        self.page = page
        page.on_resize = self._handle_resize
        self._update_layout()

    def _handle_resize(self, e):
        self._update_layout()

    def _update_layout(self):
        width = self.page.width

        # 画面サイズのカテゴリを判定
        if width < self.MOBILE_BREAKPOINT:
            self.screen_category = "mobile"
        elif width < self.TABLET_BREAKPOINT:
            self.screen_category = "tablet"
        else:
            self.screen_category = "desktop"

        # レイアウトアップデートイベントをディスパッチ
        if hasattr(self, "on_layout_change"):
            self.on_layout_change(self.screen_category)

    def get_column_count(self):
        """現在の画面サイズに適したグリッドカラム数を返す"""
        if self.screen_category == "mobile":
            return 1
        elif self.screen_category == "tablet":
            return 2
        else:
            return 4

    def get_container_width(self):
        """コンテンツコンテナの適切な幅を返す"""
        if self.screen_category == "mobile":
            return self.page.width * 0.95  # 95%幅
        elif self.screen_category == "tablet":
            return self.page.width * 0.85  # 85%幅
        else:
            return min(1200, self.page.width * 0.75)  # 最大1200px

    def get_padding(self):
        """画面サイズに適したパディングを返す"""
        if self.screen_category == "mobile":
            return 8
        elif self.screen_category == "tablet":
            return 16
        else:
            return 24

    def create_responsive_row(self, controls):
        """画面サイズに応じて行または列に変換するコンテナを返す"""
        if self.screen_category == "mobile":
            # モバイルでは垂直に積み重ねる
            return ft.Column(controls, spacing=self.get_padding())
        else:
            # その他では水平に配置
            return ft.Row(controls, spacing=self.get_padding())

# 使用例
def main(page: ft.Page):
    responsive = ResponsiveLayout(page)

    # レイアウト変更時の処理
    def on_layout_change(screen_category):
        # 画面カテゴリに基づいてUIを更新
        if screen_category == "mobile":
            # モバイル向けUIを表示
            navigation.visible = False
            app_bar.leading = ft.IconButton(icon=ft.icons.MENU, on_click=show_drawer)
        else:
            # デスクトップ向けUIを表示
            navigation.visible = True
            app_bar.leading = None
        page.update()

    responsive.on_layout_change = on_layout_change

    # レスポンシブなコンテナの作成
    def create_content():
        container_width = responsive.get_container_width()
        padding = responsive.get_padding()

        # 画面サイズに応じたコンテンツレイアウト
        content_layout = responsive.create_responsive_row([
            ft.Container(content=ft.Text("サイドバー"), width=200),
            ft.VerticalDivider(),
            ft.Container(content=ft.Text("メインコンテンツ"), expand=True)
        ])

        return ft.Container(
            content=content_layout,
            width=container_width,
            padding=padding,
            bgcolor=ft.colors.BACKGROUND
        )

    # アプリケーションUI
    app_bar = ft.AppBar(title=ft.Text("レスポンシブアプリ"))
    navigation = ft.NavigationRail(
        visible=responsive.screen_category != "mobile",
        destinations=[
            ft.NavigationRailDestination(icon=ft.icons.HOME, label="ホーム"),
            ft.NavigationRailDestination(icon=ft.icons.SETTINGS, label="設定")
        ]
    )

    def show_drawer(e):
        page.show_drawer(ft.Drawer(
            content=ft.Column([
                ft.ListTile(title=ft.Text("ホーム"), leading=ft.Icon(ft.icons.HOME)),
                ft.ListTile(title=ft.Text("設定"), leading=ft.Icon(ft.icons.SETTINGS))
            ])
        ))

    content = create_content()

    # 画面レイアウトを構築
    page.add(
        app_bar,
        ft.Row([
            navigation,
            ft.VerticalDivider(visible=navigation.visible),
            content
        ], expand=True)
    )
```

### アダプティブUIコンポーネント

```python
# /app/presentation/adaptive/adaptive_components.py
import flet as ft

class AdaptiveComponents:
    def __init__(self, page: ft.Page):
        self.page = page
        self.platform = page.platform

    def create_list_item(self, title, subtitle=None, leading=None, trailing=None):
        """プラットフォーム固有のリストアイテムを作成"""
        if self.platform == "android":
            # Androidマテリアルデザインスタイル
            return ft.ListTile(
                title=ft.Text(title),
                subtitle=ft.Text(subtitle) if subtitle else None,
                leading=leading,
                trailing=trailing,
                dense=True
            )
        elif self.platform == "ios":
            # iOS風スタイル
            # トレーリングアイコンを矢印に変更
            ios_trailing = ft.Icon(ft.icons.ARROW_FORWARD_IOS, size=16) if trailing is None else trailing

            return ft.Container(
                content=ft.Row([
                    leading if leading else ft.Container(width=0),
                    ft.Column([
                        ft.Text(title),
                        ft.Text(subtitle, size=12, color=ft.colors.GREY_600) if subtitle else ft.Container()
                    ], spacing=2, expand=True),
                    ios_trailing
                ], spacing=10),
                padding=ft.padding.symmetric(vertical=12, horizontal=16),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.GREY_300))
            )
        else:
            # Web/デスクトップ標準スタイル
            return ft.ListTile(
                title=ft.Text(title),
                subtitle=ft.Text(subtitle) if subtitle else None,
                leading=leading,
                trailing=trailing
            )

    def create_app_bar(self, title, actions=None):
        """プラットフォーム固有のアプリバーを作成"""
        if self.platform == "android":
            # Android風AppBar
            return ft.AppBar(
                title=ft.Text(title),
                center_title=False,
                bgcolor=ft.colors.BLUE_500,
                actions=actions
            )
        elif self.platform == "ios":
            # iOS風ナビゲーションバー
            return ft.Container(
                content=ft.Row([
                    ft.Text(title, weight=ft.FontWeight.BOLD),
                    ft.Row(actions) if actions else ft.Container()
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=ft.colors.WHITE,
                border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.GREY_300)),
                padding=ft.padding.only(left=16, right=16, top=12, bottom=12)
            )
        else:
            # 標準AppBar
            return ft.AppBar(
                title=ft.Text(title),
                center_title=True,
                bgcolor=ft.colors.BLUE_700,
                actions=actions
            )

    def create_bottom_navigation(self, items):
        """プラットフォーム固有のボトムナビゲーションを作成"""
        if self.platform == "android":
            # Android風ボトムナビ
            return ft.NavigationBar(
                destinations=[
                    ft.NavigationDestination(icon=item["icon"], label=item["label"])
                    for item in items
                ]
            )
        elif self.platform == "ios":
            # iOS風タブバー
            return ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Icon(item["icon"], size=24),
                        ft.Text(item["label"], size=12)
                    ], spacing=4, alignment=ft.MainAxisAlignment.CENTER, expand=True)
                    for item in items
                ]),
                bgcolor=ft.colors.WHITE,
                border=ft.border.only(top=ft.BorderSide(1, ft.colors.GREY_300)),
                padding=ft.padding.only(top=6, bottom=6)
            )
        else:
            # Web/デスクトップ向けナビゲーション
            return ft.Tabs(
                tabs=[
                    ft.Tab(
                        text=item["label"],
                        icon=item["icon"]
                    )
                    for item in items
                ]
            )

# 使用例
def main(page: ft.Page):
    adaptive = AdaptiveComponents(page)

    # プラットフォーム固有のリストアイテム
    list_item = adaptive.create_list_item(
        "タイトル",
        "サブタイトル",
        leading=ft.Icon(ft.icons.PERSON),
        trailing=ft.Icon(ft.icons.DELETE)
    )

    # プラットフォーム固有のアプリバー
    app_bar = adaptive.create_app_bar(
        "マイアプリ",
        actions=[
            ft.IconButton(ft.icons.SEARCH),
            ft.IconButton(ft.icons.MORE_VERT)
        ]
    )

    # プラットフォーム固有のボトムナビゲーション
    bottom_nav = adaptive.create_bottom_navigation([
        {"icon": ft.icons.HOME, "label": "ホーム"},
        {"icon": ft.icons.SEARCH, "label": "検索"},
        {"icon": ft.icons.PERSON, "label": "プロフィール"}
    ])

    # アプリケーションUIを構築
    page.add(
        app_bar,
        list_item,
        bottom_nav
    )
```

## アセットとリソース管理

複数プラットフォームでのアセット管理:

### アセット解決戦略

```python
# /app/core/assets/asset_resolver.py
import os
import flet as ft

class AssetResolver:
    def __init__(self, page: ft.Page):
        self.page = page
        self.platform = page.platform

        # ディレクトリ構造
        self.base_dir = "assets"
        self.image_dir = "images"
        self.fonts_dir = "fonts"
        self.data_dir = "data"

    def get_image_path(self, image_name, density=None):
        """プラットフォームとディスプレイ密度に適した画像パスを返す"""
        # 基本パス
        base_path = f"{self.base_dir}/{self.image_dir}"

        # プラットフォーム固有のディレクトリ
        platform_specific = None
        if self.platform == "android":
            platform_specific = "android"
        elif self.platform == "ios":
            platform_specific = "ios"
        elif self.platform in ["windows", "macos", "linux"]:
            platform_specific = "desktop"
        else:
            platform_specific = "web"

        # 密度別ディレクトリ
        density_dir = ""
        if density:
            density_dir = f"/{density}"

        # パスの優先順位:
        # 1. プラットフォーム+密度固有 (/android/2x/image.png)
        # 2. プラットフォーム固有 (/android/image.png)
        # 3. 密度固有 (/2x/image.png)
        # 4. 基本画像 (/image.png)
        paths_to_check = [
            f"{base_path}/{platform_specific}{density_dir}/{image_name}",
            f"{base_path}/{platform_specific}/{image_name}",
            f"{base_path}{density_dir}/{image_name}",
            f"{base_path}/{image_name}"
        ]

        # 最初に見つかったパスを返す
        for path in paths_to_check:
            if self._asset_exists(path):
                return path

        # デフォルトパス
        return f"{base_path}/{image_name}"

    def get_font(self, font_name):
        """プラットフォームに適したフォントを返す"""
        # プラットフォーム別フォントマッピング
        platform_fonts = {
            "android": {
                "sans": "Roboto",
                "serif": "Noto Serif"
            },
            "ios": {
                "sans": "SF Pro",
                "serif": "New York"
            },
            "desktop": {
                "sans": "Segoe UI" if self.platform == "windows" else "SF Pro",
                "serif": "Georgia"
            },
            "web": {
                "sans": "Helvetica, Arial, sans-serif",
                "serif": "Times New Roman, serif"
            }
        }

        # プラットフォームカテゴリを取得
        platform_category = self.platform
        if platform_category not in platform_fonts:
            platform_category = "web"  # デフォルト

        # フォントマッピングを取得
        font_map = platform_fonts[platform_category]

        # マッピングされたフォントを返す
        return font_map.get(font_name, font_name)

    def get_data_file(self, file_name):
        """データファイルのパスを返す"""
        # プラットフォーム固有のファイルがあるか確認
        platform_specific = f"{self.base_dir}/{self.data_dir}/{self.platform}/{file_name}"
        default_path = f"{self.base_dir}/{self.data_dir}/{file_name}"

        if self._asset_exists(platform_specific):
            return platform_specific

        return default_path

    def _asset_exists(self, path):
        """アセットが存在するか確認（実際のアプリでは実装が必要）"""
        # Fletアプリにバンドルされたアセットの存在チェックロジック
        # 実際の実装はFletの機能を使用する必要があります
        # ここでは単純化のためTrueを返す
        return True

# 使用例
def main(page: ft.Page):
    resolver = AssetResolver(page)

    # 画像パスを解決
    logo_path = resolver.get_image_path("logo.png", density="2x")

    # フォントの解決
    system_font = resolver.get_font("sans")

    # データファイルの解決
    config_path = resolver.get_data_file("config.json")

    # 解決されたアセットを使用
    page.add(
        ft.Image(src=logo_path),
        ft.Text("こんにちは", font_family=system_font)
    )
```

### プラットフォーム固有リソース値

```python
# /app/core/resources/resource_values.py
class ResourceValues:
    def __init__(self, platform):
        self.platform = platform
        self._init_resources()

    def _init_resources(self):
        # 基本リソース値
        self.base_values = {
            "colors": {
                "primary": "#2196F3",
                "secondary": "#FF9800",
                "background": "#FFFFFF",
                "error": "#F44336",
                "text": "#212121",
                "divider": "#BDBDBD"
            },
            "dimensions": {
                "padding_small": 8,
                "padding_medium": 16,
                "padding_large": 24,
                "icon_size_small": 18,
                "icon_size_medium": 24,
                "icon_size_large": 36,
                "text_size_small": 12,
                "text_size_medium": 16,
                "text_size_large": 20,
                "text_size_xlarge": 24
            },
            "strings": {
                "app_name": "My Flet App",
                "welcome_message": "ようこそ、Fletアプリへ",
                "loading": "読み込み中...",
                "error_message": "エラーが発生しました"
            }
        }

        # プラットフォーム固有のオーバーライド
        self.platform_values = {
            "android": {
                "colors": {
                    "primary": "#4CAF50",  # Androidはグリーン系
                },
                "dimensions": {
                    "padding_large": 20,  # Androidは少し小さめのパディング
                }
            },
            "ios": {
                "colors": {
                    "primary": "#007AFF",  # iOSはブルー系
                    "background": "#F7F7F7"  # iOSはわずかにグレーがかった背景
                },
                "strings": {
                    "loading": "読み込んでいます..."  # iOSはより丁寧な表現
                }
            },
            "web": {
                "dimensions": {
                    "padding_large": 32,  # Webはより大きめのパディング
                    "text_size_large": 22  # Webは少し大きめのテキスト
                }
            }
        }

    def get(self, resource_type, resource_name):
        """リソース値を取得"""
        # プラットフォーム固有の値があるか確認
        platform_category = self._get_platform_category()

        if (platform_category in self.platform_values and
            resource_type in self.platform_values[platform_category] and
            resource_name in self.platform_values[platform_category][resource_type]):
            return self.platform_values[platform_category][resource_type][resource_name]

        # なければ基本値を返す
        if resource_type in self.base_values and resource_name in self.base_values[resource_type]:
            return self.base_values[resource_type][resource_name]

        # どちらも見つからない場合はNoneを返す
        return None

    def _get_platform_category(self):
        """プラットフォームのカテゴリを返す"""
        if self.platform == "android":
            return "android"
        elif self.platform == "ios":
            return "ios"
        elif self.platform in ["windows", "macos", "linux"]:
            return "desktop"
        else:
            return "web"

# 使用例
def main(page: ft.Page):
    resources = ResourceValues(page.platform)

    # リソース値を取得
    primary_color = resources.get("colors", "primary")
    padding = resources.get("dimensions", "padding_medium")
    welcome_text = resources.get("strings", "welcome_message")

    # リソースを使用
    page.add(
        ft.Container(
            content=ft.Text(
                welcome_text,
                color=primary_color,
                size=resources.get("dimensions", "text_size_large")
            ),
            padding=padding
        )
    )
```

## デバイス機能へのアクセス

プラットフォーム固有機能へのアクセス:

### 機能アクセス抽象化

```python
# /app/platform/device/device_features.py
from abc import ABC, abstractmethod
from typing import Callable, Optional

class GPSInterface(ABC):
    @abstractmethod
    def get_location(self, on_location: Callable[[dict], None], on_error: Optional[Callable[[str], None]] = None):
        """位置情報を取得"""
        pass

class ShareInterface(ABC):
    @abstractmethod
    def share_text(self, text: str, title: Optional[str] = None) -> bool:
        """テキストを共有"""
        pass

    @abstractmethod
    def share_file(self, file_path: str, title: Optional[str] = None) -> bool:
        """ファイルを共有"""
        pass

# WebのGPS実装
class WebGPS(GPSInterface):
    def __init__(self, page):
        self.page = page

    def get_location(self, on_location: Callable[[dict], None], on_error: Optional[Callable[[str], None]] = None):
        # JavaScript経由でGeolocation APIにアクセス
        js_code = """
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    return {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: position.timestamp
                    };
                },
                function(error) {
                    return { error: error.message };
                }
            );
        } else {
            return { error: "Geolocation is not supported by this browser." };
        }
        """

        try:
            result = self.page.eval_js(js_code)

            # 結果の処理
            if isinstance(result, dict) and "error" not in result:
                on_location(result)
            else:
                error_message = result.get("error", "Unknown error") if isinstance(result, dict) else "Failed to get location"
                if on_error:
                    on_error(error_message)
        except Exception as e:
            if on_error:
                on_error(str(e))

# AndroidのGPS実装
class AndroidGPS(GPSInterface):
    def __init__(self, page):
        self.page = page

    def get_location(self, on_location: Callable[[dict], None], on_error: Optional[Callable[[str], None]] = None):
        # ここでは擬似的な実装
        # 実際にはFlutterのメソッドチャネルを使用してネイティブコードを呼び出す
        try:
            # 擬似データ（実際には動的に取得）
            location_data = {
                "latitude": 35.6895,
                "longitude": 139.6917,
                "accuracy": 10.0,
                "timestamp": 1625097600000
            }
            on_location(location_data)
        except Exception as e:
            if on_error:
                on_error(str(e))

# ファクトリークラス
class DeviceFeatureFactory:
    @staticmethod
    def get_gps(page) -> GPSInterface:
        platform = page.platform
        if platform == "android":
            return AndroidGPS(page)
        elif platform == "ios":
            return iOSGPS(page)  # 別途実装
        else:
            return WebGPS(page)

    @staticmethod
    def get_share(page) -> ShareInterface:
        platform = page.platform
        if platform == "android":
            return AndroidShare(page)  # 別途実装
        elif platform == "ios":
            return iOSShare(page)  # 別途実装
        else:
            return WebShare(page)  # 別途実装

# 使用例
def main(page: ft.Page):
    gps = DeviceFeatureFactory.get_gps(page)

    def on_location_received(location):
        # 位置情報を表示
        lat_lng_text.value = f"緯度: {location['latitude']}, 経度: {location['longitude']}"
        page.update()

    def on_location_error(error):
        lat_lng_text.value = f"位置情報の取得に失敗しました: {error}"
        page.update()

    lat_lng_text = ft.Text("位置情報を取得中...")

    # 位置情報を取得するボタン
    get_location_button = ft.ElevatedButton(
        "現在地を取得",
        on_click=lambda e: gps.get_location(on_location_received, on_location_error)
    )

    page.add(
        get_location_button,
        lat_lng_text
    )
```

## パフォーマンス最適化

プラットフォーム別のパフォーマンス最適化:

### 条件付きレンダリング

```python
# /app/presentation/optimized/conditional_rendering.py
import flet as ft

class OptimizedList(ft.UserControl):
    def __init__(self, page: ft.Page, items):
        super().__init__()
        self.page = page
        self.platform = page.platform
        self.items = items
        self.visible_items = []
        self.scroll_container = None

        # プラットフォームに基づいて最適化設定を決定
        if self.platform in ["android", "ios"]:
            self.buffer_size = 10  # モバイルでは少なめ
            self.render_threshold = 500  # msec
        else:
            self.buffer_size = 20  # デスクトップ/Webではより多く
            self.render_threshold = 100  # msec

    def build(self):
        # スクロール可能なコンテナを作成
        self.list_view = ft.ListView(spacing=2, padding=10, expand=True)

        # 初期表示アイテムを設定
        self._update_visible_items(0)

        # スクロールイベントの設定
        self.scroll_container = ft.Container(
            content=self.list_view,
            expand=True,
            on_scroll=self._on_scroll
        )

        return self.scroll_container

    def _create_list_item(self, item):
        """アイテム表示用のウィジェットを作成"""
        return ft.Container(
            content=ft.Text(item["title"]),
            bgcolor=ft.colors.BLUE_50,
            padding=10,
            border_radius=5
        )

    def _update_visible_items(self, start_index):
        """表示するアイテムを更新"""
        end_index = min(start_index + self.buffer_size, len(self.items))

        # 表示アイテムを設定
        self.visible_items = self.items[start_index:end_index]

        # リストビューを更新
        self.list_view.controls = [self._create_list_item(item) for item in self.visible_items]
        self.update()

    def _on_scroll(self, e):
        """スクロールイベントハンドラ"""
        # スクロール位置から表示すべきアイテムを計算
        # 実際のアプリでは、スクロール位置からインデックスを適切に計算する必要があります
        # ここでは簡略化のため、スクロール位置を使って新しい開始インデックスを計算
        scroll_y = e.scroll_y if hasattr(e, "scroll_y") else 0

        # スクロール位置から表示開始インデックスを算出（擬似コード）
        new_start_index = int(max(0, scroll_y / 50))  # 1アイテムの高さを50pxと仮定

        # 表示アイテムの範囲が変更された場合、更新
        current_start_index = self.items.index(self.visible_items[0]) if self.visible_items else 0
        if abs(new_start_index - current_start_index) > self.buffer_size / 2:
            self._update_visible_items(new_start_index)

# 使用例
def main(page: ft.Page):
    # サンプルデータ
    items = [{"id": i, "title": f"Item {i}"} for i in range(1000)]

    # 最適化されたリストを作成
    optimized_list = OptimizedList(page, items)

    page.add(
        ft.Text("最適化されたリスト", size=20),
        ft.Container(content=optimized_list, height=400, expand=True)
    )
```

### 遅延読み込み

```python
# /app/core/optimization/lazy_loading.py
import asyncio
import flet as ft

class LazyLoader:
    def __init__(self, page: ft.Page):
        self.page = page
        self.platform = page.platform
        self.is_mobile = self.platform in ["android", "ios"]

    async def load_components(self, components_dict, loading_indicator=None):
        """コンポーネントを優先度順に非同期で読み込む"""
        # 読み込み中表示
        if loading_indicator:
            loading_indicator.visible = True
            self.page.update()

        # 優先度でソート
        sorted_components = sorted(
            components_dict.items(),
            key=lambda x: x[1]["priority"]
        )

        # モバイルではより長い間隔で遅延読み込み
        delay_ms = 50 if not self.is_mobile else 100

        for component_id, config in sorted_components:
            # 優先度の高いコンポーネントから順に読み込み
            control = config["create_fn"]()

            # コンテナに追加
            target_container = config["container"]
            if hasattr(target_container, "controls"):
                target_container.controls.append(control)
            else:
                target_container.content = control

            # 画面更新
            self.page.update()

            # 次のコンポーネント読み込み前に少し待機
            await asyncio.sleep(delay_ms / 1000.0)

        # 読み込み完了
        if loading_indicator:
            loading_indicator.visible = False
            self.page.update()

# 使用例
def main(page: ft.Page):
    lazy_loader = LazyLoader(page)

    # メインコンテンツコンテナ
    main_container = ft.Column([], spacing=10)

    # ローディングインジケーター
    loading = ft.ProgressRing()

    # 各コンポーネントの生成関数
    def create_header():
        return ft.Container(
            content=ft.Text("ヘッダー", size=24),
            bgcolor=ft.colors.BLUE_100,
            padding=10,
            border_radius=5
        )

    def create_chart():
        # 重いチャートコンポーネント
        return ft.Container(
            content=ft.Text("チャートコンポーネント"),
            bgcolor=ft.colors.GREEN_100,
            padding=20,
            height=200,
            border_radius=5
        )

    def create_list():
        # 大きなリスト
        list_items = [
            ft.ListTile(title=ft.Text(f"アイテム {i}"))
            for i in range(20)
        ]
        return ft.Column(list_items, scroll=ft.ScrollMode.AUTO, height=300)

    def create_footer():
        return ft.Container(
            content=ft.Text("フッター"),
            bgcolor=ft.colors.GREY_100,
            padding=10,
            border_radius=5
        )

    # 読み込むコンポーネントの定義（優先度付き）
    components = {
        "header": {
            "create_fn": create_header,
            "container": main_container,
            "priority": 1  # 最高優先度
        },
        "chart": {
            "create_fn": create_chart,
            "container": main_container,
            "priority": 3  # 低優先度
        },
        "list": {
            "create_fn": create_list,
            "container": main_container,
            "priority": 2  # 中優先度
        },
        "footer": {
            "create_fn": create_footer,
            "container": main_container,
            "priority": 4  # 最低優先度
        }
    }

    # 初期UIを構築
    page.add(
        ft.Text("遅延読み込みデモ", size=20),
        loading,
        main_container
    )

    # コンポーネントの非同期読み込みを開始
    asyncio.create_task(lazy_loader.load_components(components, loading))
```

## 実装例とパターン

### プラットフォーム検出サービス

```python
# /app/core/platform/platform_service.py
class PlatformService:
    def __init__(self, page):
        self.page = page
        self.platform = page.platform

    def is_android(self):
        return self.platform == "android"

    def is_ios(self):
        return self.platform == "ios"

    def is_mobile(self):
        return self.is_android() or self.is_ios()

    def is_web(self):
        return not (self.is_mobile() or self.is_desktop())

    def is_desktop(self):
        return self.platform in ["windows", "macos", "linux"]

    def is_windows(self):
        return self.platform == "windows"

    def is_macos(self):
        return self.platform == "macos"

    def is_linux(self):
        return self.platform == "linux"

    def should_use_touch_ui(self):
        """タッチUI向けかどうかを判断"""
        return self.is_mobile() or (self.is_web() and self._is_touch_device())

    def get_platform_group(self):
        """プラットフォームのグループを返す（設定などで使用）"""
        if self.is_android():
            return "android"
        elif self.is_ios():
            return "ios"
        elif self.is_desktop():
            return "desktop"
        else:
            return "web"

    def _is_touch_device(self):
        """Webブラウザがタッチデバイスかどうかを判断"""
        js_code = """
        if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
            return true;
        }
        return false;
        """
        return self.page.eval_js(js_code) == True
```

### マルチプラットフォームナビゲーション管理

```python
# /app/core/navigation/navigation_manager.py
import flet as ft
from app.core.platform.platform_service import PlatformService

class NavigationManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.platform_service = PlatformService(page)
        self.views = {}
        self.current_route = "/"

        # ナビゲーション履歴
        self.history = ["/"]

        # プラットフォームに適したナビゲーションスタイルを設定
        self._setup_navigation()

    def _setup_navigation(self):
        """プラットフォームに適したナビゲーション構造を設定"""
        self.page.on_route_change = self._handle_route_change

        # モバイルの場合はAppBarに戻るボタンを表示
        if self.platform_service.is_mobile():
            self.show_back_button = True
        else:
            self.show_back_button = False

    def register_view(self, route, build_fn):
        """ルートとビルド関数を登録"""
        self.views[route] = build_fn

    def navigate(self, route):
        """指定されたルートに移動"""
        self.page.go(route)

    def go_back(self):
        """履歴の前のページに戻る"""
        if len(self.history) > 1:
            # 現在のルートを削除
            self.history.pop()
            # 前のルートを取得
            previous_route = self.history[-1]
            # 直接ナビゲーション（履歴に追加せず）
            self.page.route = previous_route
            self._handle_route_change(ft.RouteChangeEvent(route=previous_route))

    def _handle_route_change(self, e):
        """ルート変更ハンドラ"""
        new_route = e.route

        # ルートが変わった場合のみ履歴に追加
        if new_route != self.current_route:
            self.history.append(new_route)
            self.current_route = new_route

        # パラメータを含むルートのパターンマッチ
        route_parts = new_route.split("/")
        params = {}
        matched_route = None
        matched_build_fn = None

        for route_pattern, build_fn in self.views.items():
            pattern_parts = route_pattern.split("/")

            if len(route_parts) != len(pattern_parts):
                continue

            match = True
            current_params = {}

            for i, part in enumerate(pattern_parts):
                if part.startswith(":"):
                    # パラメータをキャプチャ
                    param_name = part[1:]
                    current_params[param_name] = route_parts[i]
                elif part != route_parts[i]:
                    match = False
                    break

            if match:
                matched_route = route_pattern
                matched_build_fn = build_fn
                params = current_params
                break

        # ルートが見つかった場合、ビューを構築
        if matched_build_fn:
            self._build_view(matched_build_fn, params)
        else:
            # 一致するルートがない場合は404ページ
            self._show_404_page()

    def _build_view(self, build_fn, params):
        """ビューを構築してページに設定"""
        # 現在のビューをクリア
        self.page.views.clear()

        # 新しいビューを構築
        view = build_fn(params)

        # モバイルの場合、AppBarに戻るボタンを追加
        if self.platform_service.is_mobile() and len(self.history) > 1:
            # AppBarがある場合、戻るボタンを追加
            if hasattr(view, "appbar") and view.appbar:
                view.appbar.leading = ft.IconButton(
                    icon=ft.icons.ARROW_BACK if self.platform_service.is_android() else ft.icons.ARROW_BACK_IOS,
                    on_click=lambda e: self.go_back()
                )

        # ビューをページに追加
        self.page.views.append(view)
        self.page.update()

    def _show_404_page(self):
        """404ページを表示"""
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/not-found",
                [
                    ft.AppBar(title=ft.Text("ページが見つかりません")),
                    ft.Column([
                        ft.Text("お探しのページは見つかりませんでした。", size=20),
                        ft.ElevatedButton("ホームに戻る", on_click=lambda e: self.navigate("/"))
                    ], alignment=ft.MainAxisAlignment.CENTER, expand=True)
                ]
            )
        )
        self.page.update()

# 使用例
def main(page: ft.Page):
    navigation = NavigationManager(page)

    # ビュー構築関数
    def home_view(params):
        return ft.View(
            "/",
            [
                ft.AppBar(title=ft.Text("ホーム")),
                ft.Column([
                    ft.Text("ホーム画面", size=20),
                    ft.ElevatedButton("製品ページへ", on_click=lambda e: navigation.navigate("/products")),
                    ft.ElevatedButton("設定ページへ", on_click=lambda e: navigation.navigate("/settings"))
                ])
            ]
        )

    def products_view(params):
        return ft.View(
            "/products",
            [
                ft.AppBar(title=ft.Text("製品一覧")),
                ft.Column([
                    ft.Text("製品一覧ページ", size=20),
                    ft.ListView([
                        ft.ListTile(
                            title=ft.Text(f"製品 {i}"),
                            on_click=lambda e, id=i: navigation.navigate(f"/product/{id}")
                        )
                        for i in range(1, 6)
                    ])
                ])
            ]
        )

    def product_detail_view(params):
        product_id = params.get("id", "unknown")
        return ft.View(
            f"/product/{product_id}",
            [
                ft.AppBar(title=ft.Text(f"製品詳細: {product_id}")),
                ft.Column([
                    ft.Text(f"製品 {product_id} の詳細情報", size=20),
                    ft.ElevatedButton("戻る", on_click=lambda e: navigation.go_back())
                ])
            ]
        )

    def settings_view(params):
        return ft.View(
            "/settings",
            [
                ft.AppBar(title=ft.Text("設定")),
                ft.Column([
                    ft.Text("設定ページ", size=20),
                    ft.ElevatedButton("戻る", on_click=lambda e: navigation.go_back())
                ])
            ]
        )

    # ルートを登録
    navigation.register_view("/", home_view)
    navigation.register_view("/products", products_view)
    navigation.register_view("/product/:id", product_detail_view)
    navigation.register_view("/settings", settings_view)

    # 初期ルートに移動
    navigation.navigate("/")
```

このガイドに従うことで、Fletアプリケーションの開発において、プラットフォーム間でのコード共有を最大化しつつ、各プラットフォームの特性を活かした最適な実装を実現できます。プラットフォーム固有のコードを適切に抽象化し、共通インターフェースを通じてアクセスすることで、保守性の高いマルチプラットフォームアプリケーションを構築できます。
