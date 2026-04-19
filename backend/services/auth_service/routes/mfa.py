# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""MFA endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth_service.dependencies import get_current_user
from auth_service.models.mfa import MfaSecret
from auth_service.models.user import User
from auth_service.schemas.mfa import MfaBackupResponse, MfaEnableResponse, MfaVerifyRequest, MfaVerifyResponse
from auth_service.utils import (
    build_otpauth_url,
    decrypt_secret,
    encrypt_secret,
    generate_backup_codes,
    generate_backup_salt,
    generate_mfa_secret,
    generate_qr_code_data_uri,
    hash_backup_code,
    record_audit_log,
    verify_totp,
)
from shared.config import get_settings
from shared.database import get_db
from shared.exceptions import ConflictError, ValidationError

settings = get_settings()
router = APIRouter(prefix="/api/v1/auth/mfa", tags=["mfa"])


def _create_backup_bundle() -> tuple[list[str], str, list[str]]:
    codes = generate_backup_codes()
    salt = generate_backup_salt()
    hashes = [hash_backup_code(code, salt) for code in codes]
    return codes, salt, hashes


@router.post("/enable", response_model=MfaEnableResponse)
def enable_mfa(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MfaEnableResponse:
    if user.mfa_enabled:
        raise ConflictError("MFA is already enabled")

    secret = generate_mfa_secret()
    otpauth_url = build_otpauth_url(secret, user.email, settings.service_name)
    qr_code = generate_qr_code_data_uri(otpauth_url)

    mfa_record = db.execute(select(MfaSecret).where(MfaSecret.user_id == user.id)).scalar_one_or_none()
    if mfa_record:
        mfa_record.secret_encrypted = encrypt_secret(secret)
        mfa_record.verified = False
    else:
        mfa_record = MfaSecret(
            user_id=user.id,
            secret_encrypted=encrypt_secret(secret),
            verified=False,
            backup_codes_salt=generate_backup_salt(),
            backup_codes_hashes=[],
        )
        db.add(mfa_record)

    record_audit_log(db, str(user.id), "mfa_enabled", request)
    db.commit()

    return MfaEnableResponse(secret=secret, otpauth_url=otpauth_url, qr_code_data_uri=qr_code)


@router.post("/verify", response_model=MfaVerifyResponse)
def verify_mfa(payload: MfaVerifyRequest, request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MfaVerifyResponse:
    mfa_record = db.execute(select(MfaSecret).where(MfaSecret.user_id == user.id)).scalar_one_or_none()
    if not mfa_record:
        raise ValidationError("MFA is not configured")

    secret = decrypt_secret(mfa_record.secret_encrypted)
    if not verify_totp(secret, payload.code):
        raise ValidationError("Invalid MFA code")

    backup_codes, salt, hashes = _create_backup_bundle()
    mfa_record.verified = True
    mfa_record.backup_codes_salt = salt
    mfa_record.backup_codes_hashes = hashes
    user.mfa_enabled = True

    record_audit_log(db, str(user.id), "mfa_verified", request)
    db.commit()

    return MfaVerifyResponse(backup_codes=backup_codes)


@router.post("/backup", response_model=MfaBackupResponse)
def regenerate_backup_codes(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MfaBackupResponse:
    mfa_record = db.execute(select(MfaSecret).where(MfaSecret.user_id == user.id)).scalar_one_or_none()
    if not mfa_record or not mfa_record.verified:
        raise ValidationError("MFA is not verified")

    backup_codes, salt, hashes = _create_backup_bundle()
    mfa_record.backup_codes_salt = salt
    mfa_record.backup_codes_hashes = hashes

    record_audit_log(db, str(user.id), "mfa_backup_regenerated", request)
    db.commit()

    return MfaBackupResponse(backup_codes=backup_codes)
