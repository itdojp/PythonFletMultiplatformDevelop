"""
Load testing for the application.

This module contains tests that simulate normal and peak load conditions
to verify the application's performance characteristics.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from src.backend.app.main import app
from src.backend.tests.performance.utils import LoadGenerator

# Mark all tests in this module as performance tests
pytestmark = pytest.mark.performance


class TestLoadEndpoints:
    """Test suite for load testing API endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, test_client: TestClient):
        """Setup test client and base URL."""
        self.client = test_client
        self.base_url = "http://testserver"

    @pytest.mark.parametrize(
        "endpoint,method,params",
        [
            ("/api/health", "GET", None),
            ("/api/users", "GET", None),
            ("/api/users/1", "GET", None),
        ],
    )
    async def test_endpoint_load(
        self,
        performance_metrics,
        endpoint: str,
        method: str,
        params: Optional[Dict[str, Any]],
        perf_test_config: Dict[str, Any],
    ):
        """Test load on individual endpoints.

        This test simulates multiple concurrent requests to a single endpoint
        to measure its performance under load.
        """
        config = perf_test_config["load_test"]
        num_requests = config["users"]

        async with LoadGenerator(self.base_url) as loader:
            results = await loader.run_load_test(
                method=method,
                endpoint=endpoint,
                num_requests=num_requests,
                params=params,
            )

        # Record metrics
        performance_metrics.record_test_metric("load_test_results", results)

        # Assert performance criteria
        assert (
            results["success_rate"] >= 0.95
        ), f"Success rate too low: {results['success_rate']}"
        assert (
            results["response_times"]["p95"] < 1.0
        ), f"95th percentile response time too high: {results['response_times']['p95']}s"

    async def test_mixed_workload(
        self, performance_metrics, perf_test_config: Dict[str, Any]
    ):
        """Test a mixed workload simulating real-world usage patterns."""
        config = perf_test_config["load_test"]
        num_users = config["users"]

        # Define a list of endpoints to test with their methods and parameters
        endpoints = [
            {"method": "GET", "endpoint": "/api/health", "params": None},
            {"method": "GET", "endpoint": "/api/users", "params": {"limit": 10}},
            {"method": "GET", "endpoint": "/api/users/1", "params": None},
            # Add more endpoints as needed
        ]

        # Distribute requests among endpoints
        requests_per_endpoint = num_users // len(endpoints)

        async with LoadGenerator(self.base_url) as loader:
            tasks = []

            for endpoint_config in endpoints:
                task = loader.run_load_test(
                    method=endpoint_config["method"],
                    endpoint=endpoint_config["endpoint"],
                    num_requests=requests_per_endpoint,
                    params=endpoint_config["params"],
                    progress=False,
                )
                tasks.append(task)

            # Run all load tests concurrently
            results = await asyncio.gather(*tasks)

        # Aggregate results
        total_requests = sum(r["total_requests"] for r in results)
        successful_requests = sum(r["successful_requests"] for r in results)
        success_rate = successful_requests / total_requests if total_requests > 0 else 0

        # Calculate overall response times
        all_response_times = []
        for r in results:
            all_response_times.extend(
                [t for t in r.get("response_times", []) if isinstance(t, (int, float))]
            )

        # Record metrics
        performance_metrics.record_test_metric("total_requests", total_requests)
        performance_metrics.record_test_metric(
            "successful_requests", successful_requests
        )
        performance_metrics.record_test_metric("success_rate", success_rate)

        if all_response_times:
            performance_metrics.record_test_metric(
                "avg_response_time", sum(all_response_times) / len(all_response_times)
            )
            performance_metrics.record_test_metric(
                "max_response_time", max(all_response_times)
            )
            performance_metrics.record_test_metric(
                "min_response_time", min(all_response_times)
            )

        # Assert performance criteria
        assert success_rate >= 0.95, f"Overall success rate too low: {success_rate}"

        if all_response_times:
            p95 = sorted(all_response_times)[int(len(all_response_times) * 0.95)]
            assert p95 < 2.0, f"95th percentile response time too high: {p95}s"

    @pytest.mark.parametrize("concurrent_users", [10, 50, 100])
    async def test_concurrent_users(
        self,
        performance_metrics,
        concurrent_users: int,
        perf_test_config: Dict[str, Any],
    ):
        """Test how the system handles different levels of concurrent users."""
        endpoint = "/api/health"
        method = "GET"

        async with LoadGenerator(self.base_url) as loader:
            results = await loader.run_load_test(
                method=method,
                endpoint=endpoint,
                num_requests=concurrent_users * 5,  # 5 requests per user
                params=None,
            )

        # Record metrics
        test_metric_name = f"concurrent_users_{concurrent_users}"
        performance_metrics.record_test_metric(test_metric_name, results)

        # Assert performance criteria
        assert (
            results["success_rate"] >= 0.95
        ), f"Success rate too low for {concurrent_users} users: {results['success_rate']}"
        assert (
            results["response_times"]["p95"] < 1.5
        ), f"95th percentile response time too high for {concurrent_users} users: {results['response_times']['p95']}s"


class TestDatabasePerformance:
    """Performance tests focused on database operations."""

    @pytest.fixture(autouse=True)
    def setup(self, test_client: TestClient):
        """Setup test client and base URL."""
        self.client = test_client
        self.base_url = "http://testserver"

    async def test_database_query_performance(
        self,
        performance_metrics,
        perf_test_config: Dict[str, Any],
    ):
        """Test performance of database queries under load."""
        config = perf_test_config["load_test"]
        num_queries = config["users"]

        # Test a simple query
        async with LoadGenerator(self.base_url) as loader:
            results = await loader.run_load_test(
                method="GET",
                endpoint="/api/users",
                num_requests=num_queries,
                params={"limit": 10},
            )

        # Record metrics
        performance_metrics.record_test_metric("db_query_results", results)

        # Assert performance criteria
        assert (
            results["success_rate"] >= 0.99
        ), f"Query success rate too low: {results['success_rate']}"
        assert (
            results["response_times"]["p99"] < 0.5
        ), f"99th percentile query time too high: {results['response_times']['p99']}s"

    async def test_database_write_performance(
        self,
        performance_metrics,
        perf_test_config: Dict[str, Any],
    ):
        """Test performance of database write operations under load."""
        config = perf_test_config["load_test"]
        num_writes = min(
            100, config["users"]
        )  # Limit number of writes to avoid filling up the database

        # Generate unique user data for each request
        def generate_user_data(index: int) -> Dict[str, Any]:
            timestamp = int(datetime.utcnow().timestamp())
            return {
                "username": f"loadtest_{timestamp}_{index}",
                "email": f"loadtest_{timestamp}_{index}@example.com",
                "password": "testpassword123",
                "full_name": f"Load Test User {index}",
            }

        # Test user creation
        async with LoadGenerator(self.base_url) as loader:
            results = await loader.run_load_test(
                method="POST",
                endpoint="/api/users/",
                num_requests=num_writes,
                json_data=generate_user_data,
            )

        # Record metrics
        performance_metrics.record_test_metric("db_write_results", results)

        # Assert performance criteria
        assert (
            results["success_rate"] >= 0.95
        ), f"Write success rate too low: {results['success_rate']}"
        assert (
            results["response_times"]["p95"] < 1.0
        ), f"95th percentile write time too high: {results['response_times']['p95']}s"
