"""Create local portfolio and immutable ledger tables."""

from alembic import op
import sqlalchemy as sa


revision = "0001_local_portfolio"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "portfolios",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("cash_history_complete", sa.Boolean(), nullable=False),
        sa.Column("migration_warnings_json", sa.Text(), nullable=False),
        sa.Column("content_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
    )
    op.create_table(
        "portfolio_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "portfolio_id",
            sa.String(length=64),
            sa.ForeignKey("portfolios.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("record_type", sa.String(length=10), nullable=False),
        sa.Column("event_json", sa.Text(), nullable=False),
        sa.UniqueConstraint("portfolio_id", "sequence", name="uq_portfolio_event_sequence"),
        sa.CheckConstraint("record_type IN ('TRADE', 'CASH')", name="ck_portfolio_event_type"),
    )
    op.create_table(
        "portfolio_prices",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "portfolio_id",
            sa.String(length=64),
            sa.ForeignKey("portfolios.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("market", sa.String(length=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("current_price", sa.String(length=80), nullable=False),
        sa.UniqueConstraint("portfolio_id", "ticker", name="uq_portfolio_price_ticker"),
    )
    op.create_index(
        "ix_portfolio_events_order",
        "portfolio_events",
        ["portfolio_id", "sequence"],
    )
    op.execute(
        "CREATE TRIGGER portfolio_events_no_update "
        "BEFORE UPDATE ON portfolio_events BEGIN "
        "SELECT RAISE(ABORT, 'portfolio events are append-only'); END"
    )
    op.execute(
        "CREATE TRIGGER portfolio_events_no_delete "
        "BEFORE DELETE ON portfolio_events BEGIN "
        "SELECT RAISE(ABORT, 'portfolio events are append-only'); END"
    )


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS portfolio_events_no_delete")
    op.execute("DROP TRIGGER IF EXISTS portfolio_events_no_update")
    op.drop_index("ix_portfolio_events_order", table_name="portfolio_events")
    op.drop_table("portfolio_prices")
    op.drop_table("portfolio_events")
    op.drop_table("portfolios")
