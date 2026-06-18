from __future__ import annotations

from html.parser import HTMLParser
from typing import Any

from .config import Settings
from .github_client import GitHubClient
from .readme_parser import extract_readme_images, summarize_readme


TRENDING_URL = "https://github.com/trending?since=daily"


class TrendingRepoParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_h2 = False
        self.h2_depth = 0
        self.repo_names: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "h2":
            self.in_h2 = True
            self.h2_depth = 1
            return
        if self.in_h2:
            self.h2_depth += 1
        if tag != "a" or not self.in_h2:
            return

        attrs_dict = dict(attrs)
        href = attrs_dict.get("href", "").strip("/")
        parts = href.split("/")
        if len(parts) != 2:
            return
        owner, repo = parts
        if owner in {"apps", "features", "marketplace", "sponsors", "topics", "trending"}:
            return
        repo_name = f"{owner}/{repo}"
        if repo_name not in self.repo_names:
            self.repo_names.append(repo_name)

    def handle_endtag(self, tag: str) -> None:
        if self.in_h2:
            self.h2_depth -= 1
            if tag == "h2" or self.h2_depth <= 0:
                self.in_h2 = False
                self.h2_depth = 0


def parse_trending_repo_names(html: str, limit: int = 10) -> list[str]:
    parser = TrendingRepoParser()
    parser.feed(html)
    return parser.repo_names[:limit]


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


def minimal_trending_project(repo_name: str, candidate_reason: str) -> dict[str, Any]:
    owner_name, _, name = repo_name.partition("/")
    return normalize_project(
        {
            "full_name": repo_name,
            "name": name,
            "owner": {"login": owner_name, "avatar_url": ""},
            "html_url": f"https://github.com/{repo_name}",
            "description": "",
            "stargazers_count": 0,
            "forks_count": 0,
            "watchers_count": 0,
            "open_issues_count": 0,
            "language": "",
            "topics": [],
            "created_at": "",
            "updated_at": "",
            "pushed_at": "",
            "license": None,
        },
        readme_text="",
        candidate_reason=candidate_reason,
    )


def fetch_candidate_projects(client: GitHubClient, settings: Settings) -> list[dict[str, Any]]:
    seen: set[str] = set()
    candidates: list[dict[str, Any]] = []

    html = client.get_text_url(TRENDING_URL)
    repo_names = parse_trending_repo_names(html, limit=max(settings.candidate_max * 2, 10))

    for trending_rank, repo_name in enumerate(repo_names, start=1):
        if len(candidates) >= settings.candidate_max:
            break
        if repo_name in seen:
            continue
        seen.add(repo_name)

        owner, name = repo_name.split("/", 1)
        candidate_reason = f"GitHub Trending 日榜第 {trending_rank} 名"

        raw = client.fetch_repository(owner, name)
        if not raw:
            candidates.append(minimal_trending_project(repo_name, candidate_reason))
            continue

        readme_text = client.fetch_readme_text(owner, name)
        candidates.append(normalize_project(raw, readme_text, candidate_reason=candidate_reason))

    return candidates
