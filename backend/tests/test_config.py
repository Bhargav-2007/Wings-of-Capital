# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

from shared.config import Settings


def test_settings_parsing():
    settings = Settings(
        database_url="postgresql://user:pass@localhost:5432/woc",
        jwt_secret_key="unit-test-secret",
        allowed_origins="http://localhost:8080,http://localhost:3000",
        cors_allow_methods="GET,POST",
        cors_allow_headers="Authorization,Content-Type",
    )

    assert settings.allowed_origins == ["http://localhost:8080", "http://localhost:3000"]
    assert settings.cors_methods_list == ["GET", "POST"]
    assert settings.cors_headers_list == ["Authorization", "Content-Type"]
    assert settings.jwt_signing_key == "unit-test-secret"
