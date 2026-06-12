from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from .config import FOCUS_KEYWORDS
from .history_store import History, get_star_delta
from .readme_parser import readme_quality_score


def parse_github_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def recency_score(value: str | None, half_life_days: float) -> float:
    parsed = parse_github_datetime(value)
    if not parsed:
        return 0.0
    age_days = max((datetime.now(timezone.utc) - parsed).total_seconds() / 86400, 0)
    return round(math.exp(-age_days / half_life_days), 4)


def keyword_score(project: dict[str, Any]) -> float:
    haystack = " ".join(
        [
            project.get("description") or "",
            project.get("readme_text") or "",
            " ".join(project.get("topics") or []),
            project.get("language") or "",
        ]
    ).lower()
    matches = [keyword for keyword in FOCUS_KEYWORDS if keyword.lower() in haystack]
    return round(min(len(matches) / 5, 1.0), 4)


def calculate_hot_score(project: dict[str, Any], history: History | None = None) -> tuple[float, dict[str, float | int]]:
    history = history or {}
    stars = int(project.get("stargazers_count") or 0)
    forks = int(project.get("forks_count") or 0)
    star_delta = int(project.get("star_delta") or get_star_delta(project["repo_name"], stars, history))

    star_score = min(math.log10(stars + 1) / 5, 1.0)
    fork_score = min(math.log10(forks + 1) / 4, 1.0)
    created_score = recency_score(project.get("created_at"), half_life_days=180)
    pushed_score = recency_score(project.get("pushed_at"), half_life_days=21)
    keyword_match_score = keyword_score(project)
    quality_score = readme_quality_score(project.get("readme_text") or "")
    growth_score = min(math.log1p(star_delta) / math.log(501), 1.0)

    detail = {
        "star_score": round(star_score, 4),
        "fork_score": round(fork_score, 4),
        "created_score": created_score,
        "pushed_score": pushed_score,
        "keyword_score": keyword_match_score,
        "readme_quality_score": quality_score,
        "star_delta": star_delta,
        "growth_score": round(growth_score, 4),
    }
    score = (
        25 * star_score
        + 10 * fork_score
        + 12 * created_score
        + 16 * pushed_score
        + 14 * keyword_match_score
        + 10 * quality_score
        + 13 * growth_score
    )
    return round(score, 2), detail


def rank_projects(projects: list[dict[str, Any]], history: History | None = None) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for project in projects:
        score, detail = calculate_hot_score(project, history)
        ranked.append({**project, "star_delta": detail["star_delta"], "hot_score": score, "hot_score_detail": detail})
    return sorted(ranked, key=lambda item: item["hot_score"], reverse=True)

