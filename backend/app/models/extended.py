"""Goal-based financial planning models."""
import enum
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GoalPriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    ACHIEVED = "achieved"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class FinancialGoal(Base):
    __tablename__ = "financial_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority: Mapped[GoalPriority] = mapped_column(Enum(GoalPriority), default=GoalPriority.MEDIUM)
    status: Mapped[GoalStatus] = mapped_column(Enum(GoalStatus), default=GoalStatus.ACTIVE)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)  # retirement, education, house, marriage, emergency, travel, car, other
    monthly_sip_needed: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    expected_return_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    inflation_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), default=6.0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class InsurancePolicy(Base):
    """Insurance — term, health, ULIP, endowment, motor."""
    __tablename__ = "insurance_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)  # term, health, ulip, endowment, motor, travel
    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    policy_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sum_assured: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    annual_premium: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    premium_frequency: Mapped[str] = mapped_column(String(20), default="annual")  # monthly, quarterly, annual
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    maturity_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_premium_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    maturity_value: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)  # for ULIP/endowment
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    tax_section: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 80C, 80D, 80CCC
    nominees: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ESOPHolding(Base):
    """Employee Stock Options and RSUs."""
    __tablename__ = "esop_holdings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # esop, rsu
    total_granted: Mapped[int] = mapped_column(Integer, nullable=False)
    vested: Mapped[int] = mapped_column(Integer, default=0)
    exercised: Mapped[int] = mapped_column(Integer, default=0)
    strike_price: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    current_fmv: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    grant_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_vesting_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    vesting_schedule: Mapped[str | None] = mapped_column(Text, nullable=True)  # e.g., "25% per year over 4 years"
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class CryptoHolding(Base):
    """Crypto asset tracking."""
    __tablename__ = "crypto_holdings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    coin: Mapped[str] = mapped_column(String(20), nullable=False)  # BTC, ETH, etc.
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    avg_buy_price_inr: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    buy_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    exchange: Mapped[str | None] = mapped_column(String(50), nullable=True)  # WazirX, CoinSwitch, etc.
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class TaxDeduction(Base):
    """Tax deductions claimed under various sections."""
    __tablename__ = "tax_deductions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False)  # 2025-26
    section: Mapped[str] = mapped_column(String(20), nullable=False)  # 80C, 80D, 80G, 80E, 80CCD, 80TTA, HRA
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    max_limit: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    proof_available: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class Notification(Base):
    """System notifications and alerts."""
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)  # alert, reminder, info, warning
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    action_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
