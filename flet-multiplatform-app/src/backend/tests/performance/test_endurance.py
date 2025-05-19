"""
Endurance testing for the application.

This module contains tests that verify the system's stability and performance
over an extended period under sustained load.
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from src.backend.app.main import app
from src.backend.tests.performance.utils import LoadGenerator

# Mark all tests in this module as performance tests
pytestmark = pytest.mark.performance


class TestEndurance:
    """Test suite for endurance testing."""

    @pytest.fixture(autouse=True)
    def setup(self, test_client: TestClient):
        """Setup test client and base URL."""
        self.client = test_client
        self.base_url = "http://testserver"

    async def test_sustained_load(
        self,
        performance_metrics,
        perf_test_config: Dict[str, Any],
    ):
        """Test the system under sustained load for an extended period."""
        config = perf_test_config["endurance_test"]
        duration_minutes = (
            5  # Shorter for testing, should be 60+ for real endurance test
        )

        # Define test scenarios with different weights
        scenarios = [
            {"method": "GET", "endpoint": "/api/health", "weight": 3, "params": None},
            {
                "method": "GET",
                "endpoint": "/api/users",
                "weight": 2,
                "params": {"limit": 20},
            },
            {"method": "GET", "endpoint": "/api/users/1", "weight": 1, "params": None},
        ]

        # Create weighted list of scenarios
        weighted_scenarios = []
        for scenario in scenarios:
            weighted_scenarios.extend([scenario] * scenario["weight"])

        # Initialize metrics
        total_requests = 0
        successful_requests = 0
        response_times = []

        # Calculate end time
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        iteration = 0

        print(f"\n⏱  Starting endurance test for {duration_minutes} minutes...")

        async with LoadGenerator(self.base_url) as loader:
            while datetime.now() < end_time:
                iteration += 1
                print(
                    f"\n🔄 Iteration {iteration} - {datetime.now().strftime('%H:%M:%S')}"
                )

                # Randomly select a scenario for this iteration
                scenario = random.choice(weighted_scenarios)

                # Run a small batch of requests
                batch_size = 10
                try:
                    results = await loader.run_load_test(
                        method=scenario["method"],
                        endpoint=scenario["endpoint"],
                        num_requests=batch_size,
                        params=scenario["params"],
                        progress=False,
                    )

                    # Update metrics
                    total_requests += results["total_requests"]
                    successful_requests += results["successful_requests"]

                    if "response_times" in results:
                        response_times.extend(
                            [
                                t
                                for t in results["response_times"]
                                if isinstance(t, (int, float))
                            ]
                        )

                    # Print progress
                    success_rate = (
                        (successful_requests / total_requests) * 100
                        if total_requests > 0
                        else 0
                    )
                    print(
                        f"  Requests: {total_requests} | "
                        f"Success: {success_rate:.1f}% | "
                        f"Avg. Response: {results['response_times']['avg']:.3f}s"
                    )

                    # Record metrics periodically
                    if iteration % 5 == 0:
                        performance_metrics.record_test_metric(
                            f"endurance_checkpoint_{iteration}",
                            {
                                "total_requests": total_requests,
                                "success_rate": success_rate / 100,
                                "avg_response_time": results["response_times"]["avg"],
                                "timestamp": datetime.now().isoformat(),
                            },
                        )

                except Exception as e:
                    print(f"❌ Error during endurance test: {e}")

                # Small delay between iterations
                await asyncio.sleep(1)

        # Calculate final metrics
        success_rate = (
            (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        )
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        # Record final metrics
        performance_metrics.record_test_metric(
            "endurance_final",
            {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "success_rate": success_rate / 100,
                "avg_response_time": avg_response_time,
                "duration_minutes": duration_minutes,
            },
        )

        print("\n🏁 Endurance Test Complete!")
        print(f"Total Requests: {total_requests}")
        print(f"Successful Requests: {successful_requests}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Average Response Time: {avg_response_time:.3f}s")

        # Assert that success rate remained high throughout the test
        assert (
            success_rate >= 95.0
        ), f"Success rate dropped below 95%: {success_rate:.2f}%"

    async def test_memory_leaks(
        self,
        performance_metrics,
        perf_test_config: Dict[str, Any],
    ):
        """Test for memory leaks over an extended period."""
        import os

        import psutil

        config = perf_test_config["endurance_test"]
        duration_minutes = 5  # Shorter for testing, should be 60+ for real test

        process = psutil.Process(os.getpid())

        # Track memory usage over time
        memory_samples = []

        # Initial memory reading
        memory_samples.append(process.memory_info().rss / (1024 * 1024))  # MB

        print(f"\n🧠 Starting memory leak test for {duration_minutes} minutes...")
        print(f"Initial memory usage: {memory_samples[-1]:.2f} MB")

        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        iteration = 0

        async with LoadGenerator(self.base_url) as loader:
            while datetime.now() < end_time:
                iteration += 1

                # Run a mix of operations
                if iteration % 3 == 0:
                    # Memory-intensive operation
                    await loader.run_load_test(
                        method="GET",
                        endpoint="/api/users",
                        num_requests=20,
                        params={"limit": 100},
                        progress=False,
                    )
                else:
                    # Standard operation
                    await loader.make_request(
                        method="GET",
                        endpoint="/api/health",
                    )

                # Record memory usage every few iterations
                if iteration % 5 == 0:
                    memory_mb = process.memory_info().rss / (1024 * 1024)
                    memory_samples.append(memory_mb)
                    print(f"  Iteration {iteration}: {memory_mb:.2f} MB")

                    # Record memory usage
                    performance_metrics.record_test_metric(
                        "memory_usage_mb",
                        {
                            "iteration": iteration,
                            "memory_mb": memory_mb,
                            "timestamp": datetime.now().isoformat(),
                        },
                    )

                # Small delay between iterations
                await asyncio.sleep(1)

        # Analyze memory usage trend
        if len(memory_samples) > 1:
            # Calculate memory increase per minute
            duration_hours = duration_minutes / 60
            total_increase = memory_samples[-1] - memory_samples[0]
            increase_per_hour = (
                (total_increase / duration_hours) if duration_hours > 0 else 0
            )

            print(f"\n📊 Memory Analysis:")
            print(f"Initial: {memory_samples[0]:.2f} MB")
            print(f"Final: {memory_samples[-1]:.2f} MB")
            print(f"Total Increase: {total_increase:.2f} MB")
            print(f"Increase per Hour: {increase_per_hour:.2f} MB/hour")

            # Record metrics
            performance_metrics.record_test_metric(
                "memory_leak_test",
                {
                    "initial_mb": memory_samples[0],
                    "final_mb": memory_samples[-1],
                    "total_increase_mb": total_increase,
                    "increase_per_hour_mb": increase_per_hour,
                    "duration_minutes": duration_minutes,
                },
            )

            # Check for significant memory leaks
            assert (
                increase_per_hour < 10
            ), f"Possible memory leak: {increase_per_hour:.2f} MB/hour increase"

    async def test_connection_pool_stability(
        self,
        performance_metrics,
        perf_test_config: Dict[str, Any],
    ):
        """Test the stability of database connection pools under sustained load."""
        config = perf_test_config["endurance_test"]
        duration_minutes = 5  # Shorter for testing, should be 30+ for real test

        print(
            f"\n🔌 Testing connection pool stability for {duration_minutes} minutes..."
        )

        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        iteration = 0
        successful_requests = 0
        total_requests = 0

        async with LoadGenerator(self.base_url) as loader:
            while datetime.now() < end_time:
                iteration += 1

                # Vary the load pattern
                if iteration % 10 == 0:
                    # Heavy load phase
                    batch_size = 50
                    params = {"limit": 100}
                else:
                    # Normal load phase
                    batch_size = 10
                    params = {"limit": 10}

                try:
                    # Run a batch of database queries
                    results = await loader.run_load_test(
                        method="GET",
                        endpoint="/api/users",
                        num_requests=batch_size,
                        params=params,
                        progress=False,
                    )

                    # Update metrics
                    total_requests += results["total_requests"]
                    successful_requests += results["successful_requests"]

                    # Print status
                    if iteration % 5 == 0:
                        success_rate = (
                            (successful_requests / total_requests) * 100
                            if total_requests > 0
                            else 0
                        )
                        print(
                            f"  Iteration {iteration}: "
                            f"Success Rate: {success_rate:.1f}% | "
                            f"Avg. Response: {results['response_times']['avg']:.3f}s"
                        )

                    # Record metrics periodically
                    if iteration % 10 == 0:
                        performance_metrics.record_test_metric(
                            "connection_pool_checkpoint",
                            {
                                "iteration": iteration,
                                "success_rate": (
                                    successful_requests / total_requests
                                    if total_requests > 0
                                    else 0
                                ),
                                "avg_response_time": results["response_times"]["avg"],
                                "active_connections": 0,  # Would need DB-specific code to get actual count
                                "timestamp": datetime.now().isoformat(),
                            },
                        )

                except Exception as e:
                    print(f"❌ Error during connection pool test: {e}")

                # Small delay between iterations
                await asyncio.sleep(1)

        # Calculate final success rate
        success_rate = (
            (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        )

        print("\n🏁 Connection Pool Test Complete!")
        print(f"Total Requests: {total_requests}")
        print(f"Successful Requests: {successful_requests}")
        print(f"Success Rate: {success_rate:.2f}%")

        # Assert that success rate remained high throughout the test
        assert (
            success_rate >= 99.0
        ), f"Success rate dropped below 99%: {success_rate:.2f}%"
