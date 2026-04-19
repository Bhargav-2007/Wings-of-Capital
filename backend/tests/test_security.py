# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

from shared.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hashing():
    password = "Str0ngPassword!"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_access_token_roundtrip():
    token = create_access_token("user-123")
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"
