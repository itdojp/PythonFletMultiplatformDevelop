"""
Pytest configuration for performance tests.

This module contains fixtures and configuration for performance testing.
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

import psutil
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from src.backend.app.main import app
from src.backend.core.config import settings

# Performance test configuration
PERF_TEST_CONFIG = {
    "load_test": {
        "users": 100,
        "spawn_rate": 10,
        "duration": "30s",
        "warm_up_time": 5,  # seconds
    },
    "stress_test": {
        "users": 1000,
        "spawn_rate": 100,
        "duration": "5m",
        "warm_up_time": 10,
    },
    "endurance_test": {
        "users": 100,
        "spawn_rate": 10,
        "duration": "1h",
        "warm_up_time": 30,
    },
    "scalability_test": {
        "start_users": 10,
        "max_users": 1000,
        "step_size": 50,
        "step_duration": "30s",
        "warm_up_time": 10,
    },
}

# Results directory for performance tests
RESULTS_DIR = Path("results/performance")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


class PerformanceMetrics:
    """Class to collect and store performance metrics during tests."""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.metrics: Dict[str, Any] = {
            "test_name": test_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_metrics": [],
            "test_metrics": {},
            "errors": [],
        }
        self.process = psutil.Process()

    def start_timer(self) -> None:
        """Start the performance test timer."""
        self.start_time = time.time()

    def stop_timer(self) -> None:
        """Stop the performance test timer and calculate duration."""
        self.end_time = time.time()
        self.metrics["duration_seconds"] = self.end_time - self.start_time

    def record_system_metrics(self) -> None:
        """Record current system metrics including CPU, memory, and I/O."""
        cpu_percent = self.process.cpu_percent(interval=0.1)
        memory_info = self.process.memory_info()
        io_counters = self.process.io_counters()

        self.metrics["system_metrics"].append(
            {
                "timestamp": time.time(),
                "cpu_percent": cpu_percent,
                "memory_rss_mb": memory_info.rss / (1024 * 1024),  # Convert to MB
                "memory_vms_mb": memory_info.vms / (1024 * 1024),  # Convert to MB
                "io_read_count": io_counters.read_count,
                "io_write_count": io_counters.write_count,
                "io_read_bytes": io_counters.read_bytes,
                "io_write_bytes": io_counters.write_bytes,
            }
        )

    def record_test_metric(self, name: str, value: Any) -> None:
        """Record a test-specific metric."""
        self.metrics["test_metrics"][name] = value

    def record_error(self, error: Exception) -> None:
        """Record an error that occurred during the test."""
        self.metrics["errors"].append(
            {
                "type": error.__class__.__name__,
                "message": str(error),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    def save_results(self) -> Path:
        """Save the collected metrics to a JSON file.

        Returns:
            Path: Path to the saved results file.
        """
        if not self.end_time:
            self.stop_timer()

        # Ensure results directory exists
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        # Create a filename with timestamp and test name
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{self.test_name}.json"
        filepath = RESULTS_DIR / filename

        # Save to file
        with open(filepath, "w") as f:
            json.dump(self.metrics, f, indent=2, default=str)

        return filepath


@pytest_asyncio.fixture(scope="module")
async def test_client() -> Generator[TestClient, None, None]:
    """Create a test client for FastAPI application."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def performance_metrics(request) -> Generator[PerformanceMetrics, None, None]:
    """Fixture to collect performance metrics during tests.

    Automatically starts and stops timing, and saves results at the end of the test.
    """
    metrics = PerformanceMetrics(request.node.name)
    metrics.start_timer()

    try:
        yield metrics
    except Exception as e:
        metrics.record_error(e)
        raise
    finally:
        metrics.stop_timer()
        results_file = metrics.save_results()
        print(f"\nPerformance test results saved to: {results_file}")


@pytest.fixture(scope="session")
def perf_test_config() -> Dict[str, Any]:
    """Load performance test configuration."""
    config_path = (
        settings.BASE_DIR / "tests" / "performance" / "config" / "perf_config.json"
    )
    if config_path.exists():
        with open(config_path) as f:
            return {**PERF_TEST_CONFIG, **json.load(f)}
    return PERF_TEST_CONFIG


def pytest_addoption(parser):
    """Add command line options for performance tests."""
    parser.addoption(
        "--perf-test", action="store_true", default=False, help="Run performance tests"
    )
    parser.addoption(
        "--perf-config",
        type=str,
        default=None,
        help="Path to performance test configuration file",
    )


def pytest_configure(config):
    """Configure pytest for performance testing."""
    config.addinivalue_line("markers", "performance: mark test as a performance test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    if not config.getoption("--perf-test"):
        skip_perf = pytest.mark.skip(reason="Performance tests not requested")
        for item in items:
            if "performance" in item.keywords:
                item.add_marker(skip_perf)
