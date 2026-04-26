from decimal import Decimal
import uuid


def test_create_and_list_transactions(test_client, db_session):
    from ledger_service.main import app as ledger_app
    from ledger_service.models.account import Account
    from ledger_service.models.enums import AccountType
    import ledger_service.dependencies as deps

    user_id = uuid.uuid4()

    # Create two accounts for the user
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

    acct_liab = Account(
        user_id=user_id,
        account_number="2000",
        account_name="Payable",
        account_type=AccountType.LIABILITY,
        currency="USD",
        balance=Decimal("0.00"),
        allow_negative=False,
        is_active=True,
    )

    db_session.add_all([acct_asset, acct_liab])
    db_session.flush()
    db_session.refresh(acct_asset)
    db_session.refresh(acct_liab)

    # Override auth dependency to simulate authenticated user
    ledger_app.dependency_overrides[deps.get_current_user_id] = lambda: str(user_id)
    client = test_client(ledger_app)

    payload = {
        "description": "Test",
        "reference": "T-1",
        "lines": [
            {"account_id": str(acct_asset.id), "entry_type": "DEBIT", "amount": "10.00"},
            {"account_id": str(acct_liab.id), "entry_type": "CREDIT", "amount": "10.00"},
        ],
    }

    # Create transaction via API
    res = client.post("/api/v1/ledger/transactions", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["description"] == "Test"
    assert len(data["lines"]) == 2

    # List transactions
    res = client.get("/api/v1/ledger/transactions")
    assert res.status_code == 200
    page = res.json()
    assert page.get("total", 0) >= 1
