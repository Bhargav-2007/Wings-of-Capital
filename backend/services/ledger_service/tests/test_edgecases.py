from decimal import Decimal
import datetime as dt
import uuid

import pytest

from shared.exceptions import ValidationError


def test_multi_currency_transaction_rejected(db_session):
    from ledger_service.models.account import Account
    from ledger_service.models.enums import AccountType, EntryType
    from ledger_service.schemas.transactions import TransactionCreate, TransactionLineIn
    from ledger_service.ledger.posting import post_transaction

    user_id = uuid.uuid4()

    acct_usd = Account(
        user_id=user_id,
        account_number="1000",
        account_name="Cash",
        account_type=AccountType.ASSET,
        currency="USD",
        balance=Decimal("100.00"),
        allow_negative=False,
        is_active=True,
    )

    acct_eur = Account(
        user_id=user_id,
        account_number="2000",
        account_name="SalesEUR",
        account_type=AccountType.INCOME,
        currency="EUR",
        balance=Decimal("0.00"),
        allow_negative=False,
        is_active=True,
    )

    db_session.add_all([acct_usd, acct_eur])
    db_session.flush()
    db_session.refresh(acct_usd)
    db_session.refresh(acct_eur)

    lines = [
        TransactionLineIn(account_id=str(acct_usd.id), entry_type=EntryType.DEBIT, amount=Decimal("10.00")),
        TransactionLineIn(account_id=str(acct_eur.id), entry_type=EntryType.CREDIT, amount=Decimal("10.00")),
    ]

    payload = TransactionCreate(description="FX", reference="FX-1", lines=lines)

    with pytest.raises(ValidationError):
        post_transaction(db_session, payload, str(user_id))


def test_allow_negative_allows_overdraft(db_session):
    from ledger_service.models.account import Account
    from ledger_service.models.enums import AccountType, EntryType
    from ledger_service.schemas.transactions import TransactionCreate, TransactionLineIn
    from ledger_service.ledger.posting import post_transaction

    user_id = uuid.uuid4()

    acct_asset = Account(
        user_id=user_id,
        account_number="1100",
        account_name="Cash",
        account_type=AccountType.ASSET,
        currency="USD",
        balance=Decimal("0.00"),
        allow_negative=True,
        is_active=True,
    )

    acct_liab = Account(
        user_id=user_id,
        account_number="2100",
        account_name="Payable",
        account_type=AccountType.LIABILITY,
        currency="USD",
        balance=Decimal("0.00"),
        allow_negative=True,
        is_active=True,
    )

    db_session.add_all([acct_asset, acct_liab])
    db_session.flush()
    db_session.refresh(acct_asset)
    db_session.refresh(acct_liab)

    lines = [
        TransactionLineIn(account_id=str(acct_asset.id), entry_type=EntryType.CREDIT, amount=Decimal("50.00")),
        TransactionLineIn(account_id=str(acct_liab.id), entry_type=EntryType.DEBIT, amount=Decimal("50.00")),
    ]

    payload = TransactionCreate(description="Overdraft", reference="OD-1", lines=lines)
    txn = post_transaction(db_session, payload, str(user_id))

    assert txn is not None
    db_session.refresh(acct_asset)
    db_session.refresh(acct_liab)
    assert acct_asset.balance < 0
    assert acct_liab.balance < 0


def test_balance_as_of_date_uses_transaction_lines(test_client, db_session):
    from ledger_service.main import app as ledger_app
    from ledger_service.models.account import Account
    from ledger_service.models.enums import AccountType, EntryType
    from ledger_service.schemas.transactions import TransactionCreate, TransactionLineIn
    from ledger_service.ledger.posting import post_transaction
    import ledger_service.dependencies as deps

    user_id = uuid.uuid4()

    acct_asset = Account(
        user_id=user_id,
        account_number="1000",
        account_name="Cash",
        account_type=AccountType.ASSET,
        currency="USD",
        balance=Decimal("100.00"),
        allow_negative=False,
        is_active=True,
    )

    acct_income = Account(
        user_id=user_id,
        account_number="4000",
        account_name="Sales",
        account_type=AccountType.INCOME,
        currency="USD",
        balance=Decimal("0.00"),
        allow_negative=False,
        is_active=True,
    )

    acct_expense = Account(
        user_id=user_id,
        account_number="5000",
        account_name="Expenses",
        account_type=AccountType.EXPENSE,
        currency="USD",
        balance=Decimal("0.00"),
        allow_negative=False,
        is_active=True,
    )

    db_session.add_all([acct_asset, acct_income, acct_expense])
    db_session.flush()
    db_session.refresh(acct_asset)
    db_session.refresh(acct_income)
    db_session.refresh(acct_expense)

    now = dt.datetime.now(dt.timezone.utc)
    day1 = now - dt.timedelta(days=2)
    day2 = now - dt.timedelta(days=1)

    sale_lines = [
        TransactionLineIn(account_id=str(acct_asset.id), entry_type=EntryType.DEBIT, amount=Decimal("50.00")),
        TransactionLineIn(account_id=str(acct_income.id), entry_type=EntryType.CREDIT, amount=Decimal("50.00")),
    ]
    sale_payload = TransactionCreate(description="Sale", reference="S-1", transaction_date=day1, lines=sale_lines)
    post_transaction(db_session, sale_payload, str(user_id))

    exp_lines = [
        TransactionLineIn(account_id=str(acct_expense.id), entry_type=EntryType.DEBIT, amount=Decimal("20.00")),
        TransactionLineIn(account_id=str(acct_asset.id), entry_type=EntryType.CREDIT, amount=Decimal("20.00")),
    ]
    exp_payload = TransactionCreate(description="Expense", reference="E-1", transaction_date=day2, lines=exp_lines)
    post_transaction(db_session, exp_payload, str(user_id))

    ledger_app.dependency_overrides[deps.get_current_user_id] = lambda: str(user_id)
    client = test_client(ledger_app)

    as_of_day1 = (now - dt.timedelta(days=2)).date().isoformat()
    res1 = client.get("/api/v1/ledger/reports/balance-sheet", params={"as_of_date": as_of_day1})
    assert res1.status_code == 200
    bs1 = res1.json()
    total_assets = Decimal(str(bs1["total_assets"]))
    assert total_assets == Decimal("150.00")
