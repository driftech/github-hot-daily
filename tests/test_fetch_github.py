from __future__ import annotations

from src.config import Settings
from src.fetch_github import fetch_candidate_projects, parse_trending_repo_names


def test_parse_trending_repo_names_reads_h2_repo_links_only() -> None:
    html = """
    <a href="/sponsors/example">Sponsor</a>
    <article>
      <h2><a href="/owner-one/repo-one">owner-one / repo-one</a></h2>
      <a href="/sponsors/freeCodeCamp">Sponsor</a>
    </article>
    <article>
      <h2><a href="/owner-two/repo-two">owner-two / repo-two</a></h2>
    </article>
    <article>
      <h2><a href="/apps/dependabot">Dependabot</a></h2>
    </article>
    """

    assert parse_trending_repo_names(html, limit=10) == [
        "owner-one/repo-one",
        "owner-two/repo-two",
    ]


def test_fetch_candidate_projects_keeps_trending_repo_when_api_detail_fails() -> None:
    class FakeClient:
        def get_text_url(self, url: str) -> str:
            return '<article><h2><a href="/owner/repo">owner / repo</a></h2></article>'

        def fetch_repository(self, owner: str, repo: str) -> None:
            return None

    settings = Settings(
        github_token=None,
        github_api_url="https://api.github.com",
        request_timeout_seconds=20,
        candidate_min=10,
        candidate_max=10,
        history_days=30,
    )

    projects = fetch_candidate_projects(FakeClient(), settings)  # type: ignore[arg-type]

    assert projects[0]["repo_name"] == "owner/repo"
    assert projects[0]["html_url"] == "https://github.com/owner/repo"
    assert projects[0]["candidate_reason"] == "GitHub Trending 日榜第 1 名"
