# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Multi-factor authentication helpers."""

from __future__ import annotations

import base64
import hashlib
import io
import secrets
from typing import List

import pyotp
import qrcode
from cryptography.fernet import Fernet

from shared.config import get_settings


def _fernet() -> Fernet:
    settings = get_settings()
    source = settings.mfa_encryption_key or settings.jwt_secret_key
    digest = hashlib.sha256(source.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_secret(secret: str) -> str:
    return _fernet().encrypt(secret.encode("utf-8")).decode("utf-8")


def decrypt_secret(secret_encrypted: str) -> str:
    return _fernet().decrypt(secret_encrypted.encode("utf-8")).decode("utf-8")


def generate_mfa_secret() -> str:
    return pyotp.random_base32()


def build_otpauth_url(secret: str, email: str, issuer: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def generate_qr_code_data_uri(data: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return bool(totp.verify(code, valid_window=1))


def generate_backup_codes(count: int = 10, length: int = 10) -> List[str]:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return ["".join(secrets.choice(alphabet) for _ in range(length)) for _ in range(count)]


def generate_backup_salt() -> str:
    return secrets.token_hex(16)


def hash_backup_code(code: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{code}".encode("utf-8")).hexdigest()


def verify_backup_code(code: str, salt: str, hashes: List[str]) -> bool:
    return hash_backup_code(code, salt) in hashes
