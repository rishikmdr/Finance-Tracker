import enum
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# --- Enums ---

class Exchange(str, enum.Enum):
    NSE = "NSE"
    BSE = "BSE"


class InvestmentType(str, enum.Enum):
    LONG_TERM = "long_term"
    SWING = "swing"
    POSITIONAL = "positional"
    INTRADAY = "intraday"
    IPO = "ipo"


class MFInvestmentMode(str, enum.Enum):
    SIP = "sip"
    LUMPSUM = "lumpsum"


class SIPFrequency(str, enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class FixedHoldingType(str, enum.Enum):
    EPF = "EPF"
    VPF = "VPF"
    PPF = "PPF"
    NPS = "NPS"
    FD = "FD"
    SSY = "SSY"
    BONDS = "bonds"


class PropertyType(str, enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    LAND = "land"


class GoldType(str, enum.Enum):
    PHYSICAL = "physical"
    DIGITAL = "digital"
    SGB = "SGB"


class LiabilityType(str, enum.Enum):
    HOME_LOAN = "home_loan"
    CAR_LOAN = "car_loan"
    PERSONAL_LOAN = "personal_loan"
    EDUCATION_LOAN = "education_loan"
    OTHER = "other"


# --- Models ---

class StockHolding(Base):
    __tablename__ = "holdings_stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    exchange: Mapped[Exchange] = mapped_column(Enum(Exchange), nullable=False, default=Exchange.NSE)
    investment_type: Mapped[InvestmentType] = mapped_column(
        Enum(InvestmentType), nullable=False, default=InvestmentType.LONG_TERM
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    avg_buy_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    buy_date: Mapped[date] = mapped_column(Date, nullable=False)
    broker: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="stock_holdings")


class MFHolding(Base):
    __tablename__ = "holdings_mf"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_code: Mapped[str] = mapped_column(String(20), nullable=False)
    scheme_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    units: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    avg_nav: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    investment_mode: Mapped[MFInvestmentMode] = mapped_column(
        Enum(MFInvestmentMode), nullable=False, default=MFInvestmentMode.LUMPSUM
    )
    buy_date: Mapped[date] = mapped_column(Date, nullable=False)
    folio_number: Mapped[str | None] = mapped_column(String(50))
    platform: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="mf_holdings")


class SIP(Base):
    __tablename__ = "sips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_code: Mapped[str] = mapped_column(String(20), nullable=False)
    scheme_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    day_of_month: Mapped[int] = mapped_column(Integer, nullable=False)
    frequency: Mapped[SIPFrequency] = mapped_column(
        Enum(SIPFrequency), nullable=False, default=SIPFrequency.MONTHLY
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    step_up_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="sips")
    installments: Mapped[list["SIPInstallment"]] = relationship(back_populates="sip")


class SIPInstallment(Base):
    __tablename__ = "sip_installments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sip_id: Mapped[int] = mapped_column(Integer, ForeignKey("sips.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    nav: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    units_bought: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    status: Mapped[str] = mapped_column(String(20), default="completed")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    sip: Mapped[SIP] = relationship(back_populates="installments")


class FixedHolding(Base):
    __tablename__ = "holdings_fixed"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    type: Mapped[FixedHoldingType] = mapped_column(Enum(FixedHoldingType), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))
    invested_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    current_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    interest_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    start_date: Mapped[date | None] = mapped_column(Date)
    maturity_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="fixed_holdings")


class PropertyHolding(Base):
    __tablename__ = "holdings_property"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[PropertyType] = mapped_column(
        Enum(PropertyType), nullable=False, default=PropertyType.RESIDENTIAL
    )
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    purchase_date: Mapped[date | None] = mapped_column(Date)
    estimated_current_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    last_valuation_date: Mapped[date | None] = mapped_column(Date)
    loan_outstanding: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="property_holdings")


class GoldHolding(Base):
    __tablename__ = "holdings_gold"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    type: Mapped[GoldType] = mapped_column(Enum(GoldType), nullable=False)
    quantity_grams: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    purchase_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="gold_holdings")


class Liability(Base):
    __tablename__ = "liabilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    type: Mapped[LiabilityType] = mapped_column(Enum(LiabilityType), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    principal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    outstanding: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    emi_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    bank: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="liabilities")
