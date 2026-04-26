# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Tests for Double-Entry Accounting Logic."""

import pytest
from decimal import Decimal
from sqlalchemy.orm import Session

from backend.tests.factories import create_user, create_account
from ledger_service.ledger.posting import post_transaction
from ledger_service.models.enums import AccountType, EntryType
from ledger_service.schemas.transactions import TransactionCreate, TransactionLineIn
from shared.exceptions import ValidationError


class TestPostingLogic:

    @pytest.fixture(autouse=True)
    def setup(self, db_session: Session):
        self.db = db_session
        self.user = create_user(self.db, email="posting@example.com")
        self.asset_acct = create_account(
            self.db, self.user.id, "1000", "Cash", AccountType.ASSET, balance=1000.0, allow_negative=False
        )
        self.revenue_acct = create_account(
            self.db, self.user.id, "4000", "Sales", AccountType.INCOME, balance=0.0
        )
        self.expense_acct = create_account(
            self.db, self.user.id, "5000", "Fees", AccountType.EXPENSE, balance=0.0
        )
        self.liability_acct = create_account(
            self.db, self.user.id, "2000", "Loan", AccountType.LIABILITY, balance=0.0
        )

    def test_valid_balanced_transaction(self):
        """Test a valid, balanced transaction."""
        payload = TransactionCreate(
            description="Client Payment",
            lines=[
                TransactionLineIn(
                    account_id=str(self.asset_acct.id),
                    entry_type=EntryType.DEBIT,
                    amount=Decimal("500.00"),
                ),
                TransactionLineIn(
                    account_id=str(self.revenue_acct.id),
                    entry_type=EntryType.CREDIT,
                    amount=Decimal("500.00"),
                ),
            ]
        )
        
        tx = post_transaction(self.db, payload, str(self.user.id))
        
        assert tx is not None
        self.db.refresh(self.asset_acct)
        self.db.refresh(self.revenue_acct)
        
        # Asset Debit increases balance
        assert self.asset_acct.balance == Decimal("1500.00")
        # Income Credit increases balance
        assert self.revenue_acct.balance == Decimal("500.00")

    def test_unbalanced_transaction_rejected(self):
        """Test that unbalanced transactions raise an error."""
        payload = TransactionCreate(
            description="Unbalanced",
            lines=[
                TransactionLineIn(
                    account_id=str(self.asset_acct.id),
                    entry_type=EntryType.DEBIT,
                    amount=Decimal("500.00"),
                ),
                TransactionLineIn(
                    account_id=str(self.revenue_acct.id),
                    entry_type=EntryType.CREDIT,
                    amount=Decimal("499.00"),
                ),
            ]
        )
        
        with pytest.raises(ValidationError, match="does not balance"):
            post_transaction(self.db, payload, str(self.user.id))

    def test_insufficient_balance_rejected(self):
        """Test that an account not allowing negative balances rejects transactions that drop it below zero."""
        payload = TransactionCreate(
            description="Overdraft",
            lines=[
                TransactionLineIn(
                    account_id=str(self.asset_acct.id),
                    entry_type=EntryType.CREDIT,  # Credit to asset decreases it
                    amount=Decimal("1500.00"),    # Balance is only 1000
                ),
                TransactionLineIn(
                    account_id=str(self.expense_acct.id),
                    entry_type=EntryType.DEBIT,
                    amount=Decimal("1500.00"),
                ),
            ]
        )
        
        with pytest.raises(ValidationError, match="Insufficient balance"):
            post_transaction(self.db, payload, str(self.user.id))

    def test_currency_mismatch_rejected(self):
        """Test that lines with mismatched currencies are rejected."""
        eur_acct = create_account(
            self.db, self.user.id, "1001", "EUR Cash", AccountType.ASSET, currency="EUR", balance=1000.0
        )
        
        payload = TransactionCreate(
            description="Currency Mismatch",
            lines=[
                TransactionLineIn(
                    account_id=str(self.asset_acct.id), # USD
                    entry_type=EntryType.DEBIT,
                    amount=Decimal("100.00"),
                ),
                TransactionLineIn(
                    account_id=str(eur_acct.id),        # EUR
                    entry_type=EntryType.CREDIT,
                    amount=Decimal("100.00"),
                ),
            ]
        )
        
        with pytest.raises(ValidationError, match="require FX handling"):
            post_transaction(self.db, payload, str(self.user.id))
