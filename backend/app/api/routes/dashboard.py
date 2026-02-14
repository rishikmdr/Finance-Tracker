from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.expense import Expense, Income
from app.models.holdings import (
    FixedHolding,
    GoldHolding,
    Liability,
    MFHolding,
    PropertyHolding,
    StockHolding,
)
from app.models.user import Family, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a consolidated dashboard summary for the current user."""
    stocks = db.query(StockHolding).filter(StockHolding.user_id == user.id).all()
    mf = db.query(MFHolding).filter(MFHolding.user_id == user.id).all()
    fixed = db.query(FixedHolding).filter(FixedHolding.user_id == user.id).all()
    properties = db.query(PropertyHolding).filter(PropertyHolding.user_id == user.id).all()
    gold = db.query(GoldHolding).filter(GoldHolding.user_id == user.id).all()
    liabilities_list = db.query(Liability).filter(Liability.user_id == user.id).all()

    # Calculate totals (invested amounts — live prices calculated separately)
    stock_invested = sum(s.quantity * s.avg_buy_price for s in stocks)
    mf_invested = sum(m.units * m.avg_nav for m in mf)
    fixed_total = sum(f.current_value for f in fixed)
    property_total = sum(p.estimated_current_value for p in properties)
    gold_invested = sum(g.purchase_price for g in gold)
    liabilities_total = sum(l.outstanding for l in liabilities_list)

    total_assets = stock_invested + mf_invested + fixed_total + property_total + gold_invested
    net_worth = total_assets - liabilities_total

    # Current month income & expenses
    today = date.today()
    month_start = date(today.year, today.month, 1)
    if today.month == 12:
        month_end = date(today.year + 1, 1, 1)
    else:
        month_end = date(today.year, today.month + 1, 1)

    month_income = (
        db.query(Income)
        .filter(Income.user_id == user.id, Income.date >= month_start, Income.date < month_end)
        .all()
    )
    month_expenses = (
        db.query(Expense)
        .filter(Expense.user_id == user.id, Expense.date >= month_start, Expense.date < month_end)
        .all()
    )

    total_month_income = sum(i.amount for i in month_income)
    total_month_expense = sum(e.amount for e in month_expenses)

    # Asset allocation
    allocation = {}
    if total_assets > 0:
        allocation = {
            "equity": float((stock_invested + mf_invested) / total_assets * 100),
            "fixed_income": float(fixed_total / total_assets * 100),
            "real_estate": float(property_total / total_assets * 100),
            "gold": float(gold_invested / total_assets * 100),
        }

    return {
        "net_worth": float(net_worth),
        "total_assets": float(total_assets),
        "total_liabilities": float(liabilities_total),
        "asset_breakdown": {
            "stocks": float(stock_invested),
            "mutual_funds": float(mf_invested),
            "fixed_income": float(fixed_total),
            "property": float(property_total),
            "gold": float(gold_invested),
        },
        "asset_allocation_pct": allocation,
        "month_summary": {
            "income": float(total_month_income),
            "expenses": float(total_month_expense),
            "savings": float(total_month_income - total_month_expense),
        },
        "counts": {
            "stocks": len(stocks),
            "mutual_funds": len(mf),
            "fixed_income": len(fixed),
            "properties": len(properties),
            "gold": len(gold),
            "liabilities": len(liabilities_list),
        },
    }


@router.get("/family-summary")
def get_family_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get combined family dashboard (all members' holdings)."""
    if not user.family_id:
        return get_dashboard_summary(db=db, user=user)

    family = db.query(Family).filter(Family.id == user.family_id).first()
    member_ids = [m.id for m in family.members]

    stocks = db.query(StockHolding).filter(StockHolding.user_id.in_(member_ids)).all()
    mf = db.query(MFHolding).filter(MFHolding.user_id.in_(member_ids)).all()
    fixed = db.query(FixedHolding).filter(FixedHolding.user_id.in_(member_ids)).all()
    properties = db.query(PropertyHolding).filter(PropertyHolding.user_id.in_(member_ids)).all()
    gold = db.query(GoldHolding).filter(GoldHolding.user_id.in_(member_ids)).all()
    liabilities_list = db.query(Liability).filter(Liability.user_id.in_(member_ids)).all()

    stock_invested = sum(s.quantity * s.avg_buy_price for s in stocks)
    mf_invested = sum(m.units * m.avg_nav for m in mf)
    fixed_total = sum(f.current_value for f in fixed)
    property_total = sum(p.estimated_current_value for p in properties)
    gold_invested = sum(g.purchase_price for g in gold)
    liabilities_total = sum(l.outstanding for l in liabilities_list)

    total_assets = stock_invested + mf_invested + fixed_total + property_total + gold_invested
    net_worth = total_assets - liabilities_total

    today = date.today()
    month_start = date(today.year, today.month, 1)
    if today.month == 12:
        month_end = date(today.year + 1, 1, 1)
    else:
        month_end = date(today.year, today.month + 1, 1)

    month_income = (
        db.query(Income)
        .filter(Income.user_id.in_(member_ids), Income.date >= month_start, Income.date < month_end)
        .all()
    )
    month_expenses = (
        db.query(Expense)
        .filter(
            Expense.user_id.in_(member_ids), Expense.date >= month_start, Expense.date < month_end
        )
        .all()
    )

    total_month_income = sum(i.amount for i in month_income)
    total_month_expense = sum(e.amount for e in month_expenses)

    members_summary = []
    for member in family.members:
        m_stocks = sum(
            s.quantity * s.avg_buy_price for s in stocks if s.user_id == member.id
        )
        m_mf = sum(m.units * m.avg_nav for m in mf if m.user_id == member.id)
        m_fixed = sum(f.current_value for f in fixed if f.user_id == member.id)
        m_total = m_stocks + m_mf + m_fixed
        members_summary.append({
            "id": member.id,
            "name": member.name,
            "total_assets": float(m_total),
        })

    return {
        "family_name": family.name,
        "net_worth": float(net_worth),
        "total_assets": float(total_assets),
        "total_liabilities": float(liabilities_total),
        "asset_breakdown": {
            "stocks": float(stock_invested),
            "mutual_funds": float(mf_invested),
            "fixed_income": float(fixed_total),
            "property": float(property_total),
            "gold": float(gold_invested),
        },
        "month_summary": {
            "income": float(total_month_income),
            "expenses": float(total_month_expense),
            "savings": float(total_month_income - total_month_expense),
        },
        "members": members_summary,
    }
