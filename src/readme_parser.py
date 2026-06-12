from __future__ import annotations

import re


IMAGE_PATTERN = re.compile(r"!\[[^\]]*]\(([^)]+)\)|<img[^>]+src=[\"']([^\"']+)[\"']", re.IGNORECASE)
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)]\([^)]+\)")
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")


def extract_readme_images(readme_text: str) -> list[str]:
    images: list[str] = []
    for match in IMAGE_PATTERN.finditer(readme_text):
        url = match.group(1) or match.group(2)
        if url and url not in images:
            images.append(url)
    return images[:10]


def clean_markdown_text(markdown: str) -> str:
    text = re.sub(r"```.*?```", " ", markdown, flags=re.DOTALL)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = MARKDOWN_LINK_PATTERN.sub(r"\1", text)
    text = re.sub(r"!\[[^\]]*]\([^)]+\)", " ", text)
    text = HTML_TAG_PATTERN.sub(" ", text)
    text = re.sub(r"^[#>*\-\s]+", "", text, flags=re.MULTILINE)
    return WHITESPACE_PATTERN.sub(" ", text).strip()


def summarize_readme(readme_text: str, max_chars: int = 420) -> str:
    cleaned = clean_markdown_text(readme_text)
    if not cleaned:
        return ""
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars].rsplit(" ", 1)[0].strip() + "..."


def readme_quality_score(readme_text: str) -> float:
    if not readme_text:
        return 0.0
    length_score = min(len(clean_markdown_text(readme_text)) / 2500, 1.0)
    has_install = 1.0 if re.search(r"\b(install|quickstart|getting started|usage|docs?)\b", readme_text, re.I) else 0.0
    has_examples = 1.0 if re.search(r"\b(example|demo|screenshot|api|cli)\b", readme_text, re.I) else 0.0
    has_images = 1.0 if extract_readme_images(readme_text) else 0.0
    return round(0.55 * length_score + 0.2 * has_install + 0.15 * has_examples + 0.1 * has_images, 4)

