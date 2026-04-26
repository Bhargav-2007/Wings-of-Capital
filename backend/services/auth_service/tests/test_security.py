# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Tests for Security Mechanisms."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.tests.factories import create_user


class TestSecurityFeatures:
    
    @pytest.fixture(autouse=True)
    def setup(self, db_session: Session, auth_client: TestClient):
        self.db = db_session
        self.client = auth_client

    def test_password_strength_validation(self):
        # Too short
        response = self.client.post("/api/v1/auth/register", json={
            "email": "weak1@example.com",
            "password": "Short1!"
        })
        assert response.status_code == 422

        # No uppercase
        response = self.client.post("/api/v1/auth/register", json={
            "email": "weak2@example.com",
            "password": "nouppercase123!"
        })
        assert response.status_code == 422

        # No special character
        response = self.client.post("/api/v1/auth/register", json={
            "email": "weak3@example.com",
            "password": "NoSpecialChar123"
        })
        assert response.status_code == 422

    def test_rate_limiting(self):
        """Test rate limiter. Since it relies on Redis, and we have a mock/test instance, we'll hammer the login endpoint."""
        create_user(self.db, email="rate_limit@example.com", password="MyPassword1!")
        
        # We allow 10 requests per minute in login endpoint
        # We will make 11 requests
        for _ in range(10):
            response = self.client.post("/api/v1/auth/login", json={
                "email": "rate_limit@example.com",
                "password": "MyPassword1!"
            })
            if response.status_code == 429:
                break
                
        # The 11th request MUST be 429
        response = self.client.post("/api/v1/auth/login", json={
            "email": "rate_limit@example.com",
            "password": "MyPassword1!"
        })
        
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]
