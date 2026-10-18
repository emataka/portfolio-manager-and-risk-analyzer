"""Add immutable, timestamped portfolio valuation history."""

from alembic import op
import sqlalchemy as sa


revision = "0002_portfolio_valuations"
down_revision = "0001_local_portfolio"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "portfolio_valuations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "portfolio_id",
            sa.String(length=64),
            sa.ForeignKey("portfolios.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("valuation_at", sa.String(length=40), nullable=False),
        sa.Column("market_value", sa.String(length=80), nullable=False),
        sa.Column("external_flow_after", sa.String(length=80), nullable=False),
        sa.Column("source", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.UniqueConstraint(
            "portfolio_id", "currency", "sequence", name="uq_portfolio_valuation_sequence"
        ),
        sa.UniqueConstraint(
            "portfolio_id", "currency", "valuation_at", name="uq_portfolio_valuation_timestamp"
        ),
        sa.CheckConstraint("currency IN ('USD', 'IRR')", name="ck_portfolio_valuation_currency"),
    )
    op.create_index(
        "ix_portfolio_valuations_order",
        "portfolio_valuations",
        ["portfolio_id", "currency", "sequence"],
    )
    op.execute(
        "CREATE TRIGGER portfolio_valuations_no_update "
        "BEFORE UPDATE ON portfolio_valuations BEGIN "
        "SELECT RAISE(ABORT, 'portfolio valuations are append-only'); END"
    )
    op.execute(
        "CREATE TRIGGER portfolio_valuations_no_delete "
        "BEFORE DELETE ON portfolio_valuations BEGIN "
        "SELECT RAISE(ABORT, 'portfolio valuations are append-only'); END"
    )


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS portfolio_valuations_no_delete")
    op.execute("DROP TRIGGER IF EXISTS portfolio_valuations_no_update")
    op.drop_index("ix_portfolio_valuations_order", table_name="portfolio_valuations")
    op.drop_table("portfolio_valuations")
