# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Tests for Multi-Factor Authentication."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pyotp

from backend.tests.factories import create_user
from auth_service.models.mfa import MfaSecret
from auth_service.utils.mfa import decrypt_secret


class TestMfaRoutes:
    
    @pytest.fixture(autouse=True)
    def setup(self, db_session: Session, auth_client: TestClient):
        self.db = db_session
        self.client = auth_client

    def test_enable_mfa(self):
        user = create_user(self.db, email="mfa_enable@example.com", password="MyPassword1!")
        
        # Login to get token
        login_resp = self.client.post("/api/v1/auth/login", json={
            "email": "mfa_enable@example.com",
            "password": "MyPassword1!"
        })
        access_token = login_resp.json()["access_token"]

        # Enable MFA
        response = self.client.post(
            "/api/v1/auth/mfa/enable",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "secret" in data
        assert "qr_code" in data
        
        # Verify secret in DB
        mfa_record = self.db.query(MfaSecret).filter_by(user_id=user.id).first()
        assert mfa_record is not None
        assert mfa_record.verified is False

    def test_verify_mfa(self):
        user = create_user(self.db, email="mfa_verify@example.com", password="MyPassword1!")
        
        login_resp = self.client.post("/api/v1/auth/login", json={
            "email": "mfa_verify@example.com",
            "password": "MyPassword1!"
        })
        access_token = login_resp.json()["access_token"]

        # Enable MFA
        self.client.post(
            "/api/v1/auth/mfa/enable",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        mfa_record = self.db.query(MfaSecret).filter_by(user_id=user.id).first()
        secret = decrypt_secret(mfa_record.secret_encrypted)
        
        # Generate valid TOTP code
        totp = pyotp.TOTP(secret)
        code = totp.now()

        # Verify
        verify_resp = self.client.post(
            "/api/v1/auth/mfa/verify",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"code": code}
        )
        
        assert verify_resp.status_code == 200
        data = verify_resp.json()
        assert "backup_codes" in data
        assert len(data["backup_codes"]) == 10
        
        self.db.refresh(user)
        self.db.refresh(mfa_record)
        assert user.mfa_enabled is True
        assert mfa_record.verified is True

    def test_login_with_mfa(self):
        user = create_user(self.db, email="mfa_login@example.com", password="MyPassword1!")
        
        login_resp = self.client.post("/api/v1/auth/login", json={
            "email": "mfa_login@example.com",
            "password": "MyPassword1!"
        })
        access_token = login_resp.json()["access_token"]

        self.client.post(
            "/api/v1/auth/mfa/enable",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        mfa_record = self.db.query(MfaSecret).filter_by(user_id=user.id).first()
        secret = decrypt_secret(mfa_record.secret_encrypted)
        
        totp = pyotp.TOTP(secret)
        code = totp.now()

        self.client.post(
            "/api/v1/auth/mfa/verify",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"code": code}
        )
        
        # Now try logging in again
        login_resp2 = self.client.post("/api/v1/auth/login", json={
            "email": "mfa_login@example.com",
            "password": "MyPassword1!",
            "mfa_code": totp.now()
        })
        
        assert login_resp2.status_code == 200
        assert "access_token" in login_resp2.json()
