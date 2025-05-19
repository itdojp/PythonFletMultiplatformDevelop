"""テスト環境自動セットアップスクリプト"""

import json

# ロガーの設定
import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import venv
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, List, Optional, Union


# ログ設定
def setup_logging():
    """ログ設定"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "test_environment_setup.log"

    # ログフォーマット
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # ファイルハンドラ
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
    )
    file_handler.setFormatter(formatter)

    # コンソールハンドラ
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # ルートロガーにハンドラを追加
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 既存のハンドラをクリア
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # ハンドラを追加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()


class OSName(Enum):
    """OS名"""

    WINDOWS = "windows"
    LINUX = "linux"
    DARWIN = "darwin"


class EnvironmentManager:
    """環境マネージャークラス"""

    def __init__(self):
        """初期化"""
        self.os_name = self._get_os_name()
        self.project_root = self._get_project_root()
        self.venv_path = self.project_root / ".venv"
        self.requirements_files = {
            "base": "requirements.txt",
            "dev": "requirements-dev.txt",
            "test": "requirements-test.txt",
        }

        # プラットフォーム固有の設定
        self.platform_config = self._get_platform_config()

    def _get_os_name(self) -> OSName:
        """OS名を取得"""
        system = platform.system().lower()
        if system == "windows":
            return OSName.WINDOWS
        elif system == "linux":
            return OSName.LINUX
        elif system == "darwin":
            return OSName.DARWIN
        else:
            raise RuntimeError(f"Unsupported OS: {system}")

    def _get_project_root(self) -> Path:
        """プロジェクトのルートディレクトリを取得"""
        return Path(__file__).parent.parent.resolve()

    def _get_platform_config(self) -> Dict:
        """プラットフォーム固有の設定を取得"""
        return {
            OSName.WINDOWS: {
                "python": "python",
                "pip": "pip",
                "venv_activate": str(self.venv_path / "Scripts" / "activate"),
                "venv_python": str(self.venv_path / "Scripts" / "python.exe"),
                "venv_pip": str(self.venv_path / "Scripts" / "pip.exe"),
                "path_separator": ";",
            },
            OSName.LINUX: {
                "python": "python3",
                "pip": "pip3",
                "venv_activate": f"source {self.venv_path}/bin/activate",
                "venv_python": str(self.venv_path / "bin" / "python"),
                "venv_pip": str(self.venv_path / "bin" / "pip"),
                "path_separator": ":",
            },
            OSName.DARWIN: {
                "python": "python3",
                "pip": "pip3",
                "venv_activate": f"source {self.venv_path}/bin/activate",
                "venv_python": str(self.venv_path / "bin" / "python"),
                "venv_pip": str(self.venv_path / "bin" / "pip"),
                "path_separator": ":",
            },
        }[self.os_name]

    def run_command(
        self,
        command: Union[str, List[str]],
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        """コマンドを実行

        Args:
            command: 実行するコマンド
            cwd: カレントワーキングディレクトリ
            env: 環境変数
            check: エラーチェックを行うか

        Returns:
            subprocess.CompletedProcess: 実行結果
        """
        if cwd is None:
            cwd = self.project_root

        if isinstance(command, str):
            command = command.split()

        logger.info(f"Running command: {' '.join(command)} in {cwd}")

        try:
            result = subprocess.run(
                command, cwd=cwd, env=env, check=check, text=True, capture_output=True
            )
            logger.debug(f"Command output: {result.stdout}")
            if result.stderr:
                logger.warning(f"Command error: {result.stderr}")
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with error: {e}")
            logger.error(f"Error output: {e.stderr}")
            raise

    def create_virtualenv(self) -> None:
        """仮想環境を作成"""
        if self.venv_path.exists():
            logger.info("Virtual environment already exists. Skipping creation.")
            return

        logger.info(f"Creating virtual environment at {self.venv_path}")

        try:
            # venvモジュールを使用して仮想環境を作成
            venv.create(self.venv_path, with_pip=True)
            logger.info("Virtual environment created successfully.")
        except Exception as e:
            logger.error(f"Failed to create virtual environment: {e}")
            raise

    def install_requirements(self, env_type: str = "dev") -> None:
        """依存関係をインストール

        Args:
            env_type: 環境タイプ (base, dev, test)
        """
        if env_type not in self.requirements_files:
            raise ValueError(f"Invalid environment type: {env_type}")

        requirements_file = self.requirements_files[env_type]
        requirements_path = self.project_root / requirements_file

        if not requirements_path.exists():
            logger.warning(f"Requirements file not found: {requirements_path}")
            return

        logger.info(f"Installing {env_type} requirements from {requirements_file}")

        # pipを使用して依存関係をインストール
        pip_cmd = [
            self.platform_config["venv_pip"],
            "install",
            "-r",
            str(requirements_path),
        ]

        self.run_command(pip_cmd)

    def setup_pre_commit_hooks(self) -> None:
        """pre-commitフックをセットアップ"""
        if not (self.project_root / ".pre-commit-config.yaml").exists():
            logger.warning(
                "pre-commit config file not found. Skipping pre-commit setup."
            )
            return

        # pre-commitをインストール
        self.run_command([self.platform_config["venv_pip"], "install", "pre-commit"])

        # pre-commitフックをインストール
        self.run_command(
            [self.platform_config["venv_python"], "-m", "pre_commit", "install"]
        )

        # pre-commitフックを実行
        self.run_command(
            [
                self.platform_config["venv_python"],
                "-m",
                "pre_commit",
                "run",
                "--all-files",
            ]
        )

    def setup_git_hooks(self) -> None:
        """Gitフックをセットアップ"""
        git_dir = self.project_root / ".git"
        hooks_dir = git_dir / "hooks"

        if not git_dir.exists():
            logger.warning("Not a git repository. Skipping git hooks setup.")
            return

        # hooksディレクトリが存在しない場合は作成
        hooks_dir.mkdir(exist_ok=True)

        # pre-commitフックを作成
        pre_commit_hook = hooks_dir / "pre-commit"
        with open(pre_commit_hook, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\n")
            f.write(
                f"{self.platform_config['venv_python']} -m pre_commit run --hook-stage pre-commit\n"
            )

        # 実行権限を付与 (Unix系OSのみ)
        if self.os_name != OSName.WINDOWS:
            pre_commit_hook.chmod(0o755)

        logger.info("Git hooks set up successfully.")

    def setup_test_database(self) -> None:
        """テスト用データベースをセットアップ"""
        # テスト用の設定ファイルをロード
        test_config_path = (
            self.project_root
            / "src"
            / "backend"
            / "tests"
            / "config"
            / "test_config.py"
        )

        if not test_config_path.exists():
            logger.warning("Test config file not found. Skipping test database setup.")
            return

        # テスト用データベースの初期化スクリプトを実行
        try:
            # テスト用のデータベース初期化スクリプトを実行
            init_script = self.project_root / "scripts" / "init_test_db.py"
            if init_script.exists():
                self.run_command(
                    [self.platform_config["venv_python"], str(init_script)]
                )
            else:
                logger.warning(
                    f"Test database initialization script not found: {init_script}"
                )
        except Exception as e:
            logger.error(f"Failed to set up test database: {e}")
            raise

    def setup_test_data(self) -> None:
        """テストデータをセットアップ"""
        # テストデータ生成スクリプトを実行
        try:
            test_data_script = self.project_root / "scripts" / "generate_test_data.py"
            if test_data_script.exists():
                self.run_command(
                    [self.platform_config["venv_python"], str(test_data_script)]
                )
            else:
                logger.warning(
                    f"Test data generation script not found: {test_data_script}"
                )
        except Exception as e:
            logger.error(f"Failed to generate test data: {e}")
            raise

    def setup_environment_variables(self) -> None:
        """環境変数をセットアップ"""
        # .envファイルが存在する場合は読み込む
        env_file = self.project_root / ".env"
        if env_file.exists():
            logger.info("Loading environment variables from .env file")

            # 既存の環境変数を保持
            env_vars = dict(os.environ)

            # .envファイルから環境変数を読み込む
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        env_vars[key] = value

            # 環境変数を更新
            os.environ.update(env_vars)

    def setup_test_environment(self) -> None:
        """テスト環境をセットアップ"""
        try:
            logger.info("Starting test environment setup...")

            # 1. 環境変数のセットアップ
            self.setup_environment_variables()

            # 2. 仮想環境の作成
            self.create_virtualenv()

            # 3. 依存関係のインストール
            self.install_requirements("base")
            self.install_requirements("dev")
            self.install_requirements("test")

            # 4. pre-commitフックのセットアップ
            self.setup_pre_commit_hooks()

            # 5. Gitフックのセットアップ
            self.setup_git_hooks()

            # 6. テスト用データベースのセットアップ
            self.setup_test_database()

            # 7. テストデータのセットアップ
            self.setup_test_data()

            logger.info("Test environment setup completed successfully!")

        except Exception as e:
            logger.error(f"Failed to set up test environment: {e}")
            sys.exit(1)


def main():
    """メイン関数"""
    try:
        # 環境マネージャーを作成してセットアップを実行
        env_manager = EnvironmentManager()
        env_manager.setup_test_environment()

        print("\n✅ Test environment setup completed successfully!")
        print(f"\nTo activate the virtual environment, run:")

        if env_manager.os_name == OSName.WINDOWS:
            print(f"  {env_manager.platform_config['venv_activate']}")
        else:
            print(f"  source {env_manager.platform_config['venv_activate']}")

        print("\nTo run the tests, use:")
        print("  python -m pytest")

    except Exception as e:
        print(f"\n❌ Error setting up test environment: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
