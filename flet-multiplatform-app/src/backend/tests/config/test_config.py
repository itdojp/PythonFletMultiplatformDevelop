"""テスト設定モジュール"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field


class TestEnvironment(str, Enum):
    """テスト環境の種類"""

    LOCAL = "local"
    CI = "ci"
    PRODUCTION = "production"


class TestConfig(BaseModel):
    """テスト設定モデル"""

    environment: TestEnvironment = Field(default=TestEnvironment.LOCAL)
    database_url: str = Field(default="sqlite+aiosqlite:///:memory:")
    test_data_path: str = Field(default="test-data/")
    log_level: str = Field(default="INFO")
    parallel_tests: bool = Field(default=False)
    max_workers: Optional[int] = Field(default=None)
    timeout: int = Field(default=30)
    retry_count: int = Field(default=3)
    delay_between_retries: float = Field(default=1.0)

    class Config:
        """Pydantic設定"""

        use_enum_values = True


class TestSettings:
    """テスト設定クラス"""

    @staticmethod
    def get_config() -> TestConfig:
        """テスト設定を取得

        Returns:
            TestConfig: テスト設定
        """
        # 環境変数から設定を読み込む
        env = os.getenv("TEST_ENVIRONMENT", "local")
        database_url = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        test_data_path = os.getenv("TEST_DATA_PATH", "test-data/")
        log_level = os.getenv("TEST_LOG_LEVEL", "INFO")
        parallel_tests = os.getenv("TEST_PARALLEL", "false").lower() == "true"
        max_workers = int(os.getenv("TEST_MAX_WORKERS", "0")) or None
        timeout = int(os.getenv("TEST_TIMEOUT", "30"))
        retry_count = int(os.getenv("TEST_RETRY_COUNT", "3"))
        delay_between_retries = float(os.getenv("TEST_RETRY_DELAY", "1.0"))

        return TestConfig(
            environment=env,
            database_url=database_url,
            test_data_path=test_data_path,
            log_level=log_level,
            parallel_tests=parallel_tests,
            max_workers=max_workers,
            timeout=timeout,
            retry_count=retry_count,
            delay_between_retries=delay_between_retries,
        )

    @staticmethod
    def get_test_data_path() -> str:
        """テストデータのパスを取得

        Returns:
            str: テストデータのパス
        """
        return os.getenv("TEST_DATA_PATH", "test-data/")

    @staticmethod
    def get_test_environment() -> TestEnvironment:
        """テスト環境を取得

        Returns:
            TestEnvironment: テスト環境
        """
        return TestEnvironment(os.getenv("TEST_ENVIRONMENT", "local"))

    @staticmethod
    def get_database_url() -> str:
        """データベースURLを取得

        Returns:
            str: データベースURL
        """
        return os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")

    @staticmethod
    def get_log_level() -> str:
        """ログレベルを取得

        Returns:
            str: ログレベル
        """
        return os.getenv("TEST_LOG_LEVEL", "INFO")

    @staticmethod
    def get_parallel_tests() -> bool:
        """並列テストの設定を取得

        Returns:
            bool: 並列テストの設定
        """
        return os.getenv("TEST_PARALLEL", "false").lower() == "true"

    @staticmethod
    def get_max_workers() -> Optional[int]:
        """最大ワーカー数を取得

        Returns:
            Optional[int]: 最大ワーカー数
        """
        max_workers = int(os.getenv("TEST_MAX_WORKERS", "0"))
        return max_workers if max_workers > 0 else None

    @staticmethod
    def get_timeout() -> int:
        """タイムアウトを取得

        Returns:
            int: タイムアウト（秒）
        """
        return int(os.getenv("TEST_TIMEOUT", "30"))

    @staticmethod
    def get_retry_count() -> int:
        """リトライ回数を取得

        Returns:
            int: リトライ回数
        """
        return int(os.getenv("TEST_RETRY_COUNT", "3"))

    @staticmethod
    def get_delay_between_retries() -> float:
        """リトライ間隔を取得

        Returns:
            float: リトライ間隔（秒）
        """
        return float(os.getenv("TEST_RETRY_DELAY", "1.0"))

    @staticmethod
    def load_config_from_file(config_path: str) -> Dict[str, Any]:
        """設定ファイルから設定を読み込む

        Args:
            config_path (str): 設定ファイルのパス

        Returns:
            Dict[str, Any]: 設定データ
        """
        with open(config_path) as f:
            return yaml.safe_load(f)

    @staticmethod
    def save_config_to_file(config: Dict[str, Any], config_path: str) -> None:
        """設定をファイルに保存

        Args:
            config (Dict[str, Any]): 設定データ
            config_path (str): 設定ファイルのパス
        """
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """設定のバリデーション

        Args:
            config (Dict[str, Any]): 設定データ

        Returns:
            bool: バリデーション結果
        """
        try:
            TestConfig(**config)
            return True
        except ValidationError:
            return False
