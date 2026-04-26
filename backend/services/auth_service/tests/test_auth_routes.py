# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Tests for Authentication Routes."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.tests.factories import create_user
from auth_service.models.session import Session as SessionModel


class TestAuthRoutes:
    
    @pytest.fixture(autouse=True)
    def setup(self, db_session: Session, auth_client: TestClient):
        self.db = db_session
        self.client = auth_client

    def test_register_success(self):
        payload = {
            "email": "newuser@example.com",
            "password": "ValidPassword123!"
        }
        response = self.client.post("/api/v1/auth/register", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == "newuser@example.com"
        assert data["verification_sent"] is True

    def test_register_duplicate_email(self):
        create_user(self.db, email="duplicate@example.com")
        
        payload = {
            "email": "duplicate@example.com",
            "password": "ValidPassword123!"
        }
        response = self.client.post("/api/v1/auth/register", json=payload)
        
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    def test_login_success(self):
        create_user(self.db, email="login@example.com", password="MyPassword1!")
        
        response = self.client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "MyPassword1!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "login@example.com"

        # Check session created in DB
        session = self.db.query(SessionModel).filter_by(user_id=data["user"]["id"]).first()
        assert session is not None
        assert session.revoked_at is None

    def test_login_invalid_password(self):
        create_user(self.db, email="login_fail@example.com", password="MyPassword1!")
        
        response = self.client.post("/api/v1/auth/login", json={
            "email": "login_fail@example.com",
            "password": "WrongPassword!"
        })
        
        assert response.status_code == 401

    def test_refresh_token_success(self):
        create_user(self.db, email="refresh@example.com", password="MyPassword1!")
        
        # 1. Login to get refresh token
        login_resp = self.client.post("/api/v1/auth/login", json={
            "email": "refresh@example.com",
            "password": "MyPassword1!"
        })
        refresh_token = login_resp.json()["refresh_token"]

        # 2. Refresh
        refresh_resp = self.client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert refresh_resp.status_code == 200
        data = refresh_resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["refresh_token"] != refresh_token

    def test_logout_success(self):
        user = create_user(self.db, email="logout@example.com", password="MyPassword1!")
        
        login_resp = self.client.post("/api/v1/auth/login", json={
            "email": "logout@example.com",
            "password": "MyPassword1!"
        })
        access_token = login_resp.json()["access_token"]

        # Assert session is active
        session_count = self.db.query(SessionModel).filter(
            SessionModel.user_id == str(user.id),
            SessionModel.revoked_at.is_(None)
        ).count()
        assert session_count == 1

        # Logout
        logout_resp = self.client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert logout_resp.status_code == 200

        # Assert session is revoked
        active_sessions = self.db.query(SessionModel).filter(
            SessionModel.user_id == str(user.id),
            SessionModel.revoked_at.is_(None)
        ).count()
        assert active_sessions == 0
