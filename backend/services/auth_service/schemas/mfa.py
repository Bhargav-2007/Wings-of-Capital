# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""MFA request and response schemas."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel


class MfaEnableResponse(BaseModel):
    secret: str
    otpauth_url: str
    qr_code_data_uri: str


class MfaVerifyRequest(BaseModel):
    code: str


class MfaVerifyResponse(BaseModel):
    backup_codes: List[str]


class MfaBackupResponse(BaseModel):
    backup_codes: List[str]
