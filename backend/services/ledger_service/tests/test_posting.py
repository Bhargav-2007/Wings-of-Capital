from decimal import Decimal
import pytest


def test_post_transaction_balances_and_rejections(db_session):
    from ledger_service.models.account import Account
    from ledger_service.models.enums import AccountType, EntryType
    from ledger_service.ledger.posting import post_transaction
    from ledger_service.schemas.transactions import TransactionCreate, TransactionLineIn
    from shared.security import hash_password  # noqa: F401

    # Set up a user id
    import uuid
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

    # Build a balanced transaction (debit asset, credit liability)
    lines = [
        TransactionLineIn(account_id=str(acct_asset.id), entry_type=EntryType.DEBIT, amount=Decimal("10.00")),
        TransactionLineIn(account_id=str(acct_liab.id), entry_type=EntryType.CREDIT, amount=Decimal("10.00")),
    ]

    payload = TransactionCreate(description="Test", reference="T-1", lines=lines)
    txn = post_transaction(db_session, payload, str(user_id))
    assert txn is not None

    # Attempt an unbalanced transaction -> should raise ValidationError
    from shared.exceptions import ValidationError

    bad_lines = [
        TransactionLineIn(account_id=str(acct_asset.id), entry_type=EntryType.DEBIT, amount=Decimal("5.00")),
        TransactionLineIn(account_id=str(acct_liab.id), entry_type=EntryType.CREDIT, amount=Decimal("3.00")),
    ]
    bad_payload = TransactionCreate(lines=bad_lines)
    with pytest.raises(ValidationError):
        post_transaction(db_session, bad_payload, str(user_id))

    # Attempt a transaction that would push an account negative (crediting an asset beyond balance)
    bad_lines2 = [
        TransactionLineIn(account_id=str(acct_asset.id), entry_type=EntryType.CREDIT, amount=Decimal("9999.00")),
        TransactionLineIn(account_id=str(acct_liab.id), entry_type=EntryType.DEBIT, amount=Decimal("9999.00")),
    ]
    bad_payload2 = TransactionCreate(lines=bad_lines2)
    with pytest.raises(ValidationError):
        post_transaction(db_session, bad_payload2, str(user_id))
