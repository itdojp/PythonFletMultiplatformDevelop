# Flet Multiplatform App


このプロジェクトは、Python Fletを使用してマルチプラットフォーム対応のアプリケーションを開発するためのものです。Android、iOS、Webの各プラットフォームで一貫したユーザー体験を提供することを目的としています。

## プロジェクト構成

プロジェクトのディレクトリ構成は以下の通りです：

```text
flet-multiplatform-app
├── pyproject.toml         # Pythonプロジェクト定義、依存関係 (PEP 621)
├── pytest.ini             # Pytest設定
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
│   ├── config/            # アプリケーション全体の設定
│   ├── services/          # ビジネスロジック層
│   └── utils/             # 汎用ユーティリティ関数
├── scripts/               # 各種スクリプト (テスト実行用など)
│   ├── test.sh            # テスト実行スクリプト (Linux/macOS)
│   └── test.bat           # テスト実行スクリプト (Windows)
├── tests/                 # プロジェクト全体のテスト (統合テストなど)
│   ├── conftest.py        # Pytest設定ファイル
│   └── ...
└── ...                    # .gitignore, .env.example などその他の設定ファイル
```
(上記は主要なファイルとディレクトリの構造です。詳細なファイルは省略されている場合があります。)

## 必要システム構成
- Python 3.13 以上
- Git

## セットアップ

1.  **リポジトリのクローン:**
    ```bash
    git clone <your-repository-url>
    cd flet-multiplatform-app
    ```

2.  **仮想環境の作成と有効化:**
    ```bash
    python -m venv .venv
    # Windows: .\.venv\Scripts\activate
    # macOS/Linux: source .venv/bin/activate
    ```

3.  **依存関係のインストール:**
    開発に必要な全ての依存関係（本体、テストツール、リンター等）をインストールするには、プロジェクトルート (`flet-multiplatform-app`) で以下を実行します:
    ```bash
    pip install -e .[dev]
    ```
    アプリケーションの実行のみに必要な基本的な依存関係をインストールする場合は、以下を実行します:
    ```bash
    pip install .
    ```

4.  **環境変数の設定:**
    `.env.example` ファイルを参考に `.env` ファイルを作成し、必要な環境変数を設定してください。

## アプリケーションの起動

開発時には、Flet UIアプリケーションとバックエンドAPIサーバーを個別に起動します。

1.  **Flet UIアプリケーション:**
    (`flet-multiplatform-app` ディレクトリから実行)
    ```bash
    flet run src/flet_app.py
    ```

2.  **バックエンドAPIサーバー:**
    (`flet-multiplatform-app` ディレクトリから実行)
    ```bash
    python -m uvicorn src.backend.main:app --reload --port 8001
    ```
    (APIサーバーのポートはFletアプリと衝突しないように8001などを推奨)

## ドキュメンテーション

### オンラインドキュメント

プロジェクトのドキュメントは [MkDocs](https://www.mkdocs.org/) を使用してビルド・公開できます。
ドキュメント関連の依存関係は `pyproject.toml` の `[project.optional-dependencies.docs]` (仮の名称、必要に応じて追加) に定義するか、専用の `requirements-docs.txt` を使用します。

#### ドキュメントのビルド (例: `requirements-docs.txt` を使用する場合)

1. ドキュメント用の依存関係をインストールします：
   ```bash
   pip install -r requirements-docs.txt 
   ```
   (または `pip install .[docs]` もし `pyproject.toml` に `docs` グループが定義されていれば)

2. ドキュメントをビルドします：

```bash
mkdocs build
```

3. ドキュメントをローカルで確認します：

```bash
mkdocs serve
```

これで、[http://localhost:8000](http://localhost:8000) でドキュメントを確認できます。

#### ドキュメントの構成

- **はじめに**: プロジェクトの概要とセットアップ手順
- **チュートリアル**: ステップバイステップのガイド
- **API リファレンス**: 利用可能なAPIエンドポイントの詳細
- **トラブルシューティング**: 一般的な問題と解決策
- **開発ガイド**: 開発者向けの詳細な情報

## テストの実行

### テストの実行方法

1. テストに必要な依存関係をインストールします（開発セットアップ `pip install -e .[dev]` に含まれています）：
   ```bash
   # pip install -e .[dev] を実行していれば、通常は追加のインストールは不要です。
   # requirements-test.txt は pyproject.toml の [dev] グループと内容を確認し、統一を検討してください。
   # もし requirements-test.txt が独自の依存関係を持つ場合:
   # pip install -r requirements-test.txt 
   ```

2. テストを実行します：

   **pytestコマンドを直接使用する場合 (推奨):**
   `pyproject.toml` で `pytest` の設定が定義されています。プロジェクトルートで以下を実行します:
   ```bash
   pytest
   ```
   詳細なオプション (カバレッジレポート生成など) は `pyproject.toml` の `tool.pytest.ini_options.addopts` を参照してください。

   **スクリプトを使用する場合:**

   **Windows の場合:**

```batch
scripts\test.bat
```

**Linux/macOS の場合:**

```bash
chmod +x scripts/test.sh
./scripts/test.sh
```

### テストカバレッジ


このプロジェクトでは、コードの品質を保証するためにテストカバレッジの監視を行っています。現在のカバレッジは上記のバッジで確認できます。

#### カバレッジレポートの生成

pytestの実行時にHTMLカバレッジレポートが `htmlcov/` ディレクトリに自動生成されます (`pyproject.toml` の設定による)。
```bash
# pytest 実行後
# Windows: start htmlcov/index.html
# macOS/Linux: open htmlcov/index.html
```
ターミナルでのサマリーも表示されます。

#### カバレッジの目標

このプロジェクトでは、以下のカバレッジ目標を設定しています：
- **最小要件**: 70%以上（CIで強制）
- **推奨**: 80%以上
- **理想**: 90%以上

カバレッジを改善するには、テストされていないコード行を特定し（`htmlcov`レポートで詳細を確認できます）、それらに対するテストケースを追加してください。

## その他のドキュメント

- **[開発者ガイド](./docs/DEVELOPER_GUIDE.md)**: より詳細な開発環境のセットアップ、コーディング規約、コントリビューション方法など。
- **[デザインガイドライン](./docs/design_guidelines.md)**: UI/UX デザインに関するガイドライン。
- **[Swagger UI (API Docs)]**: バックエンドAPIサーバー起動後、`/docs` エンドポイント (例: `http://localhost:8001/docs`) にてAPIドキュメントが利用可能です。
- **[Redoc (API Docs)]**: バックエンドAPIサーバー起動後、`/redoc` エンドPOINT (例: `http://localhost:8001/redoc`) にて代替のAPIドキュメントが利用可能です。


## 貢献

このプロジェクトへの貢献は大歓迎です。バグの報告や機能の提案は、GitHubのイシューを通じて行ってください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。
\n
