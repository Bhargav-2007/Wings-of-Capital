# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Shared Pydantic schemas."""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseSchema):
    error: str
    message: str
    details: dict = Field(default_factory=dict)


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserBase(BaseSchema):
    email: EmailStr


class UserOut(UserBase):
    id: str | uuid.UUID
    is_active: bool
    is_verified: bool
    mfa_enabled: bool
    created_at: dt.datetime


class PaginatedResponse(BaseSchema, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
