@echo off
REM テスト環境セットアップバッチファイル

echo =============================================
echo テスト環境セットアップを開始します
echo =============================================

REM ログディレクトリが存在しない場合は作成
if not exist "logs" mkdir logs

REM 仮想環境の作成
echo.
echo [1/5] 仮想環境を作成しています...
python -m venv .venv
if %ERRORLEVEL% NEQ 0 (
    echo エラー: 仮想環境の作成に失敗しました
    exit /b %ERRORLEVEL%
)

REM 仮想環境を有効化
call .venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo エラー: 仮想環境の有効化に失敗しました
    exit /b %ERRORLEVEL%
)

REM pipをアップグレード
echo.
echo [2/5] pipをアップグレードしています...
python -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo エラー: pipのアップグレードに失敗しました
    exit /b %ERRORLEVEL%
)

REM 依存関係をインストール
echo.
echo [3/5] 依存関係をインストールしています...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo エラー: 依存関係のインストールに失敗しました
    exit /b %ERRORLEVEL%
)

pip install -r requirements-dev.txt
if %ERRORLEVEL% NEQ 0 (
    echo エラー: 開発用依存関係のインストールに失敗しました
    exit /b %ERRORLEVEL%
)

pip install -r requirements-test.txt
if %ERRORLEVEL% NEQ 0 (
    echo エラー: テスト用依存関係のインストールに失敗しました
    exit /b %ERRORLEVEL%
)

REM テストデータベースを初期化
echo.
echo [4/5] テストデータベースを初期化しています...
python scripts/init_test_db.py
if %ERRORLEVEL% NEQ 0 (
    echo エラー: テストデータベースの初期化に失敗しました
    exit /b %ERRORLEVEL%
)

REM テストデータを生成
echo.
echo [5/5] テストデータを生成しています...
python scripts/generate_test_data.py
if %ERRORLEVEL% NEQ 0 (
    echo エラー: テストデータの生成に失敗しました
    exit /b %ERRORLEVEL%
)

echo.
echo =============================================
echo テスト環境のセットアップが完了しました！
echo =============================================
echo.
echo 以下のコマンドで仮想環境を有効化できます：
echo .venv\Scripts\activate
echo.
echo テストを実行するには：
echo python -m pytest
echo.
pause
