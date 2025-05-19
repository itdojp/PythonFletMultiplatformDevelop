"""
パフォーマンステストのためのベースクラスとユーティリティを提供するモジュール。
"""

import json
import logging
import os
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import pytest
import requests
from locust import HttpUser, between, events, task
from locust.env import Environment
from locust.runners import MasterRunner, WorkerRunner

from .config import (
    API_CONFIG,
    DATABASE_CONFIG,
    PERFORMANCE_THRESHOLDS,
    get_api_url,
    get_database_connection_string,
    get_test_data_path,
    get_test_scenario,
)
from .utils import PerformanceTestUtils

# ロガーの設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BasePerformanceTest(ABC):
    """すべてのパフォーマンステストの基底クラス。"""

    def __init__(self, test_name: Optional[str] = None):
        """初期化

        Args:
            test_name: テスト名（指定しない場合はクラス名が使用されます）
        """
        self.test_name = test_name or self.__class__.__name__
        self.base_url = API_CONFIG["base_url"]
        self.timeout = API_CONFIG["timeout"]
        self.retry_attempts = API_CONFIG["retry_attempts"]
        self.retry_delay = API_CONFIG["retry_delay"]
        self.headers = API_CONFIG["headers"].copy()

        # テストデータのパス
        self.test_data_dir = Path(__file__).parent.parent.parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)

        # テスト結果
        self.test_start_time: Optional[float] = None
        self.test_end_time: Optional[float] = None
        self.test_duration: Optional[float] = None
        self.test_results: Dict[str, Any] = {}

    def setup(self):
        """テスト環境のセットアップを行います。"""
        logger.info(f"Setting up test: {self.test_name}")
        self.test_start_time = time.time()

        # テストデータのロード
        self.test_data = self._load_test_data()

        # テスト固有のセットアップ
        self._setup()

    def teardown(self):
        """テスト環境のクリーンアップを行います。"""
        logger.info(f"Tearing down test: {self.test_name}")

        # テスト固有のクリーンアップ
        self._teardown()

        # テスト結果の記録
        self.test_end_time = time.time()
        self.test_duration = self.test_end_time - self.test_start_time

        logger.info(
            f"Test '{self.test_name}' completed in {self.test_duration:.2f} seconds"
        )

    @abstractmethod
    def _setup(self):
        """テスト固有のセットアップを行います。"""
        pass

    @abstractmethod
    def _teardown(self):
        """テスト固有のクリーンアップを行います。"""
        pass

    @abstractmethod
    def run_test(self):
        """パフォーマンステストを実行します。"""
        pass

    def _load_test_data(self, data_size: str = "small") -> Dict[str, Any]:
        """テストデータをロードします。

        Args:
            data_size: データサイズ（small, medium, large）

        Returns:
            テストデータの辞書
        """
        return PerformanceTestUtils.load_test_data(data_size)

    def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """HTTPリクエストを送信します。

        Args:
            method: HTTPメソッド（GET, POST, PUT, DELETEなど）
            endpoint: APIエンドポイント
            data: リクエストボディ
            params: クエリパラメータ
            headers: リクエストヘッダー
            **kwargs: その他の引数（requests.requestに渡されます）

        Returns:
            requests.Response: レスポンスオブジェクト
        """
        url = get_api_url(endpoint)
        headers = headers or {}
        headers.update(self.headers)

        # リトライ処理
        last_exception = None

        for attempt in range(1, self.retry_attempts + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                    **kwargs,
                )

                # ステータスコードがエラーの場合でもレスポンスを返す
                return response

            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.retry_attempts:
                    logger.warning(
                        f"Request failed (attempt {attempt}/{self.retry_attempts}): {e}. "
                        f"Retrying in {self.retry_delay} seconds..."
                    )
                    time.sleep(self.retry_delay)
                else:
                    logger.error(
                        f"All {self.retry_attempts} attempts failed. Last error: {e}"
                    )
                    raise

        # ここには通常到達しない（例外が発生するはず）
        raise last_exception or Exception("Unknown error occurred in make_request")

    def assert_response(
        self,
        response: requests.Response,
        expected_status: int = 200,
        expected_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """レスポンスを検証します。

        Args:
            response: レスポンスオブジェクト
            expected_status: 期待されるステータスコード
            expected_data: 期待されるレスポンスデータ（オプション）

        Returns:
            レスポンスのJSONデータ

        Raises:
            AssertionError: 検証に失敗した場合
        """
        try:
            response_data = response.json()
        except ValueError:
            response_data = {}

        assert response.status_code == expected_status, (
            f"Expected status {expected_status}, but got {response.status_code}. "
            f"Response: {response.text}"
        )

        if expected_data is not None:
            for key, value in expected_data.items():
                assert (
                    key in response_data
                ), f"Expected key '{key}' not found in response"
                assert (
                    response_data[key] == value
                ), f"Expected {key} to be '{value}', but got '{response_data[key]}'"

        return response_data

    def log_metrics(
        self,
        metric_name: str,
        value: float,
        unit: str = "",
        threshold: Optional[float] = None,
    ) -> None:
        """パフォーマンスメトリクスを記録します。

        Args:
            metric_name: メトリクス名
            value: メトリクスの値
            unit: メトリクスの単位
            threshold: 閾値（オプション）
        """
        log_msg = f"[METRIC] {metric_name}: {value} {unit}"
        if threshold is not None:
            status = "PASS" if value <= threshold else "FAIL"
            log_msg += f" (threshold: {threshold} {unit}, status: {status})"

        logger.info(log_msg)

        # テスト結果にメトリクスを追加
        if "metrics" not in self.test_results:
            self.test_results["metrics"] = {}

        self.test_results["metrics"][metric_name] = {
            "value": value,
            "unit": unit,
            "threshold": threshold,
            "passed": value <= threshold if threshold is not None else None,
        }


class BaseLocustTest(HttpUser):
    """Locustを使用したHTTPパフォーマンステストのためのベースクラス。"""

    # 抽象クラスとしてマーク（このクラスを直接使用しない）
    abstract = True

    # リクエスト間の待機時間（秒）
    wait_time = between(0.5, 2.5)

    # テストデータのサイズ
    test_data_size = "small"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 設定からAPIの基本URLを取得
        self.base_url = API_CONFIG["base_url"]
        self.timeout = API_CONFIG["timeout"]
        self.retry_attempts = API_CONFIG["retry_attempts"]
        self.retry_delay = API_CONFIG["retry_delay"]

        # ヘッダーを設定
        self.headers = API_CONFIG["headers"].copy()

        # テストデータをロード
        self.test_data = {}
        self._load_test_data()

    def _load_test_data(self):
        """テストデータをロードします。"""
        try:
            self.test_data = PerformanceTestUtils.load_test_data(self.test_data_size)
        except Exception as e:
            logger.error(f"Failed to load test data: {e}")

    def on_start(self):
        """Locustユーザーが実行を開始するときに呼び出されます。"""
        # SSL検証を無効化（テスト用）
        self.client.verify = False

        # 認証トークンを設定（必要に応じて）
        auth_token = os.getenv("AUTH_TOKEN")
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"

        logger.info(f"Starting test for {self.__class__.__name__}")

    def on_stop(self):
        """Locustユーザーが実行を停止するときに呼び出されます。"""
        logger.info(f"Stopping test for {self.__class__.__name__}")

    def make_request(
        self,
        method: str,
        endpoint: str,
        name: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """HTTPリクエストを送信します。

        Args:
            method: HTTPメソッド（GET, POST, PUT, DELETEなど）
            endpoint: APIエンドポイント
            name: テスト名（Locustの統計に表示されます）
            json: JSONリクエストボディ
            data: フォームデータ
            params: クエリパラメータ
            headers: リクエストヘッダー
            **kwargs: その他の引数（self.client.requestに渡されます）

        Returns:
            requests.Response: レスポンスオブジェクト
        """
        # ヘッダーをマージ
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        # リクエスト名が指定されていない場合はエンドポイントを使用
        if name is None:
            name = endpoint

        # リクエストを送信
        with self.client.request(
            method=method,
            url=(
                endpoint
                if endpoint.startswith("http")
                else f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            ),
            name=name,
            json=json,
            data=data,
            params=params,
            headers=request_headers,
            catch_response=True,
            **kwargs,
        ) as response:
            # レスポンスの検証
            if response.status_code >= 400:
                response.failure(f"Status code: {response.status_code}")
            else:
                response.success()

            return response


# Pytestフィクスチャ
@pytest.fixture(scope="module")
def base_url():
    """APIのベースURLを返します。"""
    return API_CONFIG["base_url"]


@pytest.fixture(scope="module")
def auth_headers():
    """認証ヘッダーを返します。"""
    # 実際の認証処理を実装
    token = os.getenv("AUTH_TOKEN")
    if not token:
        # テスト用のトークンを生成
        token = "test_token_12345"

    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def test_data():
    """テストデータをロードします。"""
    return PerformanceTestUtils.load_test_data("small")
