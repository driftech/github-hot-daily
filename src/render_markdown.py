from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def build_chatgpt_prompt(projects: list[dict[str, Any]]) -> str:
    trimmed = [
        {
            "repo_name": item["repo_name"],
            "html_url": item["html_url"],
            "description": item["description"],
            "language": item["language"],
            "topics": item["topics"],
            "stars": item["stargazers_count"],
            "forks": item["forks_count"],
            "star_delta": item.get("star_delta", 0),
            "readme_summary": item["readme_summary"],
            "candidate_reason": item["candidate_reason"],
            "hot_score": item["hot_score"],
        }
        for item in projects[:10]
    ]
    return (
        "你是一名中文科技公众号编辑。请基于下面的 GitHub 热点项目素材，"
        "写一篇面向开发者和技术管理者的公众号文章。要求：标题有吸引力但不夸张，"
        "每个项目说明它解决什么问题、为什么值得关注、适合谁使用，并保留项目链接。"
        "不要编造数据，不要声称已经试用。素材如下：\n\n"
        f"{json.dumps(trimmed, ensure_ascii=False, indent=2)}"
    )


def project_line(project: dict[str, Any], index: int) -> str:
    topics = ", ".join(project.get("topics") or []) or "无"
    return (
        f"### {index}. {project['repo_name']}\n\n"
        f"- 链接：{project['html_url']}\n"
        f"- 简介：{project.get('description') or '暂无简介'}\n"
        f"- 语言：{project.get('language') or '未知'}\n"
        f"- Stars/Forks/Issues：{project['stargazers_count']} / {project['forks_count']} / {project['open_issues_count']}\n"
        f"- 近日日增 Stars：{project.get('star_delta', 0)}\n"
        f"- Topics：{topics}\n"
        f"- License：{project.get('license') or '未知'}\n"
        f"- 入选原因：{project.get('candidate_reason')}\n"
        f"- 热度分：{project.get('hot_score')}，明细：{json.dumps(project.get('hot_score_detail', {}), ensure_ascii=False)}\n"
        f"- README 摘要：{project.get('readme_summary') or 'README 获取失败或内容较少'}\n"
    )


def render_daily_markdown(projects: list[dict[str, Any]], output_path: Path, prompt: str) -> None:
    now = datetime.now()
    top_projects = projects[:10]
    backup_projects = projects[10:20]
    languages = sorted({item.get("language") for item in projects if item.get("language")})
    observations = [
        f"本次共筛选出 {len(projects)} 个候选项目。",
        f"主要语言覆盖：{', '.join(languages[:8]) if languages else '暂无明确语言信息'}。",
        "候选项目来源于 GitHub Trending 日榜前列，保留 Trending 顺序；hot_score 仅作为参考指标。",
    ]

    content = [
        "# GitHub 热点项目公众号素材包",
        "",
        f"- 日期：{now.date().isoformat()}",
        f"- 生成时间：{now.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 今日总体观察",
        "",
        *[f"- {item}" for item in observations],
        "",
        "## 建议优先发布的 10 个项目",
        "",
    ]
    content.extend(project_line(project, index) for index, project in enumerate(top_projects, start=1))
    content.extend(["", "## 备选项目", ""])
    if backup_projects:
        content.extend(project_line(project, index) for index, project in enumerate(backup_projects, start=1))
    else:
        content.append("- 暂无备选项目。")
    content.extend(["", "## 复制给 ChatGPT Plus 的提示词", "", "```text", prompt, "```", ""])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(content), encoding="utf-8")
