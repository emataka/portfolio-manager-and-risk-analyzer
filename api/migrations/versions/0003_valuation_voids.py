"""Add append-only correction markers for valuation points."""

from alembic import op
import sqlalchemy as sa


revision = "0003_valuation_voids"
down_revision = "0002_portfolio_valuations"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "portfolio_valuation_voids",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "valuation_id",
            sa.Integer(),
            sa.ForeignKey("portfolio_valuations.id", ondelete="RESTRICT"),
            nullable=False,
            unique=True,
        ),
        sa.Column("reason", sa.String(length=250), nullable=False),
        sa.Column("voided_at", sa.String(length=40), nullable=False),
    )
    op.execute(
        "CREATE TRIGGER portfolio_valuation_voids_no_update "
        "BEFORE UPDATE ON portfolio_valuation_voids BEGIN "
        "SELECT RAISE(ABORT, 'portfolio valuation corrections are append-only'); END"
    )
    op.execute(
        "CREATE TRIGGER portfolio_valuation_voids_no_delete "
        "BEFORE DELETE ON portfolio_valuation_voids BEGIN "
        "SELECT RAISE(ABORT, 'portfolio valuation corrections are append-only'); END"
    )


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS portfolio_valuation_voids_no_delete")
    op.execute("DROP TRIGGER IF EXISTS portfolio_valuation_voids_no_update")
    op.drop_table("portfolio_valuation_voids")
