# Flet マルチプラットフォームアプリケーション スタートガイド

## 目次
1. [プロジェクトの概要](#プロジェクトの概要)
2. [前提条件](#前提条件)
3. [セットアップ手順](#セットアップ手順)
4. [開発環境の構築](#開発環境の構築)
5. [アプリケーションの実行](#アプリケーションの実行)
6. [テストの実行](#テストの実行)
7. [ビルドとデプロイ](#ビルドとデプロイ)
8. [ディレクトリ構成](#ディレクトリ構成)
9. [開発ワークフロー](#開発ワークフロー)
10. [トラブルシューティング](#トラブルシューティング)
11. [貢献方法](#貢献方法)

## プロジェクトの概要

このプロジェクトは、Flet を使用したマルチプラットフォーム対応のアプリケーションです。以下の特徴があります：

- クロスプラットフォーム対応（Windows, macOS, Linux, Web, モバイル）
- モダンなUI/UX
- パフォーマンステストフレームワーク統合
- CI/CDパイプラインによる自動テストとデプロイ

## 前提条件

- Python 3.9 以上
- Git
- Node.js 16 以上（Webフロントエンド開発の場合）
- Docker（コンテナ化された環境で実行する場合）

## セットアップ手順

1. リポジトリのクローン
   ```bash
   git clone <repository-url>
   cd flet-multiplatform-app
   ```

2. 仮想環境の作成と有効化
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. 依存関係のインストール
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 開発用の依存関係
   ```

## 開発環境の構築

### 推奨開発環境

- **エディタ**: VS Code または PyCharm
- **推奨拡張機能**:
  - Python
  - Pylance
  - Black Formatter
  - Prettier
  - ESLint

### 環境変数の設定

`.env` ファイルを作成し、必要な環境変数を設定します：

```env
# データベース設定
DATABASE_URL=sqlite:///./sql_app.db

# アプリケーション設定
DEBUG=True
SECRET_KEY=your-secret-key

# 外部API設定
API_BASE_URL=https://api.example.com
API_KEY=your-api-key
```

## アプリケーションの実行

### 開発モードで起動

```bash
# バックエンドサーバーの起動
uvicorn app.main:app --reload

# フロントエンド開発サーバーの起動（別ターミナルで）
dev_app.py
```

### 本番モードで起動

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 本番サーバーの起動
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## テストの実行

### 単体テスト

```bash
# すべてのテストを実行
pytest

# 特定のテストを実行
pytest tests/unit/test_example.py -v

# カバレッジレポートを生成
pytest --cov=app --cov-report=html
```

### パフォーマンステスト

```bash
# パフォーマンステストの実行
python scripts/run_perf_tests.py --config tests/performance/config/performance_config.yaml

# パフォーマンスレポートの生成
python scripts/analyze_perf_results.py --results-dir reports/performance
```

### E2Eテスト

```bash
# E2Eテストの実行
pytest tests/e2e/ --headed  # ブラウザを表示
```

## ビルドとデプロイ

### スタンドアロンアプリケーションのビルド

```bash
# Windows
pyinstaller --onefile --windowed --name myapp main.py

# macOS
pyinstaller --onefile --windowed --name myapp main.py
```

### Dockerイメージのビルドと実行

```bash
# イメージのビルド
docker build -t myapp .

# コンテナの実行
docker run -p 8000:8000 myapp
```

### クラウドデプロイ

#### Heroku

```bash
# Heroku CLIのインストール後
heroku login
heroku create

# 環境変数の設定
heroku config:set DATABASE_URL=your-database-url

# デプロイ
git push heroku main
```

## ディレクトリ構成

```
flet-multiplatform-app/
├── app/                    # アプリケーションコード
│   ├── api/               # APIエンドポイント
│   ├── core/              # コア機能
│   ├── db/                # データベース関連
│   ├── models/            # データモデル
│   ├── services/          # ビジネスロジック
│   └── main.py            # アプリケーションエントリーポイント
├── tests/                  # テストコード
│   ├── unit/              # 単体テスト
│   ├── integration/       # 統合テスト
│   ├── e2e/               # E2Eテスト
│   └── performance/       # パフォーマンステスト
├── scripts/               # 便利なスクリプト
├── static/                # 静的ファイル
├── templates/             # テンプレートファイル
├── .github/               # GitHub Actionsワークフロー
├── .env.example          # 環境変数の例
├── requirements.txt       # 依存関係
├── requirements-dev.txt   # 開発用依存関係
└── README.md             # プロジェクト概要
```

## 開発ワークフロー

1. 機能開発
   ```bash
   # 新しいブランチの作成
git checkout -b feature/your-feature-name

# 変更をコミット
git add .
git commit -m "feat: 新しい機能を追加"

# リモートリポジトリにプッシュ
git push origin feature/your-feature-name
```

2. プルリクエストの作成
   - GitHubで新しいプルリクエストを作成
   - 変更内容を説明
   - レビュアーをアサイン

3. コードレビュー
   - チームメンバーがコードをレビュー
   - 必要な変更があればコメント
   - 承認されたらマージ

4. CI/CDパイプライン
   - プッシュ時に自動でテストが実行
   - メインブランチへのマージで本番環境に自動デプロイ

## トラブルシューティング

### 一般的な問題

1. **依存関係の競合**
   ```bash
   # 仮想環境を削除して再作成
   rm -rf venv
   python -m venv venv
   source venv/bin/activate  # or .\venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **データベース接続エラー**
   - データベースが起動しているか確認
   - 接続文字列が正しいか確認
   - マイグレーションが必要な場合:
     ```bash
     alembic upgrade head
     ```

3. **フロントエンドの変更が反映されない**
   ```bash
   # キャッシュをクリアして再起動
   rm -rf __pycache__
   rm -rf .flet
   python dev_app.py
   ```

## 貢献方法

1. リポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストをオープン

## ライセンス

このプロジェクトは [MIT ライセンス](LICENSE) の下で公開されています。

## サポート

問題が発生した場合は、[Issue](https://github.com/yourusername/flet-multiplatform-app/issues) を作成してください。

---

このドキュメントはプロジェクトの進行に合わせて更新されます。最終更新日: 2025年5月19日
