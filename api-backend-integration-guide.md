# Python Flet - APIとバックエンド連携ガイド

このガイドでは、Python FletアプリケーションからバックエンドサービスやAPIとの連携方法について解説します。マルチプラットフォーム環境での効率的なデータ通信、オフライン対応、同期戦略などを学びましょう。

## 目次

1. [バックエンド連携の基本原則](#バックエンド連携の基本原則)
2. [APIクライアント設計](#apiクライアント設計)
3. [認証とセキュリティ](#認証とセキュリティ)
4. [非同期処理と状態管理](#非同期処理と状態管理)
5. [データキャッシュ戦略](#データキャッシュ戦略)
6. [オフライン対応](#オフライン対応)
7. [エラーハンドリング](#エラーハンドリング)
8. [WebSocketと実時間通信](#websocketと実時間通信)
9. [デバッグとモニタリング](#デバッグとモニタリング)
10. [実装例とパターン](#実装例とパターン)

## バックエンド連携の基本原則

マルチプラットフォームアプリでバックエンド連携を行う際の基本原則:

### レイヤー分離
- [ ] APIアクセスをビジネスロジックとUIから分離
- [ ] データ変換とマッピングを一貫したレイヤーで処理
- [ ] プラットフォーム固有の通信コードを抽象化

### データの一貫性
- [ ] すべてのプラットフォームで同じデータモデルを使用
- [ ] バックエンドレスポンスの標準化された変換処理
- [ ] エンティティマッピングの一元管理

### 通信効率
- [ ] 必要なデータのみを取得・送信
- [ ] バッチ処理による通信回数の最適化
- [ ] 帯域幅が制限された環境での動作に配慮

### クロスプラットフォーム互換
- [ ] すべてのプラットフォームで動作する通信ライブラリの選定
- [ ] ネットワーク機能のプラットフォーム差異を抽象化
- [ ] プラットフォーム固有の制限に対応

## APIクライアント設計

効率的なAPIクライアントの設計方法:

### 抽象化されたAPIサービス

```python
# /app/data/api/api_client.py
import httpx
import json
import asyncio
from typing import Dict, Any, Optional
from app.core.config import settings

class ApiClient:
    def __init__(self):
        self.base_url = settings.API_BASE_URL
        self.timeout = settings.API_TIMEOUT
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET リクエストを送信"""
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params, headers=self.headers)
            return self._handle_response(response)

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST リクエストを送信"""
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=data, headers=self.headers)
            return self._handle_response(response)

    async def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """PUT リクエストを送信"""
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(url, json=data, headers=self.headers)
            return self._handle_response(response)

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE リクエストを送信"""
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(url, headers=self.headers)
            return self._handle_response(response)

    def _handle_response(self, response):
        """レスポンスを処理"""
        if response.status_code >= 200 and response.status_code < 300:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"success": True, "data": response.text}
        else:
            error_data = {"status_code": response.status_code}
            try:
                error_data.update(response.json())
            except json.JSONDecodeError:
                error_data["message"] = response.text

            raise ApiException(error_data)

class ApiException(Exception):
    """API呼び出しエラー例外"""
    def __init__(self, error_data):
        self.error_data = error_data
        self.status_code = error_data.get("status_code", 500)
        self.message = error_data.get("message", "Unknown API error")
        super().__init__(self.message)
```

### リポジトリパターンの実装

```python
# /app/data/repositories/user_repository.py
from app.data.api.api_client import ApiClient
from app.data.models.user import User
from typing import List, Optional

class UserRepository:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    async def get_all_users(self) -> List[User]:
        """全ユーザーを取得"""
        response = await self.api_client.get("/users")

        # レスポンスからユーザーエンティティに変換
        users = []
        for user_data in response.get("data", []):
            users.append(User.from_dict(user_data))

        return users

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """IDからユーザーを取得"""
        response = await self.api_client.get(f"/users/{user_id}")

        if response.get("data"):
            return User.from_dict(response["data"])
        return None

    async def create_user(self, user: User) -> User:
        """新規ユーザーを作成"""
        response = await self.api_client.post("/users", user.to_dict())

        if response.get("data"):
            return User.from_dict(response["data"])

        # レスポンスが想定と異なる場合
        raise ValueError("Invalid response format")

    async def update_user(self, user: User) -> User:
        """ユーザー情報を更新"""
        response = await self.api_client.put(f"/users/{user.id}", user.to_dict())

        if response.get("data"):
            return User.from_dict(response["data"])

        raise ValueError("Invalid response format")

    async def delete_user(self, user_id: int) -> bool:
        """ユーザーを削除"""
        response = await self.api_client.delete(f"/users/{user_id}")

        return response.get("success", False)

# ユーザーモデル
# /app/data/models/user.py
class User:
    def __init__(self, id=None, name="", email="", role="", avatar_url=""):
        self.id = id
        self.name = name
        self.email = email
        self.role = role
        self.avatar_url = avatar_url

    @classmethod
    def from_dict(cls, data):
        """辞書からユーザーオブジェクトを生成"""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            email=data.get("email", ""),
            role=data.get("role", ""),
            avatar_url=data.get("avatar_url", "")
        )

    def to_dict(self):
        """ユーザーオブジェクトを辞書に変換"""
        data = {
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "avatar_url": self.avatar_url
        }

        # IDが設定されている場合のみ含める
        if self.id is not None:
            data["id"] = self.id

        return data
```

### サービスロケーター

```python
# /app/core/di/service_locator.py
class ServiceLocator:
    _services = {}

    @classmethod
    def register(cls, service_name, implementation):
        """サービスを登録"""
        cls._services[service_name] = implementation

    @classmethod
    def get(cls, service_name):
        """サービスを取得"""
        if service_name not in cls._services:
            raise Exception(f"Service '{service_name}' not registered")
        return cls._services[service_name]

# サービスのセットアップ
def setup_services():
    from app.data.api.api_client import ApiClient
    from app.data.repositories.user_repository import UserRepository
    from app.data.repositories.product_repository import ProductRepository

    # APIクライアントを作成
    api_client = ApiClient()

    # リポジトリを登録
    ServiceLocator.register("user_repository", UserRepository(api_client))
    ServiceLocator.register("product_repository", ProductRepository(api_client))

    return ServiceLocator
```

## 認証とセキュリティ

APIとの安全な連携のための認証と認可の実装:

### トークンベース認証

```python
# /app/data/auth/auth_service.py
import json
import time
from typing import Dict, Any, Optional
from app.data.api.api_client import ApiClient
from app.core.storage.storage_service import StorageService

class AuthService:
    def __init__(self, api_client: ApiClient, storage: StorageService):
        self.api_client = api_client
        self.storage = storage
        self.auth_token = None
        self.token_type = None
        self.token_expiry = None

        # 保存されているトークンを読み込む
        self._load_auth_token()

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """ユーザーログイン"""
        response = await self.api_client.post("/auth/login", {
            "username": username,
            "password": password
        })

        if response.get("token"):
            # トークン情報を保存
            self.auth_token = response["token"]
            self.token_type = response.get("token_type", "Bearer")
            self.token_expiry = response.get("expires_at")

            # トークンをストレージに保存
            self._save_auth_token()

            # APIクライアントのヘッダーを更新
            self._update_auth_header()

            return {
                "success": True,
                "user": response.get("user", {})
            }

        return {
            "success": False,
            "message": "Authentication failed"
        }

    async def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """新規ユーザー登録"""
        response = await self.api_client.post("/auth/register", {
            "username": username,
            "email": email,
            "password": password
        })

        return {
            "success": "user" in response,
            "user": response.get("user", {}),
            "message": response.get("message", "")
        }

    def logout(self):
        """ログアウト"""
        self.auth_token = None
        self.token_type = None
        self.token_expiry = None

        # ストレージからトークン情報を削除
        self.storage.delete("auth_token")

        # APIクライアントのヘッダーを更新
        self._update_auth_header()

    def is_authenticated(self) -> bool:
        """認証状態を確認"""
        if not self.auth_token:
            return False

        # トークンの有効期限をチェック
        if self.token_expiry:
            current_time = time.time()
            if current_time > self.token_expiry:
                # トークンが期限切れ
                return False

        return True

    async def refresh_token(self) -> bool:
        """認証トークンを更新"""
        try:
            response = await self.api_client.post("/auth/refresh", {})

            if response.get("token"):
                # 新しいトークン情報を保存
                self.auth_token = response["token"]
                self.token_type = response.get("token_type", "Bearer")
                self.token_expiry = response.get("expires_at")

                # トークンをストレージに保存
                self._save_auth_token()

                # APIクライアントのヘッダーを更新
                self._update_auth_header()

                return True
        except Exception as e:
            print(f"Token refresh failed: {e}")

        return False

    def _load_auth_token(self):
        """ストレージからトークン情報を読み込む"""
        token_data = self.storage.get("auth_token")

        if token_data:
            try:
                data = json.loads(token_data)
                self.auth_token = data.get("token")
                self.token_type = data.get("token_type")
                self.token_expiry = data.get("expires_at")

                # APIクライアントのヘッダーを更新
                self._update_auth_header()
            except json.JSONDecodeError:
                # 無効なトークンデータ
                self.storage.delete("auth_token")

    def _save_auth_token(self):
        """トークン情報をストレージに保存"""
        if self.auth_token:
            token_data = {
                "token": self.auth_token,
                "token_type": self.token_type,
                "expires_at": self.token_expiry
            }

            self.storage.set("auth_token", json.dumps(token_data))

    def _update_auth_header(self):
        """APIクライアントの認証ヘッダーを更新"""
        if self.auth_token and self.token_type:
            self.api_client.headers["Authorization"] = f"{self.token_type} {self.auth_token}"
        elif "Authorization" in self.api_client.headers:
            del self.api_client.headers["Authorization"]
```

### セキュアなストレージ

```python
# /app/core/storage/storage_service.py
from abc import ABC, abstractmethod
import json

class StorageService(ABC):
    @abstractmethod
    def set(self, key: str, value: str) -> bool:
        """値を保存"""
        pass

    @abstractmethod
    def get(self, key: str) -> str:
        """値を取得"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """値を削除"""
        pass

    def set_object(self, key: str, obj) -> bool:
        """オブジェクトをJSON形式で保存"""
        try:
            json_value = json.dumps(obj)
            return self.set(key, json_value)
        except Exception:
            return False

    def get_object(self, key: str, default=None):
        """JSON形式で保存されたオブジェクトを取得"""
        json_value = self.get(key)

        if not json_value:
            return default

        try:
            return json.loads(json_value)
        except json.JSONDecodeError:
            return default

# プラットフォーム固有の実装は前回のプラットフォーム共通コード管理ガイドを参照
```

## 非同期処理と状態管理

非同期APIコールと状態管理の連携:

### 非同期ローダー

```python
# /app/presentation/widgets/async_loader.py
import flet as ft
import asyncio
from typing import Callable, Any, Optional

class AsyncLoader(ft.UserControl):
    def __init__(
        self,
        load_fn: Callable[[], Any],
        loading_widget: Optional[ft.Control] = None,
        error_widget: Optional[ft.Control] = None
    ):
        super().__init__()
        self.load_fn = load_fn
        self.loading_widget = loading_widget or self._default_loading_widget()
        self.error_widget = error_widget or self._default_error_widget()
        self.content = None
        self.error = None
        self.is_loading = True

    def _default_loading_widget(self):
        """デフォルトのローディング表示"""
        return ft.Column([
            ft.ProgressRing(),
            ft.Text("読み込み中...", size=14)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def _default_error_widget(self):
        """デフォルトのエラー表示"""
        return ft.Column([
            ft.Icon(ft.icons.ERROR_OUTLINE, color=ft.colors.RED, size=40),
            ft.Text("読み込みに失敗しました", size=14),
            ft.ElevatedButton("再試行", on_click=self.reload)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def build(self):
        """UIを構築"""
        self.container = ft.Container(
            content=self.loading_widget,
            alignment=ft.alignment.center
        )

        # データ読み込み開始
        asyncio.create_task(self._load_data())

        return self.container

    async def _load_data(self):
        """データを非同期で読み込む"""
        self.is_loading = True
        self.content = None
        self.error = None
        self.container.content = self.loading_widget
        self.update()

        try:
            # 非同期関数の場合とそうでない場合の両方に対応
            result = self.load_fn()
            if asyncio.iscoroutine(result):
                self.content = await result
            else:
                self.content = result

            self.is_loading = False
            self.container.content = self.content
        except Exception as e:
            self.is_loading = False
            self.error = str(e)
            self.container.content = self.error_widget

        self.update()

    def reload(self, e=None):
        """データを再読み込み"""
        asyncio.create_task(self._load_data())

# 使用例
def main(page: ft.Page):
    async def load_user_data():
        # APIからデータを取得する非同期関数の例
        user_repository = ServiceLocator.get("user_repository")
        users = await user_repository.get_all_users()

        # ユーザーリストのUIを構築
        return ft.Column([
            ft.Text("ユーザー一覧", size=20, weight=ft.FontWeight.BOLD),
            ft.ListView([
                ft.ListTile(
                    leading=ft.CircleAvatar(foreground_image_url=user.avatar_url) if user.avatar_url else None,
                    title=ft.Text(user.name),
                    subtitle=ft.Text(user.email)
                )
                for user in users
            ], spacing=2)
        ])

    # AsyncLoaderを使用してデータを読み込む
    user_list_loader = AsyncLoader(load_user_data)

    # ページにローダーを追加
    page.add(user_list_loader)
```

### リアクティブな状態管理

```python
# /app/core/state/observable.py
from typing import List, Callable, Any, Generic, TypeVar

T = TypeVar('T')

class Observable(Generic[T]):
    """値の変更を監視できるオブジェクト"""
    def __init__(self, initial_value: T):
        self._value = initial_value
        self._listeners: List[Callable[[T], None]] = []

    @property
    def value(self) -> T:
        """現在値を取得"""
        return self._value

    @value.setter
    def value(self, new_value: T):
        """値を設定し、リスナーに通知"""
        if self._value != new_value:
            self._value = new_value
            self._notify_listeners()

    def subscribe(self, listener: Callable[[T], None]) -> Callable[[], None]:
        """値の変更を監視するリスナーを追加"""
        self._listeners.append(listener)

        # 登録解除関数を返す
        def unsubscribe():
            if listener in self._listeners:
                self._listeners.remove(listener)

        return unsubscribe

    def _notify_listeners(self):
        """全リスナーに値の変更を通知"""
        for listener in self._listeners:
            listener(self._value)

# 状態管理クラス
# /app/core/state/app_state.py
from app.core.state.observable import Observable
from app.data.models.user import User
from typing import List, Optional

class AppState:
    def __init__(self):
        # 認証状態
        self.is_authenticated = Observable(False)

        # 現在のユーザー
        self.current_user = Observable(None)

        # カートアイテム
        self.cart_items = Observable([])

        # 読み込み中状態
        self.is_loading = Observable(False)

        # エラーメッセージ
        self.error_message = Observable("")

    def set_authenticated(self, is_auth: bool, user: Optional[User] = None):
        """認証状態を更新"""
        self.is_authenticated.value = is_auth
        self.current_user.value = user

    def add_to_cart(self, product, quantity=1):
        """カートに商品を追加"""
        current_items = list(self.cart_items.value)

        # 既存のアイテムをチェック
        for item in current_items:
            if item["product"].id == product.id:
                item["quantity"] += quantity
                self.cart_items.value = current_items
                return

        # 新しいアイテムを追加
        current_items.append({"product": product, "quantity": quantity})
        self.cart_items.value = current_items

    def remove_from_cart(self, product_id):
        """カートから商品を削除"""
        current_items = list(self.cart_items.value)
        self.cart_items.value = [
            item for item in current_items
            if item["product"].id != product_id
        ]

    def clear_cart(self):
        """カートを空にする"""
        self.cart_items.value = []

    def set_loading(self, is_loading: bool):
        """読み込み状態を設定"""
        self.is_loading.value = is_loading

    def set_error(self, message: str):
        """エラーメッセージを設定"""
        self.error_message.value = message

# グローバルな状態インスタンス
app_state = AppState()

# 状態を使用するコンポーネント例
# /app/presentation/widgets/cart_indicator.py
import flet as ft
from app.core.state.app_state import app_state

class CartIndicator(ft.UserControl):
    def __init__(self, on_click=None):
        super().__init__()
        self.on_click = on_click

        # カート状態の変更を監視
        self._unsubscribe = app_state.cart_items.subscribe(self._update_count)

    def _update_count(self, cart_items):
        """カート内アイテム数を更新"""
        if hasattr(self, "badge"):
            count = sum(item["quantity"] for item in cart_items)
            self.badge.content.value = str(count) if count > 0 else ""
            self.badge.visible = count > 0
            self.update()

    def build(self):
        """UIを構築"""
        self.badge = ft.Badge(
            content=ft.Text("0"),
            visible=False
        )

        button = ft.IconButton(
            icon=ft.icons.SHOPPING_CART,
            on_click=self.on_click,
            badge=self.badge
        )

        # 初期値を設定
        self._update_count(app_state.cart_items.value)

        return button

    def did_unmount(self):
        """コンポーネント破棄時の処理"""
        # 監視を解除
        self._unsubscribe()
```

## データキャッシュ戦略

効率的なデータキャッシュの実装:

### キャッシュマネージャー

```python
# /app/core/cache/cache_manager.py
import json
import time
from typing import Dict, Any, Optional
from app.core.storage.storage_service import StorageService

class CacheManager:
    def __init__(self, storage: StorageService):
        self.storage = storage
        self.cache_prefix = "cache_"
        self.default_ttl = 3600  # 1時間（秒）

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """データをキャッシュに保存"""
        if ttl is None:
            ttl = self.default_ttl

        cache_data = {
            "value": value,
            "expires_at": int(time.time()) + ttl
        }

        cache_key = f"{self.cache_prefix}{key}"
        return self.storage.set_object(cache_key, cache_data)

    def get(self, key: str, default=None) -> Any:
        """キャッシュからデータを取得"""
        cache_key = f"{self.cache_prefix}{key}"
        cache_data = self.storage.get_object(cache_key)

        if not cache_data:
            return default

        # 有効期限をチェック
        expires_at = cache_data.get("expires_at", 0)
        if int(time.time()) > expires_at:
            # 期限切れの場合はキャッシュを削除
            self.delete(key)
            return default

        return cache_data.get("value", default)

    def has(self, key: str) -> bool:
        """キーが存在し、かつ有効かどうかをチェック"""
        cache_key = f"{self.cache_prefix}{key}"
        cache_data = self.storage.get_object(cache_key)

        if not cache_data:
            return False

        expires_at = cache_data.get("expires_at", 0)
        return int(time.time()) <= expires_at

    def delete(self, key: str) -> bool:
        """キャッシュからデータを削除"""
        cache_key = f"{self.cache_prefix}{key}"
        return self.storage.delete(cache_key)

    def clear(self) -> bool:
        """全てのキャッシュを削除（プラットフォーム依存）"""
        # この実装は単純化されています
        # 実際のアプリでは、ストレージサービスがキープレフィックスに基づくクリア機能を
        # 提供する必要があります
        return True

# キャッシュを活用したリポジトリの例
# /app/data/repositories/cached_product_repository.py
from app.data.api.api_client import ApiClient
from app.data.models.product import Product
from app.core.cache.cache_manager import CacheManager
from typing import List, Optional

class CachedProductRepository:
    def __init__(self, api_client: ApiClient, cache_manager: CacheManager):
        self.api_client = api_client
        self.cache_manager = cache_manager
        self.cache_ttl = 300  # 5分（秒）

    async def get_all_products(self, force_refresh=False) -> List[Product]:
        """全商品を取得（キャッシュ対応）"""
        cache_key = "products_all"

        # キャッシュチェック
        if not force_refresh and self.cache_manager.has(cache_key):
            products_data = self.cache_manager.get(cache_key)
            return [Product.from_dict(p) for p in products_data]

        # APIからデータ取得
        response = await self.api_client.get("/products")
        products_data = response.get("data", [])

        # キャッシュに保存
        self.cache_manager.set(cache_key, products_data, self.cache_ttl)

        return [Product.from_dict(p) for p in products_data]

    async def get_product_by_id(self, product_id: int, force_refresh=False) -> Optional[Product]:
        """IDから商品を取得（キャッシュ対応）"""
        cache_key = f"product_{product_id}"

        # キャッシュチェック
        if not force_refresh and self.cache_manager.has(cache_key):
            product_data = self.cache_manager.get(cache_key)
            return Product.from_dict(product_data) if product_data else None

        # APIからデータ取得
        response = await self.api_client.get(f"/products/{product_id}")
        product_data = response.get("data")

        if product_data:
            # キャッシュに保存
            self.cache_manager.set(cache_key, product_data, self.cache_ttl)
            return Product.from_dict(product_data)

        return None

    async def create_product(self, product: Product) -> Product:
        """新規商品を作成"""
        response = await self.api_client.post("/products", product.to_dict())

        if response.get("data"):
            created_product = Product.from_dict(response["data"])

            # 全商品キャッシュをクリア（無効化）
            self.cache_manager.delete("products_all")

            return created_product

        raise ValueError("Invalid response format")

    async def update_product(self, product: Product) -> Product:
        """商品情報を更新"""
        response = await self.api_client.put(f"/products/{product.id}", product.to_dict())

        if response.get("data"):
            updated_product = Product.from_dict(response["data"])

            # 関連キャッシュを更新
            self.cache_manager.delete(f"product_{product.id}")
            self.cache_manager.delete("products_all")

            return updated_product

        raise ValueError("Invalid response format")

    async def delete_product(self, product_id: int) -> bool:
        """商品を削除"""
        response = await self.api_client.delete(f"/products/{product_id}")

        success = response.get("success", False)
        if success:
            # 関連キャッシュを削除
            self.cache_manager.delete(f"product_{product_id}")
            self.cache_manager.delete("products_all")

        return success
```

## オフライン対応

オフライン環境でも動作するアプリ実装:

### ネットワーク状態監視

```python
# /app/core/network/network_monitor.py
import flet as ft
import asyncio
from typing import Callable

class NetworkMonitor:
    def __init__(self, page: ft.Page):
        self.page = page
        self.is_online = True
        self.check_interval = 10  # 秒
        self.listeners = []
        self._running = False

    def start_monitoring(self):
        """ネットワーク監視を開始"""
        if not self._running:
            self._running = True
            asyncio.create_task(self._monitor_network())

    def stop_monitoring(self):
        """ネットワーク監視を停止"""
        self._running = False

    def add_listener(self, listener: Callable[[bool], None]):
        """オンライン状態リスナーを追加"""
        self.listeners.append(listener)
        return lambda: self.listeners.remove(listener) if listener in self.listeners else None

    async def _monitor_network(self):
        """定期的にネットワーク状態をチェック"""
        while self._running:
            previous_state = self.is_online
            self.is_online = await self._check_connection()

            # 状態が変化した場合のみリスナーに通知
            if previous_state != self.is_online:
                self._notify_listeners()

            await asyncio.sleep(self.check_interval)

    async def _check_connection(self) -> bool:
        """ネットワーク接続をチェック"""
        if self.page.platform == "web":
            # Webブラウザーの場合はJavaScriptを使用
            js_code = "navigator.onLine"
            return self.page.eval_js(js_code) == True
        else:
            # ネイティブアプリの場合は簡易疎通確認
            try:
                # 単純なAPIエンドポイントにリクエスト送信
                from app.data.api.api_client import ApiClient
                api_client = ApiClient()
                await api_client.get("/ping")
                return True
            except Exception:
                return False

    def _notify_listeners(self):
        """全リスナーに状態変更を通知"""
        for listener in self.listeners:
            listener(self.is_online)

# オフライン通知UI
# /app/presentation/widgets/offline_notifier.py
import flet as ft
from app.core.network.network_monitor import NetworkMonitor

class OfflineNotifier(ft.UserControl):
    def __init__(self, network_monitor: NetworkMonitor):
        super().__init__()
        self.network_monitor = network_monitor
        self.visible = not network_monitor.is_online

    def did_mount(self):
        """マウント時の処理"""
        # ネットワーク状態監視を開始
        self.unsubscribe = self.network_monitor.add_listener(self._on_network_state_change)

    def did_unmount(self):
        """アンマウント時の処理"""
        # 監視を解除
        self.unsubscribe()

    def _on_network_state_change(self, is_online: bool):
        """ネットワーク状態変更時の処理"""
        self.visible = not is_online
        self.update()

    def build(self):
        """UIを構築"""
        return ft.Banner(
            bgcolor=ft.colors.AMBER_100,
            leading=ft.Icon(ft.icons.WIFI_OFF, color=ft.colors.AMBER_800),
            content=ft.Text("オフラインモードです。一部の機能が制限されています。"),
            actions=[
                ft.TextButton("OK", on_click=lambda e: setattr(self, "visible", False))
            ],
            visible=self.visible
        )

# メインページでの使用例
def main(page: ft.Page):
    # ネットワーク監視を初期化
    network_monitor = NetworkMonitor(page)
    network_monitor.start_monitoring()

    # オフライン通知を設定
    offline_notifier = OfflineNotifier(network_monitor)

    # ページに追加
    page.add(offline_notifier)
```

### オフラインキューとデータ同期

```python
# /app/core/sync/offline_queue.py
import json
import time
import uuid
from enum import Enum
from typing import Dict, List, Any, Callable
from app.core.storage.storage_service import StorageService

class SyncStatus(Enum):
    PENDING = "pending"
    SYNCING = "syncing"
    COMPLETED = "completed"
    FAILED = "failed"

class SyncOperation(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class SyncTask:
    def __init__(
        self,
        operation: SyncOperation,
        endpoint: str,
        data: Dict[str, Any] = None,
        task_id: str = None
    ):
        self.task_id = task_id or str(uuid.uuid4())
        self.operation = operation
        self.endpoint = endpoint
        self.data = data or {}
        self.status = SyncStatus.PENDING
        self.created_at = int(time.time())
        self.last_attempt = None
        self.error = None

    def to_dict(self):
        """辞書に変換"""
        return {
            "task_id": self.task_id,
            "operation": self.operation.value,
            "endpoint": self.endpoint,
            "data": self.data,
            "status": self.status.value,
            "created_at": self.created_at,
            "last_attempt": self.last_attempt,
            "error": self.error
        }

    @classmethod
    def from_dict(cls, data):
        """辞書からオブジェクトを生成"""
        task = cls(
            operation=SyncOperation(data["operation"]),
            endpoint=data["endpoint"],
            data=data["data"],
            task_id=data["task_id"]
        )
        task.status = SyncStatus(data["status"])
        task.created_at = data["created_at"]
        task.last_attempt = data["last_attempt"]
        task.error = data["error"]
        return task

class OfflineQueue:
    def __init__(self, storage: StorageService):
        self.storage = storage
        self.queue_key = "offline_sync_queue"
        self.tasks: List[SyncTask] = []
        self.listeners: List[Callable[[], None]] = []

        # ストレージからタスクを読み込む
        self._load_tasks()

    def _load_tasks(self):
        """ストレージからタスクを読み込む"""
        tasks_data = self.storage.get_object(self.queue_key, [])
        self.tasks = [SyncTask.from_dict(task_data) for task_data in tasks_data]

    def _save_tasks(self):
        """タスクをストレージに保存"""
        tasks_data = [task.to_dict() for task in self.tasks]
        self.storage.set_object(self.queue_key, tasks_data)

        # リスナーに通知
        self._notify_listeners()

    def add_listener(self, listener: Callable[[], None]):
        """リスナーを追加"""
        self.listeners.append(listener)
        return lambda: self.listeners.remove(listener) if listener in self.listeners else None

    def _notify_listeners(self):
        """リスナーに通知"""
        for listener in self.listeners:
            listener()

    def enqueue(self, task: SyncTask) -> str:
        """タスクをキューに追加"""
        self.tasks.append(task)
        self._save_tasks()
        return task.task_id

    def enqueue_create(self, endpoint: str, data: Dict[str, Any]) -> str:
        """作成タスクをキューに追加"""
        task = SyncTask(SyncOperation.CREATE, endpoint, data)
        return self.enqueue(task)

    def enqueue_update(self, endpoint: str, data: Dict[str, Any]) -> str:
        """更新タスクをキューに追加"""
        task = SyncTask(SyncOperation.UPDATE, endpoint, data)
        return self.enqueue(task)

    def enqueue_delete(self, endpoint: str) -> str:
        """削除タスクをキューに追加"""
        task = SyncTask(SyncOperation.DELETE, endpoint)
        return self.enqueue(task)

    def get_pending_tasks(self) -> List[SyncTask]:
        """保留中のタスクを取得"""
        return [task for task in self.tasks if task.status == SyncStatus.PENDING]

    def get_all_tasks(self) -> List[SyncTask]:
        """全タスクを取得"""
        return self.tasks.copy()

    def update_task_status(self, task_id: str, status: SyncStatus, error: str = None):
        """タスクのステータスを更新"""
        for task in self.tasks:
            if task.task_id == task_id:
                task.status = status
                task.last_attempt = int(time.time())
                if error:
                    task.error = error
                break

        self._save_tasks()

    def remove_completed_tasks(self):
        """完了タスクを削除"""
        self.tasks = [task for task in self.tasks if task.status != SyncStatus.COMPLETED]
        self._save_tasks()

    def clear(self):
        """全タスクをクリア"""
        self.tasks = []
        self._save_tasks()

# データ同期サービス
# /app/core/sync/sync_service.py
import asyncio
from typing import Dict, Any, List, Callable
from app.core.sync.offline_queue import OfflineQueue, SyncStatus, SyncOperation
from app.data.api.api_client import ApiClient, ApiException
from app.core.network.network_monitor import NetworkMonitor

class SyncService:
    def __init__(self, api_client: ApiClient, offline_queue: OfflineQueue, network_monitor: NetworkMonitor):
        self.api_client = api_client
        self.offline_queue = offline_queue
        self.network_monitor = network_monitor
        self.sync_interval = 60  # 秒
        self.is_syncing = False
        self.sync_listeners: List[Callable[[int, int], None]] = []

        # ネットワーク状態リスナーを設定
        self.network_monitor.add_listener(self._on_network_state_change)

    def start_sync(self):
        """同期処理を開始"""
        asyncio.create_task(self._sync_loop())

    def add_sync_listener(self, listener: Callable[[int, int], None]):
        """同期状態リスナーを追加"""
        self.sync_listeners.append(listener)

    def remove_sync_listener(self, listener: Callable[[int, int], None]):
        """同期状態リスナーを削除"""
        if listener in self.sync_listeners:
            self.sync_listeners.remove(listener)

    def _on_network_state_change(self, is_online: bool):
        """ネットワーク状態変更時の処理"""
        if is_online:
            # オンラインに戻ったら即時同期を実行
            asyncio.create_task(self.sync_pending_tasks())

    async def _sync_loop(self):
        """定期的に同期を実行"""
        while True:
            if self.network_monitor.is_online:
                await self.sync_pending_tasks()

            await asyncio.sleep(self.sync_interval)

    async def sync_pending_tasks(self):
        """保留中のタスクを同期"""
        if self.is_syncing:
            return

        self.is_syncing = True

        try:
            pending_tasks = self.offline_queue.get_pending_tasks()
            total_tasks = len(pending_tasks)
            completed_tasks = 0

            # リスナーに同期開始を通知
            for listener in self.sync_listeners:
                listener(completed_tasks, total_tasks)

            for task in pending_tasks:
                # タスク処理中のステータスに更新
                self.offline_queue.update_task_status(task.task_id, SyncStatus.SYNCING)

                try:
                    # タスクの種類に応じた処理
                    if task.operation == SyncOperation.CREATE:
                        await self.api_client.post(task.endpoint, task.data)
                    elif task.operation == SyncOperation.UPDATE:
                        await self.api_client.put(task.endpoint, task.data)
                    elif task.operation == SyncOperation.DELETE:
                        await self.api_client.delete(task.endpoint)

                    # 成功時はステータスを完了に更新
                    self.offline_queue.update_task_status(task.task_id, SyncStatus.COMPLETED)
                    completed_tasks += 1

                    # リスナーに進捗を通知
                    for listener in self.sync_listeners:
                        listener(completed_tasks, total_tasks)
                except ApiException as e:
                    # APIエラー時はステータスを失敗に更新
                    self.offline_queue.update_task_status(
                        task.task_id,
                        SyncStatus.FAILED,
                        f"API Error: {e.message}"
                    )
                except Exception as e:
                    # その他のエラー時もステータスを失敗に更新
                    self.offline_queue.update_task_status(
                        task.task_id,
                        SyncStatus.FAILED,
                        f"Error: {str(e)}"
                    )

            # 完了したタスクを削除
            self.offline_queue.remove_completed_tasks()

        finally:
            self.is_syncing = False

    def create_offline(self, endpoint: str, data: Dict[str, Any]) -> str:
        """オフラインでの作成処理をキューに追加"""
        return self.offline_queue.enqueue_create(endpoint, data)

    def update_offline(self, endpoint: str, data: Dict[str, Any]) -> str:
        """オフラインでの更新処理をキューに追加"""
        return self.offline_queue.enqueue_update(endpoint, data)

    def delete_offline(self, endpoint: str) -> str:
        """オフラインでの削除処理をキューに追加"""
        return self.offline_queue.enqueue_delete(endpoint)

# オフライン対応リポジトリの例
# /app/data/repositories/offline_product_repository.py
from app.data.api.api_client import ApiClient, ApiException
from app.data.models.product import Product
from app.core.cache.cache_manager import CacheManager
from app.core.sync.sync_service import SyncService
from app.core.network.network_monitor import NetworkMonitor
from typing import List, Optional, Dict, Any

class OfflineProductRepository:
    def __init__(
        self,
        api_client: ApiClient,
        cache_manager: CacheManager,
        sync_service: SyncService,
        network_monitor: NetworkMonitor
    ):
        self.api_client = api_client
        self.cache_manager = cache_manager
        self.sync_service = sync_service
        self.network_monitor = network_monitor
        self.cache_ttl = 3600  # 1時間（秒）

    async def get_all_products(self, force_refresh=False) -> List[Product]:
        """全商品を取得（オフライン対応）"""
        cache_key = "products_all"

        # オンライン時はAPIからデータ取得を試みる
        if self.network_monitor.is_online and (force_refresh or not self.cache_manager.has(cache_key)):
            try:
                response = await self.api_client.get("/products")
                products_data = response.get("data", [])

                # キャッシュに保存
                self.cache_manager.set(cache_key, products_data, self.cache_ttl)
            except Exception:
                # API通信失敗時はキャッシュを使用
                products_data = self.cache_manager.get(cache_key, [])
        else:
            # オフライン時やキャッシュ優先時はキャッシュを使用
            products_data = self.cache_manager.get(cache_key, [])

        return [Product.from_dict(p) for p in products_data]

    async def get_product_by_id(self, product_id: int, force_refresh=False) -> Optional[Product]:
        """IDから商品を取得（オフライン対応）"""
        cache_key = f"product_{product_id}"

        # オンライン時はAPIからデータ取得を試みる
        if self.network_monitor.is_online and (force_refresh or not self.cache_manager.has(cache_key)):
            try:
                response = await self.api_client.get(f"/products/{product_id}")
                product_data = response.get("data")

                if product_data:
                    # キャッシュに保存
                    self.cache_manager.set(cache_key, product_data, self.cache_ttl)
            except Exception:
                # API通信失敗時はキャッシュを使用
                product_data = self.cache_manager.get(cache_key)
        else:
            # オフライン時やキャッシュ優先時はキャッシュを使用
            product_data = self.cache_manager.get(cache_key)

        return Product.from_dict(product_data) if product_data else None

    async def create_product(self, product: Product) -> Product:
        """新規商品を作成（オフライン対応）"""
        product_data = product.to_dict()

        # オンライン時は直接API呼び出し
        if self.network_monitor.is_online:
            try:
                response = await self.api_client.post("/products", product_data)
                created_product = Product.from_dict(response.get("data", {}))

                # キャッシュを更新
                self._update_product_cache(created_product)

                return created_product
            except Exception:
                # API通信失敗時はオフラインキューに追加
                pass

        # オフライン時または通信失敗時
        # 一時的なIDを割り当て
        temp_id = -int(time.time())
        product.id = temp_id
        product_data["id"] = temp_id

        # キャッシュを更新（一時データ）
        self._update_product_cache(product)

        # 同期キューに追加
        self.sync_service.create_offline("/products", product_data)

        return product

    async def update_product(self, product: Product) -> Product:
        """商品情報を更新（オフライン対応）"""
        product_data = product.to_dict()

        # オンライン時は直接API呼び出し
        if self.network_monitor.is_online:
            try:
                response = await self.api_client.put(f"/products/{product.id}", product_data)
                updated_product = Product.from_dict(response.get("data", {}))

                # キャッシュを更新
                self._update_product_cache(updated_product)

                return updated_product
            except Exception:
                # API通信失敗時はオフラインキューに追加
                pass

        # オフライン時または通信失敗時
        # キャッシュを更新（ローカルデータ）
        self._update_product_cache(product)

        # 同期キューに追加
        self.sync_service.update_offline(f"/products/{product.id}", product_data)

        return product

    async def delete_product(self, product_id: int) -> bool:
        """商品を削除（オフライン対応）"""
        # オンライン時は直接API呼び出し
        if self.network_monitor.is_online:
            try:
                response = await self.api_client.delete(f"/products/{product_id}")
                success = response.get("success", False)

                if success:
                    # キャッシュから削除
                    self._remove_product_from_cache(product_id)

                return success
            except Exception:
                # API通信失敗時はオフラインキューに追加
                pass

        # オフライン時または通信失敗時
        # キャッシュから削除
        self._remove_product_from_cache(product_id)

        # 同期キューに追加
        self.sync_service.delete_offline(f"/products/{product_id}")

        return True

    def _update_product_cache(self, product: Product):
        """キャッシュにおける商品情報を更新"""
        # 個別の商品キャッシュを更新
        cache_key = f"product_{product.id}"
        self.cache_manager.set(cache_key, product.to_dict(), self.cache_ttl)

        # 全商品リストキャッシュの更新
        all_cache_key = "products_all"
        products_data = self.cache_manager.get(all_cache_key, [])

        # 既存の商品を探す
        product_found = False
        for i, p in enumerate(products_data):
            if p.get("id") == product.id:
                products_data[i] = product.to_dict()
                product_found = True
                break

        # 存在しない場合は追加
        if not product_found:
            products_data.append(product.to_dict())

        # 更新されたリストをキャッシュに保存
        self.cache_manager.set(all_cache_key, products_data, self.cache_ttl)

    def _remove_product_from_cache(self, product_id: int):
        """キャッシュから商品を削除"""
        # 個別の商品キャッシュを削除
        cache_key = f"product_{product_id}"
        self.cache_manager.delete(cache_key)

        # 全商品リストキャッシュから削除
        all_cache_key = "products_all"
        products_data = self.cache_manager.get(all_cache_key, [])

        # 削除対象の商品を除外
        updated_products = [p for p in products_data if p.get("id") != product_id]

        # 更新されたリストをキャッシュに保存
        self.cache_manager.set(all_cache_key, updated_products, self.cache_ttl)
```

## エラーハンドリング

APIエラーの効果的な処理:

### エラーハンドラー

```python
# /app/core/errors/error_handler.py
from typing import Dict, Any, Optional, Callable
import flet as ft
from app.data.api.api_client import ApiException

class ErrorHandler:
    def __init__(self, page: ft.Page):
        self.page = page
        self.default_handlers = {
            400: self._handle_bad_request,
            401: self._handle_unauthorized,
            403: self._handle_forbidden,
            404: self._handle_not_found,
            422: self._handle_validation_error,
            500: self._handle_server_error
        }
        self.custom_handlers = {}

    def register_handler(self, status_code: int, handler: Callable[[Dict[str, Any]], None]):
        """カスタムエラーハンドラーを登録"""
        self.custom_handlers[status_code] = handler

    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """エラーを処理"""
        context = context or {}

        if isinstance(error, ApiException):
            # APIエラーの処理
            status_code = error.status_code
            error_data = error.error_data

            # カスタムハンドラーを優先
            if status_code in self.custom_handlers:
                self.custom_handlers[status_code](error_data)
            elif status_code in self.default_handlers:
                self.default_handlers[status_code](error_data)
            else:
                self._handle_unknown_error(error_data)
        else:
            # 一般的なエラーの処理
            self._handle_generic_error(error, context)

    def _handle_bad_request(self, error_data: Dict[str, Any]):
        """400エラーの処理"""
        message = error_data.get("message", "リクエストの形式が正しくありません")
        self._show_error_dialog("リクエストエラー", message)

    def _handle_unauthorized(self, error_data: Dict[str, Any]):
        """401エラーの処理"""
        message = error_data.get("message", "認証が必要です")
        self._show_error_dialog("認証エラー", message)

        # ログイン画面に遷移
        from app.core.state.app_state import app_state
        app_state.set_authenticated(False)
        self.page.go("/login")

    def _handle_forbidden(self, error_data: Dict[str, Any]):
        """403エラーの処理"""
        message = error_data.get("message", "この操作を行う権限がありません")
        self._show_error_dialog("権限エラー", message)

    def _handle_not_found(self, error_data: Dict[str, Any]):
        """404エラーの処理"""
        message = error_data.get("message", "リクエストされたリソースが見つかりません")
        self._show_error_dialog("リソースが見つかりません", message)

    def _handle_validation_error(self, error_data: Dict[str, Any]):
        """422バリデーションエラーの処理"""
        message = error_data.get("message", "入力データが正しくありません")

        # バリデーションエラーの詳細を表示
        details = ""
        if "errors" in error_data and isinstance(error_data["errors"], dict):
            for field, errors in error_data["errors"].items():
                if isinstance(errors, list):
                    details += f"\n・{field}: {', '.join(errors)}"

        self._show_error_dialog("入力エラー", message, details=details)

    def _handle_server_error(self, error_data: Dict[str, Any]):
        """500サーバーエラーの処理"""
        message = error_data.get("message", "サーバーで問題が発生しました")
        self._show_error_dialog("サーバーエラー", message)

    def _handle_unknown_error(self, error_data: Dict[str, Any]):
        """未知のAPIエラーの処理"""
        status_code = error_data.get("status_code", "?")
        message = error_data.get("message", "不明なエラーが発生しました")
        self._show_error_dialog(f"エラー ({status_code})", message)

    def _handle_generic_error(self, error: Exception, context: Dict[str, Any]):
        """一般的なエラーの処理"""
        message = str(error)
        self._show_error_dialog("エラーが発生しました", message)

    def _show_error_dialog(self, title: str, message: str, details: str = ""):
        """エラーダイアログを表示"""
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Column([
                ft.Text(message),
                ft.Text(details) if details else ft.Container()
            ], tight=True),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self.page.dialog.open = False)
            ]
        )

        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()

# 実装例
def main(page: ft.Page):
    # エラーハンドラーの初期化
    error_handler = ErrorHandler(page)

    # カスタムエラーハンドラーの登録（例）
    def handle_rate_limit(error_data):
        reset_time = error_data.get("reset_at", "しばらく")
        message = f"リクエスト回数の上限に達しました。{reset_time}後に再試行してください。"
        page.snack_bar = ft.SnackBar(content=ft.Text(message))
        page.snack_bar.open = True
        page.update()

    error_handler.register_handler(429, handle_rate_limit)

    # API呼び出しの例
    async def load_data():
        try:
            api_client = ApiClient()
            response = await api_client.get("/protected-resource")
            # 応答の処理
        except ApiException as e:
            error_handler.handle_error(e)
        except Exception as e:
            error_handler.handle_error(e)

    # ボタンクリック時にデータ読み込み
    page.add(
        ft.ElevatedButton("データ読み込み", on_click=lambda e: asyncio.create_task(load_data()))
    )
```

### エラーバウンダリー

```python
# /app/presentation/widgets/error_boundary.py
import flet as ft
import traceback
from typing import Callable, Optional, Any

class ErrorBoundary(ft.UserControl):
    def __init__(
        self,
        child_builder: Callable[[], ft.Control],
        fallback_builder: Optional[Callable[[Exception], ft.Control]] = None
    ):
        super().__init__()
        self.child_builder = child_builder
        self.fallback_builder = fallback_builder or self._default_fallback
        self.error = None
        self.child = None

    def _default_fallback(self, error: Exception) -> ft.Control:
        """デフォルトのフォールバックUI"""
        stack_trace = traceback.format_exc()
        return ft.Column([
            ft.Text("エラーが発生しました", size=20, color=ft.colors.RED),
            ft.Text(str(error), color=ft.colors.RED_700),
            ft.Container(
                content=ft.Text(stack_trace, size=12, selectable=True),
                bgcolor=ft.colors.BLACK,
                padding=10,
                border_radius=5,
                color=ft.colors.WHITE
            ),
            ft.ElevatedButton("再試行", on_click=self.retry)
        ], spacing=10, padding=20)

    def build(self):
        """UIを構築"""
        try:
            if self.error is None:
                self.child = self.child_builder()
                return self.child
            else:
                return self.fallback_builder(self.error)
        except Exception as e:
            self.error = e
            return self.fallback_builder(e)

    def retry(self, e=None):
        """再試行"""
        self.error = None
        self.update()

# 使用例
def main(page: ft.Page):
    # 子コンポーネントビルダー（エラーを発生させる可能性あり）
    def build_data_view():
        # データ取得に成功した場合
        if page.data_loaded:
            return ft.Column([
                ft.Text("データ一覧", size=20),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID")),
                        ft.DataColumn(ft.Text("名前")),
                        ft.DataColumn(ft.Text("値"))
                    ],
                    rows=page.data
                )
            ])

        # エラーケースをシミュレート
        raise Exception("データの読み込みに失敗しました")

    # カスタムフォールバックビルダー
    def build_fallback(error):
        return ft.Column([
            ft.Icon(ft.icons.ERROR_OUTLINE, color=ft.colors.RED, size=40),
            ft.Text("データの表示中にエラーが発生しました", size=16),
            ft.Text(str(error), size=14, color=ft.colors.RED_400),
            ft.ElevatedButton("再読み込み", on_click=lambda e: setattr(page, "data_loaded", True))
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    # エラーバウンダリーをページに追加
    page.add(
        ErrorBoundary(
            child_builder=build_data_view,
            fallback_builder=build_fallback
        )
    )

    # データ読み込みシミュレーション
    page.data_loaded = False
    page.data = []
```

## WebSocketと実時間通信

リアルタイムデータ更新のためのWebSocket実装:

### WebSocketクライアント

```python
# /app/data/websocket/websocket_client.py
import asyncio
import json
import time
import flet as ft
from typing import Dict, List, Any, Callable, Optional

class WebSocketClient:
    def __init__(self, page: ft.Page, url: str):
        self.page = page
        self.url = url
        self.ws = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1.0  # 秒
        self.message_handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self.on_connect_handlers: List[Callable[[], None]] = []
        self.on_disconnect_handlers: List[Callable[[], None]] = []
        self._task = None

    async def connect(self):
        """WebSocketに接続"""
        if self.connected:
            return

        try:
            # JavaScriptを使用してWebSocketに接続
            js_code = f"""
            (function() {{
                const socket = new WebSocket('{self.url}');

                socket.onopen = function(e) {{
                    return true;
                }};

                socket.onmessage = function(e) {{
                    window._lastWebSocketMessage = e.data;
                    return true;
                }};

                socket.onclose = function(e) {{
                    window._webSocketClosed = true;
                    return false;
                }};

                socket.onerror = function(e) {{
                    window._webSocketError = true;
                    return false;
                }};

                window._webSocket = socket;
                return true;
            }})();
            """

            success = self.page.eval_js(js_code)

            if success:
                self.connected = True
                self.reconnect_attempts = 0

                # 接続ハンドラーを呼び出し
                for handler in self.on_connect_handlers:
                    handler()

                # メッセージ受信ループを開始
                self._task = asyncio.create_task(self._message_loop())
        except Exception as e:
            print(f"WebSocket connection error: {e}")
            await self._attempt_reconnect()

    async def _message_loop(self):
        """受信メッセージの処理ループ"""
        while self.connected:
            try:
                # 新規メッセージをチェック
                js_code = """
                if (window._lastWebSocketMessage !== undefined) {
                    const msg = window._lastWebSocketMessage;
                    window._lastWebSocketMessage = undefined;
                    return msg;
                }
                return null;
                """

                message = self.page.eval_js(js_code)

                if message:
                    # メッセージの処理
                    try:
                        data = json.loads(message)
                        event_type = data.get("type")

                        if event_type and event_type in self.message_handlers:
                            # イベントタイプに対応するハンドラーを呼び出し
                            for handler in self.message_handlers[event_type]:
                                handler(data)
                    except json.JSONDecodeError:
                        print(f"Invalid WebSocket message format: {message}")

                # 接続状態をチェック
                js_code = """
                if (window._webSocketClosed || window._webSocketError) {
                    window._webSocketClosed = undefined;
                    window._webSocketError = undefined;
                    return false;
                }
                return window._webSocket.readyState === 1;
                """

                is_connected = self.page.eval_js(js_code)

                if not is_connected:
                    self.connected = False

                    # 切断ハンドラーを呼び出し
                    for handler in self.on_disconnect_handlers:
                        handler()

                    # 再接続を試みる
                    await self._attempt_reconnect()
                    break

            except Exception as e:
                print(f"WebSocket message processing error: {e}")

            # 少し待機
            await asyncio.sleep(0.1)

    async def _attempt_reconnect(self):
        """接続再試行"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print("Maximum reconnection attempts reached")
            return

        self.reconnect_attempts += 1
        delay = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))  # 指数バックオフ

        print(f"Attempting to reconnect in {delay} seconds (attempt {self.reconnect_attempts})")
        await asyncio.sleep(delay)

        await self.connect()

    async def disconnect(self):
        """WebSocket接続を閉じる"""
        if not self.connected:
            return

        js_code = """
        if (window._webSocket) {
            window._webSocket.close();
            window._webSocket = undefined;
            return true;
        }
        return false;
        """

        self.page.eval_js(js_code)
        self.connected = False

        if self._task:
            self._task.cancel()
            self._task = None

    async def send(self, message: Dict[str, Any]):
        """メッセージを送信"""
        if not self.connected:
            await self.connect()
            if not self.connected:
                raise Exception("WebSocket is not connected")

        message_json = json.dumps(message)
        js_code = f"""
        if (window._webSocket && window._webSocket.readyState === 1) {{
            window._webSocket.send('{message_json}');
            return true;
        }}
        return false;
        """

        success = self.page.eval_js(js_code)
        return success

    def on_message(self, event_type: str, handler: Callable[[Dict[str, Any]], None]):
        """メッセージハンドラーを登録"""
        if event_type not in self.message_handlers:
            self.message_handlers[event_type] = []

        self.message_handlers[event_type].append(handler)

    def on_connect(self, handler: Callable[[], None]):
        """接続ハンドラーを登録"""
        self.on_connect_handlers.append(handler)

    def on_disconnect(self, handler: Callable[[], None]):
        """切断ハンドラーを登録"""
        self.on_disconnect_handlers.append(handler)

    def is_connected(self) -> bool:
        """接続状態を取得"""
        return self.connected
```

### リアルタイムデータ更新

```python
# /app/presentation/realtime/realtime_product_list.py
import flet as ft
import asyncio
from typing import List
from app.data.models.product import Product
from app.data.repositories.offline_product_repository import OfflineProductRepository
from app.data.websocket.websocket_client import WebSocketClient

class RealtimeProductList(ft.UserControl):
    def __init__(self, repository: OfflineProductRepository, ws_client: WebSocketClient):
        super().__init__()
        self.repository = repository
        self.ws_client = ws_client
        self.products = []
        self.loading = True

    def did_mount(self):
        """マウント時の処理"""
        # データ読み込み
        asyncio.create_task(self._load_data())

        # WebSocketイベントハンドラーを設定
        self.ws_client.on_connect(self._on_ws_connect)
        self.ws_client.on_message("product_created", self._on_product_created)
        self.ws_client.on_message("product_updated", self._on_product_updated)
        self.ws_client.on_message("product_deleted", self._on_product_deleted)

        # WebSocket接続
        asyncio.create_task(self.ws_client.connect())

    def build(self):
        """UIを構築"""
        self.progress = ft.ProgressRing()

        self.product_list = ft.ListView(
            spacing=2,
            padding=10,
            expand=True
        )

        return ft.Column([
            ft.Text("商品一覧（リアルタイム更新）", size=20, weight=ft.FontWeight.BOLD),
            self.progress if self.loading else self.product_list
        ])

    async def _load_data(self):
        """商品データを読み込み"""
        self.loading = True
        self.update()

        try:
            self.products = await self.repository.get_all_products()
            self._update_product_list()
        except Exception as e:
            print(f"Error loading products: {e}")

        self.loading = False
        self.update()

    def _update_product_list(self):
        """商品リストUIを更新"""
        self.product_list.controls = [
            self._create_product_item(product)
            for product in self.products
        ]
        self.update()

    def _create_product_item(self, product: Product) -> ft.Control:
        """商品アイテムUIを作成"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(product.name, weight=ft.FontWeight.BOLD, size=16),
                        ft.Container(
                            content=ft.Text(f"¥{product.price:,}", size=14),
                            bgcolor=ft.colors.BLUE_50,
                            padding=5,
                            border_radius=5
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(product.description or "説明なし", size=14)
                ]),
                padding=10,
                width=400
            )
        )

    def _on_ws_connect(self):
        """WebSocket接続時の処理"""
        print("Connected to WebSocket")

        # 商品購読メッセージを送信
        asyncio.create_task(self.ws_client.send({
            "type": "subscribe",
            "channel": "products"
        }))

    def _on_product_created(self, data):
        """商品作成イベント処理"""
        product_data = data.get("product", {})
        new_product = Product.from_dict(product_data)

        # 同じIDの商品が存在しないことを確認
        for i, product in enumerate(self.products):
            if product.id == new_product.id:
                return

        # 商品リストに追加
        self.products.append(new_product)

        # 商品リストUIを更新
        self.product_list.controls.append(self._create_product_item(new_product))
        self.update()

    def _on_product_updated(self, data):
        """商品更新イベント処理"""
        product_data = data.get("product", {})
        updated_product = Product.from_dict(product_data)

        # 既存の商品を更新
        for i, product in enumerate(self.products):
            if product.id == updated_product.id:
                self.products[i] = updated_product
                self.product_list.controls[i] = self._create_product_item(updated_product)
                self.update()
                break

    def _on_product_deleted(self, data):
        """商品削除イベント処理"""
        product_id = data.get("product_id")

        if product_id:
            # 削除された商品を商品リストから削除
            for i, product in enumerate(self.products):
                if product.id == product_id:
                    self.products.pop(i)
                    self.product_list.controls.pop(i)
                    self.update()
                    break
```

## デバッグとモニタリング

APIとバックエンド連携のデバッグとモニタリング:

### アプリ内デバッグコンソール

```python
# /app/presentation/debug/debug_console.py
import flet as ft
import json
from datetime import datetime
from typing import List, Dict, Any

class LogEntry:
    def __init__(
        self,
        message: str,
        level: str = "info",
        timestamp: float = None,
        data: Any = None
    ):
        self.message = message
        self.level = level
        self.timestamp = timestamp or datetime.now().timestamp()
        self.data = data

    @property
    def formatted_timestamp(self) -> str:
        """フォーマットされたタイムスタンプ"""
        dt = datetime.fromtimestamp(self.timestamp)
        return dt.strftime("%H:%M:%S.%f")[:-3]

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "message": self.message,
            "level": self.level,
            "timestamp": self.timestamp,
            "data": self.data
        }

class DebugConsole(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.logs: List[LogEntry] = []
        self.max_logs = 100
        self.visible = False
        self.filter_level = None

    def build(self):
        """UIを構築"""
        self.log_list = ft.ListView(
            spacing=1,
            divider_thickness=0.5,
            auto_scroll=True,
            expand=True
        )

        # フィルター設定UI
        self.level_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("all", "全てのレベル"),
                ft.dropdown.Option("debug", "デバッグ"),
                ft.dropdown.Option("info", "情報"),
                ft.dropdown.Option("warning", "警告"),
                ft.dropdown.Option("error", "エラー")
            ],
            value="all",
            on_change=self._on_filter_changed
        )

        # 検索ボックス
        self.search_field = ft.TextField(
            hint_text="検索...",
            on_change=self._on_search_changed
        )

        # ツールバー
        toolbar = ft.Row([
            ft.Text("レベル: "),
            self.level_dropdown,
            self.search_field,
            ft.IconButton(
                icon=ft.icons.DELETE_SWEEP,
                tooltip="ログをクリア",
                on_click=self._clear_logs
            ),
            ft.IconButton(
                icon=ft.icons.DOWNLOAD,
                tooltip="ログをエクスポート",
                on_click=self._export_logs
            ),
            ft.IconButton(
                icon=ft.icons.CLOSE,
                tooltip="閉じる",
                on_click=self._toggle_visibility
            )
        ], alignment=ft.MainAxisAlignment.END)

        return ft.Container(
            content=ft.Column([
                toolbar,
                self.log_list
            ]),
            bgcolor=ft.colors.BLACK,
            border_radius=5,
            padding=10,
            expand=True,
            visible=self.visible
        )

    def log(self, message: str, level: str = "info", data: Any = None):
        """ログを追加"""
        log_entry = LogEntry(message, level, data=data)

        # ログリストを更新
        self.logs.append(log_entry)

        # 最大数を超えた場合は古いログを削除
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

        # ログリストUIを更新
        self._update_log_list()

    def debug(self, message: str, data: Any = None):
        """デバッグログを追加"""
        self.log(message, "debug", data)

    def info(self, message: str, data: Any = None):
        """情報ログを追加"""
        self.log(message, "info", data)

    def warning(self, message: str, data: Any = None):
        """警告ログを追加"""
        self.log(message, "warning", data)

    def error(self, message: str, data: Any = None):
        """エラーログを追加"""
        self.log(message, "error", data)

    def _update_log_list(self):
        """ログリストUIを更新"""
        # フィルタリング
        filtered_logs = self.logs

        if self.filter_level and self.filter_level != "all":
            filtered_logs = [log for log in filtered_logs if log.level == self.filter_level]

        # 検索フィルタリング
        if hasattr(self, "search_term") and self.search_term:
            filtered_logs = [
                log for log in filtered_logs
                if self.search_term.lower() in log.message.lower()
            ]

        # ログリストUIを構築
        self.log_list.controls = [self._create_log_item(log) for log in filtered_logs]

        if self.visible:
            self.update()

    def _create_log_item(self, log: LogEntry) -> ft.Control:
        """ログアイテムUIを作成"""
        # レベルに応じた色を設定
        level_colors = {
            "debug": ft.colors.GREY,
            "info": ft.colors.BLUE,
            "warning": ft.colors.AMBER,
            "error": ft.colors.RED
        }
        color = level_colors.get(log.level, ft.colors.WHITE)

        # タイムスタンプとレベル表示
        header = ft.Row([
            ft.Text(log.formatted_timestamp, size=12, color=ft.colors.GREY),
            ft.Container(
                content=ft.Text(log.level.upper(), size=10),
                bgcolor=color,
                padding=ft.padding.only(left=5, right=5, top=2, bottom=2),
                border_radius=3
            )
        ], spacing=5)

        # メッセージ表示
        message = ft.Text(log.message, color=ft.colors.WHITE)

        # データがある場合の詳細表示
        data_text = None
        if log.data:
            try:
                if isinstance(log.data, dict) or isinstance(log.data, list):
                    data_str = json.dumps(log.data, indent=2, ensure_ascii=False)
                else:
                    data_str = str(log.data)

                data_text = ft.Text(
                    data_str,
                    size=12,
                    color=ft.colors.GREY_300,
                    selectable=True,
                    no_wrap=False
                )
            except:
                data_text = ft.Text(
                    "データの表示に失敗しました",
                    size=12,
                    color=ft.colors.GREY
                )

        # ログアイテムのコンテナ
        container_content = [header, message]
        if data_text:
            container_content.append(data_text)

        return ft.Container(
            content=ft.Column(container_content, spacing=2, tight=True),
            padding=5,
            border_radius=3,
            border=ft.border.all(1, ft.colors.GREY_800)
        )

    def _on_filter_changed(self, e):
        """レベルフィルター変更時の処理"""
        self.filter_level = self.level_dropdown.value
        self._update_log_list()

    def _on_search_changed(self, e):
        """検索テキスト変更時の処理"""
        self.search_term = self.search_field.value
        self._update_log_list()

    def _clear_logs(self, e=None):
        """ログをクリア"""
        self.logs = []
        self._update_log_list()

    def _export_logs(self, e=None):
        """ログをエクスポート"""
        # 実装例では、ログをJSONとしてエクスポート
        log_data = [log.to_dict() for log in self.logs]
        json_data = json.dumps(log_data, indent=2, ensure_ascii=False)

        # クリップボードにコピー（実際のアプリでは保存ダイアログなどを表示）
        self.page.set_clipboard(json_data)

        # 通知
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("ログがクリップボードにコピーされました"),
            action="OK"
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _toggle_visibility(self, e=None):
        """表示/非表示を切り替え"""
        self.visible = not self.visible
        self.update()

    def show(self):
        """コンソールを表示"""
        self.visible = True
        self.update()

    def hide(self):
        """コンソールを非表示"""
        self.visible = False
        self.update()

# APIクライアントとの連携
# /app/data/api/debug_api_client.py
import httpx
import json
from typing import Dict, Any, Optional
from app.data.api.api_client import ApiClient
from app.presentation.debug.debug_console import DebugConsole

class DebugApiClient(ApiClient):
    def __init__(self, debug_console: DebugConsole):
        super().__init__()
        self.debug_console = debug_console

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET リクエストを送信（デバッグ機能付き）"""
        url = f"{self.base_url}{endpoint}"
        self.debug_console.info(f"GET リクエスト: {url}", params)

        start_time = datetime.now()

        try:
            response = await super().get(endpoint, params)

            # レスポンス時間を計算
            elapsed = (datetime.now() - start_time).total_seconds() * 1000  # ミリ秒

            # レスポンスをログに記録
            self.debug_console.info(
                f"レスポンス: {url} ({elapsed:.0f}ms)",
                response
            )

            return response
        except Exception as e:
            # エラーをログに記録
            self.debug_console.error(f"エラー: {url}", str(e))
            raise

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST リクエストを送信（デバッグ機能付き）"""
        url = f"{self.base_url}{endpoint}"
        self.debug_console.info(f"POST リクエスト: {url}", data)

        start_time = datetime.now()

        try:
            response = await super().post(endpoint, data)

            # レスポンス時間を計算
            elapsed = (datetime.now() - start_time).total_seconds() * 1000  # ミリ秒

            # レスポンスをログに記録
            self.debug_console.info(
                f"レスポンス: {url} ({elapsed:.0f}ms)",
                response
            )

            return response
        except Exception as e:
            # エラーをログに記録
            self.debug_console.error(f"エラー: {url}", str(e))
            raise

    # PUT, DELETEメソッドも同様に実装

# 使用例
def main(page: ft.Page):
    # デバッグコンソールを初期化
    debug_console = DebugConsole()

    # デバッグ対応APIクライアントを作成
    api_client = DebugApiClient(debug_console)

    # デバッグコンソールトグルボタン
    debug_button = ft.FloatingActionButton(
        icon=ft.icons.BUG_REPORT,
        on_click=lambda e: debug_console.show()
    )

    # ページにコンポーネントを追加
    page.add(
        debug_console,
        debug_button
    )
```

## 実装例とパターン

### APIサービスとリポジトリの連携

APIアクセスとデータ管理を効率的に連携する総合的な実装例:

```python
# プロジェクト構造の例
# /app
#   /core
#     /config.py            # 設定
#     /di/service_locator.py # 依存性注入
#   /data
#     /api/api_client.py    # APIクライアント
#     /models/task.py       # データモデル
#     /repositories/task_repository.py # リポジトリ
#   /presentation
#     /controllers/task_controller.py # コントローラー
#     /pages/task_list_page.py # ページ
#     /widgets/task_item.py  # UI部品

# /app/core/config.py
class Settings:
    def __init__(self):
        self.API_BASE_URL = "https://api.example.com/v1"
        self.API_TIMEOUT = 10  # 秒
        self.CACHE_ENABLED = True
        self.CACHE_TTL = 300  # 5分（秒）

settings = Settings()

# /app/data/models/task.py
from datetime import datetime
from typing import Optional, Dict, Any

class Task:
    def __init__(
        self,
        id: Optional[int] = None,
        title: str = "",
        description: str = "",
        status: str = "pending",
        due_date: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.due_date = due_date
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """辞書からTaskオブジェクトを生成"""
        due_date = None
        if data.get("due_date"):
            try:
                due_date = datetime.fromisoformat(data["due_date"])
            except ValueError:
                pass

        created_at = None
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"])
            except ValueError:
                pass

        updated_at = None
        if data.get("updated_at"):
            try:
                updated_at = datetime.fromisoformat(data["updated_at"])
            except ValueError:
                pass

        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            status=data.get("status", "pending"),
            due_date=due_date,
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Taskオブジェクトを辞書に変換"""
        data = {
            "title": self.title,
            "description": self.description,
            "status": self.status
        }

        if self.id is not None:
            data["id"] = self.id

        if self.due_date:
            data["due_date"] = self.due_date.isoformat()

        return data

# /app/data/repositories/task_repository.py
from typing import List, Optional, Dict, Any
from app.data.api.api_client import ApiClient
from app.data.models.task import Task
from app.core.cache.cache_manager import CacheManager
from app.core.network.network_monitor import NetworkMonitor

class TaskRepository:
    def __init__(
        self,
        api_client: ApiClient,
        cache_manager: CacheManager,
        network_monitor: NetworkMonitor
    ):
        self.api_client = api_client
        self.cache_manager = cache_manager
        self.network_monitor = network_monitor
        self.cache_ttl = 300  # 5分（秒）

    async def get_all_tasks(self, force_refresh=False) -> List[Task]:
        """全タスクを取得"""
        cache_key = "tasks_all"

        # キャッシュチェック（オフライン時やキャッシュ優先時）
        if (not force_refresh and self.cache_manager.has(cache_key)) or not self.network_monitor.is_online:
            tasks_data = self.cache_manager.get(cache_key, [])
            return [Task.from_dict(t) for t in tasks_data]

        # APIからデータ取得
        try:
            response = await self.api_client.get("/tasks")
            tasks_data = response.get("data", [])

            # キャッシュに保存
            self.cache_manager.set(cache_key, tasks_data, self.cache_ttl)

            return [Task.from_dict(t) for t in tasks_data]
        except Exception as e:
            # エラー時はキャッシュを使用
            print(f"API error: {e}")
            tasks_data = self.cache_manager.get(cache_key, [])
            return [Task.from_dict(t) for t in tasks_data]

    async def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """IDからタスクを取得"""
        cache_key = f"task_{task_id}"

        # キャッシュチェック（オフライン時やキャッシュ優先時）
        if self.cache_manager.has(cache_key) or not self.network_monitor.is_online:
            task_data = self.cache_manager.get(cache_key)
            return Task.from_dict(task_data) if task_data else None

        # APIからデータ取得
        try:
            response = await self.api_client.get(f"/tasks/{task_id}")
            task_data = response.get("data")

            if task_data:
                # キャッシュに保存
                self.cache_manager.set(cache_key, task_data, self.cache_ttl)
                return Task.from_dict(task_data)

            return None
        except Exception as e:
            # エラー時はキャッシュを使用
            print(f"API error: {e}")
            task_data = self.cache_manager.get(cache_key)
            return Task.from_dict(task_data) if task_data else None

    async def create_task(self, task: Task) -> Task:
        """新規タスクを作成"""
        if not self.network_monitor.is_online:
            # オフライン時はエラー
            raise Exception("オフラインでの新規タスク作成はサポートされていません")

        task_data = task.to_dict()

        # APIリクエスト
        response = await self.api_client.post("/tasks", task_data)
        created_task = Task.from_dict(response.get("data", {}))

        # キャッシュを更新
        self._update_task_cache(created_task)

        return created_task

    async def update_task(self, task: Task) -> Task:
        """タスク情報を更新"""
        if not task.id:
            raise ValueError("タスクIDが設定されていません")

        task_data = task.to_dict()

        if not self.network_monitor.is_online:
            # オフライン時はキャッシュのみ更新
            self._update_task_cache(task)
            # 同期サービスに更新処理を追加（実装省略）
            return task

        # APIリクエスト
        response = await self.api_client.put(f"/tasks/{task.id}", task_data)
        updated_task = Task.from_dict(response.get("data", {}))

        # キャッシュを更新
        self._update_task_cache(updated_task)

        return updated_task

    async def delete_task(self, task_id: int) -> bool:
        """タスクを削除"""
        if not self.network_monitor.is_online:
            # オフライン時はキャッシュのみ更新
            self._remove_task_from_cache(task_id)
            # 同期サービスに削除処理を追加（実装省略）
            return True

        # APIリクエスト
        response = await self.api_client.delete(f"/tasks/{task_id}")
        success = response.get("success", False)

        if success:
            # キャッシュから削除
            self._remove_task_from_cache(task_id)

        return success

    def _update_task_cache(self, task: Task):
        """キャッシュにおけるタスク情報を更新"""
        # 個別のタスクキャッシュを更新
        cache_key = f"task_{task.id}"
        self.cache_manager.set(cache_key, task.to_dict(), self.cache_ttl)

        # 全タスクリストキャッシュの更新
        all_cache_key = "tasks_all"
        tasks_data = self.cache_manager.get(all_cache_key, [])

        # 既存のタスクを探す
        task_found = False
        for i, t in enumerate(tasks_data):
            if t.get("id") == task.id:
                tasks_data[i] = task.to_dict()
                task_found = True
                break

        # 存在しない場合は追加
        if not task_found:
            tasks_data.append(task.to_dict())

        # 更新されたリストをキャッシュに保存
        self.cache_manager.set(all_cache_key, tasks_data, self.cache_ttl)

    def _remove_task_from_cache(self, task_id: int):
        """キャッシュからタスクを削除"""
        # 個別のタスクキャッシュを削除
        cache_key = f"task_{task_id}"
        self.cache_manager.delete(cache_key)

        # 全タスクリストキャッシュから削除
        all_cache_key = "tasks_all"
        tasks_data = self.cache_manager.get(all_cache_key, [])

        # 削除対象のタスクを除外
        updated_tasks = [t for t in tasks_data if t.get("id") != task_id]

        # 更新されたリストをキャッシュに保存
        self.cache_manager.set(all_cache_key, updated_tasks, self.cache_ttl)

# /app/presentation/controllers/task_controller.py
from typing import List, Optional, Callable
from app.data.repositories.task_repository import TaskRepository
from app.data.models.task import Task
from app.core.state.observable import Observable

class TaskController:
    def __init__(self, repository: TaskRepository):
        self.repository = repository
        self.tasks = Observable([])
        self.selected_task = Observable(None)
        self.loading = Observable(False)
        self.error = Observable("")

    async def load_tasks(self, force_refresh=False):
        """タスク一覧を読み込む"""
        self.loading.value = True
        self.error.value = ""

        try:
            tasks = await self.repository.get_all_tasks(force_refresh)
            self.tasks.value = tasks
        except Exception as e:
            self.error.value = f"タスクの読み込みに失敗しました: {str(e)}"
        finally:
            self.loading.value = False

    async def get_task(self, task_id: int) -> Optional[Task]:
        """指定したIDのタスクを取得"""
        self.loading.value = True
        self.error.value = ""

        try:
            task = await self.repository.get_task_by_id(task_id)
            self.selected_task.value = task
            return task
        except Exception as e:
            self.error.value = f"タスクの取得に失敗しました: {str(e)}"
            return None
        finally:
            self.loading.value = False

    async def create_task(self, task: Task) -> Optional[Task]:
        """新規タスクを作成"""
        self.loading.value = True
        self.error.value = ""

        try:
            created_task = await self.repository.create_task(task)

            # タスク一覧に追加
            current_tasks = list(self.tasks.value)
            current_tasks.append(created_task)
            self.tasks.value = current_tasks

            return created_task
        except Exception as e:
            self.error.value = f"タスクの作成に失敗しました: {str(e)}"
            return None
        finally:
            self.loading.value = False

    async def update_task(self, task: Task) -> Optional[Task]:
        """タスクを更新"""
        self.loading.value = True
        self.error.value = ""

        try:
            updated_task = await self.repository.update_task(task)

            # タスク一覧を更新
            current_tasks = list(self.tasks.value)
            for i, t in enumerate(current_tasks):
                if t.id == updated_task.id:
                    current_tasks[i] = updated_task
                    break
            self.tasks.value = current_tasks

            # 選択中のタスクを更新
            if self.selected_task.value and self.selected_task.value.id == updated_task.id:
                self.selected_task.value = updated_task

            return updated_task
        except Exception as e:
            self.error.value = f"タスクの更新に失敗しました: {str(e)}"
            return None
        finally:
            self.loading.value = False

    async def delete_task(self, task_id: int) -> bool:
        """タスクを削除"""
        self.loading.value = True
        self.error.value = ""

        try:
            success = await self.repository.delete_task(task_id)

            if success:
                # タスク一覧から削除
                current_tasks = list(self.tasks.value)
                self.tasks.value = [t for t in current_tasks if t.id != task_id]

                # 選択中のタスクをクリア
                if self.selected_task.value and self.selected_task.value.id == task_id:
                    self.selected_task.value = None

            return success
        except Exception as e:
            self.error.value = f"タスクの削除に失敗しました: {str(e)}"
            return False
        finally:
            self.loading.value = False

# /app/presentation/widgets/task_list.py
import flet as ft
import asyncio
from app.presentation.controllers.task_controller import TaskController
from app.data.models.task import Task

class TaskList(ft.UserControl):
    def __init__(self, controller: TaskController, on_task_selected=None):
        super().__init__()
        self.controller = controller
        self.on_task_selected = on_task_selected

        # タスク状態の変更を監視
        self._unsubscribe_tasks = controller.tasks.subscribe(self._update_task_list)
        self._unsubscribe_loading = controller.loading.subscribe(self._update_loading)
        self._unsubscribe_error = controller.error.subscribe(self._update_error)

    def did_mount(self):
        """マウント時の処理"""
        # タスクデータを読み込み
        asyncio.create_task(self.controller.load_tasks())

    def will_unmount(self):
        """アンマウント時の処理"""
        # 監視を解除
        self._unsubscribe_tasks()
        self._unsubscribe_loading()
        self._unsubscribe_error()

    def build(self):
        """UIを構築"""
        self.loading_indicator = ft.ProgressRing(visible=False)
        self.error_text = ft.Text("", color=ft.colors.RED_500, visible=False)

        self.task_list_view = ft.ListView(
            spacing=2,
            padding=10,
            expand=True
        )

        self.refresh_button = ft.IconButton(
            icon=ft.icons.REFRESH,
            tooltip="更新",
            on_click=self._refresh_tasks
        )

        self.add_button = ft.FloatingActionButton(
            icon=ft.icons.ADD,
            on_click=self._add_task
        )

        return ft.Column([
            ft.Row([
                ft.Text("タスク一覧", size=20, weight=ft.FontWeight.BOLD),
                self.refresh_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.loading_indicator,
            self.error_text,
            self.task_list_view,
        ])

    def _update_task_list(self, tasks):
        """タスクリストUIを更新"""
        self.task_list_view.controls = [
            self._create_task_item(task)
            for task in tasks
        ]
        self.update()

    def _update_loading(self, is_loading):
        """ローディング状態を更新"""
        self.loading_indicator.visible = is_loading
        self.update()

    def _update_error(self, error_message):
        """エラーメッセージを更新"""
        self.error_text.value = error_message
        self.error_text.visible = bool(error_message)
        self.update()

    def _create_task_item(self, task: Task) -> ft.Control:
        """タスクアイテムUIを作成"""
        # 状態に応じた色を設定
        status_colors = {
            "pending": ft.colors.GREY,
            "in_progress": ft.colors.BLUE,
            "completed": ft.colors.GREEN,
        }
        color = status_colors.get(task.status, ft.colors.GREY)

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(
                            task.title,
                            weight=ft.FontWeight.BOLD,
                            size=16
                        ),
                        ft.Container(
                            content=ft.Text(task.status, size=12),
                            bgcolor=color,
                            padding=5,
                            border_radius=5
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(
                        task.description or "説明なし",
                        size=14,
                        color=ft.colors.GREY_800
                    )
                ]),
                padding=10,
                on_click=lambda e, task_id=task.id: self._on_task_click(task_id)
            )
        )

    def _on_task_click(self, task_id: int):
        """タスククリック時の処理"""
        if self.on_task_selected:
            self.on_task_selected(task_id)

    def _refresh_tasks(self, e=None):
        """タスクを再読み込み"""
        asyncio.create_task(self.controller.load_tasks(force_refresh=True))

    def _add_task(self, e=None):
        """タスク追加ダイアログを表示"""
        # タスク追加ダイアログを実装（省略）
        pass

# /app/presentation/pages/task_list_page.py
import flet as ft
import asyncio
from app.presentation.controllers.task_controller import TaskController
from app.presentation.widgets.task_list import TaskList

class TaskListPage(ft.UserControl):
    def __init__(self, page: ft.Page, controller: TaskController):
        super().__init__()
        self.page = page
        self.controller = controller

    def build(self):
        """UIを構築"""
        self.app_bar = ft.AppBar(
            title=ft.Text("タスク管理アプリ"),
            center_title=False,
            bgcolor=ft.colors.SURFACE_VARIANT
        )

        # タスクリストウィジェット
        self.task_list = TaskList(
            self.controller,
            on_task_selected=self._navigate_to_task_detail
        )

        # タスク追加ボタン
        self.add_button = ft.FloatingActionButton(
            icon=ft.icons.ADD,
            on_click=self._show_add_task_dialog
        )

        return ft.Column([
            self.app_bar,
            self.task_list,
        ])

    def _navigate_to_task_detail(self, task_id: int):
        """タスク詳細ページに遷移"""
        self.page.go(f"/tasks/{task_id}")

    def _show_add_task_dialog(self, e=None):
        """タスク追加ダイアログを表示"""
        title_field = ft.TextField(
            label="タイトル",
            autofocus=True
        )

        description_field = ft.TextField(
            label="説明",
            multiline=True,
            min_lines=3,
            max_lines=5
        )

        status_dropdown = ft.Dropdown(
            label="状態",
            options=[
                ft.dropdown.Option("pending", "未着手"),
                ft.dropdown.Option("in_progress", "進行中"),
                ft.dropdown.Option("completed", "完了")
            ],
            value="pending"
        )

        # ダイアログを表示
        dialog = ft.AlertDialog(
            title=ft.Text("新規タスクの追加"),
            content=ft.Column([
                title_field,
                description_field,
                status_dropdown
            ], spacing=10, tight=True),
            actions=[
                ft.TextButton("キャンセル", on_click=lambda e: setattr(self.page.dialog, "open", False)),
                ft.ElevatedButton("追加", on_click=lambda e: self._create_task(
                    title_field.value,
                    description_field.value,
                    status_dropdown.value
                ))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()

    async def _create_task(self, title: str, description: str, status: str):
        """新規タスクを作成"""
        if not title:
            # タイトルが空の場合はエラー
            self.page.snack_bar = ft.SnackBar(content=ft.Text("タイトルを入力してください"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        # タスクオブジェクトを作成
        from app.data.models.task import Task
        task = Task(
            title=title,
            description=description,
            status=status
        )

        # タスクを保存
        await self.controller.create_task(task)

        # ダイアログを閉じる
        self.page.dialog.open = False
        self.page.update()
```

### APIバージョン管理と互換性

```python
# /app/core/api/versioned_api_client.py
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings

class VersionedApiClient:
    def __init__(self, version: str = "v1"):
        self.base_url = settings.API_BASE_URL
        self.version = version
        self.timeout = settings.API_TIMEOUT
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "API-Version": version  # APIバージョンをヘッダーで指定
        }

    def get_endpoint_url(self, endpoint: str) -> str:
        """エンドポイントのURLを構築"""
        # バージョン付きのAPIエンドポイントを構築
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        return f"{self.base_url}/{self.version}/{endpoint}"

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET リクエストを送信"""
        url = self.get_endpoint_url(endpoint)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params, headers=self.headers)
            return self._handle_response(response)

    # POST, PUT, DELETE メソッドも同様に実装

    def _handle_response(self, response):
        """レスポンスを処理"""
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        else:
            self._handle_error_response(response)

    def _handle_error_response(self, response):
        """エラーレスポンスを処理"""
        error_data = {
            "status_code": response.status_code,
            "message": "Unknown error"
        }

        try:
            error_data.update(response.json())
        except:
            error_data["message"] = response.text

        # APIバージョンの互換性エラーを特別に処理
        if response.status_code == 400 and "version" in error_data.get("message", "").lower():
            # バージョン互換性エラー
            raise ApiVersionError(error_data, self.version)
        else:
            # 通常のAPIエラー
            raise ApiException(error_data)

class ApiException(Exception):
    """一般的なAPIエラー"""
    def __init__(self, error_data):
        self.error_data = error_data
        self.status_code = error_data.get("status_code", 500)
        self.message = error_data.get("message", "Unknown API error")
        super().__init__(self.message)

class ApiVersionError(ApiException):
    """APIバージョン互換性エラー"""
    def __init__(self, error_data, version):
        super().__init__(error_data)
        self.version = version
        self.message = f"API version {version} compatibility error: {self.message}"
```

このガイドに従うことで、Fletアプリケーションと外部APIやバックエンドサービスの効率的な連携が可能になります。適切なリポジトリパターンの採用、キャッシュ戦略の実装、オフライン対応、エラーハンドリングなどを通じて、あらゆる環境で安定した動作を実現できます。マルチプラットフォームアプリケーションでは、データの一貫性と同期が特に重要です。このガイドのパターンを適用することで、ユーザーに優れた体験を提供しながら、開発と保守を効率化できます。
