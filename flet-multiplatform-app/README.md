# Flet Multiplatform App


このプロジェクトは、Python Fletを使用してマルチプラットフォーム対応のアプリケーションを開発するためのものです。Android、iOS、Webの各プラットフォームで一貫したユーザー体験を提供することを目的としています。

## プロジェクト構成

プロジェクトのディレクトリ構成は以下の通りです：

```text
flet-multiplatform-app
├── src/                     # アプリケーションのソースコード
│   ├── backend/            # バックエンド
│   │   ├── __init__.py
│   │   ├── main.py         # アプリケーションのエントリーポイント
│   │   ├── app.py          # FastAPIアプリケーション
│   │   ├── api/            # APIルーター
│   │   ├── core/           # コア機能
│   │   ├── models/         # データベースモデル
│   │   ├── schemas/        # Pydanticスキーマ
│   │   ├── services/       # ビジネスロジック
│   │   ├── tests/          # バックエンドテスト
│   │   ├── utils/          # ユーティリティ
│   │   └── config/         # 設定ファイル
│   └── frontend/           # フロントエンド
│       ├── main.py         # フロントエンドのエントリーポイント
│       ├── components/     # UIコンポーネント
│       ├── pages/          # ページコンポーネント
│       └── utils/          # ユーティリティ
├── scripts/                # スクリプト
│   ├── test.sh            # テスト実行スクリプト (Linux/macOS)
│   └── test.bat           # テスト実行スクリプト (Windows)
├── tests/                  # 統合テスト
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── .env                   # 環境変数
├── .gitignore
├── pyproject.toml         # 依存関係とプロジェクト設定
├── pytest.ini            # pytest設定
└── README.md
```

## ドキュメンテーション

### オンラインドキュメント

プロジェクトのドキュメントは [MkDocs](https://www.mkdocs.org/) を使用してビルド・公開できます。

#### ドキュメントのビルド

1. ドキュメント用の依存関係をインストールします：

```bash
pip install -r requirements-docs.txt
```

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

1. テストに必要な依存関係をインストールします：

```bash
pip install -r requirements-test.txt
```

2. テストを実行します：

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

```bash
# テストを実行してカバレッジレポートを生成
pytest --cov=src --cov-report=term-missing --cov-report=html

# カバレッジレポートを表示（ブラウザで開く）
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
```

#### カバレッジの目標

- 最小カバレッジ: 70% (CIで強制)
- 推奨カバレッジ: 80%以上
- 理想的なカバレッジ: 90%以上

#### カバレッジを改善するには

1. テストされていないファイルを特定:
   ```bash
   coverage report --show-missing
   ```

2. 特定のファイルのカバレッジを確認:
   ```bash
   coverage html --include="path/to/file.py"
   ```

3. カバレッジが低いファイルに対してテストを追加してください。

## ドキュメント

- [開発者ガイド](./docs/DEVELOPER_GUIDE.md) - 開発環境のセットアップやコントリビューション方法など
- [デザインガイドライン](./docs/design_guidelines.md) - UI/UX デザインのガイドライン

## プロジェクト構成

```
flet-multiplatform-app
├── src/                     # アプリケーションのソースコード
│   ├── backend/            # バックエンド
│   │   ├── __init__.py
│   │   ├── main.py         # アプリケーションのエントリーポイント
│   │   ├── app.py          # FastAPIアプリケーション
│   │   ├── api/            # APIルーター
│   │   ├── core/           # コア機能
│   │   ├── models/         # データベースモデル
│   │   ├── schemas/        # Pydanticスキーマ
│   │   ├── services/       # ビジネスロジック
│   │   ├── tests/          # バックエンドテスト
│   │   ├── utils/          # ユーティリティ
│   │   └── config/         # 設定ファイル
│   └── frontend/           # フロントエンド
│       ├── main.py         # フロントエンドのエントリーポイント
│       ├── components/     # UIコンポーネント
│       ├── pages/          # ページコンポーネント
│       └── utils/          # ユーティリティ
├── scripts/                # スクリプト
│   ├── test.sh            # テスト実行スクリプト (Linux/macOS)
│   └── test.bat           # テスト実行スクリプト (Windows)
├── tests/                  # 統合テスト
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── .env                   # 環境変数
├── .gitignore
├── pyproject.toml         # 依存関係とプロジェクト設定
├── pytest.ini            # pytest設定
└── README.md
├── docs                    # ドキュメント
│   ├── DEVELOPER_GUIDE.md  # 開発者向けガイド
│   └── design_guidelines.md # デザインガイドライン
├── requirements.txt        # 依存関係
├── pyproject.toml         # プロジェクト設定
└── README.md               # プロジェクトの概要
```

## 使用方法

1. **依存関係のインストール**
   プロジェクトのルートディレクトリで以下のコマンドを実行して、必要なパッケージをインストールします。
   ```
   pip install -r requirements.txt
   ```

2. **アプリケーションの起動**
   `src/main.py`を実行してアプリケーションを起動します。
   ```
   python src/main.py
   ```

3. **テストの実行**
   テストを実行するには、以下のコマンドを使用します。
   ```
   pytest tests/
   ```

## 貢献

このプロジェクトへの貢献は大歓迎です。バグの報告や機能の提案は、GitHubのイシューを通じて行ってください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。
\n
