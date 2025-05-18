#!/usr/bin/env python3
"""
Performance Test Runner

This script runs all performance tests and generates a report.
"""

import argparse
import asyncio
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import uvicorn
from fastapi import FastAPI

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Configure paths
REPORTS_DIR = PROJECT_ROOT / "reports" / "performance"
RESULTS_DIR = PROJECT_ROOT / "test-results" / "performance"
TEST_DIR = PROJECT_ROOT / "tests" / "performance"

# Ensure directories exist
for directory in [REPORTS_DIR, RESULTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Test configuration
TEST_CONFIG = {
    "load_test": {
        "test_file": "test_load.py",
        "report_file": "load-test-results.xml",
        "metrics_file": "load-metrics.json"
    },
    "stress_test": {
        "test_file": "test_stress.py",
        "report_file": "stress-test-results.xml",
        "metrics_file": "stress-metrics.json"
    },
    "endurance_test": {
        "test_file": "test_endurance.py",
        "report_file": "endurance-test-results.xml",
        "metrics_file": "endurance-metrics.json"
    },
    "scalability_test": {
        "test_file": "test_scalability.py",
        "report_file": "scalability-test-results.xml",
        "metrics_file": "scalability-metrics.json"
    }
}

class PerformanceTestRunner:
    """Run performance tests and generate reports."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the PerformanceTestRunner.

        Args:
            config_path: Optional path to a custom configuration file.
                       If not provided, uses the default config file.
        """
        self.config_path = config_path or (TEST_DIR / "config" / "perf_config.json")
        self.config = self._load_config()
        self.app_process = None
        self.test_results = {}
        self.start_time = time.time()

    async def start_application(self):
        """Start the FastAPI application in a separate process."""
        print("\n🚀 Starting application...")

        # Set environment variables
        env = os.environ.copy()
        env["APP_ENV"] = "test"
        env["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/test_db"
        env["PYTHONPATH"] = str(PROJECT_ROOT)  # Add project root to PYTHONPATH

        # Start the application
        self.app_process = subprocess.Popen(
            [
                "uvicorn",
                "src.backend.app.main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"  # Enable auto-reload for development
            ],
            env=env,
            cwd=str(PROJECT_ROOT),  # Set working directory to project root
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait for the application to start
        max_attempts = 10
        for _ in range(max_attempts):
            try:
                # Try to connect to the application
                import requests
                response = requests.get("http://localhost:8000/health")
                if response.status_code == 200:
                    print("✅ Application started successfully")
                    return
            except Exception as e:
                print(f"Waiting for application to start... ({e})")
                await asyncio.sleep(2)
        
        print("❌ Failed to start application")
        self._log_process_output()
        raise RuntimeError("Failed to start application")

    async def stop_application(self):
        """Stop the FastAPI application."""
        if self.app_process:
            print("\n🛑 Stopping application...")
            self.app_process.terminate()
            try:
                self.app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.app_process.kill()
            print("✅ Application stopped")

    def _load_config(self) -> dict:
        """Load and parse the performance test configuration.

        Returns:
            dict: The loaded configuration with environment variables resolved.
        """
        try:
            from src.backend.tests.performance.utils.config_loader import load_config
            return load_config(self.config_path)
        except ImportError:
            # Fallback to direct JSON loading if the module is not available
            with open(self.config_path, encoding='utf-8') as f:
                return json.load(f)

    def _get_test_config(self, test_type: str) -> dict:
        """Get configuration for a specific test type.

        Args:
            test_type: The type of test to get configuration for.

        Returns:
            dict: The test configuration.

        Raises:
            ValueError: If the test type is not found in the configuration.
        """
        if test_type not in self.config:
            raise ValueError(f"Unknown test type: {test_type}")
        return self.config[test_type]

    async def run_tests(self, test_type: str) -> Tuple[bool, str]:
        """Run a specific type of performance test.

        Args:
            test_type: Type of test to run (load_test, stress_test, etc.)

        Returns:
            Tuple[bool, str]: A tuple containing success status and output.
        """
        try:
            config = self._get_test_config(test_type)
            test_file = TEST_DIR / f"test_{test_type}.py"
            report_file = RESULTS_DIR / f"{test_type}_results.xml"
            metrics_file = RESULTS_DIR / f"{test_type}_metrics.json"

            # Ensure results directory exists
            RESULTS_DIR.mkdir(parents=True, exist_ok=True)

            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=test_env,
                cwd=str(PROJECT_ROOT),  # Set working directory to project root
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for the process to complete with a timeout
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=3600)  # 1 hour timeout
            except asyncio.TimeoutError:
                print(f"⚠️  {test_name} timed out after 1 hour")
                process.terminate()
                return False
            
            # Log the output
            if stdout:
                print(f"\n📝 {test_name} output:")
                print(stdout.decode())
            
            if process.returncode != 0:
                print(f"❌ {test_name} failed with return code {process.returncode}")
                if stderr:
                    print(f"STDERR: {stderr.decode()}")
                return False
                
            print(f"✅ {test_name} completed successfully")
            return True
            

            status = "PASSED" if success else "FAILED"
            print(f"✅ {test_type.replace('_', ' ').title()} {status}")

            return success, output

        except Exception as e:
            error_msg = f"❌ Error running {test_type}: {str(e)}"
            print(error_msg)
            return False, error_msg

    async def run_all_tests(self) -> bool:
        """Run all performance tests.

        Returns:
            bool: True if all tests passed, False otherwise.
        """
        all_success = True

        try:
            # Start the application
            await self.start_application()

            # Get the test execution order from config or use default
            test_order = self.config.get('test_order', [
                'load_test',
                'stress_test',
                'endurance_test',
                'scalability_test'
            ])

            # Run each test type in the specified order
            for test_type in test_order:
                if test_type in self.config:  # Only run tests that are configured
                    print(f"\n{'='*50}")
                    print(f"🚀 Starting {test_type.replace('_', ' ').title()}")
                    print(f"{'='*50}")

                    success, output = await self.run_tests(test_type)
                    if not success:
                        print(f"❌ {test_type} failed with output:")
                        print(output)
                        all_success = False
                    else:
                        print(f"✅ {test_type.replace('_', ' ').title()} completed successfully")

            return all_success

        except Exception as e:
            print(f"❌ Error running performance tests: {str(e)}")
            return False

        finally:
            # Ensure the application is stopped
            await self.stop_application()

    def generate_report(self) -> Path:
        """Generate a performance test report."""
        print("\n📊 Generating performance test report...")

        # Run the analyzer
        analyzer_script = PROJECT_ROOT / "tests" / "performance" / "analyze_results.py"
        report_path = REPORTS_DIR / "performance_report.html"

        try:
            subprocess.run(
                [sys.executable, str(analyzer_script)],
                check=True,
                cwd=PROJECT_ROOT
            )
            print(f"✅ Report generated: {report_path}")
            return report_path
        except subprocess.CalledProcessError as e:
            print(f"❌ Error generating report: {e}")
            return None

    def print_summary(self):
        """Print a summary of the test results."""
        print("\n" + "=" * 50)
        print("PERFORMANCE TEST SUMMARY")
        print("=" * 50)

        total_tests = len(TEST_CONFIG)
        passed_tests = sum(1 for r in self.test_results.values() if r["success"])
        failed_tests = total_tests - passed_tests

        print(f"\n📋 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏱️  Duration: {time.time() - self.start_time:.2f} seconds")

        if failed_tests > 0:
            print("\nFailed Tests:")
            for test_type, result in self.test_results.items():
                if not result["success"]:
                    print(f"- {test_type.replace('_', ' ').title()}")
                    print(f"  Output: {result['output'][-200:]}...")

        print("\n" + "=" * 50)


async def main():
    """Main function to run the performance tests."""
    parser = argparse.ArgumentParser(description="Run performance tests")
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to performance test configuration file"
    )
    parser.add_argument(
        "--test-type",
        type=str,
        choices=list(TEST_CONFIG.keys()) + ["all"],
        default="all",
        help="Type of test to run (default: all)"
    )
    args = parser.parse_args()

    # Configure paths
    config_path = Path(args.config) if args.config else None

    # Create the test runner
    runner = PerformanceTestRunner(config_path=config_path)

    try:
        if args.test_type == "all":
            # Run all tests
            success = await runner.run_all_tests()
        else:
            # Run a specific test
            await runner.start_application()
            success, _ = await runner.run_tests(args.test_type)
            await runner.stop_application()

        # Generate and display the report
        report_path = runner.generate_report()
        runner.print_summary()

        # Exit with appropriate status code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n🚨 Test execution interrupted by user")
        await runner.stop_application()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        await runner.stop_application()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
