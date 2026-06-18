from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any


History = dict[str, list[dict[str, Any]]]


def load_history(path: Path) -> History:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def get_star_delta(repo_name: str, current_stars: int, history: History, today: date | None = None) -> int:
    today = today or date.today()
    records = history.get(repo_name, [])
    previous_records = [item for item in records if item.get("date") != today.isoformat()]
    if not previous_records:
        return 0
    previous = previous_records[-1]
    try:
        return max(current_stars - int(previous.get("stars", current_stars)), 0)
    except (TypeError, ValueError):
        return 0


def get_last_seen_days(repo_name: str, history: History, today: date | None = None) -> int | None:
    today = today or date.today()
    records = history.get(repo_name, [])
    seen_dates: list[date] = []
    for item in records:
        raw_date = item.get("date")
        if raw_date == today.isoformat():
            continue
        try:
            seen_dates.append(date.fromisoformat(str(raw_date)))
        except ValueError:
            continue
    if not seen_dates:
        return None
    return max((today - max(seen_dates)).days, 0)


def get_seen_count(repo_name: str, history: History, today: date | None = None) -> int:
    today = today or date.today()
    records = history.get(repo_name, [])
    return sum(1 for item in records if item.get("date") != today.isoformat())


def update_history(projects: list[dict[str, Any]], history: History, path: Path, keep_days: int = 30) -> History:
    today_value = date.today()
    today = today_value.isoformat()
    cutoff = today_value - timedelta(days=keep_days - 1)
    updated: History = {}

    for repo, records in history.items():
        kept_records = []
        for item in records:
            try:
                item_date = date.fromisoformat(str(item.get("date")))
            except ValueError:
                continue
            if item_date >= cutoff:
                kept_records.append(item)
        if kept_records:
            updated[repo] = kept_records

    for project in projects:
        repo_name = project["repo_name"]
        records = [item for item in updated.get(repo_name, []) if item.get("date") != today]
        records.append({"date": today, "stars": project.get("stargazers_count", 0)})
        updated[repo_name] = records[-keep_days:]

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(updated, file, ensure_ascii=False, indent=2)
    return updated
