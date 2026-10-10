import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()


def get_database_url() -> str:
    database = os.getenv("DATABASE_NAME")
    user = os.getenv("DATABASE_USER")
    password = os.getenv("DATABASE_PASSWORD")
    host = os.getenv("DATABASE_HOST")
    port = os.getenv("DATABASE_PORT")

    if not all([database, user, password, host, port]):
        raise ValueError(
            "Missing one or more database environment variables: "
            "DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT"
        )

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def ensure_database_exists() -> str:
    database = os.getenv("DATABASE_NAME")
    user = os.getenv("DATABASE_USER")
    password = os.getenv("DATABASE_PASSWORD")
    host = os.getenv("DATABASE_HOST")
    port = os.getenv("DATABASE_PORT")

    if not all([database, user, password, host, port]):
        raise ValueError(
            "Missing one or more database environment variables: "
            "DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT"
        )

    admin_url = f"postgresql://{user}:{password}@{host}:{port}/postgres"
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    with admin_engine.connect() as connection:
        result = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": database},
        )
        if result.scalar() is None:
            connection.execute(text(f'CREATE DATABASE "{database}"'))

    return get_database_url()


if __name__ == "__main__":
    ensure_database_exists()
    print("Database setup complete.")