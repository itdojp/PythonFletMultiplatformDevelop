"""
Scalability testing for the application.

This module contains tests that verify how well the system scales with increasing load,
and identify the maximum capacity before performance degrades.
"""

import asyncio
import statistics
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from src.backend.app.main import app
from src.backend.tests.performance.utils import LoadGenerator

# Mark all tests in this module as performance tests
pytestmark = pytest.mark.performance


class TestScalability:
    """Test suite for scalability testing."""

    @pytest.fixture(autouse=True)
    def setup(self, test_client: TestClient):
        """Setup test client and base URL."""
        self.client = test_client
        self.base_url = "http://testserver"

    async def run_scalability_test(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        warm_up: bool = True,
    ) -> Dict[str, Any]:
        """Run a scalability test with increasing load.

        Args:
            endpoint: API endpoint to test
            method: HTTP method
            params: Query parameters
            json_data: JSON request body
            warm_up: Whether to run a warm-up phase

        Returns:
            Dictionary with test results
        """
        # Warm-up phase
        if warm_up:
            print("\n🔥 Warming up...")
            async with LoadGenerator(self.base_url) as loader:
                await loader.run_load_test(
                    method=method,
                    endpoint=endpoint,
                    num_requests=10,
                    params=params,
                    json_data=json_data,
                    progress=False,
                )

        # Test with increasing load
        results = {}

        # Define load levels (concurrent users)
        load_levels = [
            1,
            5,
            10,
            20,
            50,
            100,
            200,
            500,
        ]  # Adjust based on expected capacity

        print(f"\n🚀 Starting scalability test for {endpoint}")

        for users in load_levels:
            print(f"\n📊 Testing with {users} concurrent users...")

            async with LoadGenerator(self.base_url) as loader:
                # Run load test for this level
                test_results = await loader.run_load_test(
                    method=method,
                    endpoint=endpoint,
                    num_requests=users * 2,  # 2 requests per user
                    params=params,
                    json_data=json_data,
                    progress=False,
                )

                # Store results
                results[users] = {
                    "success_rate": test_results["success_rate"],
                    "response_times": test_results["response_times"],
                    "throughput": (
                        test_results["successful_requests"]
                        / test_results["response_times"]["avg"]
                        if test_results["response_times"]["avg"] > 0
                        else 0
                    ),
                }

                # Print summary
                print(f"  Success Rate: {results[users]['success_rate']:.1%}")
                print(
                    f"  Avg. Response Time: {results[users]['response_times']['avg']:.3f}s"
                )
                print(f"  Throughput: {results[users]['throughput']:.1f} req/s")

                # Stop if success rate drops below 95%
                if results[users]["success_rate"] < 0.95:
                    print("⚠️  Success rate dropped below 95%, stopping test")
                    break

        return results

    async def test_read_scalability(
        self,
        performance_metrics,
        perf_test_config: Dict[str, Any],
    ):
        """Test how well the system scales with read operations."""
        config = perf_test_config["scalability_test"]

        # Run scalability test for a read-heavy endpoint
        results = await self.run_scalability_test(
            endpoint="/api/users",
            method="GET",
            params={"limit": 50},
        )

        # Analyze results
        max_users = max(results.keys())
        max_throughput = max(r["throughput"] for r in results.values())

        # Record metrics
        performance_metrics.record_test_metric(
            "read_scalability_results",
            {
                "max_concurrent_users": max_users,
                "max_throughput": max_throughput,
                "response_times": {
                    users: r["response_times"] for users, r in results.items()
                },
            },
        )

        print("\n📈 Read Scalability Test Complete!")
        print(f"Maximum Concurrent Users: {max_users}")
        print(f"Maximum Throughput: {max_throughput:.1f} requests/second")

        # Assert that the system can handle at least 100 concurrent users
        assert (
            max_users >= 100
        ), f"System failed to scale to 100 concurrent users (max: {max_users})"

    async def test_write_scalability(
        self,
        performance_metrics,
        perf_test_config: Dict[str, Any],
    ):
        """Test how well the system scales with write operations."""
        config = perf_test_config["scalability_test"]

        # Generate unique user data for each request
        timestamp = int(time.time())

        def generate_user_data(index: int) -> Dict[str, Any]:
            return {
                "username": f"user_{timestamp}_{index}",
                "email": f"user_{timestamp}_{index}@example.com",
                "password": "testpassword123",
                "full_name": f"Test User {index}",
            }

        # Run scalability test for a write-heavy endpoint
        results = await self.run_scalability_test(
            endpoint="/api/users/",
            method="POST",
            json_data=generate_user_data,
        )

        # Analyze results
        max_users = max(results.keys())
        max_throughput = max(r["throughput"] for r in results.values())

        # Record metrics
        performance_metrics.record_test_metric(
            "write_scalability_results",
            {
                "max_concurrent_users": max_users,
                "max_throughput": max_throughput,
                "response_times": {
                    users: r["response_times"] for users, r in results.items()
                },
            },
        )

        print("\n📈 Write Scalability Test Complete!")
        print(f"Maximum Concurrent Users: {max_users}")
        print(f"Maximum Throughput: {max_throughput:.1f} requests/second")

        # Assert that the system can handle at least 50 concurrent users for writes
        assert (
            max_users >= 50
        ), f"System failed to scale to 50 concurrent users for writes (max: {max_users})"

    async def test_mixed_workload_scalability(
        self,
        performance_metrics,
        perf_test_config: Dict[str, Any],
    ):
        """Test how well the system scales with a mixed read/write workload."""
        config = perf_test_config["scalability_test"]

        # Define a mix of read and write operations
        operations = [
            {
                "method": "GET",
                "endpoint": "/api/users",
                "params": {"limit": 20},
                "weight": 3,
            },
            {"method": "GET", "endpoint": "/api/users/1", "params": None, "weight": 2},
            {"method": "POST", "endpoint": "/api/users/", "params": None, "weight": 1},
        ]

        # Create weighted list of operations
        weighted_operations = []
        for op in operations:
            weighted_operations.extend([op] * op["weight"])

        # Generate unique user data for write operations
        timestamp = int(time.time())

        def generate_user_data(index: int) -> Dict[str, Any]:
            return {
                "username": f"mixed_{timestamp}_{index}",
                "email": f"mixed_{timestamp}_{index}@example.com",
                "password": "testpassword123",
                "full_name": f"Mixed Test User {index}",
            }

        # Test with increasing load
        load_levels = [1, 5, 10, 20, 50, 100]  # Fewer levels for mixed workload
        results = {}

        print("\n🚀 Starting mixed workload scalability test...")

        for users in load_levels:
            print(f"\n📊 Testing with {users} concurrent users...")

            async with LoadGenerator(self.base_url) as loader:
                # Run a mix of operations for this load level
                tasks = []

                for i in range(users * 2):  # 2 operations per user
                    op = random.choice(weighted_operations)

                    # Prepare request data
                    json_data = (
                        generate_user_data(i) if op["method"] == "POST" else None
                    )

                    # Create task
                    task = loader.make_request(
                        method=op["method"],
                        endpoint=op["endpoint"],
                        params=op["params"],
                        json_data=json_data,
                    )
                    tasks.append(task)

                # Run all tasks concurrently
                start_time = time.time()
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                duration = time.time() - start_time

                # Process responses
                successful = 0
                response_times = []

                for response in responses:
                    if isinstance(response, dict) and response.get("success", False):
                        successful += 1
                        if "response_time" in response:
                            response_times.append(response["response_time"])

                # Calculate metrics
                total_requests = len(responses)
                success_rate = successful / total_requests if total_requests > 0 else 0
                avg_response_time = (
                    statistics.mean(response_times) if response_times else 0
                )
                throughput = successful / duration if duration > 0 else 0

                # Store results
                results[users] = {
                    "success_rate": success_rate,
                    "avg_response_time": avg_response_time,
                    "throughput": throughput,
                    "total_requests": total_requests,
                    "successful_requests": successful,
                }

                # Print summary
                print(f"  Success Rate: {success_rate:.1%}")
                print(f"  Avg. Response Time: {avg_response_time:.3f}s")
                print(f"  Throughput: {throughput:.1f} req/s")

                # Stop if success rate drops below 90%
                if success_rate < 0.90:
                    print("⚠️  Success rate dropped below 90%, stopping test")
                    break

        # Analyze results
        max_users = max(results.keys())
        max_throughput = max(r["throughput"] for r in results.values())

        # Record metrics
        performance_metrics.record_test_metric(
            "mixed_workload_scalability_results",
            {
                "max_concurrent_users": max_users,
                "max_throughput": max_throughput,
                "results": results,
            },
        )

        print("\n📈 Mixed Workload Scalability Test Complete!")
        print(f"Maximum Concurrent Users: {max_users}")
        print(f"Maximum Throughput: {max_throughput:.1f} requests/second")

        # Assert that the system can handle at least 50 concurrent users with mixed workload
        assert (
            max_users >= 50
        ), f"System failed to scale to 50 concurrent users with mixed workload (max: {max_users})"
