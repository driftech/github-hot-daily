from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .config import NEGATIVE_KEYWORDS, QUERY_KEYWORDS, Settings
from .github_client import GitHubClient
from .readme_parser import clean_markdown_text, extract_readme_images, summarize_readme


def build_search_queries(now: datetime | None = None) -> list[str]:
    now = now or datetime.now(timezone.utc)
    recent_push = (now - timedelta(days=14)).date().isoformat()
    recent_create = (now - timedelta(days=180)).date().isoformat()
    base = "fork:false archived:false"
    return [
        f"{keyword} {base} pushed:>={recent_push} stars:>50"
        for keyword in QUERY_KEYWORDS
    ] + [
        f"topic:{keyword.lower()} {base} created:>={recent_create} stars:>20"
        for keyword in QUERY_KEYWORDS
        if " " not in keyword
    ]


def has_negative_signal(project: dict[str, Any], readme_text: str) -> bool:
    haystack = " ".join(
        [
            project.get("name") or "",
            project.get("full_name") or "",
            project.get("description") or "",
            " ".join(project.get("topics") or []),
            readme_text[:3000],
        ]
    ).lower()
    return any(keyword.lower() in haystack for keyword in NEGATIVE_KEYWORDS)


def is_low_information(project: dict[str, Any], readme_text: str) -> bool:
    description = (project.get("description") or "").strip()
    cleaned_readme = clean_markdown_text(readme_text)
    return not description and len(cleaned_readme) < 300


def normalize_project(raw: dict[str, Any], readme_text: str, candidate_reason: str) -> dict[str, Any]:
    owner = raw.get("owner") or {}
    license_data = raw.get("license") or {}
    repo_name = raw.get("full_name") or f"{owner.get('login', '')}/{raw.get('name', '')}"
    return {
        "repo_name": repo_name,
        "owner_name": owner.get("login") or "",
        "html_url": raw.get("html_url") or "",
        "description": raw.get("description") or "",
        "stargazers_count": raw.get("stargazers_count") or 0,
        "forks_count": raw.get("forks_count") or 0,
        "watchers_count": raw.get("watchers_count") or 0,
        "open_issues_count": raw.get("open_issues_count") or 0,
        "language": raw.get("language") or "",
        "topics": raw.get("topics") or [],
        "created_at": raw.get("created_at") or "",
        "updated_at": raw.get("updated_at") or "",
        "pushed_at": raw.get("pushed_at") or "",
        "license": license_data.get("spdx_id") or license_data.get("name") or "",
        "readme_text": readme_text,
        "readme_summary": summarize_readme(readme_text),
        "avatar_url": owner.get("avatar_url") or "",
        "readme_images": extract_readme_images(readme_text),
        "candidate_reason": candidate_reason,
        "hot_score": 0,
        "hot_score_detail": {},
    }


def fetch_candidate_projects(client: GitHubClient, settings: Settings) -> list[dict[str, Any]]:
    seen: set[str] = set()
    candidates: list[dict[str, Any]] = []
    queries = build_search_queries()

    for query in queries:
        if len(candidates) >= settings.candidate_max * 3:
            break
        for raw in client.search_repositories(query, per_page=15):
            repo_name = raw.get("full_name")
            if not repo_name or repo_name in seen:
                continue
            seen.add(repo_name)
            if raw.get("fork") or raw.get("archived") or raw.get("disabled"):
                continue

            owner = (raw.get("owner") or {}).get("login")
            name = raw.get("name")
            readme_text = client.fetch_readme_text(owner, name) if owner and name else ""
            if is_low_information(raw, readme_text):
                continue
            if has_negative_signal(raw, readme_text):
                continue

            candidates.append(normalize_project(raw, readme_text, candidate_reason=f"匹配 GitHub 搜索条件：{query}"))

    return candidates

