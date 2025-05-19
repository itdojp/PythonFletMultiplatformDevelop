"""
API Performance Tests

This module contains performance tests for the API endpoints.
"""

import json
import logging
import os
import time

from locust import HttpUser, between, events, task
from locust.runners import MasterRunner, WorkerRunner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "test_data")

# API endpoints
API_ENDPOINTS = {
    "get_items": "/api/items/",
    "get_item": "/api/items/{id}",
    "create_item": "/api/items/",
    "update_item": "/api/items/{id}",
    "delete_item": "/api/items/{id}",
}


# Test data
class TestData:
    """Load and manage test data."""

    _instance = None
    _data = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TestData, cls).__new__(cls)
            cls._load_test_data()
        return cls._instance

    @classmethod
    def _load_test_data(cls):
        """Load test data from JSON files."""
        test_data_files = {
            "items": "test_items.json",
            "users": "test_users.json",
        }

        for data_type, filename in test_data_files.items():
            filepath = os.path.join(TEST_DATA_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    cls._data[data_type] = json.load(f)
                logger.info(f"Loaded test data from {filepath}")
            except FileNotFoundError:
                logger.warning(f"Test data file not found: {filepath}")
                cls._data[data_type] = []

    @classmethod
    def get_test_data(cls, data_type: str, index: int = 0, default=None):
        """Get test data by type and index."""
        data = cls._data.get(data_type, [])
        if not data:
            return default
        return data[index % len(data)] if data else default


# Custom event hooks
def setup_test_environment(environment):
    """Setup test environment."""
    if not isinstance(environment.runner, WorkerRunner):
        logger.info("Setting up test environment...")
        # Preload test data
        TestData()


def teardown_test_environment(environment):
    """Teardown test environment."""
    if not isinstance(environment.runner, WorkerRunner):
        logger.info("Tearing down test environment...")


# Register event hooks
events.test_start.add_listener(setup_test_environment)
events.test_stop.add_listener(teardown_test_environment)


class ApiUser(HttpUser):
    """Simulate API users with different behaviors."""

    wait_time = between(1, 3)  # Wait between 1-3 seconds between tasks
    host = "http://localhost:8000"  # Base URL for the API

    def on_start(self):
        """Called when a user starts."""
        self.client.verify = False  # Disable SSL verification for testing
        self.test_data = TestData()

    @task(3)  # Higher weight means more frequent execution
    def get_items(self):
        """Test getting a list of items."""
        with self.client.get(
            API_ENDPOINTS["get_items"], name="Get Items", catch_response=True
        ) as response:
            self._validate_response(response)

    @task(2)
    def get_item(self):
        """Test getting a single item."""
        item = self.test_data.get_test_data("items")
        if not item:
            return

        with self.client.get(
            API_ENDPOINTS["get_item"].format(id=item.get("id", 1)),
            name="Get Item",
            catch_response=True,
        ) as response:
            self._validate_response(response)

    @task(1)
    def create_item(self):
        """Test creating an item."""
        item_data = self.test_data.get_test_data("items")
        if not item_data:
            return

        with self.client.post(
            API_ENDPOINTS["create_item"],
            json=item_data,
            name="Create Item",
            catch_response=True,
        ) as response:
            self._validate_response(response, expected_codes=[201])

    def _validate_response(self, response, expected_codes=None):
        """Validate the API response."""
        if expected_codes is None:
            expected_codes = [200]

        if response.status_code not in expected_codes:
            response.failure(
                f"Unexpected status code: {response.status_code}. "
                f"Expected: {expected_codes}"
            )
        else:
            response.success()


# Example of a more specific test scenario
class ReadHeavyUser(ApiUser):
    """Simulate a user that mostly reads data."""

    @task(5)
    def read_operations(self):
        """Perform read operations."""
        self.get_items()
        self.get_item()

    @task(1)
    def write_operations(self):
        """Perform write operations."""
        self.create_item()


class WriteHeavyUser(ApiUser):
    """Simulate a user that mostly writes data."""

    @task(1)
    def read_operations(self):
        """Perform read operations."""
        self.get_items()
        self.get_item()

    @task(5)
    def write_operations(self):
        """Perform write operations."""
        self.create_item()


# Add this to run the test directly for debugging
if __name__ == "__main__":
    import os

    os.system("locust -f test_api_performance.py")
