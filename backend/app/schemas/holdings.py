from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.holdings import (
    Exchange,
    FixedHoldingType,
    GoldType,
    InvestmentType,
    LiabilityType,
    MFInvestmentMode,
    PropertyType,
    SIPFrequency,
)


# --- Stocks ---

class StockHoldingCreate(BaseModel):
    symbol: str
    exchange: Exchange = Exchange.NSE
    investment_type: InvestmentType = InvestmentType.LONG_TERM
    quantity: Decimal
    avg_buy_price: Decimal
    buy_date: date
    broker: str | None = None
    notes: str | None = None


class StockHoldingUpdate(BaseModel):
    symbol: str | None = None
    exchange: Exchange | None = None
    investment_type: InvestmentType | None = None
    quantity: Decimal | None = None
    avg_buy_price: Decimal | None = None
    buy_date: date | None = None
    broker: str | None = None
    notes: str | None = None


class StockHoldingResponse(BaseModel):
    id: int
    symbol: str
    exchange: str
    investment_type: str
    quantity: Decimal
    avg_buy_price: Decimal
    buy_date: date
    broker: str | None
    notes: str | None
    created_at: datetime
    # Live data (populated by service layer)
    current_price: Decimal | None = None
    day_change_pct: float | None = None
    current_value: Decimal | None = None
    pnl: Decimal | None = None
    pnl_pct: float | None = None

    model_config = {"from_attributes": True}


# --- Mutual Funds ---

class MFHoldingCreate(BaseModel):
    scheme_code: str
    scheme_name: str
    category: str | None = None
    units: Decimal
    avg_nav: Decimal
    investment_mode: MFInvestmentMode = MFInvestmentMode.LUMPSUM
    buy_date: date
    folio_number: str | None = None
    platform: str | None = None


class MFHoldingResponse(BaseModel):
    id: int
    scheme_code: str
    scheme_name: str
    category: str | None
    units: Decimal
    avg_nav: Decimal
    investment_mode: str
    buy_date: date
    folio_number: str | None
    platform: str | None
    created_at: datetime
    current_nav: Decimal | None = None
    current_value: Decimal | None = None
    pnl: Decimal | None = None
    pnl_pct: float | None = None

    model_config = {"from_attributes": True}


# --- SIP ---

class SIPCreate(BaseModel):
    scheme_code: str
    scheme_name: str
    amount: Decimal
    day_of_month: int
    frequency: SIPFrequency = SIPFrequency.MONTHLY
    start_date: date
    end_date: date | None = None
    step_up_percent: Decimal | None = None


class SIPResponse(BaseModel):
    id: int
    scheme_code: str
    scheme_name: str
    amount: Decimal
    day_of_month: int
    frequency: str
    start_date: date
    end_date: date | None
    step_up_percent: Decimal | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Fixed Income ---

class FixedHoldingCreate(BaseModel):
    type: FixedHoldingType
    name: str | None = None
    invested_amount: Decimal
    current_value: Decimal
    interest_rate: Decimal | None = None
    start_date: date | None = None
    maturity_date: date | None = None
    notes: str | None = None


class FixedHoldingResponse(BaseModel):
    id: int
    type: str
    name: str | None
    invested_amount: Decimal
    current_value: Decimal
    interest_rate: Decimal | None
    start_date: date | None
    maturity_date: date | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Property ---

class PropertyHoldingCreate(BaseModel):
    name: str
    type: PropertyType = PropertyType.RESIDENTIAL
    purchase_price: Decimal
    purchase_date: date | None = None
    estimated_current_value: Decimal
    last_valuation_date: date | None = None
    loan_outstanding: Decimal | None = None
    is_shared: bool = False
    notes: str | None = None


class PropertyHoldingResponse(BaseModel):
    id: int
    name: str
    type: str
    purchase_price: Decimal
    purchase_date: date | None
    estimated_current_value: Decimal
    last_valuation_date: date | None
    loan_outstanding: Decimal | None
    is_shared: bool
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Gold ---

class GoldHoldingCreate(BaseModel):
    type: GoldType
    quantity_grams: Decimal
    purchase_price: Decimal
    purchase_date: date | None = None


class GoldHoldingResponse(BaseModel):
    id: int
    type: str
    quantity_grams: Decimal
    purchase_price: Decimal
    purchase_date: date | None
    created_at: datetime
    current_price_per_gram: Decimal | None = None
    current_value: Decimal | None = None
    pnl: Decimal | None = None

    model_config = {"from_attributes": True}


# --- Liabilities ---

class LiabilityCreate(BaseModel):
    type: LiabilityType
    name: str
    principal: Decimal
    outstanding: Decimal
    interest_rate: Decimal
    emi_amount: Decimal | None = None
    start_date: date | None = None
    end_date: date | None = None
    bank: str | None = None


class LiabilityResponse(BaseModel):
    id: int
    type: str
    name: str
    principal: Decimal
    outstanding: Decimal
    interest_rate: Decimal
    emi_amount: Decimal | None
    start_date: date | None
    end_date: date | None
    bank: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
