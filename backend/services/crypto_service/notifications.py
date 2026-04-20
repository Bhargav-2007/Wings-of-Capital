# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Notification utilities for crypto alerts."""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Any, Dict

import requests

from shared.config import get_settings
from shared.exceptions import AppError


def send_email_notification(to_address: str, subject: str, body: str) -> None:
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
        raise AppError("Failed to send alert email", status_code=500, details={"reason": str(exc)}) from exc


def send_webhook_notification(url: str, payload: Dict[str, Any]) -> None:
    timeout_seconds = float(os.getenv("ALERT_WEBHOOK_TIMEOUT_SECONDS", "10"))
    try:
        response = requests.post(url, json=payload, timeout=timeout_seconds)
        response.raise_for_status()
    except Exception as exc:
        raise AppError("Failed to send webhook notification", status_code=500, details={"reason": str(exc)}) from exc
