#!/usr/bin/env python3
"""
Performance Test Runner

This script runs performance tests using Locust and generates reports.
"""

import argparse
import asyncio
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from locust import events, runners
from locust.env import Environment
from locust.log import setup_logging
from locust.runners import MasterRunner, WorkerRunner

# Configure logging
setup_logging("INFO", None)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "base_url": "http://localhost:8000",
    "scenarios": {
        "smoke": {
            "description": "Quick smoke test",
            "users": 1,
            "spawn_rate": 1,
            "run_time": "30s",
            "thresholds": {
                "response_time_p95": 1000,
                "error_rate": 0.01,
                "throughput": 5,
            },
        }
    },
    "locust": {
        "host": "http://localhost:8000",
        "web_port": 8089,
        "headless": True,
        "loglevel": "INFO",
    },
}


class PerformanceTestRunner:
    """Run performance tests and generate reports."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the test runner.

        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.results_dir = Path("results")
        self.reports_dir = Path("reports/performance")
        self._setup_directories()
        self._setup_logging()
        self.environment = None
        self.test_results = {}

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults.

        Args:
            config_path: Path to the configuration file

        Returns:
            Dictionary with configuration
        """
        if not config_path:
            return DEFAULT_CONFIG

        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f) or {}

            # Merge with default config
            merged_config = DEFAULT_CONFIG.copy()
            self._merge_dict(merged_config, config)
            return merged_config

        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return DEFAULT_CONFIG

    def _merge_dict(self, base: Dict, update: Dict) -> None:
        """Recursively merge two dictionaries."""
        for k, v in update.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._merge_dict(base[k], v)
            else:
                base[k] = v

    def _setup_directories(self) -> None:
        """Create necessary directories."""
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self) -> None:
        """Configure logging."""
        log_file = self.reports_dir / "performance_tests.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)

    async def run_test(self, test_file: str, scenario: str) -> Dict[str, Any]:
        """Run a single performance test.

        Args:
            test_file: Path to the test file
            scenario: Name of the scenario to run

        Returns:
            Dictionary with test results
        """
        if scenario not in self.config.get("scenarios", {}):
            raise ValueError(f"Unknown scenario: {scenario}")

        scenario_config = self.config["scenarios"][scenario]
        locust_config = self.config.get("locust", {})

        # Set up Locust environment
        self.environment = Environment(
            user_classes=[],
            host=locust_config.get("host", "http://localhost:8000"),
            events=events,
        )

        # Register event handlers
        self._register_event_handlers(scenario)

        # Start Locust
        runner = self.environment.create_local_runner()

        try:
            # Start the test
            logger.info(f"Starting performance test: {scenario}")

            # Run the test
            await runner.start(
                user_count=scenario_config["users"],
                spawn_rate=scenario_config["spawn_rate"],
                wait=True,
            )

            # Wait for the test to complete
            await asyncio.sleep(self._parse_duration(scenario_config["run_time"]))

            # Stop the test
            await runner.stop()

            # Generate report
            report = self._generate_report(scenario)

            logger.info(f"Performance test completed: {scenario}")
            return report

        except Exception as e:
            logger.error(f"Error during performance test: {e}")
            raise

    def _register_event_handlers(self, scenario: str) -> None:
        """Register event handlers for Locust."""
        if not self.environment:
            return

        # Store test start time
        test_start_time = time.time()

        @self.environment.events.test_start.add_listener
        def on_test_start(environment, **kwargs):
            logger.info(f"Test started: {scenario}")

        @self.environment.events.test_stop.add_listener
        def on_test_stop(environment, **kwargs):
            logger.info(f"Test stopped: {scenario}")

        @self.environment.events.request.add_listener
        def on_request(
            request_type,
            name,
            response_time,
            response_length,
            exception,
            context,
            **kwargs,
        ):
            if exception:
                logger.warning(f"Request failed: {name} - {exception}")

    def _parse_duration(self, duration_str: str) -> int:
        """Parse a duration string (e.g., '30s', '5m') into seconds."""
        if duration_str.endswith("s"):
            return int(duration_str[:-1])
        elif duration_str.endswith("m"):
            return int(duration_str[:-1]) * 60
        elif duration_str.endswith("h"):
            return int(duration_str[:-1]) * 3600
        else:
            return int(duration_str)

    def _generate_report(self, scenario: str) -> Dict[str, Any]:
        """Generate a test report."""
        if not self.environment or not self.environment.runner:
            return {}

        stats = self.environment.runner.stats
        total_requests = sum(stat.num_requests for stat in stats.values())
        total_failures = sum(stat.num_failures for stat in stats.values())

        # Calculate response time percentiles
        response_times = []
        for stat in stats.values():
            if hasattr(stat, "response_times"):
                response_times.extend([t for t in stat.response_times.values()])

        report = {
            "scenario": scenario,
            "timestamp": datetime.now().isoformat(),
            "total_requests": total_requests,
            "total_failures": total_failures,
            "failure_rate": total_failures / max(1, total_requests),
            "response_time": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "median": (
                    sorted(response_times)[len(response_times) // 2]
                    if response_times
                    else 0
                ),
                "p95": (
                    sorted(response_times)[int(len(response_times) * 0.95)]
                    if response_times
                    else 0
                ),
                "p99": (
                    sorted(response_times)[int(len(response_times) * 0.99)]
                    if response_times
                    else 0
                ),
            },
            "rps": total_requests
            / max(
                1, self._parse_duration(self.config["scenarios"][scenario]["run_time"])
            ),
        }

        # Save report
        report_file = self.reports_dir / f"{scenario}_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report generated: {report_file}")
        return report


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run performance tests")
    parser.add_argument(
        "--config",
        type=str,
        default="tests/performance/config/performance_config.yaml",
        help="Path to the configuration file",
    )
    parser.add_argument(
        "--scenario", type=str, default="smoke", help="Scenario to run (default: smoke)"
    )
    return parser.parse_args()


async def main():
    """Main function."""
    args = parse_args()

    try:
        # Initialize test runner
        runner = PerformanceTestRunner(args.config)

        # Run the test
        report = await runner.run_test(
            test_file="tests/performance/test_api_performance.py",
            scenario=args.scenario,
        )

        # Print summary
        print("\n=== Test Summary ===")
        print(f"Scenario: {report['scenario']}")
        print(f"Total Requests: {report['total_requests']}")
        print(
            f"Failures: {report['total_failures']} ({report['failure_rate']*100:.2f}%)"
        )
        print(f"RPS: {report['rps']:.2f}")
        print(f"Response Time (p95): {report['response_time']['p95']:.2f}ms")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
