import os
import sys
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure test environment variables are set before importing application code
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("BCRYPT_ROUNDS", "4")
os.environ.setdefault("PASSWORD_MIN_LENGTH", "1")

# Make the `services` directory importable (so packages like `auth_service` resolve)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SERVICES_PATH = os.path.join(REPO_ROOT, "services")
if SERVICES_PATH not in sys.path:
    sys.path.insert(0, SERVICES_PATH)

# Use an in-memory SQLite engine that persists across connections for tests
ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False, expire_on_commit=False)

# Patch shared.database to use the in-memory engine/session for tests
import shared.database as _database  # type: ignore
_database.ENGINE = ENGINE
_database.SessionLocal = TestingSessionLocal

# Provide a small fake Redis client so rate-limiting and pub/sub do not require a running Redis
import shared.redis as _redis  # type: ignore


class _FakeRedis:
    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, name, value, ex=None):
        self._store[name] = value
        return True

    def delete(self, key):
        return int(self._store.pop(key, None) is not None)

    def incr(self, key):
        self._store[key] = int(self._store.get(key, 0)) + 1
        return self._store[key]

    def expire(self, key, seconds):
        return True

    def publish(self, channel, message):
        return 1


def _fake_get_redis_client():
    return _FakeRedis()


_redis.get_redis_client = _fake_get_redis_client

# Avoid trying to send real emails or write external audit logs during tests
try:
    import auth_service.utils as _auth_utils  # type: ignore
    _auth_utils.send_email = lambda *a, **k: None
    _auth_utils.record_audit_log = lambda *a, **k: None
except Exception:
    # If the auth service isn't importable yet, tests that need it will import later
    pass


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create DB schema for tests (imports models so they're registered)."""
    # Import models to ensure they're registered with the Declarative Base metadata
    try:
        import auth_service.models.user  # noqa: F401
        import auth_service.models.session  # noqa: F401
        import auth_service.models.mfa  # noqa: F401
    except Exception:
        pass

    try:
        import ledger_service.models.account  # noqa: F401
        import ledger_service.models.transaction  # noqa: F401
        import ledger_service.models.transaction_line  # noqa: F401
    except Exception:
        pass

    from shared.models import Base  # type: ignore

    Base.metadata.create_all(bind=ENGINE)
    yield
    Base.metadata.drop_all(bind=ENGINE)


@pytest.fixture()
def db_session():
    """Provide a SQLAlchemy session for tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


from fastapi.testclient import TestClient


@pytest.fixture
def test_client(db_session):
    """Factory fixture that returns a `TestClient` for a given FastAPI `app`.

    Usage in tests:
        client = test_client(auth_service.main.app)
    """

    def _make_client(app):
        # Override the DB dependency so the app uses the test session
        import shared.database as _db  # type: ignore

        def _override_get_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[_db.get_db] = _override_get_db
        return TestClient(app)

    return _make_client
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
