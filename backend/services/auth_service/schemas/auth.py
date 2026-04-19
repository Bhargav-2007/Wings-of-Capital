# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Auth service request and response schemas."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from shared.schemas import TokenResponse, UserOut


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12)


class RegisterResponse(BaseModel):
    user: UserOut
    verification_sent: bool


class VerifyEmailRequest(BaseModel):
    token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None
    backup_code: Optional[str] = None


class LoginResponse(TokenResponse):
    user: UserOut


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutResponse(BaseModel):
    message: str
