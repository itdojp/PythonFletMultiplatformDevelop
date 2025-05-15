# チュートリアル

このチュートリアルでは、Flet マルチプラットフォームアプリケーションの基本的な開発フローを学びます。

## 目次

1. [最初の画面を作成する](#1-最初の画面を作成する)
2. [データベースとの連携](#2-データベースとの連携)
3. [APIエンドポイントの作成](#3-apiエンドポイントの作成)
4. [認証の実装](#4-認証の実装)
5. [アプリケーションのビルドとデプロイ](#5-アプリケーションのビルドとデプロイ)

## 1. 最初の画面を作成する

フロントエンドのメインエントリーポイントである `src/frontend/main.py` を編集します：

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Flet アプリ"
    page.add(ft.Text("こんにちは、Flet！"))

ft.app(target=main)
```

## 2. データベースとの連携

バックエンドでデータベースモデルを定義します。`src/backend/models/` ディレクトリに新しいモデルファイルを作成します。

## 3. APIエンドポイントの作成

FastAPI ルーターを使用して、RESTful API エンドポイントを作成します。`src/backend/api/` ディレクトリに新しいルーターを追加します。

## 4. 認証の実装

JWT を使用した認証フローを実装します。`src/backend/core/security.py` に認証関連のユーティリティを実装します。

## 5. アプリケーションのビルドとデプロイ

アプリケーションをビルドしてデプロイする手順：

```bash
# 依存関係のインストール
pip install -r requirements.txt

# フロントエンドのビルド
cd frontend
npm run build

# バックエンドの起動
cd ..
python -m src.backend.main
```

## 次のステップ

- [API リファレンス](./api_reference.md)で詳細なAPI仕様を確認
- [トラブルシューティング](./troubleshooting.md)で問題解決のヒントを確認
