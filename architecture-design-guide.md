# Python Flet - マルチプラットフォームアーキテクチャ設計ガイド

> **対象Fletバージョン**: 0.19.0以上
>
> **最終更新日**: 2025年5月10日
>
> **注意**: Fletは活発に開発が進んでいるフレームワークです。最新の情報は[Flet公式ドキュメント](https://flet.dev/docs/)を参照してください。

このガイドは、Python Fletを使用したマルチプラットフォームアプリケーション開発のためのアーキテクチャ設計方針を提供します。適切なアーキテクチャ設計により、コードの保守性、拡張性、テスト容易性を向上させ、効率的な開発プロセスを実現します。

> **関連ガイド**:
> - [プラットフォーム共通コード管理ガイド](./cross-platform-code-management-guide.md) - 共通コードとプラットフォーム固有コードの分離方法
> - [APIとバックエンド連携ガイド](./api-backend-integration-guide.md) - データアクセス層の設計と実装
> - [テスト戦略とQAガイド](./testing-qa-guide.md) - アーキテクチャに基づいたテスト手法

## 目次

1. [アーキテクチャの基本原則](#アーキテクチャの基本原則)
2. [推奨アーキテクチャパターン](#推奨アーキテクチャパターン)
3. [プロジェクト構造](#プロジェクト構造)
4. [コンポーネント設計](#コンポーネント設計)
5. [状態管理](#状態管理)
6. [ナビゲーション設計](#ナビゲーション設計)
7. [データアクセス層](#データアクセス層)
8. [依存関係の管理](#依存関係の管理)
9. [実装例](#実装例)

## アーキテクチャの基本原則

Fletアプリケーションの設計において重要な原則:

### 関心の分離
- [ ] ビジネスロジック、UI、データアクセスを明確に分離する
- [ ] 各コンポーネントに単一の責任を持たせる
- [ ] インターフェースを通じてコンポーネント間の通信を行う

### 可読性と保守性
- [ ] 命名規則を一貫させる（snake_case関数、CamelCaseクラスなど）
- [ ] コードのドキュメンテーションを充実させる
- [ ] 複雑なロジックは小さな関数に分割する

### テスト容易性
- [ ] ユニットテスト可能な設計にする
- [ ] モックやスタブを活用できる構造にする
- [ ] テスト自動化を考慮した設計にする

### スケーラビリティ
- [ ] 将来の機能追加を考慮した拡張性を持たせる
- [ ] パフォーマンスのボトルネックを予測し対策する
- [ ] コードの再利用性を高める

## 推奨アーキテクチャパターン

Fletアプリケーションに適したアーキテクチャパターン:

### MVCパターン
基本的でわかりやすいパターン:
- **Model**: データとビジネスロジック
- **View**: ユーザーインターフェース（Flet UI コンポーネント）
- **Controller**: ModelとViewの橋渡し役

```
/app
  /models        # データモデルとビジネスロジック
  /views         # Fletのページとコンポーネント
  /controllers   # ビューとモデルを連携させるコントローラー
```

### MVVMパターン
より高度な分離を実現するパターン:
- **Model**: データとドメインロジック
- **View**: ユーザーインターフェース（Fletコンポーネント）
- **ViewModel**: ViewとModelの間のデータバインディング

```
/app
  /models        # データモデルとドメインロジック
  /views         # Fletのページとコンポーネント
  /viewmodels    # ViewとModelをバインドするViewModel
```

### Clean Architecture
より高度な分離と依存関係制御:
- **Entities**: ビジネスオブジェクト
- **Use Cases**: ビジネスルール
- **Interface Adapters**: 外部とのインターフェース
- **Frameworks & Drivers**: 外部ライブラリとの連携

```
/app
  /domain        # エンティティとビジネスルール
    /entities    # ビジネスオブジェクト
    /usecases    # ビジネスロジック
  /data          # データアクセス層
    /repositories # データの保存と取得
    /datasources  # 外部データソースとの連携
  /presentation  # UI層
    /pages       # Fletページ
    /widgets     # 再利用可能なFletコンポーネント
    /viewmodels  # ビジネスロジックとUIの橋渡し
```

## プロジェクト構造

推奨されるフォルダ構造:

```
/my_flet_app/
  /app                  # アプリケーションコード
    /assets             # 静的ファイル（画像、フォント等）
    /core               # 核となるアプリケーションロジック
      /constants        # 定数
      /theme            # テーマ定義
      /utils            # ユーティリティ関数
    /data               # データ関連
      /models           # データモデル
      /repositories     # データリポジトリ
      /services         # 外部サービス連携
    /presentation       # UI関連
      /pages            # アプリのページ
      /widgets          # 再利用可能なウィジェット
      /controllers      # UIコントローラー
    /platform           # プラットフォーム固有の実装
  /tests                # テストコード
  main.py               # アプリケーションのエントリーポイント
  requirements.txt      # 依存パッケージリスト
  README.md             # プロジェクト説明
```

## コンポーネント設計

### ページ構造
ページは機能単位で分割し、以下の構造に従う:

```python
# /app/presentation/pages/home_page.py
import flet as ft
from app.presentation.widgets.product_card import ProductCard
from app.presentation.controllers.home_controller import HomeController

class HomePage(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.controller = HomeController()

    def build(self):
        # ページのUIを構築
        self.title = ft.Text("ホーム", size=24, weight=ft.FontWeight.BOLD)
        self.product_list = ft.Column(spacing=10)

        # データを読み込み表示
        self._load_products()

        return ft.Column([
            self.title,
            self.product_list
        ], spacing=20, scroll=ft.ScrollMode.AUTO)

    def _load_products(self):
        products = self.controller.get_products()
        self.product_list.controls = [
            ProductCard(product=p, on_click=self._on_product_click)
            for p in products
        ]

    def _on_product_click(self, e, product_id):
        # 商品詳細ページへナビゲーション
        self.controller.navigate_to_product_detail(self.page, product_id)
```

### 再利用可能なコンポーネント
UI要素を再利用可能なコンポーネントとして設計:

```python
# /app/presentation/widgets/product_card.py
import flet as ft
from app.data.models.product import Product

class ProductCard(ft.UserControl):
    def __init__(self, product: Product, on_click=None):
        super().__init__()
        self.product = product
        self.on_click = on_click

    def build(self):
        return ft.Card(
            elevation=4,
            content=ft.Container(
                content=ft.Column([
                    ft.Image(src=self.product.image_url, width=120, height=120),
                    ft.Text(self.product.name, weight=ft.FontWeight.BOLD),
                    ft.Text(f"¥{self.product.price:,}", size=14),
                    ft.ElevatedButton(
                        text="詳細を見る",
                        on_click=lambda e: self.on_click(e, self.product.id) if self.on_click else None
                    )
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                padding=10,
                width=150
            )
        )
```

### コントローラー
ビジネスロジックとUIを分離:

```python
# /app/presentation/controllers/home_controller.py
from app.data.repositories.product_repository import ProductRepository

class HomeController:
    def __init__(self):
        self.product_repository = ProductRepository()

    def get_products(self):
        # データを取得
        return self.product_repository.get_all_products()

    def navigate_to_product_detail(self, page, product_id):
        # ナビゲーション処理
        page.go(f"/product/{product_id}")
```

## 状態管理

Fletアプリケーションにおける状態管理の方法:

### ローカル状態
単一コンポーネント内での状態管理:

```python
class Counter(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.count = 0

    def build(self):
        self.text_number = ft.Text(str(self.count), size=24)

        return ft.Column([
            self.text_number,
            ft.Row([
                ft.ElevatedButton("増加", on_click=self._increment),
                ft.ElevatedButton("減少", on_click=self._decrement)
            ])
        ])

    def _increment(self, e):
        self.count += 1
        self.text_number.value = str(self.count)
        self.update()

    def _decrement(self, e):
        self.count -= 1
        self.text_number.value = str(self.count)
        self.update()
```

### グローバル状態
複数コンポーネント間での状態共有:

```python
# /app/core/state/app_state.py
class AppState:
    def __init__(self):
        self.user = None
        self.cart_items = []
        self.theme_mode = "light"
        self._listeners = []

    def add_listener(self, listener):
        self._listeners.append(listener)

    def remove_listener(self, listener):
        self._listeners.remove(listener)

    def notify_listeners(self):
        for listener in self._listeners:
            listener()

    def add_to_cart(self, product, quantity=1):
        # カートに商品を追加
        self.cart_items.append({"product": product, "quantity": quantity})
        self.notify_listeners()

    def set_theme_mode(self, mode):
        self.theme_mode = mode
        self.notify_listeners()

# アプリ全体で単一のインスタンスを使用
app_state = AppState()
```

### 状態管理のベストプラクティス
- [ ] 状態の変更は単一の場所で行う
- [ ] 状態変更後は必要なコンポーネントだけを更新する
- [ ] イミュータブルな状態管理を心がける
- [ ] 複雑な状態管理には専用のステートマネージャーの導入を検討する

## ナビゲーション設計

### ルーティング
Fletでのルーティング実装:

```python
# /app/core/router/router.py
class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.routes = {
            "/": self._home_route,
            "/products": self._products_route,
            "/product/:id": self._product_detail_route,
            "/settings": self._settings_route
        }

    def initialize(self):
        self.page.on_route_change = self._handle_route_change
        # 初期ルートを設定
        self.page.go("/")

    def _handle_route_change(self, route_event):
        new_route = route_event.route

        # パラメータを含むルートの処理
        route_parts = new_route.split("/")

        for route_pattern, handler in self.routes.items():
            pattern_parts = route_pattern.split("/")

            if len(route_parts) != len(pattern_parts):
                continue

            params = {}
            match = True

            for i, part in enumerate(pattern_parts):
                if part.startswith(":"):
                    # パラメータをキャプチャ
                    param_name = part[1:]
                    params[param_name] = route_parts[i]
                elif part != route_parts[i]:
                    match = False
                    break

            if match:
                # ルートに一致するハンドラを呼び出す
                self.page.views.clear()
                view = handler(params)
                self.page.views.append(view)
                self.page.update()
                return

        # 一致するルートがない場合は404ページ
        self._not_found_route()

    def _home_route(self, params=None):
        from app.presentation.pages.home_page import HomePage
        return ft.View("/", [HomePage(self.page)])

    def _products_route(self, params=None):
        from app.presentation.pages.products_page import ProductsPage
        return ft.View("/products", [ProductsPage(self.page)])

    def _product_detail_route(self, params):
        from app.presentation.pages.product_detail_page import ProductDetailPage
        product_id = params.get("id")
        return ft.View(f"/product/{product_id}", [ProductDetailPage(self.page, product_id)])

    def _settings_route(self, params=None):
        from app.presentation.pages.settings_page import SettingsPage
        return ft.View("/settings", [SettingsPage(self.page)])

    def _not_found_route(self):
        from app.presentation.pages.not_found_page import NotFoundPage
        self.page.views.append(ft.View("/not-found", [NotFoundPage(self.page)]))
        self.page.update()
```

### ナビゲーションのベストプラクティス
- [ ] 一貫したナビゲーションパターンを使用する
- [ ] ナビゲーション状態をURLと同期させる
- [ ] ディープリンクをサポートする
- [ ] 戻るボタンの適切な処理を実装する

## データアクセス層

### リポジトリパターン
データアクセスをビジネスロジックから分離:

```python
# /app/data/models/product.py
class Product:
    def __init__(self, id, name, description, price, image_url):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.image_url = image_url

# /app/data/repositories/product_repository.py
import json
import os
from app.data.models.product import Product

class ProductRepository:
    def __init__(self):
        self.products = []
        self._load_products()

    def _load_products(self):
        # ローカルJSONファイルからデータを読み込む例
        try:
            path = os.path.join(os.path.dirname(__file__), "../data/products.json")
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.products = [
                    Product(
                        id=item["id"],
                        name=item["name"],
                        description=item["description"],
                        price=item["price"],
                        image_url=item["image_url"]
                    )
                    for item in data
                ]
        except Exception as e:
            print(f"Failed to load products: {e}")
            # 例外時にはダミーデータを用意
            self.products = [
                Product(1, "サンプル商品", "説明文", 1000, "https://example.com/img.jpg")
            ]

    def get_all_products(self):
        return self.products

    def get_product_by_id(self, id):
        for product in self.products:
            if product.id == id:
                return product
        return None

    def search_products(self, keyword):
        keyword = keyword.lower()
        return [p for p in self.products if keyword in p.name.lower() or keyword in p.description.lower()]
```

### サービス層
外部APIや複雑なデータ処理を担当:

```python
# /app/data/services/auth_service.py
import requests
from app.core.constants.api_endpoints import API_BASE_URL

class AuthService:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token = None

    def login(self, username, password):
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                return {"success": True, "user": data.get("user")}
            else:
                return {"success": False, "message": "ログインに失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"エラーが発生しました: {str(e)}"}

    def get_user_profile(self):
        if not self.token:
            return {"success": False, "message": "ログインが必要です"}

        try:
            response = requests.get(
                f"{self.base_url}/user/profile",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                return {"success": True, "profile": response.json()}
            else:
                return {"success": False, "message": "プロフィール取得に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"エラーが発生しました: {str(e)}"}
```

## 依存関係の管理

### 依存性注入
テスト容易性と柔軟性を高める依存性注入:

```python
# シンプルな依存性注入コンテナ
class Container:
    def __init__(self):
        self._services = {}

    def register(self, interface, implementation):
        self._services[interface] = implementation

    def resolve(self, interface):
        if interface not in self._services:
            raise Exception(f"Service {interface} not registered")
        return self._services[interface]

# アプリケーションの依存関係を設定
def setup_dependencies():
    container = Container()

    # リポジトリの登録
    from app.data.repositories.product_repository import ProductRepository
    container.register("product_repository", ProductRepository())

    # サービスの登録
    from app.data.services.auth_service import AuthService
    container.register("auth_service", AuthService())

    return container

# 依存関係の利用例
class ProductController:
    def __init__(self, container):
        self.product_repository = container.resolve("product_repository")

    def get_featured_products(self):
        products = self.product_repository.get_all_products()
        # 特集商品のみをフィルタリング
        return [p for p in products if p.is_featured]
```

### プラットフォーム固有実装の依存性注入

マルチプラットフォーム開発において、依存性注入はプラットフォーム固有の実装を抽象化する重要な手段です。「プラットフォーム共通コード管理ガイド」で説明されているように、共通インターフェースを定義し、各プラットフォーム向けの実装を提供することで、コードの共有と分離を同時に実現できます。

```python
# プラットフォーム固有の実装を登録する例
def setup_platform_dependencies(page):
    container = Container()

    # プラットフォーム検出
    platform = page.platform

    # ストレージサービスの登録（プラットフォーム固有の実装）
    if platform in ["android", "ios"]:
        from app.platform.storage.mobile_storage import MobileStorage
        container.register("storage_service", MobileStorage(page))
    else:
        from app.platform.storage.web_storage import WebStorage
        container.register("storage_service", WebStorage(page))

    # 通知サービスの登録（プラットフォーム固有の実装）
    if platform == "android":
        from app.platform.notification.android_notification import AndroidNotification
        container.register("notification_service", AndroidNotification(page))
    elif platform == "ios":
        from app.platform.notification.ios_notification import IOSNotification
        container.register("notification_service", IOSNotification(page))
    else:
        from app.platform.notification.web_notification import WebNotification
        container.register("notification_service", WebNotification(page))

    return container
```

プラットフォーム固有の実装をコントローラやビューモデルから隠蔽することで、ビジネスロジックは共通コードとして一度だけ記述できます。これにより、各プラットフォームの特性を活かしながらも、コードの重複を最小限に抑えられます。状態管理と組み合わせることで、プラットフォーム間で一貫した動作が保証されます。

## 実装例

### アプリケーションのエントリーポイント

```python
# main.py
import flet as ft
from app.core.router.router import Router
from app.core.state.app_state import app_state
from app.core.theme.app_theme import get_app_theme

def main(page: ft.Page):
    # ページの初期設定
    page.title = "Flet Sample App"
    page.theme = get_app_theme(app_state.theme_mode)

    # 依存関係の設定
    from app.core.di.container import setup_dependencies
    container = setup_dependencies()

    # ルーターの初期化
    router = Router(page)
    router.initialize()

    # テーマ切り替え機能
    def toggle_theme(e):
        new_mode = "dark" if app_state.theme_mode == "light" else "light"
        app_state.set_theme_mode(new_mode)
        page.theme = get_app_theme(new_mode)
        page.update()

    # テーマ切り替えボタンをページに追加
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.icons.BRIGHTNESS_6,
        on_click=toggle_theme
    )

# Fletアプリを起動
ft.app(target=main)
```

### 構造化されたコンポーネント例

```python
# /app/presentation/pages/product_list_page.py
import flet as ft
from app.presentation.widgets.product_card import ProductCard
from app.presentation.controllers.product_controller import ProductController
from app.core.di.container import setup_dependencies

class ProductListPage(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        container = setup_dependencies()
        self.controller = ProductController(container)
        self.products = []
        self.loading = True

    def build(self):
        self.app_bar = ft.AppBar(
            title=ft.Text("商品一覧"),
            center_title=False,
            bgcolor=ft.colors.SURFACE_VARIANT
        )

        self.search_field = ft.TextField(
            hint_text="商品を検索...",
            expand=True,
            on_change=self._on_search_change
        )

        self.product_grid = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=200,
            child_aspect_ratio=0.7,
            spacing=10,
            run_spacing=10,
        )

        self.loading_indicator = ft.ProgressRing()

        # 初期データ読み込み
        self._load_products()

        return ft.Column([
            self.app_bar,
            ft.Container(content=self.search_field, padding=10),
            ft.Container(
                content=self.loading_indicator if self.loading else self.product_grid,
                expand=True,
                padding=10
            )
        ])

    def _load_products(self):
        self.loading = True
        self.update()

        # 非同期データ読み込みをシミュレート
        import asyncio

        async def load():
            # 実際のアプリではここでAPIコールなどを行う
            await asyncio.sleep(1)  # データ取得の遅延をシミュレート
            self.products = self.controller.get_all_products()
            self._update_product_grid()
            self.loading = False
            self.update()

        asyncio.create_task(load())

    def _update_product_grid(self):
        self.product_grid.controls = [
            ProductCard(
                product=product,
                on_click=lambda e, id=product.id: self._on_product_click(id)
            )
            for product in self.products
        ]

    def _on_search_change(self, e):
        keyword = self.search_field.value
        if not keyword:
            # 検索フィールドが空の場合、全商品を表示
            self._update_product_grid()
        else:
            # 検索キーワードでフィルタリング
            filtered_products = self.controller.search_products(keyword)
            self.product_grid.controls = [
                ProductCard(
                    product=product,
                    on_click=lambda e, id=product.id: self._on_product_click(id)
                )
                for product in filtered_products
            ]
        self.product_grid.update()

    def _on_product_click(self, product_id):
        # 商品詳細ページに遷移
        self.page.go(f"/product/{product_id}")
```

このアーキテクチャ設計ガイドに従うことで、スケーラブルで保守性の高いFletアプリケーションを構築できます。プロジェクトの規模や要件に応じて、提案されたパターンを適切に採用してください。特に、マルチプラットフォーム開発では、プラットフォーム固有の要素を適切に抽象化し、共通コードを最大化する設計が重要です。
