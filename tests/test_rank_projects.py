from __future__ import annotations

from src.rank_projects import rank_projects


def make_project(repo_name: str, stars: int, star_delta: int, description: str) -> dict:
    return {
        "repo_name": repo_name,
        "description": description,
        "stargazers_count": stars,
        "forks_count": max(stars // 10, 1),
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-06-01T00:00:00Z",
        "pushed_at": "2026-06-01T00:00:00Z",
        "language": "Python",
        "topics": ["ai", "llm"],
        "readme_text": "Install usage example. " * 200,
        "star_delta": star_delta,
    }


def test_rank_projects_considers_growth_not_only_total_stars() -> None:
    old_large_repo = make_project("owner/old-large", stars=8000, star_delta=0, description="Python utility")
    fast_growing_repo = make_project("owner/fast-growing", stars=1200, star_delta=300, description="AI LLM agent framework")

    ranked = rank_projects([old_large_repo, fast_growing_repo], history={})

    assert ranked[0]["repo_name"] == "owner/fast-growing"
    assert ranked[0]["hot_score"] > ranked[1]["hot_score"]
    assert ranked[0]["hot_score_detail"]["growth_score"] > ranked[1]["hot_score_detail"]["growth_score"]

