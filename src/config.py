from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output"
HISTORY_PATH = OUTPUT_DIR / "history.json"
PROJECTS_PATH = OUTPUT_DIR / "projects.json"
DAILY_RAW_PATH = OUTPUT_DIR / "daily_raw.md"
CHATGPT_PROMPT_PATH = OUTPUT_DIR / "chatgpt_prompt.txt"


FOCUS_KEYWORDS = [
    "ai",
    "llm",
    "agent",
    "mcp",
    "rag",
    "python",
    "developer tools",
    "productivity",
    "automation",
    "frontend",
    "web",
    "security",
    "data",
    "open source models",
    "cli",
]

@dataclass(frozen=True)
class Settings:
    github_token: str | None
    github_api_url: str
    request_timeout_seconds: int
    candidate_min: int
    candidate_max: int
    history_days: int


def load_settings() -> Settings:
    return Settings(
        github_token=os.getenv("GITHUB_TOKEN"),
        github_api_url=os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/"),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20")),
        candidate_min=int(os.getenv("CANDIDATE_MIN", "10")),
        candidate_max=int(os.getenv("CANDIDATE_MAX", "10")),
        history_days=int(os.getenv("HISTORY_DAYS", "30")),
    )
