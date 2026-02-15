"""Portfolio analytics — XIRR, returns, trends, savings rate."""
import math
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.expense import Expense, Income
from app.models.holdings import (
    FixedHolding, GoldHolding, Liability, MFHolding, PropertyHolding, StockHolding,
)
from app.models.ai_memory import PriceCache


def xirr(cashflows: list[tuple[date, float]], guess: float = 0.1) -> float | None:
    """Calculate XIRR (Extended Internal Rate of Return).
    cashflows: list of (date, amount) where negative = investment, positive = redemption/current value.
    """
    if not cashflows or len(cashflows) < 2:
        return None

    dates = [cf[0] for cf in cashflows]
    amounts = [cf[1] for cf in cashflows]
    min_date = min(dates)

    def npv(rate):
        return sum(
            amount / (1 + rate) ** ((d - min_date).days / 365.25)
            for d, amount in cashflows
        )

    # Newton-Raphson
    rate = guess
    for _ in range(200):
        nv = npv(rate)
        # Derivative
        dnv = sum(
            -amount * ((d - min_date).days / 365.25)
            / (1 + rate) ** ((d - min_date).days / 365.25 + 1)
            for d, amount in cashflows
        )
        if abs(dnv) < 1e-12:
            break
        new_rate = rate - nv / dnv
        if abs(new_rate - rate) < 1e-9:
            return round(new_rate * 100, 2)
        rate = new_rate
        if rate < -0.99:
            rate = -0.99

    return round(rate * 100, 2) if abs(npv(rate)) < 1.0 else None


def calculate_stock_returns(db: Session, user_id: int) -> list[dict]:
    """Calculate XIRR and absolute returns for each stock."""
    stocks = db.query(StockHolding).filter(StockHolding.user_id == user_id).all()
    results = []

    for stock in stocks:
        ticker_symbol = f"{stock.symbol}.{'NS' if stock.exchange.value == 'NSE' else 'BO'}"
        cached = db.query(PriceCache).filter(PriceCache.symbol == ticker_symbol).first()
        current_price = cached.price if cached else None

        invested = float(stock.quantity * stock.avg_buy_price)
        current_value = float(stock.quantity) * current_price if current_price else None
        pnl = current_value - invested if current_value else None
        pnl_pct = (pnl / invested * 100) if pnl is not None and invested > 0 else None

        # XIRR
        stock_xirr = None
        if current_value and stock.buy_date:
            cashflows = [
                (stock.buy_date, -invested),
                (date.today(), current_value),
            ]
            stock_xirr = xirr(cashflows)

        results.append({
            "id": stock.id,
            "symbol": stock.symbol,
            "exchange": stock.exchange.value,
            "investment_type": stock.investment_type.value,
            "quantity": float(stock.quantity),
            "avg_buy_price": float(stock.avg_buy_price),
            "buy_date": str(stock.buy_date),
            "current_price": current_price,
            "invested": invested,
            "current_value": current_value,
            "pnl": round(pnl, 2) if pnl is not None else None,
            "pnl_pct": round(pnl_pct, 2) if pnl_pct is not None else None,
            "xirr": stock_xirr,
            "day_change_pct": cached.day_change_pct if cached else None,
        })

    return results


def calculate_mf_returns(db: Session, user_id: int) -> list[dict]:
    """Calculate returns for mutual fund holdings."""
    mfs = db.query(MFHolding).filter(MFHolding.user_id == user_id).all()
    results = []

    for mf in mfs:
        cache_key = f"MF:{mf.scheme_code}"
        cached = db.query(PriceCache).filter(PriceCache.symbol == cache_key).first()
        current_nav = cached.price if cached else None

        invested = float(mf.units * mf.avg_nav)
        current_value = float(mf.units) * current_nav if current_nav else None
        pnl = current_value - invested if current_value else None
        pnl_pct = (pnl / invested * 100) if pnl is not None and invested > 0 else None

        mf_xirr = None
        if current_value and mf.buy_date:
            cashflows = [(mf.buy_date, -invested), (date.today(), current_value)]
            mf_xirr = xirr(cashflows)

        results.append({
            "id": mf.id,
            "scheme_code": mf.scheme_code,
            "scheme_name": mf.scheme_name,
            "category": mf.category,
            "units": float(mf.units),
            "avg_nav": float(mf.avg_nav),
            "investment_mode": mf.investment_mode.value,
            "current_nav": current_nav,
            "invested": invested,
            "current_value": current_value,
            "pnl": round(pnl, 2) if pnl is not None else None,
            "pnl_pct": round(pnl_pct, 2) if pnl_pct is not None else None,
            "xirr": mf_xirr,
        })

    return results


def calculate_net_worth_snapshot(db: Session, user_id: int) -> dict:
    """Calculate detailed net worth with live prices."""
    stock_returns = calculate_stock_returns(db, user_id)
    mf_returns = calculate_mf_returns(db, user_id)
    fixed = db.query(FixedHolding).filter(FixedHolding.user_id == user_id).all()
    props = db.query(PropertyHolding).filter(PropertyHolding.user_id == user_id).all()
    gold_holdings = db.query(GoldHolding).filter(GoldHolding.user_id == user_id).all()
    liabilities = db.query(Liability).filter(Liability.user_id == user_id).all()

    # Gold with live price
    gold_cache = db.query(PriceCache).filter(PriceCache.symbol == "GOLD:INR_PER_GRAM").first()
    gold_price_per_gram = gold_cache.price if gold_cache else None

    stocks_current = sum(s["current_value"] or s["invested"] for s in stock_returns)
    stocks_invested = sum(s["invested"] for s in stock_returns)
    mf_current = sum(m["current_value"] or m["invested"] for m in mf_returns)
    mf_invested = sum(m["invested"] for m in mf_returns)
    fixed_total = sum(float(f.current_value) for f in fixed)
    prop_total = sum(float(p.estimated_current_value) for p in props)

    gold_current = 0
    gold_invested = 0
    for g in gold_holdings:
        gold_invested += float(g.purchase_price)
        if gold_price_per_gram:
            gold_current += float(g.quantity_grams) * gold_price_per_gram
        else:
            gold_current += float(g.purchase_price)

    liab_total = sum(float(l.outstanding) for l in liabilities)

    total_assets = stocks_current + mf_current + fixed_total + prop_total + gold_current
    total_invested = stocks_invested + mf_invested + sum(float(f.invested_amount) for f in fixed) + sum(float(p.purchase_price) for p in props) + gold_invested
    net_worth = total_assets - liab_total
    total_pnl = total_assets - total_invested

    allocation = {}
    if total_assets > 0:
        allocation = {
            "equity": round((stocks_current + mf_current) / total_assets * 100, 1),
            "fixed_income": round(fixed_total / total_assets * 100, 1),
            "real_estate": round(prop_total / total_assets * 100, 1),
            "gold": round(gold_current / total_assets * 100, 1),
        }

    return {
        "net_worth": round(net_worth, 2),
        "total_assets": round(total_assets, 2),
        "total_invested": round(total_invested, 2),
        "total_liabilities": round(liab_total, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl / total_invested * 100, 2) if total_invested > 0 else 0,
        "breakdown": {
            "stocks": {"invested": stocks_invested, "current": stocks_current},
            "mutual_funds": {"invested": mf_invested, "current": mf_current},
            "fixed_income": fixed_total,
            "property": prop_total,
            "gold": {"invested": gold_invested, "current": gold_current},
        },
        "allocation": allocation,
        "stocks": stock_returns,
        "mutual_funds": mf_returns,
    }


def monthly_income_expense_trend(db: Session, user_id: int, months: int = 12) -> list[dict]:
    """Get monthly income vs expense trend."""
    today = date.today()
    results = []

    for i in range(months - 1, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1

        month_start = date(y, m, 1)
        if m == 12:
            month_end = date(y + 1, 1, 1)
        else:
            month_end = date(y, m + 1, 1)

        income_total = (
            db.query(func.coalesce(func.sum(Income.amount), 0))
            .filter(Income.user_id == user_id, Income.date >= month_start, Income.date < month_end)
            .scalar()
        )
        expense_total = (
            db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(Expense.user_id == user_id, Expense.date >= month_start, Expense.date < month_end)
            .scalar()
        )

        results.append({
            "month": month_start.strftime("%b %Y"),
            "income": float(income_total),
            "expenses": float(expense_total),
            "savings": float(income_total) - float(expense_total),
        })

    return results


def expense_category_breakdown(db: Session, user_id: int, month: int, year: int) -> list[dict]:
    """Get expense breakdown by category for a month."""
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1)
    else:
        month_end = date(year, month + 1, 1)

    expenses = (
        db.query(Expense)
        .filter(Expense.user_id == user_id, Expense.date >= month_start, Expense.date < month_end)
        .all()
    )

    by_category = {}
    for e in expenses:
        cat_name = "Uncategorized"
        if e.category:
            cat_name = e.category.name
        by_category[cat_name] = by_category.get(cat_name, 0) + float(e.amount)

    total = sum(by_category.values())
    return [
        {"category": cat, "amount": amt, "percentage": round(amt / total * 100, 1) if total > 0 else 0}
        for cat, amt in sorted(by_category.items(), key=lambda x: -x[1])
    ]
