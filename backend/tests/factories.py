"""Lightweight test factories for backend tests.

These factories intentionally avoid heavy external dependencies so tests can run
in more constrained CI environments. They wrap model creation and commit to
the provided `db_session`.
"""
from datetime import datetime, timezone, timedelta

from shared.security import hash_password


def create_user(db_session, email: str = "user@example.com", password: str = "StrongPassw0rd!"):
    # Import locally to avoid top-level import-time side-effects
    from auth_service.models.user import User

    user = User(
        email=email,
        password_hash=hash_password(password),
        is_active=True,
        is_verified=False,
        mfa_enabled=False,
    )
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    return user


def create_session(db_session, user_id, token_hash: str = "test-hash", expires_days: int = 7):
    from auth_service.models.session import Session as SessionModel

    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)
    session = SessionModel(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db_session.add(session)
    db_session.flush()
    db_session.refresh(session)
    return session
