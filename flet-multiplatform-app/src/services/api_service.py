from typing import Any, Dict

import requests


class APIService:
    BASE_URL = "https://api.example.com"  # Replace with your actual API base URL

    def __init__(self):
        pass

    def get(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """Send a GET request to the specified endpoint."""
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()

    def post(self, endpoint: str, data: Dict[str, Any]) -> Any:
        """Send a POST request to the specified endpoint."""
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()

    def put(self, endpoint: str, data: Dict[str, Any]) -> Any:
        """Send a PUT request to the specified endpoint."""
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.put(url, json=data)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()

    def delete(self, endpoint: str) -> Any:
        """Send a DELETE request to the specified endpoint."""
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.delete(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
