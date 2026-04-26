# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Tests for Ledger Service Routes."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.tests.factories import create_user, create_account
from ledger_service.models.account import Account


class TestLedgerRoutes:

    @pytest.fixture(autouse=True)
    def setup(self, db_session: Session, ledger_client: TestClient, auth_client: TestClient):
        self.db = db_session
        self.client = ledger_client
        self.auth_client = auth_client
        
        # We need an authenticated user context
        self.user = create_user(self.db, email="ledger@example.com", password="MyPassword1!")
        
        # Login via auth client to get a real token (or we could just mock it, but integration is better)
        resp = self.auth_client.post("/api/v1/auth/login", json={
            "email": "ledger@example.com",
            "password": "MyPassword1!"
        })
        self.token = resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_create_account(self):
        payload = {
            "account_number": "1001",
            "account_name": "Main Checking",
            "account_type": "ASSET",
            "currency": "USD",
            "allow_negative": False
        }
        
        response = self.client.post(
            "/api/v1/ledger/accounts",
            json=payload,
            headers=self.headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["account_number"] == "1001"
        assert data["balance"] == "0.00"

    def test_create_duplicate_account(self):
        create_account(self.db, self.user.id, account_number="1002")
        
        payload = {
            "account_number": "1002",
            "account_name": "Duplicate",
            "account_type": "ASSET",
            "currency": "USD",
            "allow_negative": False
        }
        
        response = self.client.post(
            "/api/v1/ledger/accounts",
            json=payload,
            headers=self.headers
        )
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    def test_list_accounts(self):
        create_account(self.db, self.user.id, account_number="2001", account_type="ASSET")
        create_account(self.db, self.user.id, account_number="2002", account_type="LIABILITY")
        
        response = self.client.get(
            "/api/v1/ledger/accounts",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 2
        
        # Test filtering
        filter_resp = self.client.get(
            "/api/v1/ledger/accounts?account_type=LIABILITY",
            headers=self.headers
        )
        assert filter_resp.status_code == 200
        filtered_data = filter_resp.json()
        assert all(item["account_type"] == "LIABILITY" for item in filtered_data["items"])

    def test_get_balance(self):
        account = create_account(self.db, self.user.id, account_number="3001", balance=1500.50)
        
        response = self.client.get(
            f"/api/v1/ledger/accounts/{account.id}/balance",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["balance"] == "1500.50"
        assert data["currency"] == "USD"
