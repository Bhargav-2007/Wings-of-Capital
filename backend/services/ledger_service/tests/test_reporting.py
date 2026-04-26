# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Tests for Ledger Reporting Logic."""

import pytest
import datetime as dt
from decimal import Decimal
from sqlalchemy.orm import Session

from backend.tests.factories import create_user, create_account
from ledger_service.ledger.posting import post_transaction
from ledger_service.ledger.reporting import trial_balance, income_statement, balance_sheet
from ledger_service.models.enums import AccountType, EntryType
from ledger_service.schemas.transactions import TransactionCreate, TransactionLineIn


class TestReportingLogic:

    @pytest.fixture(autouse=True)
    def setup(self, db_session: Session):
        self.db = db_session
        self.user = create_user(self.db, email="reporting@example.com")
        self.asset = create_account(self.db, self.user.id, "1000", "Cash", AccountType.ASSET)
        self.revenue = create_account(self.db, self.user.id, "4000", "Sales", AccountType.INCOME)
        self.expense = create_account(self.db, self.user.id, "5000", "Fees", AccountType.EXPENSE)
        self.liability = create_account(self.db, self.user.id, "2000", "Loan", AccountType.LIABILITY)
        self.equity = create_account(self.db, self.user.id, "3000", "Capital", AccountType.EQUITY)

    def test_trial_balance(self):
        # Transaction 1: Revenue
        post_transaction(self.db, TransactionCreate(
            description="Sale",
            transaction_date=dt.datetime.now(dt.timezone.utc),
            lines=[
                TransactionLineIn(account_id=str(self.asset.id), entry_type=EntryType.DEBIT, amount=Decimal("1000.00")),
                TransactionLineIn(account_id=str(self.revenue.id), entry_type=EntryType.CREDIT, amount=Decimal("1000.00")),
            ]
        ), str(self.user.id))

        today = dt.date.today()
        accounts, opening, period, closing = trial_balance(self.db, str(self.user.id), today, today)
        
        assert str(self.asset.id) in closing
        assert str(self.revenue.id) in closing
        assert closing[str(self.asset.id)] == Decimal("1000.00")
        assert closing[str(self.revenue.id)] == Decimal("1000.00")

    def test_income_statement(self):
        # Transaction: Revenue 1000, Expense 200 => Net Income 800
        post_transaction(self.db, TransactionCreate(
            description="Sale",
            lines=[
                TransactionLineIn(account_id=str(self.asset.id), entry_type=EntryType.DEBIT, amount=Decimal("1000.00")),
                TransactionLineIn(account_id=str(self.revenue.id), entry_type=EntryType.CREDIT, amount=Decimal("1000.00")),
            ]
        ), str(self.user.id))
        
        post_transaction(self.db, TransactionCreate(
            description="Fee",
            lines=[
                TransactionLineIn(account_id=str(self.expense.id), entry_type=EntryType.DEBIT, amount=Decimal("200.00")),
                TransactionLineIn(account_id=str(self.asset.id), entry_type=EntryType.CREDIT, amount=Decimal("200.00")),
            ]
        ), str(self.user.id))

        today = dt.date.today()
        income, expense = income_statement(self.db, str(self.user.id), today, today)
        
        assert income == Decimal("1000.00")
        assert expense == Decimal("200.00")
        assert income - expense == Decimal("800.00")

    def test_balance_sheet(self):
        # Asset: +1000 - 200 = 800
        # Revenue: +1000
        # Expense: +200
        post_transaction(self.db, TransactionCreate(
            description="Capital injection",
            lines=[
                TransactionLineIn(account_id=str(self.asset.id), entry_type=EntryType.DEBIT, amount=Decimal("5000.00")),
                TransactionLineIn(account_id=str(self.equity.id), entry_type=EntryType.CREDIT, amount=Decimal("5000.00")),
            ]
        ), str(self.user.id))
        
        assets, liabilities, equity = balance_sheet(self.db, str(self.user.id), dt.date.today())
        
        assert assets == Decimal("5000.00")
        assert equity == Decimal("5000.00")
        assert liabilities == Decimal("0.00")
