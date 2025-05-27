# 開発者ガイド

このドキュメントは、Flet Multiplatform App プロジェクトに貢献する開発者向けのガイドです。

## 目次

1. [開発環境のセットアップ](#開発環境のセットアップ)
2. [プロジェクトの構造](#プロジェクトの構造)
3. [開発ワークフロー](#開発ワークフロー)
4. [テストの実行方法](#テストの実行方法)
5. [コーディング規約](#コーディング規約)
6. [プルリクエストの手順](#プルリクエストの手順)
7. [デバッグ方法](#デバッグ方法)
8. [リリース手順](#リリース手順)

## 開発環境のセットアップ

### 前提条件

- Python 3.13 以上
- Git
- (オプション) Docker と Docker Compose（ローカルでのデータベースを使用する場合）

### セットアップ手順

1. リポジトリをクローンします：
   ```bash
   git clone https://github.com/your-repository/flet-multiplatform-app.git
   cd flet-multiplatform-app
   ```

2. 仮想環境を作成して有効化します：
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. 依存関係をインストールします：
   プロジェクトのルートディレクトリ（`flet-multiplatform-app`）で以下を実行します。
   ```bash
   pip install -e .[dev]
   ```
   これにより、プロジェクトが編集可能モードでインストールされ、開発に必要な全ての依存関係（テストツール、リンター等）も一緒にインストールされます。

4. 環境変数を設定します（必要に応じて `.env` ファイルを作成）：
   ```env
   # データベース設定
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=flet_dev
   POSTGRES_PORT=5432

   # セキュリティ設定
   SECRET_KEY=your-secret-key-here
   ```

5. データベースをセットアップします：
   ```bash
   # マイグレーションを適用
   alembic upgrade head
   ```
   (注意: `alembic.ini` とマイグレーションスクリプトは `src/backend/alembic/` 以下に配置されています。)

### アプリケーションの起動

開発時には、Flet UIアプリケーションとバックエンドAPIサーバーを個別に起動する必要があります。

1.  **Flet UIアプリケーションの起動 (開発モード):**
    `flet-multiplatform-app` ディレクトリから以下を実行します。
    ```bash
    flet run src/flet_app.py
    ```
    これにより、Fletアプリケーションが起動し、ソースコードの変更が自動的にリロードされます。

2.  **バックエンドAPIサーバーの起動 (開発モード):**
    `flet-multiplatform-app` ディレクトリから以下を実行します。
    ```bash
    python -m uvicorn src.backend.main:app --reload --port 8001
    ```
    これにより、バックエンドAPIサーバーがポート8001で起動し、ソースコードの変更が自動的にリロードされます。
    (FletのWebビューがデフォルトで8000番ポートを使用する場合があるため、バックエンドAPIには異なるポート番号（例: 8001）を指定することを推奨します。)

    *代替のFastAPIアプリケーションについて:* `src/main.py` にもFastAPIアプリケーションのエントリーポイントが存在しますが、これはFlet UIが主に使用する `src/backend/main.py` とは異なる目的である可能性があります。開発時は主に上記の `src.backend.main:app` を使用してください。

## プロジェクトの構造

```
flet-multiplatform-app/
├── .env                   # 環境変数 (実際の値は.envファイルに記述し、.env.exampleを元に作成)
├── .github/               # GitHub Actions ワークフローファイル
├── .vscode/               # VS Code 設定ファイル (オプション)
├── Dockerfile             # Dockerイメージ構築用ファイル
├── README.md              # プロジェクトの概要説明
├── alembic.ini            # Alembic設定ファイル (実際には src/backend/alembic.ini が主)
├── docs/                  # プロジェクトドキュメント
│   ├── DEVELOPER_GUIDE.md # このファイル
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
├── .pre-commit-config.yaml # pre-commitフック設定
└── pytest.ini             # Pytest設定ファイル
```
(上記は主要なファイルとディレクトリの構造です。詳細なファイルは省略されている場合があります。)

## 開発ワークフロー

1. 最新の変更を取得します：
   ```bash
   git fetch origin main
   git checkout main
   git pull origin main
   ```

2. 新しいブランチを作成します：
   ```bash
   git checkout -b feature/your-feature-name
   # または
   git checkout -b fix/issue-number-description
   ```

3. 変更を加え、コミットします：
   ```bash
   # 変更をステージング
   git add .

   # コミット（自動フォーマットとリンターが実行されます）
   git commit -m "feat: 新しい機能を追加"
   ```

   コミットメッセージの形式：
   - `feat:` 新機能
   - `fix:` バグ修正
   - `docs:` ドキュメントの変更
   - `style:` コードのフォーマット、セミコロンの追加など
   - `refactor:` リファクタリング
   - `test:` テストの追加・修正
   - `chore:` ビルドプロセスやドキュメント生成などの補助ツールの変更

4. 変更をプッシュします：
   ```bash
   git push -u origin your-branch-name
   ```

5. GitHub でプルリクエストを作成します。

## テストの実行方法

### ユニットテストの実行

```bash
pytest tests/unit
```

### 統合テストの実行

```bash
pytest tests/integration
```

### カバレッジレポートの生成

```bash
pytest --cov=src --cov-report=html tests/
```

### テストカバレッジの確認

```bash
# ターミナルで表示
pytest --cov=src --cov-report=term-missing

# HTML レポートを生成してブラウザで開く
pytest --cov=src --cov-report=html
python -m http.server 8000 -d htmlcov
```

## コーディング規約

### Python コーディング規約

- [PEP 8](https://peps.python.org/pep-0008/) に準拠
- 型ヒントを積極的に使用
- ドキュメント文字列（docstring）は Google スタイルを使用

### コードフォーマット

コードは自動フォーマットされます：

```bash
# コードの自動フォーマット
black .


# インポートの自動ソート
isort .
```

### リンター

以下のリンターを使用しています：

```bash
# コードの静的解析
flake8

# 型チェック
mypy .
```

### コミット前のチェック

pre-commit フレームワークを使用して、コミット前に自動的にコードチェックを実行します：

```bash
# pre-commit フックをインストール
pre-commit install

# 手動で全ファイルをチェック
pre-commit run --all-files
```

## プルリクエストの手順

1. プルリクエストを作成する前に、最新の `main` ブランチをマージします：
   ```bash
   git checkout main
   git pull origin main
   git checkout your-branch
   git merge main
   ```

2. テストを実行して、すべてのテストがパスすることを確認します。

3. コードのフォーマットとリンターのチェックを実行します。

4. 変更内容を説明する明確なプルリクエストを作成します。
   - 変更の目的
   - 影響範囲
   - テストケース
   - スクリーンショット（UIの変更がある場合）

5. 少なくとも1人の開発者から承認を得てからマージします。

## デバッグ方法

### VS Code でのデバッグ

1. `.vscode/launch.json` にデバッグ構成が含まれています。
2. F5 キーを押すか、デバッグビューからデバッグを開始します。

### ログの確認

アプリケーションのログは `logs/app.log` に出力されます。

### データベースのデバッグ

```bash
# データベースに接続
psql -h localhost -U postgres -d flet_dev

# テーブル一覧を表示
\dt

# クエリの実行
SELECT * FROM your_table LIMIT 10;
```

## リリース手順

1. バージョン番号を更新します（`src/__init__.py` と `pyproject.toml`）。

2. 変更履歴（CHANGELOG.md）を更新します。

3. リリースブランチを作成してプッシュします：
   ```bash
   git checkout -b release/vX.Y.Z
   git push origin release/vX.Y.Z
   ```

4. GitHub で新しいリリースを作成します。

5. タグをプッシュして、GitHub Actions でビルドと公開を実行します。
