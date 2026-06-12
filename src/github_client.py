from __future__ import annotations

import base64
import logging
from typing import Any

import requests

from .config import Settings


LOGGER = logging.getLogger(__name__)


class GitHubClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "github-hot-daily",
            }
        )
        if settings.github_token:
            self.session.headers["Authorization"] = f"Bearer {settings.github_token}"

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        url = f"{self.settings.github_api_url}{path}"
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.settings.request_timeout_seconds,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            LOGGER.warning("GitHub request failed: %s params=%s error=%s", path, params, exc)
            return None
        except ValueError as exc:
            LOGGER.warning("GitHub response is not JSON: %s error=%s", path, exc)
            return None

    def search_repositories(self, query: str, per_page: int = 20) -> list[dict[str, Any]]:
        payload = self.get_json(
            "/search/repositories",
            params={
                "q": query,
                "sort": "updated",
                "order": "desc",
                "per_page": min(per_page, 100),
            },
        )
        if not payload:
            return []
        return payload.get("items", [])

    def fetch_readme_text(self, owner: str, repo: str) -> str:
        payload = self.get_json(f"/repos/{owner}/{repo}/readme")
        if not payload:
            return ""
        encoded = payload.get("content")
        if not encoded:
            return ""
        try:
            return base64.b64decode(encoded, validate=False).decode("utf-8", errors="replace")
        except (ValueError, TypeError) as exc:
            LOGGER.warning("README decode failed: %s/%s error=%s", owner, repo, exc)
            return ""

