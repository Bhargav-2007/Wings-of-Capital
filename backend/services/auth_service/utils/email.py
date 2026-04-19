# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Email sending utilities."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage

from shared.config import get_settings
from shared.exceptions import AppError


def send_email(to_address: str, subject: str, body: str) -> None:
    settings = get_settings()

    if not settings.smtp_user or not settings.smtp_password:
        raise AppError("SMTP credentials are not configured", status_code=500)

    sender = settings.smtp_from or settings.smtp_user

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
    except Exception as exc:
        raise AppError("Failed to send email", status_code=500, details={"reason": str(exc)}) from exc
