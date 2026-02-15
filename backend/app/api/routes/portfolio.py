"""API routes — Settings, AI, Prices, Analytics."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.settings import UserSettings
from app.models.user import User
from app.services.ai.engine import (
    analyze_portfolio,
    chat,
    get_conversations,
    get_conversation_messages,
)
from app.services.portfolio.analytics import (
    calculate_net_worth_snapshot,
    calculate_stock_returns,
    calculate_mf_returns,
    monthly_income_expense_trend,
    expense_category_breakdown,
)
from app.services.portfolio.price_service import (
    get_gold_price,
    get_index_value,
    get_mf_nav,
    get_stock_price,
    refresh_all_prices,
)

router = APIRouter()


# ===== SETTINGS =====

class SettingsUpdate(BaseModel):
    anthropic_api_key: str | None = None
    currency: str | None = None
    theme: str | None = None
    notifications_enabled: bool | None = None
    monthly_budget: float | None = None
    emergency_fund_target: float | None = None
    retirement_age: int | None = None
    risk_profile: str | None = None
    notes: str | None = None


class SettingsResponse(BaseModel):
    has_api_key: bool
    api_key_preview: str | None
    currency: str
    theme: str
    notifications_enabled: bool
    monthly_budget: float | None
    emergency_fund_target: float | None
    retirement_age: int | None
    risk_profile: str | None
    notes: str | None


def _get_or_create_settings(db: Session, user_id: int) -> UserSettings:
    s = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not s:
        s = UserSettings(user_id=user_id)
        db.add(s)
        db.commit()
        db.refresh(s)
    return s


@router.get("/settings", response_model=SettingsResponse)
def get_settings(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = _get_or_create_settings(db, user.id)
    return SettingsResponse(
        has_api_key=bool(s.anthropic_api_key),
        api_key_preview=f"sk-ant-...{s.anthropic_api_key[-6:]}" if s.anthropic_api_key else None,
        currency=s.currency,
        theme=s.theme,
        notifications_enabled=s.notifications_enabled,
        monthly_budget=s.monthly_budget,
        emergency_fund_target=s.emergency_fund_target,
        retirement_age=s.retirement_age,
        risk_profile=s.risk_profile,
        notes=s.notes,
    )


@router.put("/settings", response_model=SettingsResponse)
def update_settings(
    data: SettingsUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = _get_or_create_settings(db, user.id)

    if data.anthropic_api_key is not None:
        # Validate key format
        key = data.anthropic_api_key.strip()
        if key and not key.startswith("sk-ant-"):
            raise HTTPException(400, "Invalid API key format. Should start with 'sk-ant-'")
        s.anthropic_api_key = key if key else None
    if data.currency is not None:
        s.currency = data.currency
    if data.theme is not None:
        s.theme = data.theme
    if data.notifications_enabled is not None:
        s.notifications_enabled = data.notifications_enabled
    if data.monthly_budget is not None:
        s.monthly_budget = data.monthly_budget
    if data.emergency_fund_target is not None:
        s.emergency_fund_target = data.emergency_fund_target
    if data.retirement_age is not None:
        s.retirement_age = data.retirement_age
    if data.risk_profile is not None:
        if data.risk_profile not in ("conservative", "moderate", "aggressive"):
            raise HTTPException(400, "risk_profile must be conservative, moderate, or aggressive")
        s.risk_profile = data.risk_profile
    if data.notes is not None:
        s.notes = data.notes

    db.commit()
    db.refresh(s)
    return SettingsResponse(
        has_api_key=bool(s.anthropic_api_key),
        api_key_preview=f"sk-ant-...{s.anthropic_api_key[-6:]}" if s.anthropic_api_key else None,
        currency=s.currency,
        theme=s.theme,
        notifications_enabled=s.notifications_enabled,
        monthly_budget=s.monthly_budget,
        emergency_fund_target=s.emergency_fund_target,
        retirement_age=s.retirement_age,
        risk_profile=s.risk_profile,
        notes=s.notes,
    )


@router.delete("/settings/api-key")
def delete_api_key(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = _get_or_create_settings(db, user.id)
    s.anthropic_api_key = None
    db.commit()
    return {"message": "API key removed"}


# ===== AI ANALYSIS =====

@router.get("/portfolio/analysis")
def portfolio_analysis(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = _get_or_create_settings(db, user.id)
    return analyze_portfolio(db, user.id, s.anthropic_api_key)


# ===== AI CHAT =====

class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None


@router.post("/chat")
def chat_endpoint(
    data: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not data.message.strip():
        raise HTTPException(400, "Message cannot be empty")
    s = _get_or_create_settings(db, user.id)
    return chat(db, user.id, data.message.strip(), data.conversation_id, s.anthropic_api_key)


@router.get("/conversations")
def list_conversations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_conversations(db, user.id)


@router.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_conversation_messages(db, user.id, conversation_id)


# ===== PRICES =====

@router.post("/prices/refresh")
def refresh_prices(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = refresh_all_prices(db, user.id)
    return {"message": "Prices refreshed", "updated": result}


@router.get("/prices/stock/{symbol}")
def stock_price(
    symbol: str,
    exchange: str = "NSE",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_stock_price(symbol, exchange, db)


@router.get("/prices/mf/{scheme_code}")
def mf_nav(
    scheme_code: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_mf_nav(scheme_code, db)


@router.get("/prices/gold")
def gold_price(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_gold_price(db)


@router.get("/prices/index/{index}")
def index_value(
    index: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_index_value(index, db)


# ===== ANALYTICS =====

@router.get("/portfolio/net-worth")
def net_worth_snapshot(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return calculate_net_worth_snapshot(db, user.id)


@router.get("/portfolio/stock-returns")
def stock_returns(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return calculate_stock_returns(db, user.id)


@router.get("/portfolio/mf-returns")
def mf_returns(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return calculate_mf_returns(db, user.id)


@router.get("/portfolio/trends")
def trends(
    months: int = Query(12, ge=1, le=36),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return monthly_income_expense_trend(db, user.id, months)


@router.get("/portfolio/expense-breakdown")
def expense_breakdown(
    month: int = Query(None, ge=1, le=12),
    year: int = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    m = month or date.today().month
    y = year or date.today().year
    return expense_category_breakdown(db, user.id, m, y)


# ===== EXPORT =====

@router.get("/portfolio/export")
def export_portfolio(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export full portfolio as JSON for backup."""
    snapshot = calculate_net_worth_snapshot(db, user.id)
    trends_data = monthly_income_expense_trend(db, user.id, 12)
    return {
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "exported_at": date.today().isoformat(),
        "portfolio": snapshot,
        "trends": trends_data,
    }
