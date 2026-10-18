from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker


def database_url(path):
    resolved = Path(path).expanduser().resolve()
    return URL.create("sqlite", database=str(resolved))


def make_engine(path):
    resolved = Path(path).expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        database_url(resolved),
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def run_migrations(path):
    resolved = Path(path).expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    project_root = Path(__file__).resolve().parent.parent
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "api" / "migrations"))
    config.set_main_option(
        "sqlalchemy.url",
        # ConfigParser treats '%' as interpolation syntax; Alembic will
        # unescape this when reading the option before SQLAlchemy parses it.
        database_url(resolved).render_as_string(hide_password=False).replace("%", "%%"),
    )
    command.upgrade(config, "head")


def make_session_factory(path):
    return sessionmaker(bind=make_engine(path), expire_on_commit=False)
