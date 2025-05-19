#!/usr/bin/env python3
"""
Generate sample performance metrics for testing.

This script creates sample baseline and current metrics files
that can be used to test the performance regression checker.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict


def generate_sample_metrics(
    base_value: float, variation: float = 0.1
) -> Dict[str, Any]:
    """Generate sample performance metrics with some random variation.

    Args:
        base_value: Base value for the metrics
        variation: Maximum variation (as a fraction of base_value)

    Returns:
        Dictionary containing sample metrics
    """

    # Add some random variation to the base value
    def with_variation(value: float) -> float:
        return value * (1 + random.uniform(-variation, variation))

    # Generate timestamps for the last 24 hours
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    timestamps = [
        (start_time + timedelta(minutes=30 * i)).isoformat() + "Z"
        for i in range(48)  # 48 * 30 minutes = 24 hours
    ]

    # Generate time series data
    time_series = {
        "response_time": [with_variation(base_value) for _ in range(48)],
        "throughput": [with_variation(100) for _ in range(48)],
        "error_rate": [random.uniform(0, 0.02) for _ in range(48)],
        "timestamps": timestamps,
    }

    # Generate summary statistics
    return {
        "metadata": {
            "test_name": "sample_performance_test",
            "start_time": start_time.isoformat() + "Z",
            "end_time": end_time.isoformat() + "Z",
            "duration_seconds": 86400,  # 24 hours
            "version": "1.0.0",
        },
        "summary": {
            "response_time_ms": {
                "min": with_variation(base_value * 0.8),
                "max": with_variation(base_value * 1.2),
                "mean": with_variation(base_value),
                "p50": with_variation(base_value),
                "p90": with_variation(base_value * 1.1),
                "p95": with_variation(base_value * 1.15),
                "p99": with_variation(base_value * 1.2),
            },
            "throughput_rps": {
                "min": with_variation(80),
                "max": with_variation(120),
                "mean": with_variation(100),
            },
            "error_rate": {
                "total_requests": int(with_variation(100000)),
                "failed_requests": int(with_variation(500)),
                "error_rate": with_variation(0.005),
            },
            "concurrent_users": {"min": 1, "max": 100, "average": 50},
        },
        "time_series": time_series,
        "endpoints": {
            "/api/users": {
                "response_time_ms": with_variation(base_value * 0.9),
                "requests": int(with_variation(20000)),
                "errors": int(with_variation(100)),
            },
            "/api/items": {
                "response_time_ms": with_variation(base_value * 1.1),
                "requests": int(with_variation(30000)),
                "errors": int(with_variation(150)),
            },
            "/api/orders": {
                "response_time_ms": with_variation(base_value * 1.2),
                "requests": int(with_variation(15000)),
                "errors": int(with_variation(75)),
            },
            "/api/search": {
                "response_time_ms": with_variation(base_value * 0.8),
                "requests": int(with_variation(35000)),
                "errors": int(with_variation(175)),
            },
        },
    }


def main():
    """Generate sample metrics files."""
    output_dir = Path("test_data/performance")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate baseline metrics (good performance)
    baseline_metrics = generate_sample_metrics(100)  # 100ms response time
    with open(output_dir / "baseline_metrics.json", "w") as f:
        json.dump(baseline_metrics, f, indent=2)

    # Generate current metrics (slightly worse performance)
    current_metrics = generate_sample_metrics(120)  # 120ms response time (20% slower)
    with open(output_dir / "current_metrics.json", "w") as f:
        json.dump(current_metrics, f, indent=2)

    print(f"Generated sample metrics in {output_dir.absolute()}")
    print("Run the following command to check for regressions:")
    print(
        f"python scripts/check_performance.py --baseline {output_dir}/baseline_metrics.json --current {output_dir}/current_metrics.json --threshold 0.1"
    )


if __name__ == "__main__":
    main()
