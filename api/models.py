from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PortfolioRow(Base):
    __tablename__ = "portfolios"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    cash_history_complete: Mapped[bool] = mapped_column(Boolean, nullable=False)
    migration_warnings_json: Mapped[str] = mapped_column(Text, nullable=False)
    content_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[str] = mapped_column(String(40), nullable=False)


class PortfolioEventRow(Base):
    __tablename__ = "portfolio_events"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "sequence", name="uq_portfolio_event_sequence"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id", ondelete="RESTRICT"), nullable=False
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    record_type: Mapped[str] = mapped_column(String(10), nullable=False)
    event_json: Mapped[str] = mapped_column(Text, nullable=False)


class PortfolioPriceRow(Base):
    __tablename__ = "portfolio_prices"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "ticker", name="uq_portfolio_price_ticker"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    portfolio_id: Mapped[str] = mapped_column(
        ForeignKey("portfolios.id", ondelete="RESTRICT"), nullable=False
    )
    ticker: Mapped[str] = mapped_column(String(32), nullable=False)
    market: Mapped[str] = mapped_column(String(2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    current_price: Mapped[str] = mapped_column(String(80), nullable=False)


class PortfolioValuationRow(Base):
    __tablename__ = "portfolio_valuations"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "currency", "sequence", name="uq_portfolio_valuation_sequence"),
        UniqueConstraint("portfolio_id", "currency", "valuation_at", name="uq_portfolio_valuation_timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    portfolio_id: Mapped[str] = mapped_column(ForeignKey("portfolios.id", ondelete="RESTRICT"), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    valuation_at: Mapped[str] = mapped_column(String(40), nullable=False)
    market_value: Mapped[str] = mapped_column(String(80), nullable=False)
    external_flow_after: Mapped[str] = mapped_column(String(80), nullable=False)
    source: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[str] = mapped_column(String(40), nullable=False)


class PortfolioValuationVoidRow(Base):
    __tablename__ = "portfolio_valuation_voids"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    valuation_id: Mapped[int] = mapped_column(
        ForeignKey("portfolio_valuations.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    reason: Mapped[str] = mapped_column(String(250), nullable=False)
    voided_at: Mapped[str] = mapped_column(String(40), nullable=False)
