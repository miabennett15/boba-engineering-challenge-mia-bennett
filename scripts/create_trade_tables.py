import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from app.database import Base
from app.services.models import Trade
from scripts.setup_database import ensure_database_exists


load_dotenv()


def load_trades_from_excel() -> tuple[list[dict], int]:
    '''
    Load trades from the Excel file, clean the data, and return a list of dictionaries
    representing the trades and the number of skipped rows due to missing or invalid data.
    '''
    project_root = Path(__file__).resolve().parents[1]
    excel_path = project_root / "data" / "trades.xlsx"

    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    df = pd.read_excel(excel_path)

    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]

    rename_map = {
        "trade_id": "trade_id",
        "tradeid": "trade_id",
        "commodity": "commodity",
        "contract": "contract",
        "size": "size",
        "trader": "trader",
        "source_file": "source_file",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    required = ["trade_id", "commodity", "contract", "size", "trader"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required Excel columns: {missing}. "
            f"Available columns: {list(df.columns)}"
        )

    cleaned_rows: list[dict] = []
    skipped_rows = 0
    seen_trade_ids: set[int] = set()

    for _, row in df[required].iterrows():
        try:
            trade_id = int(float(row["trade_id"]))
        except (TypeError, ValueError):
            skipped_rows += 1
            continue

        commodity = str(row["commodity"]).strip() if not pd.isna(row["commodity"]) else ""
        contract = str(row["contract"]).strip() if not pd.isna(row["contract"]) else ""
        trader = str(row["trader"]).strip() if not pd.isna(row["trader"]) else ""
        size = pd.to_numeric(row["size"], errors="coerce")

        if not commodity or not contract or not trader or pd.isna(size):
            skipped_rows += 1
            continue

        if trade_id in seen_trade_ids:
            skipped_rows += 1
            continue

        seen_trade_ids.add(trade_id)
        cleaned_rows.append(
            {
                "trade_id": trade_id,
                "commodity": commodity.upper(),
                "contract": contract.upper(),
                "size": float(size),
                "trader": trader.title(),
                "source_file": excel_path.name,
            }
        )

    return cleaned_rows, skipped_rows


def create_tables() -> None:
    database_url = ensure_database_exists()
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)

    rows_to_insert, skipped_rows = load_trades_from_excel()

    inserted_count = 0
    with Session(engine) as session:
        existing_trade_ids = set(session.execute(select(Trade.trade_id)).scalars().all())
        for row in rows_to_insert:
            if row["trade_id"] not in existing_trade_ids:
                session.add(Trade(**row))
                inserted_count += 1
                existing_trade_ids.add(row["trade_id"])

        session.commit()

    with engine.connect() as connection:
        table_exists = connection.execute(
            text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'trades')")
        ).scalar()
        row_count = connection.execute(text("SELECT COUNT(*) FROM trades")).scalar()

    print(f"Database tables created and data loaded from {Path(__file__).resolve().parents[1] / 'data' / 'trades.xlsx'}")
    print(f"Table exists: {table_exists}")
    print(f"Rows inserted: {inserted_count}")
    print(f"Rows skipped (missing/invalid/duplicate): {skipped_rows}")
    print(f"Row count in trades: {row_count}")


if __name__ == "__main__":
    create_tables()
