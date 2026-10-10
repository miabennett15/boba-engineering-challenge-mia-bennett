import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database import Base
from app.services.models import Trade
from scripts.setup_database import ensure_database_exists


app = FastAPI(title="Trades API", version="1.0.0")

DATABASE_URL = ensure_database_exists()
engine = create_engine(DATABASE_URL)


class TradeResponse(BaseModel):
    trade_id: int
    commodity: str
    contract: str
    size: float
    trader: str
    source_file: str

    model_config = ConfigDict(from_attributes=True)


class PositionResponse(BaseModel):
    commodity: str
    contract: str
    net_quantity: float


@app.get("/trades/{trade_id}", response_model=TradeResponse)
def get_trade(trade_id: int):
    with Session(engine) as session:
        trade = session.execute(
            select(Trade).where(Trade.trade_id == trade_id)
        ).scalar_one_or_none()

    if trade is None:
        raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")

    return trade


@app.get("/trades", response_model=list[TradeResponse])
def list_trades(
    commodity: Optional[str] = Query(default=None),
    contract: Optional[str] = Query(default=None),
    trader: Optional[str] = Query(default=None),
):
    stmt = select(Trade)

    if commodity is not None:
        stmt = stmt.where(Trade.commodity == commodity.upper())
    if contract is not None:
        stmt = stmt.where(Trade.contract == contract.upper())
    if trader is not None:
        stmt = stmt.where(Trade.trader == trader.title())

    stmt = stmt.order_by(Trade.trade_id)

    with Session(engine) as session:
        trades = session.execute(stmt).scalars().all()

    return trades


@app.get("/positions", response_model=list[PositionResponse])
def get_positions(
    commodity: Optional[str] = Query(default=None),
    contract: Optional[str] = Query(default=None),
):
    stmt = (
        select(
            Trade.commodity,
            Trade.contract,
            func.sum(Trade.size).label("net_quantity"),
        )
        .group_by(Trade.commodity, Trade.contract)
        .order_by(Trade.commodity, Trade.contract)
    )

    if commodity is not None:
        stmt = stmt.where(Trade.commodity == commodity.upper())
    if contract is not None:
        stmt = stmt.where(Trade.contract == contract.upper())

    with Session(engine) as session:
        rows = session.execute(stmt).all()

    return [
        {
            "commodity": row[0],
            "contract": row[1],
            "net_quantity": float(row[2] or 0),
        }
        for row in rows
    ]


@app.get("/")
def health_check():
    return {"status": "ok", "service": "trades-api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
