# テスト環境セットアップガイド

このドキュメントでは、プロジェクトのテスト環境をセットアップする手順を説明します。

## 前提条件

- Python 3.8 以上がインストールされていること
- Git がインストールされていること（推奨）

## セットアップ手順

### Windows の場合

1. コマンドプロンプトを管理者として開きます
2. プロジェクトのルートディレクトリに移動します
3. 以下のコマンドを実行します：
   ```
   setup_test_env.bat
   ```

### Linux/macOS の場合

1. ターミナルを開きます
2. プロジェクトのルートディレクトリに移動します
3. 以下のコマンドを実行して実行権限を付与します：
   ```bash
   chmod +x setup_test_env.sh
   ```
4. 以下のコマンドを実行します：
   ```bash
   ./setup_test_env.sh
   ```

## セットアップの内容

セットアップスクリプトは以下の処理を自動的に実行します：

1. Python 仮想環境の作成（`.venv` ディレクトリ）
2. 必要なパッケージのインストール
   - `requirements.txt` に記載されたパッケージ
   - `requirements-dev.txt` に記載された開発用パッケージ
   - `requirements-test.txt` に記載されたテスト用パッケージ
3. テストデータベースの初期化
4. テストデータの生成

## テストの実行

セットアップが完了したら、以下のコマンドでテストを実行できます：

```bash
# 仮想環境を有効化（Windows）
.venv\Scripts\activate

# 仮想環境を有効化（Linux/macOS）
source .venv/bin/activate

# すべてのテストを実行
pytest

# 特定のテストファイルを実行
pytest tests/test_example.py

# 特定のテスト関数を実行
pytest tests/test_example.py::test_function_name

# カバレッジレポートを生成
pytest --cov=src tests/
```

## トラブルシューティング

### 仮想環境の有効化に失敗する場合

- スクリプトの実行権限を確認してください
- すでに仮想環境が有効になっている場合は、一度 `deactivate` を実行してから再度試してください

### 依存関係のインストールに失敗する場合

- インターネット接続を確認してください
- プロキシ環境下の場合は、適切なプロキシ設定を追加してください
- 古いパッケージが競合している場合は、仮想環境を削除してから再セットアップしてください

### テストデータベースの初期化に失敗する場合

- データベースサーバーが起動していることを確認してください
- 設定ファイル（`config/test_config.py`）の接続情報を確認してください
- データベースのパーミッションを確認してください

## カスタマイズ

### テストデータのカスタマイズ

`scripts/generate_test_data.py` を編集することで、生成するテストデータの内容をカスタマイズできます。

### テスト設定のカスタマイズ

`pytest.ini` ファイルを編集することで、pytest の動作をカスタマイズできます。

## メンテナンス

### 依存関係の更新

依存関係を更新した場合は、以下のコマンドで `requirements*.txt` を更新してください：

```bash
# メインの依存関係を更新
pip freeze > requirements.txt

# 開発用依存関係を更新
pip freeze > requirements-dev.txt

# テスト用依存関係を更新
pip freeze > requirements-test.txt
```

### 仮想環境の再作成

問題が発生した場合は、仮想環境を削除して再作成することができます：

```bash
# 仮想環境を無効化
deactivate

# 仮想環境ディレクトリを削除
rm -rf .venv  # Linux/macOS
rmdir /s /q .venv  # Windows

# 再度セットアップを実行
# Windows
setup_test_env.bat
# Linux/macOS
./setup_test_env.sh
```

## ライセンス

このプロジェクトは [MIT ライセンス](LICENSE) の下で公開されています。
