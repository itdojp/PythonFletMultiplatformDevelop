"""
Performance benchmark configurations for the application.
"""

from typing import Any, Dict

# Performance thresholds (in milliseconds)
RESPONSE_TIME_THRESHOLDS = {
    "p50": 100,  # 50th percentile
    "p90": 200,  # 90th percentile
    "p95": 300,  # 95th percentile
    "p99": 500,  # 99th percentile
    "max": 1000,  # Maximum response time
}

# Error rate thresholds (in percentage)
ERROR_RATE_THRESHOLD = 0.1  # 0.1% maximum error rate

# Throughput thresholds (requests per second)
THROUGHPUT_THRESHOLDS = {
    "min": 10,  # Minimum requests per second
    "target": 50,  # Target requests per second
}

# Test scenarios with different load patterns
LOAD_TEST_SCENARIOS = {
    "smoke": {
        "users": 1,
        "spawn_rate": 1,
        "duration": "30s",
        "description": "Smoke test with minimal load",
    },
    "load": {
        "users": 10,
        "spawn_rate": 1,
        "duration": "1m",
        "description": "Normal load test",
    },
    "stress": {
        "users": 100,
        "spawn_rate": 10,
        "duration": "2m",
        "description": "Stress test with high load",
    },
    "soak": {
        "users": 20,
        "spawn_rate": 1,
        "duration": "30m",
        "description": "Soak test for stability",
    },
}


def get_scenario(name: str) -> Dict[str, Any]:
    """Get a test scenario by name.

    Args:
        name: Name of the scenario

    Returns:
        Dictionary with scenario configuration

    Raises:
        ValueError: If the scenario doesn't exist
    """
    if name not in LOAD_TEST_SCENARIOS:
        raise ValueError(f"Unknown scenario: {name}")
    return LOAD_TEST_SCENARIOS[name]


def get_all_scenarios() -> Dict[str, Dict[str, Any]]:
    """Get all available test scenarios.

    Returns:
        Dictionary of all test scenarios
    """
    return LOAD_TEST_SCENARIOS
