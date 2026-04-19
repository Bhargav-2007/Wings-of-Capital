# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Shared exception types and helpers."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import HTTPException


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500, code: str = "error", details: Optional[dict] = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed", details: Optional[dict] = None) -> None:
        super().__init__(message, status_code=422, code="validation_error", details=details)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", details: Optional[dict] = None) -> None:
        super().__init__(message, status_code=404, code="not_found", details=details)


class AuthError(AppError):
    def __init__(self, message: str = "Unauthorized", details: Optional[dict] = None) -> None:
        super().__init__(message, status_code=401, code="unauthorized", details=details)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict", details: Optional[dict] = None) -> None:
        super().__init__(message, status_code=409, code="conflict", details=details)


class RateLimitError(AppError):
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[dict] = None) -> None:
        super().__init__(message, status_code=429, code="rate_limited", details=details)


def to_http_exception(error: AppError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail={
            "error": error.code,
            "message": error.message,
            "details": error.details,
        },
    )


def handle_exception(error: Exception) -> HTTPException:
    if isinstance(error, AppError):
        return to_http_exception(error)
    return HTTPException(status_code=500, detail={"error": "internal_error", "message": str(error)})
