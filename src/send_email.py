from __future__ import annotations

import logging
import mimetypes
import os
import smtplib
from datetime import date
from email.message import EmailMessage
from pathlib import Path

from .config import OUTPUT_DIR


LOGGER = logging.getLogger(__name__)

REQUIRED_ENV_VARS = [
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "MAIL_FROM",
    "MAIL_TO",
]


def _load_smtp_config() -> dict[str, str] | None:
    config = {key: os.getenv(key, "").strip() for key in REQUIRED_ENV_VARS}
    if any(not value for value in config.values()):
        LOGGER.info("SMTP 配置不完整，已跳过邮件发送。")
        return None
    return config


def _build_message(config: dict[str, str], output_dir: Path) -> EmailMessage:
    today = date.today().isoformat()
    daily_raw_path = output_dir / "daily_raw.md"
    body = ""
    if daily_raw_path.exists():
        body = daily_raw_path.read_text(encoding="utf-8")
    else:
        LOGGER.warning("附件不存在，已跳过：%s", daily_raw_path)
        body = "daily_raw.md 不存在，请查看 GitHub Actions artifact。"

    message = EmailMessage()
    message["Subject"] = f"【GitHub 热点素材】{today} 今日项目候选"
    message["From"] = config["MAIL_FROM"]
    message["To"] = config["MAIL_TO"]
    message.set_content(body)

    attachment_paths = [
        daily_raw_path,
        output_dir / "projects.json",
        output_dir / "chatgpt_prompt.txt",
        output_dir / "history.json",
    ]
    for path in attachment_paths:
        if not path.exists():
            LOGGER.warning("附件不存在，已跳过：%s", path)
            continue

        content_type, _ = mimetypes.guess_type(path.name)
        maintype, subtype = (content_type or "application/octet-stream").split("/", 1)
        message.add_attachment(
            path.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=path.name,
        )

    return message


def _send_message(config: dict[str, str], message: EmailMessage) -> None:
    port = int(config["SMTP_PORT"])
    recipients = [item.strip() for item in config["MAIL_TO"].split(",") if item.strip()]

    if port in {465, 994}:
        with smtplib.SMTP_SSL(config["SMTP_HOST"], port, timeout=30) as smtp:
            smtp.login(config["SMTP_USER"], config["SMTP_PASSWORD"])
            smtp.send_message(message, to_addrs=recipients)
        return

    with smtplib.SMTP(config["SMTP_HOST"], port, timeout=30) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(config["SMTP_USER"], config["SMTP_PASSWORD"])
        smtp.send_message(message, to_addrs=recipients)


def send_email_with_attachments(output_dir: Path = OUTPUT_DIR) -> None:
    config = _load_smtp_config()
    if not config:
        return

    try:
        message = _build_message(config, output_dir)
        _send_message(config, message)
        LOGGER.info("邮件发送成功：%s", config["MAIL_TO"])
    except Exception as exc:
        LOGGER.error("邮件发送失败：%s", exc)

