# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Test data factories for creating SQLAlchemy models in tests."""

import uuid
from typing import Optional

from auth_service.models.user import User
from ledger_service.models.account import Account
from ledger_service.models.enums import AccountType
from shared.security import hash_password


def create_user(
    db_session,
    email: str = "test@example.com",
    password: str = "StrongPassword123!",
    is_active: bool = True,
    is_verified: bool = True,
    mfa_enabled: bool = False,
) -> User:
    """Create and persist a test user."""
    user = User(
        email=email,
        password_hash=hash_password(password),
        is_active=is_active,
        is_verified=is_verified,
        mfa_enabled=mfa_enabled,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_account(
    db_session,
    user_id: uuid.UUID,
    account_number: str = "1000",
    account_name: str = "Checking Account",
    account_type: AccountType = AccountType.ASSET,
    currency: str = "USD",
    balance: float = 0.0,
    allow_negative: bool = False,
) -> Account:
    """Create and persist a test ledger account."""
    from decimal import Decimal

    account = Account(
        user_id=user_id,
        account_number=account_number,
        account_name=account_name,
        account_type=account_type,
        currency=currency,
        balance=Decimal(str(balance)),
        allow_negative=allow_negative,
        is_active=True,
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account
