"""User settings model — stores per-user encrypted API keys and preferences."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    anthropic_api_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    theme: Mapped[str] = mapped_column(String(20), default="light")
    notifications_enabled: Mapped[bool] = mapped_column(default=True)
    monthly_budget: Mapped[float | None] = mapped_column(nullable=True)
    emergency_fund_target: Mapped[float | None] = mapped_column(nullable=True)
    retirement_age: Mapped[int | None] = mapped_column(nullable=True)
    risk_profile: Mapped[str | None] = mapped_column(String(20), nullable=True)  # conservative, moderate, aggressive
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
