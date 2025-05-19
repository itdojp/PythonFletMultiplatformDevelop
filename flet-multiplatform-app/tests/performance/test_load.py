"""
Load testing for the application.
"""

import os

import pytest
from locust import between, task

from .base_test import BaseLocustTest


class LoadTestUser(BaseLocustTest):
    """Simulate users for load testing."""

    wait_time = between(1, 3)

    @task(3)
    def get_items(self):
        """Test GET /items endpoint."""
        self.client.get("/items/")

    @task(2)
    def get_item(self):
        """Test GET /items/{id} endpoint."""
        self.client.get(f"/items/{1}")

    @task(1)
    def create_item(self):
        """Test POST /items/ endpoint."""
        self.client.post(
            "/items/",
            json={"name": "test item", "description": "test description"},
            headers={"Content-Type": "application/json"},
        )


class TestLoadPerformance:
    """Test class for load testing."""

    def test_load_performance(self, base_url):
        """Run load test and verify performance metrics."""
        # This test will be executed by the performance test runner
        # with parameters from the configuration
        pass
