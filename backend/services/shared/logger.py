# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Structured JSON logging with request context."""

from __future__ import annotations

import contextvars
import logging
from typing import Optional

from pythonjsonlogger import jsonlogger

_request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")
_service_name_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("service_name", default="wings-of-capital")


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_ctx.get()
        record.service_name = _service_name_ctx.get()
        return True


def set_request_id(request_id: str) -> None:
    _request_id_ctx.set(request_id)


def get_request_id() -> str:
    return _request_id_ctx.get()


def set_service_name(service_name: str) -> None:
    _service_name_ctx.set(service_name)


def _build_formatter(use_json: bool) -> logging.Formatter:
    if use_json:
        return jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(service_name)s",
            rename_fields={"levelname": "level", "asctime": "timestamp"},
        )
    return logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def init_logging(service_name: str, level: str = "INFO", use_json: bool = True) -> None:
    set_service_name(service_name)

    logger = logging.getLogger()
    logger.setLevel(level.upper())

    handler = logging.StreamHandler()
    handler.setLevel(level.upper())
    handler.setFormatter(_build_formatter(use_json))
    handler.addFilter(RequestContextFilter())

    logger.handlers.clear()
    logger.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name)
