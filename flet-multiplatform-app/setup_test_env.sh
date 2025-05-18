#!/bin/bash
# テスト環境セットアップスクリプト (Linux/macOS用)

echo "============================================="
echo "テスト環境セットアップを開始します"
echo "============================================="

# ログディレクトリが存在しない場合は作成
mkdir -p logs

# 仮想環境の作成
echo -e "\n[1/5] 仮想環境を作成しています..."
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "エラー: 仮想環境の作成に失敗しました"
    exit 1
fi

# 仮想環境を有効化
echo -e "\n[2/5] 仮想環境を有効化しています..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "エラー: 仮想環境の有効化に失敗しました"
    exit 1
fi

# pipをアップグレード
echo -e "\n[3/5] pipをアップグレードしています..."
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "エラー: pipのアップグレードに失敗しました"
    exit 1
fi

# 依存関係をインストール
echo -e "\n[4/5] 依存関係をインストールしています..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "エラー: 依存関係のインストールに失敗しました"
    exit 1
fi

pip install -r requirements-dev.txt
if [ $? -ne 0 ]; then
    echo "エラー: 開発用依存関係のインストールに失敗しました"
    exit 1
fi

pip install -r requirements-test.txt
if [ $? -ne 0 ]; then
    echo "エラー: テスト用依存関係のインストールに失敗しました"
    exit 1
fi

# テストデータベースを初期化
echo -e "\n[5/5] テストデータベースを初期化しています..."
python3 scripts/init_test_db.py
if [ $? -ne 0 ]; then
    echo "エラー: テストデータベースの初期化に失敗しました"
    exit 1
fi

# テストデータを生成
echo -e "\n[6/6] テストデータを生成しています..."
python3 scripts/generate_test_data.py
if [ $? -ne 0 ]; then
    echo "エラー: テストデータの生成に失敗しました"
    exit 1
fi

echo -e "\n============================================="
echo "テスト環境のセットアップが完了しました！"
echo "============================================="
echo -e "\n以下のコマンドで仮想環境を有効化できます："
echo "source .venv/bin/activate"
echo -e "\nテストを実行するには："
echo "python -m pytest"
echo ""
