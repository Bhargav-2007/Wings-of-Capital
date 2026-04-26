from decimal import Decimal
import datetime as dt
import uuid


def test_trial_balance_and_reports(test_client, db_session):
    from ledger_service.main import app as ledger_app
    from ledger_service.models.account import Account
    from ledger_service.models.enums import AccountType, EntryType
    from ledger_service.ledger.posting import post_transaction
    from ledger_service.schemas.transactions import TransactionCreate, TransactionLineIn
    import ledger_service.dependencies as deps

    user_id = uuid.uuid4()

    # Create accounts for different types
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

    # Debug: show initial balances and id types
    print("DEBUG initial:", str(acct_asset.id), type(acct_asset.id), acct_asset.balance)
    print("DEBUG initial income:", str(acct_income.id), acct_income.balance)
    print("DEBUG initial expense:", str(acct_expense.id), acct_expense.balance)

    # Post a sale (debit asset, credit income)
    lines_sale = [
        TransactionLineIn(account_id=str(acct_asset.id), entry_type=EntryType.DEBIT, amount=Decimal("50.00")),
        TransactionLineIn(account_id=str(acct_income.id), entry_type=EntryType.CREDIT, amount=Decimal("50.00")),
    ]
    sale_payload = TransactionCreate(description="Sale", reference="S-1", lines=lines_sale)
    post_transaction(db_session, sale_payload, str(user_id))

    # Debug: after sale
    db_session.refresh(acct_asset)
    db_session.refresh(acct_income)
    print("DEBUG after sale asset:", acct_asset.balance)
    print("DEBUG after sale income:", acct_income.balance)

    # Post an expense (debit expense, credit asset)
    lines_exp = [
        TransactionLineIn(account_id=str(acct_expense.id), entry_type=EntryType.DEBIT, amount=Decimal("20.00")),
        TransactionLineIn(account_id=str(acct_asset.id), entry_type=EntryType.CREDIT, amount=Decimal("20.00")),
    ]
    exp_payload = TransactionCreate(description="Expense", reference="E-1", lines=lines_exp)
    post_transaction(db_session, exp_payload, str(user_id))

    # Debug: after expense
    db_session.refresh(acct_asset)
    db_session.refresh(acct_expense)
    print("DEBUG after expense asset:", acct_asset.balance)
    print("DEBUG after expense expense:", acct_expense.balance)

    # Call report endpoints via test client
    ledger_app.dependency_overrides[deps.get_current_user_id] = lambda: str(user_id)
    client = test_client(ledger_app)

    period_start = dt.date.today() - dt.timedelta(days=1)
    period_end = dt.date.today() + dt.timedelta(days=1)

    # Trial balance
    res = client.get(
        "/api/v1/ledger/reports/trial-balance",
        params={"period_start": period_start.isoformat(), "period_end": period_end.isoformat()},
    )
    assert res.status_code == 200
    tb = res.json()
    total_debits = Decimal(str(tb["total_debits"]))
    total_credits = Decimal(str(tb["total_credits"]))
    assert total_debits == total_credits
    assert total_debits == Decimal("70.00")

    # Income statement
    res = client.get(
        "/api/v1/ledger/reports/income-statement",
        params={"period_start": period_start.isoformat(), "period_end": period_end.isoformat()},
    )
    assert res.status_code == 200
    is_data = res.json()
    total_income = Decimal(str(is_data["total_income"]))
    total_expense = Decimal(str(is_data["total_expense"]))
    assert total_income == Decimal("50.00")
    assert total_expense == Decimal("20.00")

    # Balance sheet (as_of_date omitted -> uses account balances)
    res = client.get("/api/v1/ledger/reports/balance-sheet")
    assert res.status_code == 200
    bs = res.json()
    total_assets = Decimal(str(bs["total_assets"]))
    # asset started 100 +50 -20 = 130
    assert total_assets == Decimal("130.00")
