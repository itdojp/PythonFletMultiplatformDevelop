# はじめに

Flet マルチプラットフォーム開発テンプレートへようこそ。このドキュメントでは、プロジェクトのセットアップから実行までの基本的な手順を説明します。

## 前提条件

- Python 3.8 以上
- Node.js 16 以上（フロントエンド開発の場合）
- Docker（コンテナ環境で実行する場合）

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd flet-multiplatform-app
```

### 2. 仮想環境の作成と有効化

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env` ファイルを作成し、必要な環境変数を設定します：

```env
# データベース設定
DATABASE_URL=sqlite:///./test.db

# セキュリティ設定
SECRET_KEY=your-secret-key
```

## アプリケーションの実行

### 開発モードで起動

```bash
python -m src.backend.main
```

### フロントエンドの開発サーバーを起動（別ターミナルで）

```bash
cd frontend
npm install
npm run dev
```

## 次のステップ

- [チュートリアル](./tutorial.md)を参照して、アプリケーションの開発を始めましょう
- [API リファレンス](./api_reference.md)で利用可能なエンドポイントを確認
- [トラブルシューティング](./troubleshooting.md)で一般的な問題の解決策を確認
