"""Pond API client."""

import os
from typing import Any

import requests


class PondClient:
    """Client for the Pond REST API."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
    ):
        self.base_url = (base_url or os.environ.get("POND_BASE_URL", "")).rstrip("/")
        self.api_key = api_key or os.environ.get("POND_API_KEY", "")

        if not self.base_url:
            raise ValueError(
                "POND_BASE_URL not set. "
                "Set it in your environment or pass base_url."
            )
        if not self.api_key:
            raise ValueError(
                "POND_API_KEY not set. "
                "Set it in your environment or pass api_key."
            )

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    def _post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make a POST request to the API."""
        url = f"{self.base_url}/api/v1/{endpoint}"
        response = requests.post(url, json=data, headers=self._headers(), timeout=60)
        response.raise_for_status()
        return response.json()

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a GET request to the API."""
        url = f"{self.base_url}/api/v1/{endpoint}"
        response = requests.get(url, params=params, headers=self._headers(), timeout=60)
        response.raise_for_status()
        return response.json()

    def _get_no_auth(self, endpoint: str) -> dict[str, Any]:
        """Make a GET request without auth (for health check)."""
        url = f"{self.base_url}/api/v1/{endpoint}"
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.json()

    def store(self, content: str, tags: list[str] | None = None) -> dict[str, Any]:
        """Store a memory."""
        data = {"content": content}
        if tags:
            data["tags"] = tags
        return self._post("store", data)

    def search(self, query: str, limit: int = 10) -> dict[str, Any]:
        """Search memories."""
        return self._post("search", {"query": query, "limit": limit})

    def recent(self, hours: float = 24, limit: int = 10) -> dict[str, Any]:
        """Get recent memories."""
        return self._post("recent", {"hours": hours, "limit": limit})

    def init(self) -> dict[str, Any]:
        """Initialize context."""
        return self._post("init", {})

    def health(self) -> dict[str, Any]:
        """Check system health."""
        return self._get_no_auth("health")
