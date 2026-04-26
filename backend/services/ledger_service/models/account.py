# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Account model for chart of accounts."""

from __future__ import annotations

from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import Boolean, Numeric, String
from shared.db_types import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.models import BaseModel

from .enums import AccountType


class Account(BaseModel):
    __tablename__ = "accounts"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "account_number", name="uq_accounts_user_account_number"),
    )

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    account_number: Mapped[str] = mapped_column(String(32), nullable=False)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(
        sa.Enum(AccountType, name="account_type"), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    allow_negative: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
