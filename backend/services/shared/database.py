# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Database utilities for SQLAlchemy engines and sessions."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings

_settings = get_settings()


def _create_engine(database_url: str) -> Engine:
    if database_url.startswith("sqlite"):
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=None,
        )
    return create_engine(
        database_url,
        pool_size=_settings.database_pool_size,
        max_overflow=_settings.database_max_overflow,
        pool_pre_ping=True,
    )


ENGINE: Engine = _create_engine(_settings.database_url)
TIMESCALE_ENGINE: Optional[Engine] = (
    _create_engine(_settings.timescale_url) if _settings.timescale_url else None
)

SessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False, expire_on_commit=False)
TimescaleSessionLocal = (
    sessionmaker(bind=TIMESCALE_ENGINE, autocommit=False, autoflush=False, expire_on_commit=False)
    if TIMESCALE_ENGINE
    else None
)


def health_check(engine: Engine) -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_timescale_db() -> Generator[Session, None, None]:
    if not TimescaleSessionLocal:
        raise RuntimeError("TimescaleDB is not configured")
    db = TimescaleSessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def timescale_session_scope() -> Generator[Session, None, None]:
    if not TimescaleSessionLocal:
        raise RuntimeError("TimescaleDB is not configured")
    session = TimescaleSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
