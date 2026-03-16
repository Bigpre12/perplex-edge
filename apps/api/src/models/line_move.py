from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base

class LineMove(Base):
    __tablename__ = "line_moves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sport: Mapped[str] = mapped_column(String, index=True, nullable=False)
    player: Mapped[str] = mapped_column(String, index=True, nullable=False)
    market: Mapped[str] = mapped_column(String, nullable=False)
    open_line: Mapped[float] = mapped_column(Float, nullable=False)
    current_line: Mapped[float] = mapped_column(Float, nullable=False)
    direction: Mapped[str] = mapped_column(String, nullable=False)
    book: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
