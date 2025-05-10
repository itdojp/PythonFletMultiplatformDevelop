# Python Flet - テスト戦略とQAガイド

このガイドでは、Python Fletアプリケーションに対する効果的なテスト戦略と品質保証（QA）のアプローチについて解説します。マルチプラットフォームアプリケーションの品質を確保するために必要なテスト手法、自動化、ベストプラクティスを学びましょう。

## 目次

1. [テスト戦略の基本原則](#テスト戦略の基本原則)
2. [テストピラミッドの構築](#テストピラミッドの構築)
3. [ユニットテスト](#ユニットテスト)
4. [インテグレーションテスト](#インテグレーションテスト)
5. [UIテスト](#uiテスト)
6. [パフォーマンステスト](#パフォーマンステスト)
7. [クロスプラットフォームテスト](#クロスプラットフォームテスト)
8. [継続的インテグレーション](#継続的インテグレーション)
9. [テスト管理とレポート](#テスト管理とレポート)
10. [実装例とパターン](#実装例とパターン)

## テスト戦略の基本原則

Fletアプリケーションのテスト戦略に関する基本原則:

### テストの重要性
- [ ] 複数プラットフォームでの一貫した動作確保
- [ ] バグの早期発見による開発コスト削減
- [ ] 安全なリファクタリングと機能追加の実現
- [ ] ユーザー体験の品質保証

### テスト対象範囲
- [ ] ビジネスロジック（モデル、サービス、ユーティリティ）
- [ ] データアクセス層（API連携、ローカルストレージ）
- [ ] ビュー層（UIコンポーネント、ページ）
- [ ] プラットフォーム固有の実装
- [ ] 多言語対応と国際化

### テスト環境の設定
- [ ] 開発環境と分離されたテスト環境の構築
- [ ] モックとスタブを使用した外部依存の模倣
- [ ] 一貫性のあるテストデータの準備
- [ ] プラットフォーム固有の環境設定

## テストピラミッドの構築

効率的なテスト戦略のためのテストピラミッド:

### テストピラミッドの概念
1. **ユニットテスト** (土台): 最も多くのテストで、最小の実装単位をテスト
2. **インテグレーションテスト** (中間): 複数のコンポーネント間の連携をテスト
3. **UIテスト / E2Eテスト** (頂点): ユーザーの視点からのフローをテスト

### テストの分布比率の目安
- ユニットテスト: 70% (開発時に継続的に作成)
- インテグレーションテスト: 20% (主要なシナリオを網羅)
- UIテスト: 10% (重要なユーザーフローのみ)

### 各レベルのトレードオフ
- **ユニットテスト**: 実行速度が速く、フィードバックが迅速。しかし、統合的な問題を発見できない
- **インテグレーションテスト**: システム全体の動作確認が可能。しかし、セットアップが複雑で実行コストが高い
- **UIテスト**: 実際のユーザー体験を検証できる。しかし、実行が最も遅く、メンテナンスコストが高い

## ユニットテスト

個別のコンポーネントをテストする方法:

### テストフレームワークの選定

```python
# requirements-dev.txt
pytest==7.4.0
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.11.1
```

### テストディレクトリ構造

```
/my_flet_app
  /app             # アプリケーションコード
    /core          # 核となるロジック
    /data          # データモデルとリポジトリ
    /presentation  # UI関連
  /tests           # テストコード
    /unit          # ユニットテスト
      /core        # coreモジュールのテスト
      /data        # dataモジュールのテスト
      /presentation # presentationモジュールのテスト
    /integration   # インテグレーションテスト
    /ui            # UIテスト
    conftest.py    # テスト設定とフィクスチャ
  pytest.ini       # Pytestの設定
```

### テスト設定

```python
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    ui: UI tests
    slow: Slow running tests
    android: Android platform tests
    ios: iOS platform tests
    web: Web platform tests
```

### ビジネスロジックのテスト

```python
# /tests/unit/core/test_utils.py
import pytest
from app.core.utils.string_utils import truncate_string, is_valid_email

class TestStringUtils:
    def test_truncate_string(self):
        # 基本ケース
        assert truncate_string("Hello World", 5) == "Hello..."
        
        # 長さが十分な場合は切り詰めない
        assert truncate_string("Hello", 10) == "Hello"
        
        # エッジケース
        assert truncate_string("", 5) == ""
        assert truncate_string("Hello", 0) == "..."
    
    def test_is_valid_email(self):
        # 有効なメールアドレス
        assert is_valid_email("user@example.com") == True
        assert is_valid_email("user.name+tag@example.co.jp") == True
        
        # 無効なメールアドレス
        assert is_valid_email("user@") == False
        assert is_valid_email("user@example") == False
        assert is_valid_email("user example.com") == False
        assert is_valid_email("") == False

# /tests/unit/data/models/test_user.py
import pytest
from app.data.models.user import User

class TestUserModel:
    def test_from_dict(self):
        # 完全なデータから作成
        user_data = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "role": "admin"
        }
        user = User.from_dict(user_data)
        
        assert user.id == 1
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.role == "admin"
        
        # 必須項目のみのデータから作成
        minimal_data = {
            "id": 2,
            "name": "Jane"
        }
        user = User.from_dict(minimal_data)
        
        assert user.id == 2
        assert user.name == "Jane"
        assert user.email == ""  # デフォルト値
        assert user.role == "user"  # デフォルト値
    
    def test_to_dict(self):
        # オブジェクトから辞書に変換
        user = User(id=1, name="John Doe", email="john@example.com")
        user_dict = user.to_dict()
        
        assert user_dict["id"] == 1
        assert user_dict["name"] == "John Doe"
        assert user_dict["email"] == "john@example.com"
        
        # IDなしのケース
        user_without_id = User(name="Jane")
        user_dict = user_without_id.to_dict()
        
        assert "id" not in user_dict
        assert user_dict["name"] == "Jane"
    
    def test_is_admin(self):
        admin = User(role="admin")
        normal_user = User(role="user")
        
        assert admin.is_admin() == True
        assert normal_user.is_admin() == False
```

### モックを使用したリポジトリのテスト

```python
# /tests/unit/data/repositories/test_user_repository.py
import pytest
import json
from unittest.mock import MagicMock, patch
from app.data.repositories.user_repository import UserRepository
from app.data.api.api_client import ApiClient
from app.data.models.user import User

@pytest.fixture
def mock_api_client():
    """APIクライアントのモック"""
    mock_client = MagicMock(spec=ApiClient)
    return mock_client

@pytest.fixture
def user_repository(mock_api_client):
    """テスト用のユーザーリポジトリ"""
    return UserRepository(mock_api_client)

class TestUserRepository:
    @pytest.mark.asyncio
    async def test_get_all_users(self, user_repository, mock_api_client):
        # モックレスポンスを設定
        mock_response = {
            "data": [
                {"id": 1, "name": "User 1", "email": "user1@example.com"},
                {"id": 2, "name": "User 2", "email": "user2@example.com"}
            ]
        }
        mock_api_client.get.return_value = mock_response
        
        # テスト対象メソッドを実行
        users = await user_repository.get_all_users()
        
        # 検証
        mock_api_client.get.assert_called_once_with("/users")
        assert len(users) == 2
        assert users[0].id == 1
        assert users[0].name == "User 1"
        assert users[1].id == 2
        assert users[1].name == "User 2"
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, user_repository, mock_api_client):
        # モックレスポンスを設定
        mock_response = {
            "data": {"id": 1, "name": "User 1", "email": "user1@example.com"}
        }
        mock_api_client.get.return_value = mock_response
        
        # テスト対象メソッドを実行
        user = await user_repository.get_user_by_id(1)
        
        # 検証
        mock_api_client.get.assert_called_once_with("/users/1")
        assert user.id == 1
        assert user.name == "User 1"
        assert user.email == "user1@example.com"
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_repository, mock_api_client):
        # モックレスポンスを設定（データなし）
        mock_response = {"data": None}
        mock_api_client.get.return_value = mock_response
        
        # テスト対象メソッドを実行
        user = await user_repository.get_user_by_id(999)
        
        # 検証
        assert user is None
        mock_api_client.get.assert_called_once_with("/users/999")
    
    @pytest.mark.asyncio
    async def test_create_user(self, user_repository, mock_api_client):
        # テスト用のユーザー
        new_user = User(name="New User", email="new@example.com")
        
        # モックレスポンスを設定
        mock_response = {
            "data": {"id": 3, "name": "New User", "email": "new@example.com"}
        }
        mock_api_client.post.return_value = mock_response
        
        # テスト対象メソッドを実行
        created_user = await user_repository.create_user(new_user)
        
        # 検証
        mock_api_client.post.assert_called_once_with("/users", new_user.to_dict())
        assert created_user.id == 3
        assert created_user.name == "New User"
        assert created_user.email == "new@example.com"
```

### 依存性注入を使用したコントローラーのテスト

```python
# /tests/unit/presentation/controllers/test_user_controller.py
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.presentation.controllers.user_controller import UserController
from app.data.repositories.user_repository import UserRepository
from app.data.models.user import User

@pytest.fixture
def mock_user_repository():
    """ユーザーリポジトリのモック"""
    mock_repo = MagicMock(spec=UserRepository)
    # 非同期メソッドのモック
    mock_repo.get_all_users = AsyncMock()
    mock_repo.get_user_by_id = AsyncMock()
    mock_repo.create_user = AsyncMock()
    mock_repo.update_user = AsyncMock()
    mock_repo.delete_user = AsyncMock()
    return mock_repo

@pytest.fixture
def user_controller(mock_user_repository):
    """テスト用のユーザーコントローラー"""
    return UserController(mock_user_repository)

class TestUserController:
    @pytest.mark.asyncio
    async def test_load_users(self, user_controller, mock_user_repository):
        # モックデータを設定
        mock_users = [
            User(id=1, name="User 1"),
            User(id=2, name="User 2")
        ]
        mock_user_repository.get_all_users.return_value = mock_users
        
        # 初期状態を確認
        assert user_controller.loading.value == False
        assert user_controller.error.value == ""
        assert len(user_controller.users.value) == 0
        
        # テスト対象メソッドを実行
        await user_controller.load_users()
        
        # 検証
        mock_user_repository.get_all_users.assert_called_once()
        assert user_controller.loading.value == False  # ロード完了後はFalse
        assert user_controller.error.value == ""  # エラーなし
        assert len(user_controller.users.value) == 2
        assert user_controller.users.value[0].id == 1
        assert user_controller.users.value[1].id == 2
    
    @pytest.mark.asyncio
    async def test_load_users_error(self, user_controller, mock_user_repository):
        # リポジトリメソッドが例外を投げるように設定
        mock_user_repository.get_all_users.side_effect = Exception("Network error")
        
        # テスト対象メソッドを実行
        await user_controller.load_users()
        
        # 検証
        assert user_controller.loading.value == False  # ロード完了後はFalse
        assert "失敗" in user_controller.error.value  # エラーメッセージが設定されている
        assert len(user_controller.users.value) == 0  # データは空のまま
    
    @pytest.mark.asyncio
    async def test_get_user(self, user_controller, mock_user_repository):
        # モックデータを設定
        mock_user = User(id=1, name="User 1")
        mock_user_repository.get_user_by_id.return_value = mock_user
        
        # テスト対象メソッドを実行
        user = await user_controller.get_user(1)
        
        # 検証
        mock_user_repository.get_user_by_id.assert_called_once_with(1)
        assert user.id == 1
        assert user.name == "User 1"
        assert user_controller.selected_user.value.id == 1
```

### コンポーネントのユニットテスト

```python
# /tests/unit/presentation/widgets/test_user_list.py
import pytest
import flet as ft
from unittest.mock import MagicMock, patch
import asyncio
from app.presentation.widgets.user_list import UserList
from app.presentation.controllers.user_controller import UserController
from app.data.models.user import User

@pytest.fixture
def mock_user_controller():
    """ユーザーコントローラーのモック"""
    mock_controller = MagicMock(spec=UserController)
    # Observableプロパティをセットアップ
    mock_controller.users = MagicMock()
    mock_controller.users.value = []
    mock_controller.users.subscribe = MagicMock(return_value=lambda: None)
    
    mock_controller.loading = MagicMock()
    mock_controller.loading.value = False
    mock_controller.loading.subscribe = MagicMock(return_value=lambda: None)
    
    mock_controller.error = MagicMock()
    mock_controller.error.value = ""
    mock_controller.error.subscribe = MagicMock(return_value=lambda: None)
    
    # load_usersメソッドをモック
    mock_controller.load_users = MagicMock()
    
    return mock_controller

@pytest.fixture
def user_list_widget(mock_user_controller):
    """テスト用のUserListウィジェット"""
    return UserList(mock_user_controller, on_task_selected=lambda id: None)

class TestUserList:
    def test_build_initial_state(self, user_list_widget):
        # buildメソッドを呼び出す
        result = user_list_widget.build()
        
        # 基本構造を検証
        assert isinstance(result, ft.Column)
        
        # ヘッダー部分を検証
        assert len(result.controls) > 0
        header_row = next((c for c in result.controls if isinstance(c, ft.Row)), None)
        assert header_row is not None
        assert any(isinstance(c, ft.Text) and "一覧" in c.value for c in header_row.controls)
        
        # リストビューが存在することを確認
        assert hasattr(user_list_widget, 'task_list_view')
        assert isinstance(user_list_widget.task_list_view, ft.ListView)
    
    def test_did_mount(self, user_list_widget, mock_user_controller):
        # did_mountメソッドを呼び出す
        user_list_widget.did_mount()
        
        # コントローラーのload_usersメソッドが呼び出されたことを確認
        mock_user_controller.load_users.assert_called_once()
    
    def test_update_user_list(self, user_list_widget, mock_user_controller):
        # モックユーザーデータを作成
        mock_users = [
            User(id=1, name="User 1", email="user1@example.com"),
            User(id=2, name="User 2", email="user2@example.com")
        ]
        
        # _update_user_listメソッドを呼び出す
        user_list_widget._update_user_list(mock_users)
        
        # リストビューのコントロールが更新されていることを確認
        assert len(user_list_widget.task_list_view.controls) == 2
        
        # 各アイテムの内容を確認（実装に依存）
        # この例では、TaskListの_create_task_itemメソッドが各ユーザーに対して
        # Cardを生成すると仮定
        first_item = user_list_widget.task_list_view.controls[0]
        assert isinstance(first_item, ft.Card)
        
        # カードの内容にユーザー名が含まれていることを確認
        card_content = first_item.content
        assert "User 1" in str(card_content)
```

## インテグレーションテスト

コンポーネント間の連携をテストする方法:

### フィクスチャとセットアップ

```python
# /tests/conftest.py
import pytest
import asyncio
import os
import json
from unittest.mock import patch, MagicMock
import flet as ft
from app.core.config import settings
from app.data.api.api_client import ApiClient
from app.core.di.service_locator import setup_services, ServiceLocator

@pytest.fixture
def test_page():
    """テスト用のFlet Pageオブジェクト"""
    page = MagicMock(spec=ft.Page)
    page.platform = "desktop"
    page.width = 1024
    page.height = 768
    return page

@pytest.fixture
def mock_api_responses():
    """APIモックレスポンスを読み込む"""
    responses = {}
    mock_dir = os.path.join(os.path.dirname(__file__), "mock_data")
    
    if os.path.exists(mock_dir):
        for filename in os.listdir(mock_dir):
            if filename.endswith(".json"):
                path = os.path.join(mock_dir, filename)
                with open(path, "r") as f:
                    key = filename.split(".")[0]  # 拡張子を除いたファイル名
                    responses[key] = json.load(f)
    
    return responses

@pytest.fixture
def mock_api_client(mock_api_responses):
    """モックAPIクライアント"""
    class MockApiClient:
        async def get(self, endpoint, params=None):
            # エンドポイントからレスポンスキーを取得
            key = endpoint.strip("/").replace("/", "_")
            if key in mock_api_responses:
                return mock_api_responses[key]
            raise Exception(f"Mock response not found for endpoint: {endpoint}")
        
        async def post(self, endpoint, data):
            # POSTリクエストのモックレスポンス
            key = f"{endpoint.strip('/').replace('/', '_')}_post"
            if key in mock_api_responses:
                return mock_api_responses[key]
            # 汎用的な成功レスポンス
            return {"success": True, "data": data}
        
        async def put(self, endpoint, data):
            # PUTリクエストのモックレスポンス
            key = f"{endpoint.strip('/').replace('/', '_')}_put"
            if key in mock_api_responses:
                return mock_api_responses[key]
            # 汎用的な成功レスポンス
            return {"success": True, "data": data}
        
        async def delete(self, endpoint):
            # DELETEリクエストのモックレスポンス
            key = f"{endpoint.strip('/').replace('/', '_')}_delete"
            if key in mock_api_responses:
                return mock_api_responses[key]
            # 汎用的な成功レスポンス
            return {"success": True}
    
    return MockApiClient()

@pytest.fixture
def mock_storage():
    """モックストレージサービス"""
    class MockStorage:
        def __init__(self):
            self.data = {}
        
        def set(self, key, value):
            self.data[key] = value
            return True
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def delete(self, key):
            if key in self.data:
                del self.data[key]
                return True
            return False
    
    return MockStorage()

@pytest.fixture
def setup_test_services(mock_api_client, mock_storage):
    """テスト用のサービスをセットアップ"""
    # サービスロケーターをセットアップ
    service_locator = ServiceLocator()
    
    # モックサービスを登録
    service_locator.register("api_client", mock_api_client)
    service_locator.register("storage", mock_storage)
    
    # その他の必要なサービスを登録
    from app.data.repositories.user_repository import UserRepository
    service_locator.register("user_repository", UserRepository(mock_api_client))
    
    return service_locator
```

### リポジトリとAPIクライアントの統合テスト

```python
# /tests/integration/data/test_user_repository_integration.py
import pytest
import asyncio
from app.data.repositories.user_repository import UserRepository
from app.data.models.user import User

@pytest.mark.integration
class TestUserRepositoryIntegration:
    @pytest.mark.asyncio
    async def test_get_all_users_integration(self, mock_api_client):
        # リポジトリをセットアップ
        repository = UserRepository(mock_api_client)
        
        # ユーザー一覧を取得
        users = await repository.get_all_users()
        
        # 検証
        assert len(users) > 0
        assert all(isinstance(user, User) for user in users)
        assert users[0].id is not None
        assert users[0].name is not None
    
    @pytest.mark.asyncio
    async def test_create_and_get_user_integration(self, mock_api_client):
        # リポジトリをセットアップ
        repository = UserRepository(mock_api_client)
        
        # 新しいユーザーを作成
        new_user = User(name="Integration Test User", email="test@example.com")
        created_user = await repository.create_user(new_user)
        
        # 作成されたユーザーを取得
        user_id = created_user.id
        retrieved_user = await repository.get_user_by_id(user_id)
        
        # 検証
        assert retrieved_user is not None
        assert retrieved_user.id == user_id
        assert retrieved_user.name == "Integration Test User"
        assert retrieved_user.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_update_user_integration(self, mock_api_client):
        # リポジトリをセットアップ
        repository = UserRepository(mock_api_client)
        
        # ユーザーを取得して更新
        users = await repository.get_all_users()
        user_to_update = users[0]
        
        # 更新するフィールドを変更
        original_name = user_to_update.name
        user_to_update.name = "Updated Name"
        
        # ユーザーを更新
        updated_user = await repository.update_user(user_to_update)
        
        # 検証
        assert updated_user.id == user_to_update.id
        assert updated_user.name == "Updated Name"
        assert updated_user.name != original_name
    
    @pytest.mark.asyncio
    async def test_delete_user_integration(self, mock_api_client):
        # リポジトリをセットアップ
        repository = UserRepository(mock_api_client)
        
        # ユーザーを作成
        new_user = User(name="User To Delete", email="delete@example.com")
        created_user = await repository.create_user(new_user)
        
        # ユーザーを削除
        result = await repository.delete_user(created_user.id)
        
        # 検証
        assert result == True
        
        # 削除されたことを確認
        deleted_user = await repository.get_user_by_id(created_user.id)
        assert deleted_user is None
```

### コントローラーとリポジトリの統合テスト

```python
# /tests/integration/presentation/test_user_controller_integration.py
import pytest
import asyncio
from app.presentation.controllers.user_controller import UserController
from app.data.repositories.user_repository import UserRepository
from app.data.models.user import User

@pytest.mark.integration
class TestUserControllerIntegration:
    @pytest.fixture
    def user_controller(self, mock_api_client):
        """テスト用のユーザーコントローラー"""
        repository = UserRepository(mock_api_client)
        return UserController(repository)
    
    @pytest.mark.asyncio
    async def test_load_users_integration(self, user_controller):
        # 初期状態を確認
        assert user_controller.loading.value == False
        assert user_controller.error.value == ""
        assert len(user_controller.users.value) == 0
        
        # ユーザーを読み込む
        await user_controller.load_users()
        
        # 検証
        assert user_controller.loading.value == False  # ロード完了後はFalse
        assert user_controller.error.value == ""  # エラーなし
        assert len(user_controller.users.value) > 0  # ユーザーが読み込まれている
    
    @pytest.mark.asyncio
    async def test_create_user_integration(self, user_controller):
        # 新しいユーザーを作成
        new_user = User(name="Controller Test User", email="controller@example.com")
        
        # コントローラーを使用してユーザーを作成
        created_user = await user_controller.create_user(new_user)
        
        # 検証
        assert created_user is not None
        assert created_user.id is not None
        assert created_user.name == "Controller Test User"
        
        # ユーザーリストが更新されていることを確認
        users = user_controller.users.value
        assert any(user.id == created_user.id for user in users)
    
    @pytest.mark.asyncio
    async def test_update_user_integration(self, user_controller):
        # ユーザーを読み込む
        await user_controller.load_users()
        
        # 最初のユーザーを取得
        user = user_controller.users.value[0]
        original_name = user.name
        
        # ユーザー名を変更
        user.name = "Updated By Controller"
        
        # コントローラーを使用してユーザーを更新
        updated_user = await user_controller.update_user(user)
        
        # 検証
        assert updated_user is not None
        assert updated_user.id == user.id
        assert updated_user.name == "Updated By Controller"
        assert updated_user.name != original_name
        
        # ユーザーリストが更新されていることを確認
        users = user_controller.users.value
        updated_user_in_list = next((u for u in users if u.id == user.id), None)
        assert updated_user_in_list is not None
        assert updated_user_in_list.name == "Updated By Controller"
    
    @pytest.mark.asyncio
    async def test_delete_user_integration(self, user_controller):
        # 新しいユーザーを作成
        new_user = User(name="User To Delete", email="delete@example.com")
        created_user = await user_controller.create_user(new_user)
        
        # ユーザーIDを取得
        user_id = created_user.id
        
        # コントローラーを使用してユーザーを削除
        result = await user_controller.delete_user(user_id)
        
        # 検証
        assert result == True
        
        # ユーザーリストから削除されていることを確認
        users = user_controller.users.value
        assert not any(user.id == user_id for user in users)
```

## UIテスト

ユーザーインターフェースの自動テスト:

### UIテストの基本アプローチ

```python
# /tests/ui/test_login_page.py
import pytest
import flet as ft
from unittest.mock import MagicMock, patch
from app.presentation.pages.login_page import LoginPage
from app.data.auth.auth_service import AuthService

@pytest.mark.ui
class TestLoginPageUI:
    @pytest.fixture
    def mock_auth_service(self):
        """認証サービスのモック"""
        mock_service = MagicMock(spec=AuthService)
        # loginメソッドをモック
        mock_service.login = MagicMock(return_value={"success": True})
        return mock_service
    
    @pytest.fixture
    def login_page(self, test_page, mock_auth_service):
        """テスト用のログインページ"""
        return LoginPage(test_page, mock_auth_service)
    
    def test_login_page_initial_render(self, login_page):
        """ログインページの初期レンダリングをテスト"""
        # buildメソッドを呼び出してUIを構築
        ui = login_page.build()
        
        # UIの構造を検証
        assert isinstance(ui, ft.Column)
        
        # ユーザー名フィールドが存在することを確認
        username_field = next((c for c in ui.controls if hasattr(c, 'label') and c.label == "ユーザー名"), None)
        assert username_field is not None
        assert isinstance(username_field, ft.TextField)
        
        # パスワードフィールドが存在することを確認
        password_field = next((c for c in ui.controls if hasattr(c, 'label') and c.label == "パスワード"), None)
        assert password_field is not None
        assert isinstance(password_field, ft.TextField)
        assert password_field.password == True  # パスワードフィールドである
        
        # ログインボタンが存在することを確認
        login_button = next((c for c in ui.controls if isinstance(c, ft.ElevatedButton) and c.text == "ログイン"), None)
        assert login_button is not None
    
    def test_login_button_disabled_when_fields_empty(self, login_page):
        """フィールドが空の場合、ログインボタンが無効になることをテスト"""
        # buildメソッドを呼び出してUIを構築
        login_page.build()
        
        # ユーザー名とパスワードフィールドへの参照を取得
        username_field = login_page.username_field
        password_field = login_page.password_field
        login_button = login_page.login_button
        
        # 初期状態では両方のフィールドが空なのでボタンは無効
        assert login_button.disabled == True
        
        # ユーザー名のみを入力
        username_field.value = "testuser"
        login_page._validate_form()
        assert login_button.disabled == True
        
        # パスワードのみを入力
        username_field.value = ""
        password_field.value = "password"
        login_page._validate_form()
        assert login_button.disabled == True
        
        # 両方入力
        username_field.value = "testuser"
        password_field.value = "password"
        login_page._validate_form()
        assert login_button.disabled == False
    
    @pytest.mark.asyncio
    async def test_login_success(self, login_page, mock_auth_service, test_page):
        """ログイン成功時の動作をテスト"""
        # ログインページを構築
        login_page.build()
        
        # ユーザー名とパスワードを設定
        login_page.username_field.value = "testuser"
        login_page.password_field.value = "password"
        login_page._validate_form()
        
        # 認証サービスの戻り値を設定
        mock_auth_service.login.return_value = {"success": True, "user": {"name": "Test User"}}
        
        # ログインボタンのクリックをシミュレート
        await login_page._login_click(None)
        
        # 認証サービスが正しいパラメータで呼び出されたか確認
        mock_auth_service.login.assert_called_once_with("testuser", "password")
        
        # ホーム画面への遷移が行われたか確認
        test_page.go.assert_called_once_with("/")
    
    @pytest.mark.asyncio
    async def test_login_failure(self, login_page, mock_auth_service):
        """ログイン失敗時の動作をテスト"""
        # ログインページを構築
        login_page.build()
        
        # ユーザー名とパスワードを設定
        login_page.username_field.value = "testuser"
        login_page.password_field.value = "wrong_password"
        login_page._validate_form()
        
        # 認証サービスの戻り値を設定（失敗）
        mock_auth_service.login.return_value = {"success": False, "message": "Invalid credentials"}
        
        # ログインボタンのクリックをシミュレート
        await login_page._login_click(None)
        
        # 認証サービスが呼び出されたか確認
        mock_auth_service.login.assert_called_once()
        
        # エラーメッセージが表示されたか確認
        assert login_page.error_text.visible == True
        assert "Invalid credentials" in login_page.error_text.value
        
        # ホーム画面への遷移が行われていないことを確認
        login_page.page.go.assert_not_called()
```

### ページナビゲーションとルーティングのテスト

```python
# /tests/ui/test_navigation.py
import pytest
import flet as ft
from unittest.mock import MagicMock, patch
from app.core.router.router import Router
from app.presentation.pages.home_page import HomePage
from app.presentation.pages.settings_page import SettingsPage

@pytest.mark.ui
class TestNavigationUI:
    @pytest.fixture
    def router(self, test_page):
        """テスト用のルーター"""
        router = Router(test_page)
        
        # テスト用のルートを登録
        router.routes = {
            "/": lambda params: ft.View("/", [HomePage(test_page)]),
            "/settings": lambda params: ft.View("/settings", [SettingsPage(test_page)]),
            "/user/:id": lambda params: ft.View(f"/user/{params['id']}", [MagicMock()])
        }
        
        return router
    
    def test_initial_route(self, router, test_page):
        """初期ルートのテスト"""
        # ルーターを初期化
        router.initialize()
        
        # 初期ルートが設定されていることを確認
        test_page.on_route_change = router._handle_route_change
        test_page.go.assert_called_once_with("/")
    
    def test_navigate_to_settings(self, router, test_page):
        """設定ページへのナビゲーションをテスト"""
        # ルーターを初期化
        router.initialize()
        
        # ルートチェンジイベントを作成
        route_event = MagicMock()
        route_event.route = "/settings"
        
        # ルートチェンジハンドラーを呼び出す
        router._handle_route_change(route_event)
        
        # ページビューがクリアされ、新しいビューが追加されたことを確認
        test_page.views.clear.assert_called_once()
        test_page.views.append.assert_called_once()
        
        # 追加されたビューが正しいことを確認
        view = test_page.views.append.call_args[0][0]
        assert view.route == "/settings"
        assert isinstance(view.controls[0], SettingsPage)
    
    def test_navigate_with_params(self, router, test_page):
        """パラメータ付きルートのテスト"""
        # ルーターを初期化
        router.initialize()
        
        # ルートチェンジイベントを作成
        route_event = MagicMock()
        route_event.route = "/user/123"
        
        # ルートチェンジハンドラーを呼び出す
        router._handle_route_change(route_event)
        
        # 追加されたビューが正しいことを確認
        view = test_page.views.append.call_args[0][0]
        assert view.route == "/user/123"
    
    def test_404_route(self, router, test_page):
        """存在しないルートのテスト"""
        # ルーターを初期化
        router.initialize()
        
        # 存在しないルートへのナビゲーション
        route_event = MagicMock()
        route_event.route = "/nonexistent"
        
        # ルートチェンジハンドラーを呼び出す
        router._handle_route_change(route_event)
        
        # 404ページが表示されることを確認
        view = test_page.views.append.call_args[0][0]
        assert "not-found" in view.route
```

### プラットフォーム固有のUIテスト

```python
# /tests/ui/test_platform_adaptive_ui.py
import pytest
import flet as ft
from unittest.mock import MagicMock
from app.presentation.widgets.adaptive_components import AdaptiveComponents

@pytest.mark.ui
class TestPlatformAdaptiveUI:
    @pytest.fixture
    def android_page(self):
        """Android用のモックページ"""
        page = MagicMock(spec=ft.Page)
        page.platform = "android"
        return page
    
    @pytest.fixture
    def ios_page(self):
        """iOS用のモックページ"""
        page = MagicMock(spec=ft.Page)
        page.platform = "ios"
        return page
    
    @pytest.fixture
    def web_page(self):
        """Web用のモックページ"""
        page = MagicMock(spec=ft.Page)
        page.platform = "web"
        return page
    
    def test_create_app_bar_android(self, android_page):
        """Androidプラットフォーム向けのAppBarテスト"""
        adaptive = AdaptiveComponents(android_page)
        
        # AppBarを作成
        app_bar = adaptive.create_app_bar("テストタイトル")
        
        # Androidスタイルの検証
        assert isinstance(app_bar, ft.AppBar)
        assert app_bar.title.value == "テストタイトル"
        assert app_bar.center_title == False  # Androidは左寄せ
        assert app_bar.bgcolor == ft.colors.BLUE_500  # Androidの色
    
    def test_create_app_bar_ios(self, ios_page):
        """iOSプラットフォーム向けのAppBarテスト"""
        adaptive = AdaptiveComponents(ios_page)
        
        # AppBarを作成
        app_bar = adaptive.create_app_bar("テストタイトル")
        
        # iOS風のコンテナであることを確認
        assert isinstance(app_bar, ft.Container)
        
        # iOSスタイルの検証（実装に依存）
        row = app_bar.content
        assert isinstance(row, ft.Row)
        assert any(isinstance(c, ft.Text) and c.value == "テストタイトル" for c in row.controls)
        assert app_bar.bgcolor == ft.colors.WHITE  # iOS風の色
    
    def test_create_bottom_navigation_multiple_platforms(self, android_page, ios_page, web_page):
        """複数プラットフォーム向けのボトムナビゲーションテスト"""
        # ナビゲーション項目
        items = [
            {"icon": ft.icons.HOME, "label": "ホーム"},
            {"icon": ft.icons.SEARCH, "label": "検索"},
            {"icon": ft.icons.PERSON, "label": "プロフィール"}
        ]
        
        # Android版
        android_adaptive = AdaptiveComponents(android_page)
        android_nav = android_adaptive.create_bottom_navigation(items)
        
        assert isinstance(android_nav, ft.NavigationBar)  # マテリアルデザイン
        assert len(android_nav.destinations) == 3
        
        # iOS版
        ios_adaptive = AdaptiveComponents(ios_page)
        ios_nav = ios_adaptive.create_bottom_navigation(items)
        
        assert isinstance(ios_nav, ft.Container)  # iOS風カスタムナビ
        assert ios_nav.bgcolor == ft.colors.WHITE
        
        # Web版
        web_adaptive = AdaptiveComponents(web_page)
        web_nav = web_adaptive.create_bottom_navigation(items)
        
        assert isinstance(web_nav, ft.Tabs)  # Webはタブ形式
        assert len(web_nav.tabs) == 3
```

## パフォーマンステスト

アプリケーションのパフォーマンス評価:

### レンダリングパフォーマンステスト

```python
# /tests/performance/test_rendering_performance.py
import pytest
import time
import flet as ft
from unittest.mock import MagicMock
from app.presentation.widgets.user_list import UserList
from app.data.models.user import User

@pytest.mark.performance
class TestRenderingPerformance:
    @pytest.fixture
    def mock_user_controller_with_many_users(self):
        """多数のユーザーデータを持つモックコントローラー"""
        mock_controller = MagicMock()
        
        # 100ユーザーのデータを生成
        users = [
            User(id=i, name=f"User {i}", email=f"user{i}@example.com")
            for i in range(1, 101)
        ]
        
        # Observableプロパティをセットアップ
        mock_controller.users = MagicMock()
        mock_controller.users.value = users
        mock_controller.users.subscribe = MagicMock(return_value=lambda: None)
        
        mock_controller.loading = MagicMock()
        mock_controller.loading.value = False
        mock_controller.loading.subscribe = MagicMock(return_value=lambda: None)
        
        mock_controller.error = MagicMock()
        mock_controller.error.value = ""
        mock_controller.error.subscribe = MagicMock(return_value=lambda: None)
        
        return mock_controller
    
    def test_user_list_render_performance(self, mock_user_controller_with_many_users):
        """UserListコンポーネントのレンダリングパフォーマンスをテスト"""
        # テスト用のリストウィジェット
        user_list = UserList(
            mock_user_controller_with_many_users,
            on_task_selected=lambda id: None
        )
        
        # レンダリング時間を計測
        start_time = time.time()
        user_list.build()
        end_time = time.time()
        
        render_time = end_time - start_time
        print(f"UserList rendering time: {render_time:.4f} seconds")
        
        # レンダリング時間が閾値以下であることを確認
        # 注: この閾値は環境によって調整が必要
        assert render_time < 0.5, f"Rendering took too long: {render_time:.4f} seconds"
        
        # リストアイテムが正しく生成されていることを確認
        assert len(user_list.task_list_view.controls) == 100
    
    def test_incremental_update_performance(self, mock_user_controller_with_many_users):
        """増分更新のパフォーマンスをテスト"""
        # テスト用のリストウィジェット
        user_list = UserList(
            mock_user_controller_with_many_users,
            on_task_selected=lambda id: None
        )
        
        # 初期レンダリング
        user_list.build()
        
        # 単一アイテムの更新時間を計測
        user = mock_user_controller_with_many_users.users.value[0]
        user.name = "Updated Name"
        
        start_time = time.time()
        user_list._update_user_list(mock_user_controller_with_many_users.users.value)
        end_time = time.time()
        
        update_time = end_time - start_time
        print(f"Single item update time: {update_time:.4f} seconds")
        
        # 更新時間が閾値以下であることを確認
        assert update_time < 0.3, f"Update took too long: {update_time:.4f} seconds"
```

### メモリ使用量テスト

```python
# /tests/performance/test_memory_usage.py
import pytest
import psutil
import os
import gc
import flet as ft
from unittest.mock import MagicMock
from app.presentation.widgets.user_list import UserList
from app.data.models.user import User

@pytest.mark.performance
class TestMemoryUsage:
    @pytest.fixture
    def mock_user_controller_with_many_users(self):
        """多数のユーザーデータを持つモックコントローラー"""
        mock_controller = MagicMock()
        
        # 1000ユーザーのデータを生成
        users = [
            User(id=i, name=f"User {i}", email=f"user{i}@example.com")
            for i in range(1, 1001)
        ]
        
        # Observableプロパティをセットアップ
        mock_controller.users = MagicMock()
        mock_controller.users.value = users
        mock_controller.users.subscribe = MagicMock(return_value=lambda: None)
        
        mock_controller.loading = MagicMock()
        mock_controller.loading.value = False
        mock_controller.loading.subscribe = MagicMock(return_value=lambda: None)
        
        mock_controller.error = MagicMock()
        mock_controller.error.value = ""
        mock_controller.error.subscribe = MagicMock(return_value=lambda: None)
        
        return mock_controller
    
    def get_memory_usage(self):
        """現在のプロセスのメモリ使用量をMB単位で取得"""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return memory_info.rss / 1024 / 1024  # MBに変換
    
    def test_user_list_memory_usage(self, mock_user_controller_with_many_users):
        """UserListコンポーネントのメモリ使用量をテスト"""
        # 事前にガベージコレクションを実行
        gc.collect()
        
        # 初期メモリ使用量を計測
        initial_memory = self.get_memory_usage()
        print(f"Initial memory usage: {initial_memory:.2f} MB")
        
        # テスト用のリストウィジェットを作成
        user_list = UserList(
            mock_user_controller_with_many_users,
            on_task_selected=lambda id: None
        )
        
        # レンダリング
        user_list.build()
        
        # レンダリング後のメモリ使用量を計測
        after_render_memory = self.get_memory_usage()
        print(f"Memory usage after rendering: {after_render_memory:.2f} MB")
        
        # メモリ増加量を計算
        memory_increase = after_render_memory - initial_memory
        print(f"Memory increase: {memory_increase:.2f} MB")
        
        # メモリ増加が閾値以下であることを確認
        # 注: この閾値は環境やアプリケーションによって調整が必要
        assert memory_increase < 50, f"Memory usage increase too high: {memory_increase:.2f} MB"
        
        # クリーンアップ
        user_list = None
        gc.collect()
        
        # クリーンアップ後のメモリ使用量を計測
        after_cleanup_memory = self.get_memory_usage()
        print(f"Memory usage after cleanup: {after_cleanup_memory:.2f} MB")
        
        # メモリリークがないことを確認（完全に元に戻らなくても大幅な削減があるべき）
        assert after_cleanup_memory < after_render_memory * 0.8, "Possible memory leak detected"
```

### API応答時間のシミュレーション

```python
# /tests/performance/test_api_response_time.py
import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch
from app.data.api.api_client import ApiClient
from app.data.repositories.user_repository import UserRepository
from app.presentation.controllers.user_controller import UserController

@pytest.mark.performance
class TestApiResponseTime:
    @pytest.fixture
    def slow_api_client(self):
        """レスポンスが遅いAPIクライアントのモック"""
        mock_client = AsyncMock(spec=ApiClient)
        
        # get_all_usersに対応するレスポンス
        async def slow_get(*args, **kwargs):
            # 1秒の遅延をシミュレート
            await asyncio.sleep(1)
            return {
                "data": [
                    {"id": 1, "name": "User 1", "email": "user1@example.com"},
                    {"id": 2, "name": "User 2", "email": "user2@example.com"}
                ]
            }
        
        mock_client.get = slow_get
        return mock_client
    
    @pytest.mark.asyncio
    async def test_slow_api_response_handling(self, slow_api_client):
        """遅いAPI応答に対するUIの動作をテスト"""
        # リポジトリとコントローラーを作成
        repository = UserRepository(slow_api_client)
        controller = UserController(repository)
        
        # 初期状態を確認
        assert controller.loading.value == False
        
        # ロード開始時間を記録
        start_time = time.time()
        
        # ロード処理を開始
        load_task = asyncio.create_task(controller.load_users())
        
        # 0.1秒後にローディング状態をチェック
        await asyncio.sleep(0.1)
        assert controller.loading.value == True, "Loading indicator should be shown immediately"
        
        # ロード完了を待機
        await load_task
        
        # 完了時間を記録
        end_time = time.time()
        total_time = end_time - start_time
        
        # 検証
        assert controller.loading.value == False, "Loading indicator should be hidden after completion"
        assert total_time >= 1.0, "Total time should include API delay"
        assert len(controller.users.value) == 2, "Data should be loaded despite delay"
        assert controller.error.value == "", "No error should be shown for slow response"
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, slow_api_client):
        """タイムアウトの処理をテスト"""
        # APIクライアントのgetメソッドを書き換えてタイムアウトを発生させる
        async def timeout_get(*args, **kwargs):
            await asyncio.sleep(5)  # タイムアウトよりも長い遅延
            return {}
        
        slow_api_client.get = timeout_get
        
        # タイムアウト設定を変更（実際のアプリでの実装に依存）
        with patch('app.core.config.settings.API_TIMEOUT', 1.0):
            # リポジトリとコントローラーを作成
            repository = UserRepository(slow_api_client)
            controller = UserController(repository)
            
            # ロード処理を実行
            await controller.load_users()
            
            # 検証
            assert controller.loading.value == False, "Loading indicator should be hidden after timeout"
            assert "タイムアウト" in controller.error.value or "timeout" in controller.error.value.lower(), "Error message should indicate timeout"
```

## クロスプラットフォームテスト

複数プラットフォームでの一貫した動作を確認:

### プラットフォーム特性のモック

```python
# /tests/conftest.py に追加
@pytest.fixture
def android_page():
    """Android向けのモックページ"""
    page = MagicMock(spec=ft.Page)
    page.platform = "android"
    page.width = 360
    page.height = 640
    return page

@pytest.fixture
def ios_page():
    """iOS向けのモックページ"""
    page = MagicMock(spec=ft.Page)
    page.platform = "ios"
    page.width = 375
    page.height = 667
    return page

@pytest.fixture
def web_page():
    """Web向けのモックページ"""
    page = MagicMock(spec=ft.Page)
    page.platform = "web"
    page.width = 1024
    page.height = 768
    return page

@pytest.fixture
def desktop_page():
    """デスクトップ向けのモックページ"""
    page = MagicMock(spec=ft.Page)
    page.platform = "windows"  # macos, linux も可能
    page.width = 1280
    page.height = 800
    return page
```

### レスポンシブデザインのテスト

```python
# /tests/cross_platform/test_responsive_layout.py
import pytest
import flet as ft
from unittest.mock import MagicMock
from app.presentation.responsive.responsive_layout import ResponsiveLayout

@pytest.mark.cross_platform
class TestResponsiveLayout:
    def test_mobile_layout(self, android_page):
        """モバイルサイズでのレイアウトをテスト"""
        responsive = ResponsiveLayout(android_page)
        
        # レイアウトカテゴリが正しいことを確認
        assert responsive.screen_category == "mobile"
        
        # モバイル向けの設定が適用されていることを確認
        assert responsive.get_column_count() == 1
        assert responsive.get_container_width() == android_page.width * 0.95
        assert responsive.get_padding() == 8
    
    def test_tablet_layout(self, ios_page):
        """タブレットサイズでのレイアウトをテスト"""
        # iOSページの幅をタブレットサイズに変更
        ios_page.width = 768
        ios_page.height = 1024
        
        responsive = ResponsiveLayout(ios_page)
        
        # レイアウトカテゴリが正しいことを確認
        assert responsive.screen_category == "tablet"
        
        # タブレット向けの設定が適用されていることを確認
        assert responsive.get_column_count() == 2
        assert responsive.get_container_width() == ios_page.width * 0.85
        assert responsive.get_padding() == 16
    
    def test_desktop_layout(self, desktop_page):
        """デスクトップサイズでのレイアウトをテスト"""
        responsive = ResponsiveLayout(desktop_page)
        
        # レイアウトカテゴリが正しいことを確認
        assert responsive.screen_category == "desktop"
        
        # デスクトップ向けの設定が適用されていることを確認
        assert responsive.get_column_count() == 4
        assert responsive.get_container_width() <= 1200  # 最大幅に制限
        assert responsive.get_padding() == 24
    
    def test_responsive_row_layout(self, android_page, desktop_page):
        """レスポンシブな行レイアウトをテスト"""
        # モバイルでの動作
        mobile_responsive = ResponsiveLayout(android_page)
        mobile_row = mobile_responsive.create_responsive_row([
            ft.Text("Item 1"),
            ft.Text("Item 2")
        ])
        
        # モバイルでは垂直レイアウト（Column）になる
        assert isinstance(mobile_row, ft.Column)
        
        # デスクトップでの動作
        desktop_responsive = ResponsiveLayout(desktop_page)
        desktop_row = desktop_responsive.create_responsive_row([
            ft.Text("Item 1"),
            ft.Text("Item 2")
        ])
        
        # デスクトップでは水平レイアウト（Row）になる
        assert isinstance(desktop_row, ft.Row)
    
    def test_layout_change_event(self, android_page):
        """レイアウト変更イベントをテスト"""
        responsive = ResponsiveLayout(android_page)
        
        # イベントハンドラーをセットアップ
        mock_handler = MagicMock()
        responsive.on_layout_change = mock_handler
        
        # 画面サイズを変更してリサイズイベントを発生させる
        android_page.width = 1024  # デスクトップサイズに変更
        responsive._handle_resize(None)
        
        # イベントハンドラーが呼び出されたことを確認
        mock_handler.assert_called_once_with("desktop")
        
        # レイアウトカテゴリが更新されていることを確認
        assert responsive.screen_category == "desktop"
```

### プラットフォーム固有の実装テスト

```python
# /tests/cross_platform/test_platform_specific.py
import pytest
from unittest.mock import MagicMock
import flet as ft
from app.platform.storage.storage_factory import StorageFactory
from app.platform.notification.notification_service import NotificationService

@pytest.mark.cross_platform
class TestPlatformSpecificImplementations:
    def test_storage_factory(self, android_page, ios_page, web_page, desktop_page):
        """各プラットフォームで適切なストレージ実装が選択されることをテスト"""
        # Androidのストレージ
        android_storage = StorageFactory.get_storage(android_page)
        assert "AndroidStorage" in android_storage.__class__.__name__
        
        # iOSのストレージ
        ios_storage = StorageFactory.get_storage(ios_page)
        assert "IOSStorage" in ios_storage.__class__.__name__
        
        # Webのストレージ
        web_storage = StorageFactory.get_storage(web_page)
        assert "WebStorage" in web_storage.__class__.__name__
        
        # デスクトップのストレージ
        desktop_storage = StorageFactory.get_storage(desktop_page)
        assert "DesktopStorage" in desktop_storage.__class__.__name__
    
    def test_notification_service(self, android_page, ios_page, web_page):
        """各プラットフォームで適切な通知サービスが選択されることをテスト"""
        # Androidの通知サービス
        android_notification = NotificationService(android_page)
        assert android_notification.is_available() == True
        
        # iOSの通知サービス
        ios_notification = NotificationService(ios_page)
        assert ios_notification.is_available() == True
        
        # Webの通知サービス
        web_notification = NotificationService(web_page)
        # Webでの利用可能性はブラウザ依存だが、テスト環境では常にFalseとなる
        assert web_notification.is_available() == False
```

### 多言語対応テスト

```python
# /tests/cross_platform/test_localization.py
import pytest
import os
import json
from app.i18n.translation_manager import TranslationManager
from app.i18n.locale_detector import LocaleDetector
from app.i18n.direction_manager import DirectionManager

@pytest.mark.cross_platform
class TestLocalization:
    @pytest.fixture
    def translation_manager(self):
        """テスト用の翻訳マネージャー"""
        # テスト用のロケールディレクトリパス
        locales_dir = os.path.join(os.path.dirname(__file__), "../mock_data/locales")
        
        # ディレクトリが存在しない場合は作成
        if not os.path.exists(locales_dir):
            os.makedirs(locales_dir)
        
        # テスト用の翻訳ファイルを作成
        translations = {
            "en": {
                "app": {
                    "title": "Test App",
                    "welcome": "Welcome, {name}!"
                },
                "common": {
                    "cancel": "Cancel",
                    "save": "Save"
                }
            },
            "ja": {
                "app": {
                    "title": "テストアプリ",
                    "welcome": "ようこそ、{name}さん！"
                },
                "common": {
                    "cancel": "キャンセル",
                    "save": "保存"
                }
            },
            "ar": {
                "app": {
                    "title": "تطبيق الاختبار",
                    "welcome": "مرحبًا، {name}!"
                },
                "common": {
                    "cancel": "إلغاء",
                    "save": "حفظ"
                }
            }
        }
        
        # 翻訳ファイルを保存
        for locale, data in translations.items():
            file_path = os.path.join(locales_dir, f"{locale}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 翻訳マネージャーを作成
        manager = TranslationManager(locales_dir, default_locale="en")
        return manager
    
    def test_translation(self, translation_manager):
        """翻訳機能をテスト"""
        # デフォルト言語（英語）での翻訳
        assert translation_manager.translate("app.title") == "Test App"
        assert translation_manager.translate("app.welcome", {"name": "John"}) == "Welcome, John!"
        
        # 日本語に切り替え
        translation_manager.set_locale("ja")
        assert translation_manager.translate("app.title") == "テストアプリ"
        assert translation_manager.translate("app.welcome", {"name": "John"}) == "ようこそ、Johnさん！"
        
        # アラビア語に切り替え
        translation_manager.set_locale("ar")
        assert translation_manager.translate("app.title") == "تطبيق الاختبار"
        assert translation_manager.translate("app.welcome", {"name": "John"}) == "مرحبًا، John!"
        
        # 存在しないキーの場合はキー自体を返す
        assert translation_manager.translate("nonexistent.key") == "nonexistent.key"
    
    def test_rtl_detection(self):
        """RTL言語の検出をテスト"""
        direction_manager = DirectionManager()
        
        # LTR言語
        assert direction_manager.is_rtl("en") == False
        assert direction_manager.is_rtl("ja") == False
        assert direction_manager.is_rtl("fr") == False
        
        # RTL言語
        assert direction_manager.is_rtl("ar") == True
        assert direction_manager.is_rtl("he") == True
        assert direction_manager.is_rtl("fa") == True
        
        # 複合ロケール
        assert direction_manager.is_rtl("ar-EG") == True
        assert direction_manager.is_rtl("en-US") == False
        
        # テキスト方向
        assert direction_manager.get_text_direction("en") == "ltr"
        assert direction_manager.get_text_direction("ar") == "rtl"
        
        # Flex方向
        assert direction_manager.get_flex_direction("en", "row") == "row"
        assert direction_manager.get_flex_direction("ar", "row") == "row-reverse"
```

## 継続的インテグレーション

テストの自動化と継続的な品質チェック:

### GitHub Actionsの設定

```yaml
# /.github/workflows/test.yml
name: Test

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10]
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    
    - name: Run unit tests
      run: |
        pytest tests/unit -v
    
    - name: Run integration tests
      run: |
        pytest tests/integration -v
    
    - name: Generate coverage report
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 black isort
    
    - name: Lint with flake8
      run: |
        flake8 app tests
    
    - name: Check formatting with black
      run: |
        black --check app tests
    
    - name: Check imports with isort
      run: |
        isort --check-only --profile black app tests
```

### Makefileによるローカルテスト

```makefile
# /Makefile
.PHONY: setup test lint format unit integration ui performance clean

setup:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest

unit:
	pytest tests/unit -v

integration:
	pytest tests/integration -v

ui:
	pytest tests/ui -v

performance:
	pytest tests/performance -v

cross-platform:
	pytest tests/cross_platform -v

coverage:
	pytest --cov=app --cov-report=html
	@echo "Open htmlcov/index.html in your browser to view coverage report"

lint:
	flake8 app tests
	black --check app tests
	isort --check-only --profile black app tests

format:
	black app tests
	isort --profile black app tests

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
```

## テスト管理とレポート

テスト結果の記録と分析:

### HTMLレポートの設定

```python
# /pytest.ini に追加
[pytest]
...
addopts = --html=report.html --self-contained-html
```

### カスタムログと結果収集

```python
# /tests/conftest.py に追加
import pytest
import logging
import os
from datetime import datetime

@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """テストログの設定"""
    # ログディレクトリの作成
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # 現在日時を含むログファイル名を生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"test_run_{timestamp}.log")
    
    # ロガーの設定
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger("test_logger")
    logger.info("Test run started")
    
    yield
    
    logger.info("Test run completed")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """テスト結果をログに記録"""
    outcome = yield
    result = outcome.get_result()
    
    logger = logging.getLogger("test_logger")
    
    if result.when == "call":
        if result.passed:
            logger.info(f"PASSED: {item.name}")
        elif result.failed:
            logger.error(f"FAILED: {item.name}")
            if call.excinfo:
                logger.error(f"Exception: {call.excinfo}")
        elif result.skipped:
            logger.warning(f"SKIPPED: {item.name}")
```

## 実装例とパターン

Fletアプリケーションに対する実際のテストパターン:

### フォームバリデーションのテスト

```python
# /tests/unit/presentation/forms/test_registration_form.py
import pytest
import flet as ft
from app.presentation.forms.registration_form import RegistrationForm

class TestRegistrationForm:
    @pytest.fixture
    def registration_form(self, test_page):
        """テスト用の登録フォーム"""
        return RegistrationForm(test_page, on_submit=lambda data: None)
    
    def test_initial_state(self, registration_form):
        """フォームの初期状態をテスト"""
        # フォームを構築
        form = registration_form.build()
        
        # 必須フィールドが存在することを確認
        assert hasattr(registration_form, "username_field")
        assert hasattr(registration_form, "email_field")
        assert hasattr(registration_form, "password_field")
        assert hasattr(registration_form, "confirm_password_field")
        
        # 送信ボタンの初期状態が無効であることを確認
        assert registration_form.submit_button.disabled == True
    
    def test_valid_form_submission(self, registration_form):
        """有効なフォーム送信をテスト"""
        # フォームを構築
        registration_form.build()
        
        # フォームに有効な値を入力
        registration_form.username_field.value = "testuser"
        registration_form.email_field.value = "test@example.com"
        registration_form.password_field.value = "Password123"
        registration_form.confirm_password_field.value = "Password123"
        
        # フォームのバリデーションを実行
        registration_form._validate_form(None)
        
        # 送信ボタンが有効になったことを確認
        assert registration_form.submit_button.disabled == False
        
        # エラーメッセージが表示されていないことを確認
        assert registration_form.username_field.error_text == None
        assert registration_form.email_field.error_text == None
        assert registration_form.password_field.error_text == None
        assert registration_form.confirm_password_field.error_text == None
    
    def test_invalid_email_format(self, registration_form):
        """無効なメールフォーマットをテスト"""
        # フォームを構築
        registration_form.build()
        
        # 基本的な有効なデータを設定
        registration_form.username_field.value = "testuser"
        registration_form.password_field.value = "Password123"
        registration_form.confirm_password_field.value = "Password123"
        
        # 無効なメールアドレスを設定
        registration_form.email_field.value = "invalid-email"
        
        # フォームのバリデーションを実行
        registration_form._validate_form(None)
        
        # 送信ボタンが無効のままであることを確認
        assert registration_form.submit_button.disabled == True
        
        # メールフィールドにエラーメッセージが表示されていることを確認
        assert registration_form.email_field.error_text is not None
        assert "有効" in registration_form.email_field.error_text or "valid" in registration_form.email_field.error_text.lower()
    
    def test_password_mismatch(self, registration_form):
        """パスワードの不一致をテスト"""
        # フォームを構築
        registration_form.build()
        
        # 基本的な有効なデータを設定
        registration_form.username_field.value = "testuser"
        registration_form.email_field.value = "test@example.com"
        
        # 一致しないパスワードを設定
        registration_form.password_field.value = "Password123"
        registration_form.confirm_password_field.value = "DifferentPassword"
        
        # フォームのバリデーションを実行
        registration_form._validate_form(None)
        
        # 送信ボタンが無効のままであることを確認
        assert registration_form.submit_button.disabled == True
        
        # 確認パスワードフィールドにエラーメッセージが表示されていることを確認
        assert registration_form.confirm_password_field.error_text is not None
        assert "一致" in registration_form.confirm_password_field.error_text or "match" in registration_form.confirm_password_field.error_text.lower()
    
    def test_password_complexity(self, registration_form):
        """パスワードの複雑さ要件をテスト"""
        # フォームを構築
        registration_form.build()
        
        # 基本的な有効なデータを設定
        registration_form.username_field.value = "testuser"
        registration_form.email_field.value = "test@example.com"
        
        # 複雑さが不足するパスワードを設定
        simple_passwords = [
            "short",       # 短すぎる
            "onlylowercase",  # 大文字なし
            "ONLYUPPERCASE",  # 小文字なし
            "without1number",  # 数字なし
            "12345678"      # 文字なし
        ]
        
        for password in simple_passwords:
            registration_form.password_field.value = password
            registration_form.confirm_password_field.value = password
            
            # フォームのバリデーションを実行
            registration_form._validate_form(None)
            
            # 送信ボタンが無効のままであることを確認
            assert registration_form.submit_button.disabled == True
            
            # パスワードフィールドにエラーメッセージが表示されていることを確認
            assert registration_form.password_field.error_text is not None
```

### ナビゲーションガードのテスト

```python
# /tests/unit/core/router/test_navigation_guards.py
import pytest
from unittest.mock import MagicMock
import flet as ft
from app.core.router.router import Router
from app.core.router.navigation_guards import require_auth

@pytest.fixture
def auth_state():
    """認証状態のモック"""
    return MagicMock(is_authenticated=False)

@pytest.fixture
def router_with_guards(test_page, auth_state):
    """ナビゲーションガード付きのルーター"""
    router = Router(test_page)
    
    # 認証が必要なルートを追加
    @require_auth(auth_state)
    def protected_route(params):
        return ft.View("/protected", [MagicMock()])
    
    # 公開ルートを追加
    def public_route(params):
        return ft.View("/public", [MagicMock()])
    
    # ログインルートを追加
    def login_route(params):
        return ft.View("/login", [MagicMock()])
    
    # ルートを登録
    router.routes = {
        "/protected": protected_route,
        "/public": public_route,
        "/login": login_route
    }
    
    # ルーター設定
    router.auth_redirect = "/login"
    
    return router, auth_state

class TestNavigationGuards:
    def test_unauthenticated_access_to_protected_route(self, router_with_guards):
        """未認証状態での保護されたルートへのアクセスをテスト"""
        router, auth_state = router_with_guards
        
        # 認証状態を未認証に設定
        auth_state.is_authenticated = False
        
        # ルートチェンジイベントを作成
        route_event = MagicMock()
        route_event.route = "/protected"
        
        # ルートチェンジハンドラーを呼び出す
        router._handle_route_change(route_event)
        
        # ログインページにリダイレクトされることを確認
        router.page.go.assert_called_with("/login")
    
    def test_authenticated_access_to_protected_route(self, router_with_guards):
        """認証状態での保護されたルートへのアクセスをテスト"""
        router, auth_state = router_with_guards
        
        # 認証状態を認証済みに設定
        auth_state.is_authenticated = True
        
        # ルートチェンジイベントを作成
        route_event = MagicMock()
        route_event.route = "/protected"
        
        # ルートチェンジハンドラーを呼び出す
        router._handle_route_change(route_event)
        
        # ビューが追加されていることを確認
        router.page.views.append.assert_called_once()
        view = router.page.views.append.call_args[0][0]
        assert view.route == "/protected"
        
        # リダイレクトされていないことを確認
        router.page.go.assert_not_called()
    
    def test_access_to_public_route(self, router_with_guards):
        """公開ルートへのアクセスをテスト（認証状態に関わらず）"""
        router, auth_state = router_with_guards
        
        # 認証状態を未認証に設定
        auth_state.is_authenticated = False
        
        # ルートチェンジイベントを作成
        route_event = MagicMock()
        route_event.route = "/public"
        
        # ルートチェンジハンドラーを呼び出す
        router._handle_route_change(route_event)
        
        # ビューが追加されていることを確認
        router.page.views.append.assert_called_once()
        view = router.page.views.append.call_args[0][0]
        assert view.route == "/public"
        
        # リダイレクトされていないことを確認
        router.page.go.assert_not_called()
```

### APIエラーハンドリングのテスト

```python
# /tests/unit/core/errors/test_error_handler.py
import pytest
from unittest.mock import MagicMock
import flet as ft
from app.core.errors.error_handler import ErrorHandler
from app.data.api.api_client import ApiException

class TestErrorHandler:
    @pytest.fixture
    def error_handler(self, test_page):
        """テスト用のエラーハンドラー"""
        return ErrorHandler(test_page)
    
    def test_handle_api_error_400(self, error_handler):
        """400エラー処理のテスト"""
        # APIエラー例外を作成
        error_data = {
            "status_code": 400,
            "message": "Invalid request parameters"
        }
        error = ApiException(error_data)
        
        # エラー処理を実行
        error_handler.handle_error(error)
        
        # エラーダイアログが表示されていることを確認
        assert error_handler.page.dialog is not None
        assert error_handler.page.dialog.open == True
        
        # ダイアログにエラーメッセージが含まれていることを確認
        title_text = error_handler.page.dialog.title.value
        assert "リクエストエラー" in title_text or "Request Error" in title_text
        
        # メッセージが表示されていることを確認
        content = error_handler.page.dialog.content
        assert "Invalid request parameters" in str(content)
    
    def test_handle_api_error_401(self, error_handler):
        """401エラー処理のテスト"""
        # APIエラー例外を作成
        error_data = {
            "status_code": 401,
            "message": "Authentication required"
        }
        error = ApiException(error_data)
        
        # エラー処理を実行
        error_handler.handle_error(error)
        
        # エラーダイアログが表示されていることを確認
        assert error_handler.page.dialog is not None
        assert error_handler.page.dialog.open == True
        
        # ログインページへリダイレクトされていることを確認
        error_handler.page.go.assert_called_once_with("/login")
    
    def test_handle_api_error_422(self, error_handler):
        """バリデーションエラー処理のテスト"""
        # バリデーションエラー例外を作成
        error_data = {
            "status_code": 422,
            "message": "Validation error",
            "errors": {
                "username": ["Username is already taken"],
                "email": ["Invalid email format"]
            }
        }
        error = ApiException(error_data)
        
        # エラー処理を実行
        error_handler.handle_error(error)
        
        # エラーダイアログが表示されていることを確認
        assert error_handler.page.dialog is not None
        assert error_handler.page.dialog.open == True
        
        # エラー詳細が表示されていることを確認
        content = error_handler.page.dialog.content
        content_str = str(content)
        assert "Validation error" in content_str
        assert "username" in content_str
        assert "Username is already taken" in content_str
        assert "email" in content_str
        assert "Invalid email format" in content_str
    
    def test_custom_error_handler(self, error_handler):
        """カスタムエラーハンドラーのテスト"""
        # カスタムエラーハンドラーを登録
        custom_handler = MagicMock()
        error_handler.register_handler(429, custom_handler)
        
        # APIエラー例外を作成
        error_data = {
            "status_code": 429,
            "message": "Too many requests"
        }
        error = ApiException(error_data)
        
        # エラー処理を実行
        error_handler.handle_error(error)
        
        # カスタムハンドラーが呼び出されたことを確認
        custom_handler.assert_called_once_with(error_data)
        
        # デフォルトのダイアログ処理が実行されていないことを確認
        assert error_handler.page.dialog is None or error_handler.page.dialog.open != True
```

このテスト戦略とQAガイドに従うことで、Fletアプリケーションの品質を継続的に確保できます。複数のプラットフォームにまたがる一貫した動作、パフォーマンス、UI/UXなど、様々な側面を効果的にテストし、高品質なアプリケーションを提供しましょう。自動テストを開発プロセスに組み込むことで、新機能の追加やコードのリファクタリングを安全に行うことができ、プロジェクトの持続可能な発展を促進できます。特にマルチプラットフォーム開発では、テストによる品質保証が成功の鍵となります。