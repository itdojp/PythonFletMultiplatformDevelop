""
Performance testing utilities.

This module provides utility functions and classes for performance testing,
including load generation, metrics collection, and result analysis.
"""

from typing import Dict, Any, List, Optional, Callable, Union
import time
import random
import asyncio
import statistics
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial
import json
from pathlib import Path

import aiohttp
import psutil
import numpy as np
from tqdm import tqdm


class LoadGenerator:
    """Generate load for performance testing."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        max_workers: int = 100,
        timeout: int = 30,
    ):
        """Initialize the load generator.

        Args:
            base_url: Base URL of the API to test
            max_workers: Maximum number of concurrent workers
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.max_workers = max_workers
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = None

    async def __aenter__(self):
        """Create an aiohttp session."""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()

    async def make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request and return timing information.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (e.g., "/api/users")
            params: Query parameters
            json_data: JSON request body
            headers: HTTP headers

        Returns:
            Dict containing response data and timing information
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use 'async with LoadGenerator()'")

        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        status_code = None
        error = None

        try:
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers,
            ) as response:
                status_code = response.status
                response_data = await response.json()
                response_time = time.time() - start_time

                return {
                    "status_code": status_code,
                    "response_time": response_time,
                    "data": response_data,
                    "success": 200 <= status_code < 300,
                    "error": None,
                }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "status_code": status_code,
                "response_time": response_time,
                "data": None,
                "success": False,
                "error": str(e),
            }

    async def run_load_test(
        self,
        method: str,
        endpoint: str,
        num_requests: int,
        params: Optional[Dict] = None,
        json_data: Optional[Union[Dict, Callable]] = None,
        headers: Optional[Dict] = None,
        progress: bool = True,
    ) -> Dict[str, Any]:
        """Run a load test with multiple concurrent requests.

        Args:
            method: HTTP method
            endpoint: API endpoint
            num_requests: Number of requests to make
            params: Query parameters (can be a function that takes an index)
            json_data: JSON request body (can be a function that takes an index)
            headers: HTTP headers
            progress: Whether to show a progress bar

        Returns:
            Aggregated test results
        """
        results = []
        semaphore = asyncio.Semaphore(self.max_workers)

        async def make_request_with_semaphore(index: int):
            async with semaphore:
                # Generate dynamic parameters if callable
                req_params = params(index) if callable(params) else params
                req_json = json_data(index) if callable(json_data) else json_data

                result = await self.make_request(
                    method=method,
                    endpoint=endpoint,
                    params=req_params,
                    json_data=req_json,
                    headers=headers,
                )
                return result

        # Run requests concurrently
        tasks = [make_request_with_semaphore(i) for i in range(num_requests)]

        if progress:
            print(f"Sending {num_requests} requests to {method} {endpoint}")
            with tqdm(total=num_requests) as pbar:
                for coro in asyncio.as_completed(tasks):
                    result = await coro
                    results.append(result)
                    pbar.update(1)
        else:
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        successful_requests = [r for r in results if r and r.get("success", False)]
        failed_requests = [r for r in results if not r or not r.get("success", True)]

        response_times = [r["response_time"] for r in results if r and "response_time" in r]

        return {
            "total_requests": num_requests,
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": len(successful_requests) / num_requests if num_requests > 0 else 0,
            "response_times": {
                "min": min(response_times, default=0),
                "max": max(response_times, default=0),
                "avg": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "p90": np.percentile(response_times, 90) if response_times else 0,
                "p95": np.percentile(response_times, 95) if response_times else 0,
                "p99": np.percentile(response_times, 99) if response_times else 0,
            },
            "status_codes": {
                str(r["status_code"]): sum(1 for req in results if req and req.get("status_code") == r["status_code"])
                for r in results
                if r and "status_code" in r
            },
            "errors": [r["error"] for r in results if r and "error" in r and r["error"] is not None],
        }


def analyze_performance_results(results_dir: Union[str, Path]) -> Dict[str, Any]:
    """Analyze performance test results from JSON files.

    Args:
        results_dir: Directory containing performance test result JSON files

    Returns:
        Aggregated analysis of all test results
    """
    results_dir = Path(results_dir)
    if not results_dir.exists() or not results_dir.is_dir():
        raise ValueError(f"Results directory not found: {results_dir}")

    result_files = list(results_dir.glob("*.json"))
    if not result_files:
        return {"message": "No result files found"}

    all_results = []

    for result_file in result_files:
        try:
            with open(result_file, "r") as f:
                result_data = json.load(f)
                all_results.append(result_data)
        except Exception as e:
            print(f"Error loading result file {result_file}: {e}")

    if not all_results:
        return {"message": "No valid result data found"}

    # Aggregate metrics
    durations = [r.get("duration_seconds", 0) for r in all_results]
    test_metrics = [r.get("test_metrics", {}) for r in all_results]

    # Calculate statistics
    return {
        "total_tests": len(all_results),
        "avg_duration_seconds": statistics.mean(durations) if durations else 0,
        "min_duration_seconds": min(durations, default=0),
        "max_duration_seconds": max(durations, default=0),
        "tests_by_status": {
            "success": sum(1 for r in all_results if not r.get("errors")),
            "failed": sum(1 for r in all_results if r.get("errors")),
        },
        "common_errors": statistics.mode(
            [e["message"] for r in all_results for e in r.get("errors", [])]
        ) if any(r.get("errors") for r in all_results) else "No common errors",
        "test_metrics_summary": {
            # Add more specific metric summaries as needed
        },
    }
