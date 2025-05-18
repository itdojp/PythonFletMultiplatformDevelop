# テスト環境の設定

このドキュメントでは、バックエンドとフロントエンドのテスト環境の設定について説明します。

## バックエンドのテスト環境

### 設定

バックエンドのテスト環境は、以下の設定を使用します：

```python
# src/backend/config/test_config.py

class TestSettings:
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    TEST_DATABASE_ECHO = False
    TEST_SECRET_KEY = "test-secret-key"
    TEST_ALGORITHM = "HS256"
    TEST_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    TEST_ENVIRONMENT = "test"
    TEST_DEBUG = True
```

### テストデータベース

テストデータベースは、SQLiteのメモリーデータベースを使用します。各テスト実行時に自動的に作成され、終了時に削除されます。

### テスト実行

バックエンドのテストを実行するには、以下のコマンドを使用します：

```bash
cd backend
python -m pytest tests/
```

## フロントエンドのテスト環境

### 設定

フロントエンドのテスト環境は、以下の設定を使用します：

```python
# src/frontend/config/test_config.py

class FrontendTestSettings:
    TEST_API_URL = "http://localhost:8000/api/v1"
    TEST_API_TIMEOUT = 10
    TEST_WINDOW_WIDTH = 1200
    TEST_WINDOW_HEIGHT = 800
    TEST_THEME_MODE = "light"
    TEST_ENVIRONMENT = "test"
    TEST_DEBUG = True
```

### テストUI

テスト用のFlet UIは、以下の設定で実行されます：
- ウィンドウサイズ: 1200x800ピクセル
- テーマ: ライトモード
- APIタイムアウト: 10秒

### テスト実行

フロントエンドのテストを実行するには、以下のコマンドを使用します：

```bash
cd frontend
python -m pytest tests/
```

## 注意事項

- テスト環境は、`TESTING`環境変数が`True`のときに有効になります
- テストデータベースは、各テスト実行時に自動的に初期化されます
- テスト用のAPIエンドポイントは、`TEST_API_URL`環境変数で設定できます
