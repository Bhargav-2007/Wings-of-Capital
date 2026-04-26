import os
import sys
import pytest

# Fail fast on Python versions known to be incompatible with the pinned SQLAlchemy
# used by this repo's tests. SQLAlchemy's typing internals may not be compatible
# with Python 3.14 in older releases; provide a clear actionable message.
if sys.version_info >= (3, 14):
    raise RuntimeError(
        "Python 3.14+ is not supported by the current test configuration.\n"
        "Please create a virtualenv using Python 3.11 (recommended) or 3.12 and re-run tests.\n"
        "Example:\n"
        "  sudo apt install -y python3.11 python3.11-venv python3.11-dev\n"
        "  python3.11 -m venv .venv\n"
        "  source .venv/bin/activate\n"
        "  python -m pip install --upgrade pip\n"
        "  pip install -r backend/tests/requirements-dev.txt\n"
        "  pytest backend/services/auth_service/tests/ -v\n"
    )

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure test environment variables are set before importing application code
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("BCRYPT_ROUNDS", "4")
os.environ.setdefault("PASSWORD_MIN_LENGTH", "1")

# Make the `backend/services` directory importable (so packages like `auth_service` resolve)
BACKEND_DIR = os.path.dirname(__file__)
SERVICES_PATH = os.path.join(BACKEND_DIR, "services")
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

    def ping(self):
        return True

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
    pass

# Monkeypatch verification token helpers to avoid requiring `python-jose`/cryptography in tests
try:
    import auth_service.utils.tokens as _tokens  # type: ignore

    def _fake_create_verification_token(subject: str, expires_hours: int = 24) -> str:
        return f"fake-token:{subject}"

    def _fake_decode_verification_token(token: str) -> dict:
        if token.startswith("fake-token:"):
            return {"sub": token.split(":", 1)[1]}
        raise RuntimeError("Invalid token")

    _tokens.create_verification_token = _fake_create_verification_token
    _tokens.decode_verification_token = _fake_decode_verification_token
except Exception:
    pass

# Monkeypatch MFA encrypt/decrypt to avoid `cryptography` dependency during tests
try:
    import auth_service.utils.mfa as _mfa_utils  # type: ignore

    _mfa_utils.encrypt_secret = lambda s: s
    _mfa_utils.decrypt_secret = lambda s: s
except Exception:
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
