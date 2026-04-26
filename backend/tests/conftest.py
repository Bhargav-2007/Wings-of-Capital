# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Root conftest.py — patches environment and external dependencies before any app import."""

import os
import sys
from unittest.mock import MagicMock, patch

# ── 1. Environment overrides (MUST happen before ANY app import) ─────────────
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TIMESCALE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "unit-test-secret"
os.environ["REDIS_URL"] = "redis://localhost:6379/9"
os.environ["ENVIRONMENT"] = "testing"
os.environ["RATE_LIMIT_ENABLED"] = "false"  # Disable rate limiting globally in tests

# ── 2. Patch Redis globally at module level before any import uses it ─────────
class _FakeRedisConn:
    """In-memory Redis stub that satisfies the Redis client protocol."""
    def __init__(self):
        self._data: dict = {}

    def incr(self, key, amount=1):
        self._data[key] = self._data.get(key, 0) + amount
        return self._data[key]

    def expire(self, key, seconds):
        pass

    def get(self, key):
        return self._data.get(key)

    def set(self, name, value, ex=None):
        self._data[name] = value
        return True

    def delete(self, *keys):
        count = 0
        for k in keys:
            if k in self._data:
                del self._data[k]
                count += 1
        return count

    def publish(self, channel, message):
        return 0

    def ping(self):
        return True


_fake_redis_conn = _FakeRedisConn()


def _fake_get_redis_client():
    return _fake_redis_conn


# Inject the fake into shared.redis before anything imports it
import shared.redis as _redis_mod
_redis_mod.get_redis_client = _fake_get_redis_client
_redis_mod._pool = MagicMock()  # prevent real connection pool creation


class _FakeRedisClient:
    """Drop-in replacement for shared.redis.RedisClient."""
    def __init__(self):
        self.client = _fake_redis_conn

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value, ttl_seconds=None):
        return self.client.set(name=key, value=value, ex=ttl_seconds)

    def delete(self, key):
        return self.client.delete(key)

    def incr(self, key, ttl_seconds=None):
        val = self.client.incr(key)
        if ttl_seconds:
            self.client.expire(key, ttl_seconds)
        return val

    def publish(self, channel, message):
        return 0

    def set_json(self, key, value, ttl_seconds=None):
        import json
        return self.set(key, json.dumps(value), ttl_seconds)

    def get_json(self, key):
        import json
        raw = self.get(key)
        return json.loads(raw) if raw else None


_redis_mod.RedisClient = _FakeRedisClient

# ── 3. Patch send_email to be a no-op in tests ──────────────────────────────
import auth_service.utils.email as _email_mod
_email_mod.send_email = lambda to_address, subject, body: None

# ── 4. Now import everything we need ─────────────────────────────────────────
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from shared.models import BaseModel
from shared.database import get_db
from shared.config import get_settings


# ── 5. Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def engine():
    """Create an in-memory SQLite engine shared across all tests in the session."""
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    BaseModel.metadata.create_all(bind=eng)
    yield eng
    BaseModel.metadata.drop_all(bind=eng)


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """Per-test transactional session that rolls back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def auth_client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient wired to the auth service with DB overridden."""
    from auth_service.main import app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def ledger_client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient wired to the ledger service with DB overridden."""
    from ledger_service.main import app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
    app.dependency_overrides.clear()
