"""
A simple performance test script to verify the testing setup.
"""

import time

import pytest
from locust import HttpUser, between, task


class SimpleTestUser(HttpUser):
    """Simple test user that makes requests to the API."""

    wait_time = between(1, 3)

    @task
    def hello_world(self):
        """Test the root endpoint."""
        self.client.get("/")


def test_simple_performance():
    """Simple test to verify the testing setup."""
    # This is a placeholder test that will always pass
    # The actual performance testing will be done by Locust
    assert True
