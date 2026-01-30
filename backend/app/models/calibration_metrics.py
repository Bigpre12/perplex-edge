"""CalibrationMetrics model for tracking model calibration over time."""

from datetime import date as date_type
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, Float, Integer, String, Date, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.sport import Sport


class CalibrationMetrics(Base):
    """
    Stores calibration metrics by probability bucket for tracking model accuracy.
    
    Calibration measures whether predicted probabilities match actual hit rates.
    E.g., if you predict 60% confidence, ~60% of those picks should hit.
    
    Computed daily for each sport and probability bucket to track drift over time.
    """
    
    __tablename__ = "calibration_metrics"
    __table_args__ = (
        Index("ix_calibration_date_sport", "date", "sport_id"),
        Index("ix_calibration_bucket", "probability_bucket"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    
    # Probability bucket (e.g., "50-55", "55-60", "60-65", etc.)
    probability_bucket: Mapped[str] = mapped_column(String(10), nullable=False)
    bucket_min: Mapped[float] = mapped_column(Float, nullable=False)
    bucket_max: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Calibration metrics
    predicted_prob: Mapped[float] = mapped_column(Float, nullable=False)
    # Average predicted probability in this bucket
    
    actual_hit_rate: Mapped[float] = mapped_column(Float, nullable=False)
    # Actual percentage of picks that hit in this bucket
    
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    # Number of picks in this bucket
    
    brier_score: Mapped[float] = mapped_column(Float, nullable=False)
    # Brier score = mean((predicted - actual)^2). Lower is better.
    # Perfect calibration = 0, worst = 1
    
    # ROI tracking
    total_wagered: Mapped[float] = mapped_column(Float, default=0.0)
    # Total units wagered in this bucket (e.g., $100 per pick)
    
    total_profit: Mapped[float] = mapped_column(Float, default=0.0)
    # Net profit/loss in this bucket
    
    roi_percent: Mapped[float] = mapped_column(Float, default=0.0)
    # ROI percentage = (total_profit / total_wagered) * 100
    
    # Average CLV for picks in this bucket
    avg_clv_cents: Mapped[Optional[float]] = mapped_column(Float)
    
    # Relationships
    sport: Mapped["Sport"] = relationship()

    def __repr__(self) -> str:
        return (
            f"<CalibrationMetrics(date={self.date}, bucket='{self.probability_bucket}', "
            f"predicted={self.predicted_prob:.1%}, actual={self.actual_hit_rate:.1%}, n={self.sample_size})>"
        )
