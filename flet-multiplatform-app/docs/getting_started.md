# はじめに

Flet マルチプラットフォーム開発テンプレートへようこそ。このドキュメントでは、プロジェクトのセットアップから実行までの基本的な手順を説明します。

## 前提条件

- Python 3.13 以上
- Git
- Docker（オプション: コンテナ環境で実行する場合）

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <repository-url> # リポジトリのURLに置き換えてください
cd flet-multiplatform-app
```

### 2. 仮想環境の作成と有効化

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```
(注: 仮想環境のディレクトリ名として `.venv` を推奨します)

### 3. 依存関係のインストール

プロジェクトの基本的な依存関係をインストールするには、`flet-multiplatform-app` ディレクトリで以下を実行します:
```bash
pip install .
```
開発ツール（テスト、リンター等）を含む完全な開発環境をセットアップする場合は、開発者ガイドを参照し `pip install .[dev]` を使用してください。

### 4. 環境変数の設定

`.env` ファイルを作成し、必要な環境変数を設定します：

```env
# データベース設定
DATABASE_URL=sqlite:///./test.db

# セキュリティ設定
SECRET_KEY=your-secret-key
```

## アプリケーションの実行

開発時には、Flet UIアプリケーションとバックエンドAPIサーバーを個別に起動する必要があります。

1.  **Flet UIアプリケーションの起動 (開発モード):**
    `flet-multiplatform-app` ディレクトリから以下を実行します。
    ```bash
    flet run src/flet_app.py
    ```
    これにより、Fletアプリケーションが起動し、UI関連のソースコード変更が自動的にリロードされます。

2.  **バックエンドAPIサーバーの起動 (開発モード):**
    `flet-multiplatform-app` ディレクトリから以下を実行します。
    ```bash
    python -m uvicorn src.backend.main:app --reload --port 8001
    ```
    これにより、バックエンドAPIサーバーがポート8001で起動し、API関連のソースコード変更が自動的にリロードされます。
    (FletのWebビューがデフォルトで8000番ポートを使用する場合があるため、APIサーバーには異なるポート（例: 8001）を指定することを推奨します。)

詳細な開発環境のセットアップやデバッグ方法については、[開発者ガイド](./DEVELOPER_GUIDE.md)を参照してください。

## 次のステップ

- [チュートリアル](./tutorial.md) を参照して、アプリケーションの開発を始めましょう。
- [API リファレンス](./api_reference.md) で利用可能なエンドポイントを確認してください。
- [トラブルシューティング](./troubleshooting.md) で一般的な問題の解決策を確認してください。
- より詳細な開発情報については、[開発者ガイド](./DEVELOPER_GUIDE.md) を参照してください。
