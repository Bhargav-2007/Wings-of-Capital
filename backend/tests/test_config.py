# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

from shared.config import Settings


def test_settings_parsing(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/woc")
    monkeypatch.setenv("JWT_SECRET_KEY", "unit-test-secret")
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:8080,http://localhost:3000")
    monkeypatch.setenv("CORS_ALLOW_METHODS", "GET,POST")
    monkeypatch.setenv("CORS_ALLOW_HEADERS", "Authorization,Content-Type")

    settings = Settings()

    assert settings.allowed_origins == ["http://localhost:8080", "http://localhost:3000"]
    assert settings.cors_methods_list == ["GET", "POST"]
    assert settings.cors_headers_list == ["Authorization", "Content-Type"]
    assert settings.jwt_signing_key == "unit-test-secret"
