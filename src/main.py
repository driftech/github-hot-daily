from __future__ import annotations

import json
import logging

from .config import CHATGPT_PROMPT_PATH, DAILY_RAW_PATH, HISTORY_PATH, OUTPUT_DIR, PROJECTS_PATH, load_settings
from .fetch_github import fetch_candidate_projects
from .github_client import GitHubClient
from .history_store import load_history, update_history
from .rank_projects import score_projects
from .render_markdown import build_chatgpt_prompt, render_daily_markdown
from .send_email import send_email_with_attachments


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
LOGGER = logging.getLogger(__name__)


def main() -> None:
    settings = load_settings()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    history = load_history(HISTORY_PATH)
    client = GitHubClient(settings)
    candidates = fetch_candidate_projects(client, settings)
    ranked = score_projects(candidates, history)[: settings.candidate_max]

    update_history(ranked, history, HISTORY_PATH, keep_days=settings.history_days)

    PROJECTS_PATH.write_text(json.dumps(ranked, ensure_ascii=False, indent=2), encoding="utf-8")
    prompt = build_chatgpt_prompt(ranked)
    CHATGPT_PROMPT_PATH.write_text(prompt, encoding="utf-8")
    render_daily_markdown(ranked, DAILY_RAW_PATH, prompt)

    LOGGER.info("Generated %s candidate projects", len(ranked))
    if len(ranked) < settings.candidate_min:
        LOGGER.warning("Only %s candidates generated; consider broadening search conditions", len(ranked))

    send_email_with_attachments()


if __name__ == "__main__":
    main()
