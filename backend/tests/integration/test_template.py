# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Template for Integration Tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.tests.factories import create_user


class TestIntegrationTemplate:
    """
    Template pattern: Setup -> Action -> Assert.
    Use this as a reference for writing robust integration tests.
    """

    @pytest.fixture(autouse=True)
    def setup(self, db_session: Session, auth_client: TestClient):
        self.db = db_session
        self.client = auth_client

    def test_example_flow(self):
        # 1. Setup Data
        user = create_user(self.db, email="template@example.com")
        
        # 2. Action
        response = self.client.post("/api/v1/auth/login", json={
            "email": "template@example.com",
            "password": "StrongPassword123!"
        })

        # 3. Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "template@example.com"
