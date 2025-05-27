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

- Python 3.13 以上
- Git
- Docker（オプション: コンテナ化された環境で実行する場合）

## セットアップ手順

1. リポジトリのクローン
   ```bash
   git clone <repository-url> # ご自身のレポジトリURLに置き換えてください
   cd flet-multiplatform-app
   ```

2. 仮想環境の作成と有効化
   ```bash
   # Windows
   python -m venv .venv
   .\.venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   (注: 仮想環境のディレクトリ名として `.venv` を推奨します)

3. 依存関係のインストール
   基本的な依存関係をインストールするには、`flet-multiplatform-app` ディレクトリで以下を実行します:
   ```bash
   pip install .
   ```
   開発ツール（テスト、リンター等）を含む完全な開発環境をセットアップする場合は、`pip install .[dev]` を使用します。詳細は [開発者ガイド](./DEVELOPER_GUIDE.md) を参照してください。

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

開発時には、Flet UIアプリケーションとバックエンドAPIサーバーを個別に起動する必要があります。

1.  **Flet UIアプリケーションの起動 (開発モード):**
    `flet-multiplatform-app` ディレクトリから以下を実行します。
    ```bash
    flet run src/flet_app.py
    ```
    これにより、Fletアプリケーションが起動し、UI関連のソースコードの変更が自動的にリロードされます。

2.  **バックエンドAPIサーバーの起動 (開発モード):**
    `flet-multiplatform-app` ディレクトリから以下を実行します。
    ```bash
    python -m uvicorn src.backend.main:app --reload --port 8001
    ```
    これにより、バックエンドAPIサーバーがポート8001で起動し、API関連のソースコードの変更が自動的にリロードされます。
    (FletのWebビューがデフォルトで8000番ポートを使用する場合があるため、APIサーバーには異なるポート（例: 8001）を指定することを推奨します。)

詳細な開発環境のセットアップやデバッグ方法については、[開発者ガイド](./DEVELOPER_GUIDE.md)を参照してください。

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

プロジェクトの主要なディレクトリとファイルの構造は以下の通りです。

```
flet-multiplatform-app/
├── .env                   # 環境変数 (実際の値は.envファイルに記述し、.env.exampleを元に作成)
├── .github/               # GitHub Actions ワークフローファイル
├── Dockerfile             # Dockerイメージ構築用ファイル
├── README.md              # プロジェクトの概要説明
├── docs/                  # プロジェクトドキュメント
│   ├── GETTING_STARTED_JA.md # このファイル
│   └── ...
├── pyproject.toml         # Pythonプロジェクト定義、依存関係 (PEP 621)
├── src/                   # ソースコード
│   ├── __init__.py
│   ├── app.py             # Flet UIの構造やカスタムコントロールを定義
│   ├── flet_app.py        # Flet UIアプリケーションのメインエントリーポイント
│   ├── main.py            # FastAPIアプリケーションのエントリーポイント (src.backend.mainとは別)
│   ├── assets/            # 画像、フォントなどの静的アセット
│   ├── backend/           # バックエンドAPI (FastAPI)
│   │   ├── __init__.py
│   │   ├── app.py         # FastAPIアプリケーションインスタンスの定義
│   │   ├── main.py        # バックエンドAPIの起動スクリプト
│   │   ├── alembic/       # Alembicデータベースマイグレーション用ディレクトリ
│   │   │   ├── versions/  # マイグレーションスクリプト
│   │   │   └── env.py     # Alembic実行環境設定
│   │   ├── alembic.ini    # Alembic設定ファイル (こちらが主に使われる)
│   │   ├── api/           # APIルーター定義
│   │   ├── core/          # 設定読み込み、共通ロジックなど
│   │   ├── db/            # データベースセッション、エンジン設定
│   │   ├── models/        # SQLAlchemyデータベースモデル
│   │   ├── schemas/       # Pydanticデータスキーマ
│   │   └── tests/         # バックエンド固有のテスト
│   ├── components/        # Flet UIコンポーネント (共通部品など)
│   ├── config/            # アプリケーション全体の設定 (データベース接続情報など)
│   ├── services/          # ビジネスロジック層
│   └── utils/             # 汎用ユーティリティ関数
├── tests/                 # プロジェクト全体のテスト (統合テストなど)
│   ├── conftest.py        # Pytest設定ファイル
│   └── ...
├── .gitignore             # Git管理対象外ファイル設定
└── pytest.ini             # Pytest設定ファイル
```
(上記は主要なファイルとディレクトリの構造です。詳細なファイルは省略されている場合があります。)

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

3. **フロントエンドの変更が反映されない (Flet)**
   FletアプリケーションでUIの変更が反映されない場合は、以下の手順を試してください：
   - アプリケーションを再起動する。
   - ブラウザで実行している場合は、ブラウザのキャッシュをクリアする（Ctrl+Shift+R または Cmd+Shift+R）。
   - `flet run` を使用している場合、ターミナルにエラーメッセージが表示されていないか確認する。
   - `build` ディレクトリや `assets` 内のキャッシュが問題になることは稀ですが、最終手段として関連しそうな一時ファイルを確認することも考慮できます。

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
