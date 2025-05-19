"""パフォーマンステストの設定ファイル"""

from pathlib import Path
from typing import Any, Dict, Optional

# ベースディレクトリ
BASE_DIR = Path(__file__).parent.parent.parent
TEST_DATA_DIR = BASE_DIR / "test_data"
RESULTS_DIR = BASE_DIR / "results"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# ディレクトリが存在しない場合は作成
for directory in [TEST_DATA_DIR, RESULTS_DIR, REPORTS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# テストデータの設定
TEST_DATA_CONFIG = {
    "small": {
        "users": 100,
        "products": 1000,
        "orders": 10000,
        "customers": 1000,
        "transactions": 50000,
    },
    "medium": {
        "users": 1000,
        "products": 10000,
        "orders": 100000,
        "customers": 5000,
        "transactions": 500000,
    },
    "large": {
        "users": 10000,
        "products": 50000,
        "orders": 1000000,
        "customers": 50000,
        "transactions": 5000000,
    },
}

# テストシナリオの設定
TEST_SCENARIOS = {
    "load_test": {
        "description": "通常の負荷テスト",
        "users": 10,
        "spawn_rate": 1,
        "duration": "30s",
        "data_size": "small",
        "enabled": True,
    },
    "stress_test": {
        "description": "高負荷テスト",
        "users": 100,
        "spawn_rate": 10,
        "duration": "1m",
        "data_size": "small",
        "enabled": True,
    },
    "endurance_test": {
        "description": "耐久テスト",
        "users": 5,
        "spawn_rate": 1,
        "duration": "2m",
        "data_size": "small",
        "enabled": True,
    },
    "large_data_test": {
        "description": "大規模データテスト",
        "users": 10,
        "spawn_rate": 1,
        "duration": "1m",
        "data_size": "medium",
        "enabled": False,  # デフォルトでは無効
    },
}

# データベース設定
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "performance_test_db",
    "user": "test_user",
    "password": "test_password",
    "pool_size": 20,
    "max_overflow": 10,
    "pool_timeout": 30,
    "pool_recycle": 3600,
}

# API設定
API_CONFIG = {
    "base_url": "http://localhost:8000",
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1,
    "auth_token": "test_token",
    "headers": {"Content-Type": "application/json", "Accept": "application/json"},
}

# パフォーマンス閾値
PERFORMANCE_THRESHOLDS = {
    "response_time": {
        "p50": 200,  # ms
        "p90": 500,  # ms
        "p95": 1000,  # ms
        "p99": 2000,  # ms
        "max": 5000,  # ms
    },
    "error_rate": {"warning": 0.01, "critical": 0.05},  # 1%  # 5%
    "throughput": {
        "min_rps": 10,  # 1秒あたりの最小リクエスト数
        "target_rps": 100,  # 1秒あたりの目標リクエスト数
    },
}


def get_test_data_path(data_type: str, data_size: str = "small") -> Path:
    """テストデータのパスを取得"""
    return TEST_DATA_DIR / data_size / f"{data_type}.json"


def get_test_scenario(scenario_name: str) -> Dict[str, Any]:
    """テストシナリオを取得"""
    scenario = TEST_SCENARIOS.get(scenario_name)
    if not scenario:
        raise ValueError(f"Unknown scenario: {scenario_name}")
    if not scenario["enabled"]:
        raise ValueError(f"Scenario {scenario_name} is not enabled")
    return scenario


def get_database_connection_string() -> str:
    """データベース接続文字列を取得"""
    return (
        f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@"
        f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
    )


def get_api_url(endpoint: str) -> str:
    """APIエンドポイントの完全なURLを取得"""
    base_url = API_CONFIG["base_url"].rstrip("/")
    endpoint = endpoint.lstrip("/")
    return f"{base_url}/{endpoint}"
