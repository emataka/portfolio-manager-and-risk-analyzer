"""Import one validated portfolio JSON snapshot into the local SQLite database."""

import argparse
import os
from pathlib import Path

from core.persistence.portfolio_store import load_portfolio

from api.database import run_migrations
from api.repository import SQLitePortfolioRepository


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default=os.environ.get("PORTFOLIO_API_FILE"),
        help="Source portfolio JSON file (defaults to PORTFOLIO_API_FILE).",
    )
    parser.add_argument(
        "--database",
        default=os.environ.get("PORTFOLIO_API_DB", "data/portfolio.sqlite3"),
        help="SQLite database path (defaults to PORTFOLIO_API_DB or data/portfolio.sqlite3).",
    )
    parser.add_argument(
        "--portfolio-id",
        default=os.environ.get("PORTFOLIO_API_PORTFOLIO_ID", "local"),
        help="Local portfolio identifier (default: local).",
    )
    parser.add_argument("--name", default="Local portfolio", help="Display name for the portfolio.")
    args = parser.parse_args()

    if not args.source:
        parser.error("Provide --source or set PORTFOLIO_API_FILE to a portfolio JSON file.")

    source = Path(args.source).expanduser()
    try:
        portfolio = load_portfolio(source)
        run_migrations(args.database)
        imported = SQLitePortfolioRepository(args.database).import_once(
            args.portfolio_id,
            args.name,
            portfolio,
        )
    except Exception as error:
        parser.exit(2, f"Migration failed; database import was not completed: {error}\n")

    if imported:
        print(f"Imported {len(portfolio.transactions)} ledger events into SQLite.")
    else:
        print("This exact portfolio snapshot was already imported; database was not changed.")
    print(f"Database: {Path(args.database).expanduser().resolve()}")
    print(f"Portfolio id: {args.portfolio_id}")


if __name__ == "__main__":
    main()
