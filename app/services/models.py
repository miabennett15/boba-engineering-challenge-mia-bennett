from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    trade_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
    )

    commodity: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    contract: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    size: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    trader: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    source_file: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )