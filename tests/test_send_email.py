from __future__ import annotations

import logging

from src.send_email import REQUIRED_ENV_VARS, send_email_with_attachments


def test_send_email_skips_when_smtp_config_missing(monkeypatch, tmp_path, caplog) -> None:
    for key in REQUIRED_ENV_VARS:
        monkeypatch.delenv(key, raising=False)

    caplog.set_level(logging.INFO)

    send_email_with_attachments(tmp_path)

    assert "SMTP 配置不完整，已跳过邮件发送。" in caplog.text
