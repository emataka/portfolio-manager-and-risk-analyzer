"""Apply pending schema migrations to the local SQLite database."""

import argparse
import os
from pathlib import Path

from api.database import run_migrations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database",
        default=os.environ.get("PORTFOLIO_API_DB", "data/portfolio.sqlite3"),
        help="SQLite database path (defaults to PORTFOLIO_API_DB or data/portfolio.sqlite3).",
    )
    args = parser.parse_args()
    database = Path(args.database).expanduser()
    try:
        run_migrations(database)
    except Exception as error:
        parser.exit(2, f"Database migration failed: {error}\n")
    print(f"Database schema is up to date: {database.resolve()}")


if __name__ == "__main__":
    main()
