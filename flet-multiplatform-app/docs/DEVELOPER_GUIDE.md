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

- Python 3.10 以上
- Git
- (オプション) Docker と Docker Compose（ローカルでのデータベースを使用する場合）

### セットアップ手順

1. リポジトリをクローンします：
   ```bash
   git clone https://github.com/your-username/flet-multiplatform-app.git
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
   ```bash
   pip install -e ".[dev]"
   ```

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

## プロジェクトの構造

```
flet-multiplatform-app/
├── .github/                  # GitHub Actions ワークフローファイル
├── .vscode/                  # VS Code 設定ファイル
├── docs/                     # ドキュメント
├── migrations/               # データベースマイグレーションファイル
├── src/                      # ソースコード
│   ├── backend/              # バックエンド関連のコード
│   │   ├── api/              # API エンドポイント
│   │   ├── core/             # コア機能
│   │   ├── db/               # データベース関連
│   │   └── models/           # データモデル
│   ├── components/           # フロントエンドコンポーネント
│   │   ├── common/           # 共通コンポーネント
│   │   └── navigation/       # ナビゲーション関連コンポーネント
│   ├── config/               # 設定ファイル
│   ├── services/             # ビジネスロジック
│   ├── static/               # 静的ファイル
│   ├── styles/               # スタイルシート
│   └── utils/                # ユーティリティ関数
├── tests/                    # テストコード
├── .env.example             # 環境変数のサンプル
├── .gitignore
├── .pre-commit-config.yaml   # pre-commit 設定
├── alembic.ini              # Alembic 設定
├── pyproject.toml           # プロジェクト設定と依存関係
└── README.md                # プロジェクト概要
```

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
