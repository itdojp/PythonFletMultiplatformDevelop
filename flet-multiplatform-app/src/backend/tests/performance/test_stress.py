"""
Stress testing for the application.

This module contains tests that push the system beyond normal operational capacity,
often to a breaking point, to observe how the system behaves under extreme conditions.
"""

import asyncio
import random
from typing import Any, Dict, List, Optional

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from src.backend.app.main import app
from src.backend.tests.performance.utils import LoadGenerator

# Mark all tests in this module as performance tests
pytestmark = pytest.mark.performance


class TestStressEndpoints:
    """Test suite for stress testing API endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, test_client: TestClient):
        """Setup test client and base URL."""
        self.client = test_client
        self.base_url = "http://testserver"

    async def test_high_concurrent_users(
        self,
        performance_metrics,
        perf_test_config: Dict[str, Any],
    ):
        """Test the system with a very high number of concurrent users."""
        config = perf_test_config["stress_test"]
        num_users = config["users"]

        # Define a list of endpoints to test
        endpoints = [
            {"method": "GET", "endpoint": "/api/health"},
            {"method": "GET", "endpoint": "/api/users"},
            {"method": "GET", "endpoint": "/api/users/1"},
        ]

        async with LoadGenerator(self.base_url) as loader:
            # Warm-up phase
            print(f"\n🔥 Warming up with {num_users // 10} requests...")
            await loader.run_load_test(
                method="GET",
                endpoint="/api/health",
                num_requests=num_users // 10,
                progress=False,
            )

            # Main stress test
            print(f"🚀 Starting stress test with {num_users} concurrent users...")

            tasks = []
            for _ in range(num_users):
                # Randomly select an endpoint for each user
                endpoint = random.choice(endpoints)
                task = loader.run_load_test(
                    method=endpoint["method"],
                    endpoint=endpoint["endpoint"],
                    num_requests=5,  # Each user makes 5 requests
                    progress=False,
                )
                tasks.append(task)

            # Run all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        successful_requests = 0
        total_requests = 0
        response_times = []

        for result in results:
            if isinstance(result, Exception):
                print(f"Error in stress test: {result}")
                continue

            successful_requests += result["successful_requests"]
            total_requests += result["total_requests"]

            if "response_times" in result:
                response_times.extend([t for t in result["response_times"] if isinstance(t, (int, float))])

        success_rate = successful_requests / total_requests if total_requests > 0 else 0

        # Record metrics
        performance_metrics.record_test_metric("total_requests", total_requests)
        performance_metrics.record_test_metric("successful_requests", successful_requests)
        performance_metrics.record_test_metric("success_rate", success_rate)

        if response_times:
            performance_metrics.record_test_metric("avg_response_time", sum(response_times) / len(response_times))
            performance_metrics.record_test_metric("max_response_time", max(response_times))
            performance_metrics.record_test_metric("min_response_time", min(response_times))

        print(f"\n📊 Stress Test Results:")
        print(f"Total Requests: {total_requests}")
        print(f"Successful Requests: {successful_requests}")
        print(f"Success Rate: {success_rate:.2%}")

        if response_times:
            print(f"Average Response Time: {sum(response_times) / len(response_times):.3f}s")
            print(f"Max Response Time: {max(response_times):.3f}s")
            print(f"Min Response Time: {min(response_times):.3f}s")

        # Assert performance criteria (more lenient than load tests)
        assert success_rate >= 0.80, f"Success rate too low under stress: {success_rate:.2%}"

    async def test_system_under_extreme_load(
        self,
        performance_metrics,
        perf_test_config: Dict[str, Any],
    ):
        """Test the system under extreme load conditions."""
        config = perf_test_config["stress_test"]
        num_requests = config["users"] * 2  # Even more aggressive than standard stress test

        # Test a mix of read and write operations
        endpoints = [
            {"method": "GET", "endpoint": "/api/health", "weight": 5},
            {"method": "GET", "endpoint": "/api/users", "weight": 3},
            {"method": "GET", "endpoint": "/api/users/1", "weight": 2},
        ]

        # Create a weighted list of endpoints
        weighted_endpoints = []
        for endpoint in endpoints:
            weighted_endpoints.extend([endpoint] * endpoint["weight"])

        async with LoadGenerator(self.base_url) as loader:
            # Warm-up phase
            print(f"\n🔥 Warming up with {num_requests // 10} requests...")
            await loader.run_load_test(
                method="GET",
                endpoint="/api/health",
                num_requests=num_requests // 10,
                progress=False,
            )

            # Main stress test
            print(f"💥 Starting extreme load test with {num_requests} requests...")

            results = []
            batch_size = 100

            for i in range(0, num_requests, batch_size):
                current_batch_size = min(batch_size, num_requests - i)

                # Randomly select endpoints for this batch
                batch_endpoints = random.choices(
                    weighted_endpoints,
                    k=current_batch_size
                )

                # Create tasks for this batch
                tasks = []
                for endpoint in batch_endpoints:
                    task = loader.make_request(
                        method=endpoint["method"],
                        endpoint=endpoint["endpoint"],
                    )
                    tasks.append(task)

                # Run batch
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                results.extend([r for r in batch_results if not isinstance(r, Exception)])

                # Print progress
                print(f"  Processed {min(i + current_batch_size, num_requests)}/{num_requests} requests...")

        # Process results
        successful_requests = sum(1 for r in results if r.get("success", False))
        total_requests = len(results)
        success_rate = successful_requests / total_requests if total_requests > 0 else 0

        response_times = [r["response_time"] for r in results if "response_time" in r]

        # Record metrics
        performance_metrics.record_test_metric("extreme_load_results", {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": success_rate,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
        })

        print(f"\n📊 Extreme Load Test Results:")
        print(f"Total Requests: {total_requests}")
        print(f"Successful Requests: {successful_requests}")
        print(f"Success Rate: {success_rate:.2%}")

        if response_times:
            print(f"Average Response Time: {sum(response_times) / len(response_times):.3f}s")

        # Assert that the system didn't completely fail
        assert success_rate > 0.5, f"System failed under extreme load: {success_rate:.2%} success rate"


class TestResourceUtilization:
    """Tests focused on monitoring and analyzing resource utilization under stress."""

    @pytest.fixture(autouse=True)
    def setup(self, test_client: TestClient):
        """Setup test client and base URL."""
        self.client = test_client
        self.base_url = "http://testserver"

    async def test_memory_usage_under_load(
        self,
        performance_metrics,
        perf_test_config: Dict[str, Any],
    ):
        """Test memory usage under sustained load."""
        import os

        import psutil

        config = perf_test_config["stress_test"]
        num_requests = config["users"]

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB

        # Run load test
        async with LoadGenerator(self.base_url) as loader:
            results = await loader.run_load_test(
                method="GET",
                endpoint="/api/users",
                num_requests=num_requests,
                params={"limit": 50},
            )

        # Get memory usage after test
        final_memory = process.memory_info().rss / (1024 * 1024)  # MB
        memory_increase = final_memory - initial_memory

        # Record metrics
        performance_metrics.record_test_metric("memory_usage_mb", final_memory)
        performance_metrics.record_test_metric("memory_increase_mb", memory_increase)
        performance_metrics.record_test_metric("memory_usage_per_request_mb", memory_increase / num_requests if num_requests > 0 else 0)

        print(f"\n💾 Memory Usage:")
        print(f"Initial: {initial_memory:.2f} MB")
        print(f"Final: {final_memory:.2f} MB")
        print(f"Increase: {memory_increase:.2f} MB")
        print(f"Per request: {memory_increase / num_requests if num_requests > 0 else 0:.4f} MB")

        # Assert that memory usage is within reasonable bounds
        assert memory_increase < 100, f"Memory increase too high: {memory_increase:.2f} MB"

    async def test_cpu_usage_under_load(
        self,
        performance_metrics,
        perf_test_config: Dict[str, Any],
    ):
        """Test CPU usage under sustained load."""
        import psutil

        config = perf_test_config["stress_test"]
        duration = 30  # seconds

        # Start measuring CPU usage
        psutil.cpu_percent(interval=None)  # Initialize

        # Run load test in the background
        async def run_load():
            async with LoadGenerator(self.base_url) as loader:
                return await loader.run_load_test(
                    method="GET",
                    endpoint="/api/users",
                    num_requests=config["users"],
                    params={"limit": 50},
                    progress=False,
                )

        load_task = asyncio.create_task(run_load())

        # Monitor CPU usage during the test
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_percent_during_test = []

        while not load_task.done():
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_percent_during_test.append(cpu_percent)
            print(f"CPU Usage: {cpu_percent:.1f}%")

        # Get test results
        results = await load_task

        # Calculate average CPU usage
        avg_cpu = sum(cpu_percent_during_test) / len(cpu_percent_during_test) if cpu_percent_during_test else 0

        # Record metrics
        performance_metrics.record_test_metric("avg_cpu_percent", avg_cpu)
        performance_metrics.record_test_metric("max_cpu_percent", max(cpu_percent_during_test) if cpu_percent_during_test else 0)

        print(f"\n💻 CPU Usage During Test:")
        print(f"Average: {avg_cpu:.1f}%")
        print(f"Max: {max(cpu_percent_during_test) if cpu_percent_during_test else 0:.1f}%")

        # Assert that CPU usage is within reasonable bounds
        assert avg_cpu < 90, f"Average CPU usage too high: {avg_cpu:.1f}%"
