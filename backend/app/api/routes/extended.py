"""API routes for goals, insurance, ESOP, crypto, tax, notifications."""
from datetime import date, datetime, timezone
from decimal import Decimal
from math import log, pow as fpow

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.extended import (
    CryptoHolding, ESOPHolding, FinancialGoal, GoalPriority, GoalStatus,
    InsurancePolicy, Notification, TaxDeduction,
)
from app.models.holdings import PropertyHolding, SIP
from app.models.user import User

router = APIRouter()


# ===== GOALS =====

class GoalCreate(BaseModel):
    name: str
    description: str | None = None
    target_amount: float
    current_amount: float = 0
    target_date: date
    priority: str = "medium"
    category: str | None = None
    expected_return_pct: float | None = 12.0
    inflation_pct: float | None = 6.0
    notes: str | None = None


class GoalUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    target_amount: float | None = None
    current_amount: float | None = None
    target_date: date | None = None
    priority: str | None = None
    status: str | None = None
    category: str | None = None
    expected_return_pct: float | None = None
    inflation_pct: float | None = None
    notes: str | None = None


def _calculate_sip_needed(target: float, current: float, months: int, annual_return: float) -> float:
    """Calculate monthly SIP needed to reach a target amount."""
    if months <= 0:
        return 0
    r = annual_return / 100 / 12  # monthly rate
    if r <= 0:
        return max(0, (target - current) / months)
    # Future value of current amount
    fv_current = current * fpow(1 + r, months)
    remaining = target - fv_current
    if remaining <= 0:
        return 0
    # SIP formula: FV = P * ((1+r)^n - 1) / r * (1+r)
    sip = remaining / (((fpow(1 + r, months) - 1) / r) * (1 + r))
    return max(0, round(sip, 0))


@router.get("/goals")
def list_goals(
    status: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(FinancialGoal).filter(FinancialGoal.user_id == user.id)
    if status:
        q = q.filter(FinancialGoal.status == GoalStatus(status))
    goals = q.order_by(FinancialGoal.target_date).all()

    result = []
    for g in goals:
        months_left = max(0, (g.target_date.year - date.today().year) * 12 + g.target_date.month - date.today().month)
        progress = float(g.current_amount) / float(g.target_amount) * 100 if g.target_amount else 0
        sip_needed = _calculate_sip_needed(
            float(g.target_amount), float(g.current_amount),
            months_left, float(g.expected_return_pct or 12),
        )
        # Inflation-adjusted target
        inflation_adjusted = float(g.target_amount) * fpow(1 + float(g.inflation_pct or 6) / 100, months_left / 12) if months_left > 0 else float(g.target_amount)

        result.append({
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "target_amount": float(g.target_amount),
            "current_amount": float(g.current_amount),
            "target_date": g.target_date.isoformat(),
            "priority": g.priority.value,
            "status": g.status.value,
            "category": g.category,
            "expected_return_pct": float(g.expected_return_pct) if g.expected_return_pct else None,
            "inflation_pct": float(g.inflation_pct) if g.inflation_pct else None,
            "notes": g.notes,
            "progress_pct": round(progress, 1),
            "months_left": months_left,
            "monthly_sip_needed": sip_needed,
            "inflation_adjusted_target": round(inflation_adjusted, 0),
            "on_track": progress >= (100 - months_left / max(1, (g.target_date - g.created_at.date()).days / 30) * 100) if months_left > 0 else progress >= 100,
        })
    return result


@router.post("/goals")
def create_goal(
    data: GoalCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    months = max(0, (data.target_date.year - date.today().year) * 12 + data.target_date.month - date.today().month)
    sip_needed = _calculate_sip_needed(data.target_amount, data.current_amount, months, data.expected_return_pct or 12)

    goal = FinancialGoal(
        user_id=user.id,
        name=data.name,
        description=data.description,
        target_amount=data.target_amount,
        current_amount=data.current_amount,
        target_date=data.target_date,
        priority=GoalPriority(data.priority),
        category=data.category,
        expected_return_pct=data.expected_return_pct,
        inflation_pct=data.inflation_pct,
        monthly_sip_needed=sip_needed,
        notes=data.notes,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return {"id": goal.id, "message": "Goal created", "monthly_sip_needed": sip_needed}


@router.put("/goals/{goal_id}")
def update_goal(
    goal_id: int,
    data: GoalUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = db.query(FinancialGoal).filter(FinancialGoal.id == goal_id, FinancialGoal.user_id == user.id).first()
    if not goal:
        raise HTTPException(404, "Goal not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "priority" and value:
            value = GoalPriority(value)
        if field == "status" and value:
            value = GoalStatus(value)
        setattr(goal, field, value)
    db.commit()
    return {"message": "Goal updated"}


@router.delete("/goals/{goal_id}")
def delete_goal(
    goal_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = db.query(FinancialGoal).filter(FinancialGoal.id == goal_id, FinancialGoal.user_id == user.id).first()
    if not goal:
        raise HTTPException(404, "Goal not found")
    db.delete(goal)
    db.commit()
    return {"message": "Goal deleted"}


# ===== INSURANCE =====

class InsuranceCreate(BaseModel):
    type: str
    provider: str
    policy_number: str | None = None
    sum_assured: float
    annual_premium: float
    premium_frequency: str = "annual"
    start_date: date | None = None
    maturity_date: date | None = None
    next_premium_date: date | None = None
    maturity_value: float | None = None
    tax_section: str | None = None
    nominees: str | None = None
    notes: str | None = None


@router.get("/insurance")
def list_insurance(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    policies = db.query(InsurancePolicy).filter(InsurancePolicy.user_id == user.id).all()
    return [
        {
            "id": p.id, "type": p.type, "provider": p.provider,
            "policy_number": p.policy_number,
            "sum_assured": float(p.sum_assured), "annual_premium": float(p.annual_premium),
            "premium_frequency": p.premium_frequency,
            "start_date": p.start_date.isoformat() if p.start_date else None,
            "maturity_date": p.maturity_date.isoformat() if p.maturity_date else None,
            "next_premium_date": p.next_premium_date.isoformat() if p.next_premium_date else None,
            "maturity_value": float(p.maturity_value) if p.maturity_value else None,
            "is_active": p.is_active, "tax_section": p.tax_section,
            "nominees": p.nominees, "notes": p.notes,
        }
        for p in policies
    ]


@router.post("/insurance")
def create_insurance(data: InsuranceCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    policy = InsurancePolicy(user_id=user.id, **data.model_dump())
    db.add(policy)
    db.commit()
    return {"id": policy.id, "message": "Insurance policy added"}


@router.delete("/insurance/{policy_id}")
def delete_insurance(policy_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id, InsurancePolicy.user_id == user.id).first()
    if not p:
        raise HTTPException(404, "Policy not found")
    db.delete(p)
    db.commit()
    return {"message": "Policy deleted"}


# ===== ESOP =====

class ESOPCreate(BaseModel):
    company: str
    type: str = "esop"
    total_granted: int
    vested: int = 0
    exercised: int = 0
    strike_price: float | None = None
    current_fmv: float | None = None
    grant_date: date | None = None
    next_vesting_date: date | None = None
    vesting_schedule: str | None = None
    notes: str | None = None


@router.get("/esop")
def list_esop(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    holdings = db.query(ESOPHolding).filter(ESOPHolding.user_id == user.id).all()
    return [
        {
            "id": h.id, "company": h.company, "type": h.type,
            "total_granted": h.total_granted, "vested": h.vested, "exercised": h.exercised,
            "unvested": h.total_granted - h.vested,
            "exercisable": h.vested - h.exercised,
            "strike_price": float(h.strike_price) if h.strike_price else None,
            "current_fmv": float(h.current_fmv) if h.current_fmv else None,
            "potential_value": float((h.vested - h.exercised) * (h.current_fmv - (h.strike_price or 0))) if h.current_fmv and h.vested > h.exercised else None,
            "grant_date": h.grant_date.isoformat() if h.grant_date else None,
            "next_vesting_date": h.next_vesting_date.isoformat() if h.next_vesting_date else None,
            "vesting_schedule": h.vesting_schedule,
        }
        for h in holdings
    ]


@router.post("/esop")
def create_esop(data: ESOPCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    h = ESOPHolding(user_id=user.id, **data.model_dump())
    db.add(h)
    db.commit()
    return {"id": h.id, "message": "ESOP added"}


@router.delete("/esop/{esop_id}")
def delete_esop(esop_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    h = db.query(ESOPHolding).filter(ESOPHolding.id == esop_id, ESOPHolding.user_id == user.id).first()
    if not h:
        raise HTTPException(404, "ESOP not found")
    db.delete(h)
    db.commit()
    return {"message": "ESOP deleted"}


# ===== CRYPTO =====

class CryptoCreate(BaseModel):
    coin: str
    quantity: float
    avg_buy_price_inr: float
    buy_date: date | None = None
    exchange: str | None = None
    notes: str | None = None


@router.get("/crypto")
def list_crypto(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    holdings = db.query(CryptoHolding).filter(CryptoHolding.user_id == user.id).all()
    return [
        {
            "id": h.id, "coin": h.coin, "quantity": float(h.quantity),
            "avg_buy_price_inr": float(h.avg_buy_price_inr),
            "invested": float(h.quantity * h.avg_buy_price_inr),
            "buy_date": h.buy_date.isoformat() if h.buy_date else None,
            "exchange": h.exchange, "notes": h.notes,
        }
        for h in holdings
    ]


@router.post("/crypto")
def create_crypto(data: CryptoCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    h = CryptoHolding(user_id=user.id, **data.model_dump())
    db.add(h)
    db.commit()
    return {"id": h.id, "message": "Crypto added"}


@router.delete("/crypto/{crypto_id}")
def delete_crypto(crypto_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    h = db.query(CryptoHolding).filter(CryptoHolding.id == crypto_id, CryptoHolding.user_id == user.id).first()
    if not h:
        raise HTTPException(404, "Crypto not found")
    db.delete(h)
    db.commit()
    return {"message": "Crypto deleted"}


# ===== TAX =====

TAX_LIMITS = {
    "80C": 150000, "80D_self": 25000, "80D_parents": 50000, "80D_senior": 50000,
    "80G": None, "80E": None, "80CCD_1B": 50000, "80TTA": 10000,
    "80TTB": 50000, "HRA": None, "24B": 200000, "80EEA": 150000,
}


@router.get("/tax/deductions")
def list_deductions(
    fy: str = Query(None, description="Financial year e.g. 2025-26"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not fy:
        today = date.today()
        fy = f"{today.year - 1}-{str(today.year)[2:]}" if today.month < 4 else f"{today.year}-{str(today.year + 1)[2:]}"

    deductions = db.query(TaxDeduction).filter(
        TaxDeduction.user_id == user.id, TaxDeduction.financial_year == fy
    ).all()

    by_section: dict[str, list] = {}
    for d in deductions:
        by_section.setdefault(d.section, []).append({
            "id": d.id, "description": d.description, "amount": float(d.amount),
            "proof_available": d.proof_available,
        })

    sections = []
    for section, items in by_section.items():
        total = sum(i["amount"] for i in items)
        limit = TAX_LIMITS.get(section)
        sections.append({
            "section": section,
            "items": items,
            "total": total,
            "limit": limit,
            "remaining": max(0, limit - total) if limit else None,
            "utilized_pct": round(total / limit * 100, 1) if limit else None,
        })

    total_deductions = sum(s["total"] for s in sections)
    return {"financial_year": fy, "sections": sections, "total_deductions": total_deductions}


class TaxDeductionCreate(BaseModel):
    financial_year: str
    section: str
    description: str
    amount: float
    proof_available: bool = False
    notes: str | None = None


@router.post("/tax/deductions")
def create_deduction(data: TaxDeductionCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    limit = TAX_LIMITS.get(data.section)
    d = TaxDeduction(
        user_id=user.id, max_limit=limit, **data.model_dump()
    )
    db.add(d)
    db.commit()
    return {"id": d.id, "message": "Deduction added"}


@router.delete("/tax/deductions/{deduction_id}")
def delete_deduction(deduction_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    d = db.query(TaxDeduction).filter(TaxDeduction.id == deduction_id, TaxDeduction.user_id == user.id).first()
    if not d:
        raise HTTPException(404, "Deduction not found")
    db.delete(d)
    db.commit()
    return {"message": "Deduction deleted"}


@router.get("/tax/regime-comparison")
def regime_comparison(
    annual_income: float = Query(..., description="Gross annual income"),
    total_deductions: float = Query(0, description="Total deductions under old regime"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Compare old vs new tax regime for the given income."""
    def calc_old(income: float, deductions: float) -> dict:
        taxable = max(0, income - deductions - 50000)  # standard deduction
        slabs = [(250000, 0), (250000, 0.05), (500000, 0.20), (float('inf'), 0.30)]
        tax = 0
        remaining = taxable
        for slab_size, rate in slabs:
            chunk = min(remaining, slab_size)
            tax += chunk * rate
            remaining -= chunk
            if remaining <= 0:
                break
        cess = tax * 0.04
        return {"taxable_income": taxable, "tax": round(tax), "cess": round(cess), "total": round(tax + cess)}

    def calc_new(income: float) -> dict:
        taxable = max(0, income - 75000)  # new standard deduction
        slabs = [(400000, 0), (400000, 0.05), (400000, 0.10), (400000, 0.15), (400000, 0.20), (float('inf'), 0.30)]
        tax = 0
        remaining = taxable
        for slab_size, rate in slabs:
            chunk = min(remaining, slab_size)
            tax += chunk * rate
            remaining -= chunk
            if remaining <= 0:
                break
        cess = tax * 0.04
        return {"taxable_income": taxable, "tax": round(tax), "cess": round(cess), "total": round(tax + cess)}

    old = calc_old(annual_income, total_deductions)
    new = calc_new(annual_income)
    savings = old["total"] - new["total"]

    return {
        "gross_income": annual_income,
        "total_deductions": total_deductions,
        "old_regime": old,
        "new_regime": new,
        "savings_with_new": savings if savings > 0 else 0,
        "savings_with_old": -savings if savings < 0 else 0,
        "recommended": "new" if savings > 0 else "old",
    }


# ===== NOTIFICATIONS =====

@router.get("/notifications")
def list_notifications(
    unread_only: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Notification).filter(Notification.user_id == user.id)
    if unread_only:
        q = q.filter(Notification.is_read == False)  # noqa
    notifs = q.order_by(Notification.created_at.desc()).limit(50).all()
    return [
        {
            "id": n.id, "type": n.type, "title": n.title, "message": n.message,
            "is_read": n.is_read, "action_url": n.action_url,
            "created_at": n.created_at.isoformat(),
        }
        for n in notifs
    ]


@router.put("/notifications/{notif_id}/read")
def mark_read(notif_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    n = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user.id).first()
    if n:
        n.is_read = True
        db.commit()
    return {"message": "Marked as read"}


@router.put("/notifications/read-all")
def mark_all_read(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(
        Notification.user_id == user.id, Notification.is_read == False  # noqa
    ).update({"is_read": True})
    db.commit()
    return {"message": "All marked as read"}


# ===== SMART ALERTS GENERATOR =====

@router.post("/notifications/generate")
def generate_alerts(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Auto-generate relevant financial alerts for the user."""
    alerts = []
    today = date.today()

    # SIP reminders (due in next 3 days)
    sips = db.query(SIP).filter(SIP.user_id == user.id, SIP.is_active == True).all()  # noqa
    for sip in sips:
        if abs(sip.day_of_month - today.day) <= 3 or (today.day > 25 and sip.day_of_month <= 3):
            alerts.append(("reminder", f"SIP Due: {sip.scheme_name}", f"₹{sip.amount:,.0f} SIP for {sip.scheme_name} is due on the {sip.day_of_month}th", "/mutual-funds"))

    # Insurance premium reminders
    policies = db.query(InsurancePolicy).filter(InsurancePolicy.user_id == user.id, InsurancePolicy.is_active == True).all()  # noqa
    for p in policies:
        if p.next_premium_date and (p.next_premium_date - today).days <= 15 and (p.next_premium_date - today).days >= 0:
            alerts.append(("warning", f"Premium Due: {p.provider}", f"₹{p.annual_premium:,.0f} {p.type} premium due on {p.next_premium_date}", "/insurance"))

    # FD maturity alerts
    from app.models.holdings import FixedHolding
    fds = db.query(FixedHolding).filter(FixedHolding.user_id == user.id).all()
    for fd in fds:
        if fd.maturity_date and (fd.maturity_date - today).days <= 30 and (fd.maturity_date - today).days >= 0:
            alerts.append(("alert", f"{fd.type.value} Maturing Soon", f"{fd.name or fd.type.value} worth ₹{fd.current_value:,.0f} matures on {fd.maturity_date}", "/fixed-income"))

    # Goal deadline alerts
    goals = db.query(FinancialGoal).filter(FinancialGoal.user_id == user.id, FinancialGoal.status == GoalStatus.ACTIVE).all()
    for g in goals:
        months_left = (g.target_date.year - today.year) * 12 + g.target_date.month - today.month
        progress = float(g.current_amount / g.target_amount * 100) if g.target_amount else 0
        if months_left <= 6 and progress < 80:
            alerts.append(("warning", f"Goal at Risk: {g.name}", f"Only {progress:.0f}% done with {months_left} months left. Need ₹{float(g.target_amount - g.current_amount):,.0f} more.", "/goals"))

    # Tax deadline (March)
    if today.month in (1, 2, 3) and today.month <= 3:
        alerts.append(("info", "Tax Season Reminder", "Check your 80C/80D deductions before March 31st. Invest in ELSS, PPF, or insurance if you have unused limits.", "/tax"))

    # ESOP vesting
    esops = db.query(ESOPHolding).filter(ESOPHolding.user_id == user.id).all()
    for e in esops:
        if e.next_vesting_date and (e.next_vesting_date - today).days <= 30 and (e.next_vesting_date - today).days >= 0:
            alerts.append(("info", f"ESOP Vesting: {e.company}", f"{e.total_granted - e.vested} shares vesting on {e.next_vesting_date}", "/esop"))

    # Save new alerts
    created = 0
    for type_, title, message, url in alerts:
        # Avoid duplicates (same title in last 7 days)
        existing = db.query(Notification).filter(
            Notification.user_id == user.id,
            Notification.title == title,
            Notification.created_at >= datetime(today.year, today.month, max(1, today.day - 7), tzinfo=timezone.utc),
        ).first()
        if not existing:
            db.add(Notification(user_id=user.id, type=type_, title=title, message=message, action_url=url))
            created += 1

    db.commit()
    return {"message": f"Generated {created} new alerts", "total_alerts": len(alerts)}


# ===== RENTAL INCOME FOR PROPERTIES =====

@router.get("/properties/rental-summary")
def rental_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get rental income summary for all properties."""
    from app.models.expense import Income
    properties = db.query(PropertyHolding).filter(PropertyHolding.user_id == user.id).all()
    rental_income = db.query(Income).filter(Income.user_id == user.id, Income.source == "RENTAL").all()

    total_rental = sum(float(r.amount) for r in rental_income)
    total_property_value = sum(float(p.estimated_current_value) for p in properties)

    return {
        "total_properties": len(properties),
        "total_property_value": total_property_value,
        "total_rental_income_ytd": total_rental,
        "gross_yield_pct": round(total_rental * 12 / total_property_value * 100, 2) if total_property_value > 0 else 0,
        "properties": [
            {
                "id": p.id, "name": p.name, "type": p.type.value,
                "value": float(p.estimated_current_value),
                "loan_outstanding": float(p.loan_outstanding) if p.loan_outstanding else 0,
            }
            for p in properties
        ],
    }


# ===== EMERGENCY FUND CALCULATOR =====

@router.get("/emergency-fund")
def emergency_fund_status(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Calculate emergency fund adequacy."""
    from app.models.expense import Expense, Income
    from app.models.holdings import FixedHolding, FixedHoldingType
    from app.models.settings import UserSettings

    # Get monthly expenses (average of last 6 months)
    six_months_ago = date(date.today().year, max(1, date.today().month - 6), 1)
    expenses = db.query(Expense).filter(Expense.user_id == user.id, Expense.date >= six_months_ago).all()
    total_expense = sum(float(e.amount) for e in expenses)
    months_data = max(1, min(6, (date.today() - six_months_ago).days / 30))
    monthly_expense = total_expense / months_data

    # Count liquid assets (savings FD, liquid MF, cash equivalents)
    liquid_fixed = db.query(FixedHolding).filter(
        FixedHolding.user_id == user.id,
        FixedHolding.type.in_([FixedHoldingType.FD]),
    ).all()
    liquid_amount = sum(float(f.current_value) for f in liquid_fixed)

    # Get target from settings
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    target_months = 6  # default
    if settings and settings.emergency_fund_target:
        target_amount = settings.emergency_fund_target
    else:
        target_amount = monthly_expense * target_months

    months_covered = liquid_amount / monthly_expense if monthly_expense > 0 else 0
    adequacy_pct = liquid_amount / target_amount * 100 if target_amount > 0 else 0

    return {
        "avg_monthly_expense": round(monthly_expense, 0),
        "liquid_assets": round(liquid_amount, 0),
        "target_amount": round(target_amount, 0),
        "months_covered": round(months_covered, 1),
        "adequacy_pct": round(adequacy_pct, 1),
        "status": "adequate" if months_covered >= 6 else "warning" if months_covered >= 3 else "critical",
        "shortfall": round(max(0, target_amount - liquid_amount), 0),
    }
