"""phase3 schema updates

Revision ID: 004_phase3_schema
Revises: 003_crypto_schema
Create Date: 2026-04-20 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "004_phase3_schema"
down_revision = "003_crypto_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("price_alerts", sa.Column("notify_email", sa.String(length=255), nullable=True))
    op.add_column("price_alerts", sa.Column("webhook_url", sa.String(length=2048), nullable=True))
    op.add_column(
        "price_alerts",
        sa.Column("notify_on_trigger", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.add_column("price_alerts", sa.Column("last_notified_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "ai_model_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric_name", sa.String(length=64), nullable=False),
        sa.Column("metric_value", sa.Numeric(24, 12), nullable=False),
        sa.Column("dataset_symbol", sa.String(length=16), nullable=True),
        sa.Column("dataset_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dataset_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dataset_size", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["model_id"], ["ai_models.id"]),
    )
    op.create_index("ix_ai_model_metrics_model_id", "ai_model_metrics", ["model_id"], unique=False)
    op.create_index("ix_ai_model_metrics_metric_name", "ai_model_metrics", ["metric_name"], unique=False)
    op.create_index("ix_ai_model_metrics_dataset_symbol", "ai_model_metrics", ["dataset_symbol"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ai_model_metrics_dataset_symbol", table_name="ai_model_metrics")
    op.drop_index("ix_ai_model_metrics_metric_name", table_name="ai_model_metrics")
    op.drop_index("ix_ai_model_metrics_model_id", table_name="ai_model_metrics")
    op.drop_table("ai_model_metrics")

    op.drop_column("price_alerts", "last_notified_at")
    op.drop_column("price_alerts", "notify_on_trigger")
    op.drop_column("price_alerts", "webhook_url")
    op.drop_column("price_alerts", "notify_email")
