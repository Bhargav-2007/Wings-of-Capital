"""crypto schema

Revision ID: 003_crypto_schema
Revises: 002_ledger_schema
Create Date: 2026-04-19 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003_crypto_schema"
down_revision = "002_ledger_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "holdings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("symbol", sa.String(length=16), nullable=False),
        sa.Column("quantity", sa.Numeric(24, 12), nullable=False),
        sa.Column("cost_basis", sa.Numeric(24, 12), nullable=False),
        sa.Column("acquired_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_holdings_user_id", "holdings", ["user_id"], unique=False)
    op.create_index("ix_holdings_symbol", "holdings", ["symbol"], unique=False)

    op.create_table(
        "market_prices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("symbol", sa.String(length=16), nullable=False),
        sa.Column("price_usd", sa.Numeric(24, 12), nullable=False),
        sa.Column("volume_24h", sa.Numeric(24, 12), nullable=False),
        sa.Column("market_cap", sa.Numeric(24, 12), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_market_prices_symbol", "market_prices", ["symbol"], unique=False)
    op.create_index("ix_market_prices_timestamp", "market_prices", ["timestamp"], unique=False)

    op.create_table(
        "price_alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("symbol", sa.String(length=16), nullable=False),
        sa.Column("target_price", sa.Numeric(24, 12), nullable=False),
        sa.Column(
            "condition",
            sa.Enum("ABOVE", "BELOW", name="price_alert_condition"),
            nullable=False,
        ),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_price_alerts_user_id", "price_alerts", ["user_id"], unique=False)
    op.create_index("ix_price_alerts_symbol", "price_alerts", ["symbol"], unique=False)

    op.create_table(
        "ai_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("accuracy", sa.Numeric(6, 4), nullable=False, server_default="0"),
        sa.Column("deployment_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "ARCHIVED", name="ai_model_status"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("ai_models")
    op.drop_index("ix_price_alerts_symbol", table_name="price_alerts")
    op.drop_index("ix_price_alerts_user_id", table_name="price_alerts")
    op.drop_table("price_alerts")
    op.drop_index("ix_market_prices_timestamp", table_name="market_prices")
    op.drop_index("ix_market_prices_symbol", table_name="market_prices")
    op.drop_table("market_prices")
    op.drop_index("ix_holdings_symbol", table_name="holdings")
    op.drop_index("ix_holdings_user_id", table_name="holdings")
    op.drop_table("holdings")
    op.execute("DROP TYPE IF EXISTS ai_model_status")
    op.execute("DROP TYPE IF EXISTS price_alert_condition")
