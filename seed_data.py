#!/usr/bin/env python3
"""
Seed script: 5 years of realistic data for the Sharma family.

PERSONAS:
  Rahul Sharma (34) — Senior Software Engineer @ Infosys, Bangalore
    - Earns 28L/yr (2026), started at 14L in 2021
    - Aggressive investor: loves stocks, does some swing trading
    - Has ESOPs from previous startup (Razorpay)
    - Handles the family's stock portfolio
    - Risk profile: aggressive

  Priya Sharma (31) — Product Manager @ Flipkart, Bangalore
    - Earns 22L/yr (2026), started at 12L in 2021
    - Conservative-moderate investor: prefers MFs, PPF, gold
    - Manages the family's mutual fund SIPs and insurance
    - Risk profile: moderate

  Family: The Sharmas (combined)
    - Married in 2019, daughter Ananya born 2022
    - Bought 2BHK in Whitefield in 2022 (85L, 60L home loan)
    - Family goals: daughter's education, retirement at 50, second property
    - Monthly expenses: ~1.2L (rent till 2022, then EMI + maintenance)
"""

import random
import sys
import os
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# Override DATABASE_URL to SQLite before importing anything else
os.environ["DATABASE_URL"] = "sqlite:///./finance_tracker.db"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_engine = create_engine("sqlite:///./finance_tracker.db", connect_args={"check_same_thread": False})
_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

# Patch the database module before other imports
import app.core.database as db_mod
db_mod.engine = _engine
db_mod.SessionLocal = _SessionLocal

from app.core.database import Base
from app.core.security import hash_password
from app.models.user import User, Family, UserRole
from app.models.expense import Expense, Income, ExpenseCategory, ImportSource, IncomeSource, Earner
from app.models.holdings import (
    StockHolding, MFHolding, SIP, SIPInstallment, FixedHolding, PropertyHolding,
    GoldHolding, Liability, Exchange, InvestmentType, MFInvestmentMode, SIPFrequency,
    FixedHoldingType, PropertyType, GoldType, LiabilityType,
)
from app.models.ai_memory import UserMemory, ChatConversation, ChatMessage, PriceCache, MemoryCategory
from app.models.settings import UserSettings
from app.models.extended import (
    FinancialGoal, InsurancePolicy, ESOPHolding, CryptoHolding,
    TaxDeduction, Notification, GoalPriority, GoalStatus,
)

random.seed(42)


def d(year, month, day=1):
    return date(year, month, min(day, 28))


def main():
    print("Creating all tables...")
    Base.metadata.create_all(bind=_engine)

    db = _SessionLocal()
    try:
        # Clean existing data
        for model in [
            Notification, TaxDeduction, CryptoHolding, ESOPHolding, InsurancePolicy,
            FinancialGoal, UserSettings, ChatMessage, ChatConversation, UserMemory, PriceCache,
            SIPInstallment, SIP, Expense, Income, StockHolding, MFHolding, FixedHolding,
            PropertyHolding, GoldHolding, Liability, ExpenseCategory, User, Family,
        ]:
            db.query(model).delete()
        db.commit()
        print("Cleaned existing data.")

        # ============ FAMILY ============
        family = Family(name="The Sharmas")
        db.add(family)
        db.flush()

        # ============ USERS ============
        rahul = User(
            email="rahul@sharma.com", name="Rahul Sharma",
            password_hash=hash_password("sharma2021"),
            family_id=family.id, family_role=UserRole.OWNER,
        )
        priya = User(
            email="priya@sharma.com", name="Priya Sharma",
            password_hash=hash_password("sharma2021"),
            family_id=family.id, family_role=UserRole.MEMBER,
        )
        db.add_all([rahul, priya])
        db.flush()
        print(f"Created Rahul (id={rahul.id}) and Priya (id={priya.id}), Family id={family.id}")

        # ============ SETTINGS ============
        db.add(UserSettings(user_id=rahul.id, monthly_budget=120000, emergency_fund_target=600000, retirement_age=50, risk_profile="aggressive"))
        db.add(UserSettings(user_id=priya.id, monthly_budget=100000, emergency_fund_target=500000, retirement_age=52, risk_profile="moderate"))

        # ============ EXPENSE CATEGORIES ============
        cats = {}
        for name in ["Housing", "Groceries", "Dining Out", "Transport", "Utilities", "Shopping",
                      "Healthcare", "Education", "Entertainment", "Travel", "Insurance",
                      "EMI Payments", "Childcare", "Personal Care", "Gifts", "Misc"]:
            c = ExpenseCategory(name=name)
            db.add(c)
            db.flush()
            cats[name] = c.id
        print(f"Created {len(cats)} expense categories.")

        # ============ RAHUL'S STOCKS (5 years of buying) ============
        stock_history = [
            # (symbol, buy_date, qty, avg_price, type, notes)
            ("TCS", d(2021, 3, 15), 10, 3150, "long_term", "First stock purchase"),
            ("INFY", d(2021, 5, 10), 25, 1380, "long_term", "IT sector bet"),
            ("RELIANCE", d(2021, 8, 20), 8, 2180, "long_term", "Conglomerate play"),
            ("HDFCBANK", d(2021, 11, 5), 15, 1520, "long_term", "Banking sector"),
            ("TATAMOTORS", d(2022, 1, 18), 50, 485, "swing", "EV turnaround bet"),
            ("BAJFINANCE", d(2022, 4, 12), 5, 6800, "long_term", "Financial services"),
            ("ITC", d(2022, 7, 25), 100, 285, "long_term", "Dividend play"),
            ("WIPRO", d(2022, 10, 8), 30, 395, "positional", "IT dip buy"),
            ("ADANIENT", d(2023, 1, 5), 10, 3500, "swing", "Adani rally"),
            ("SBIN", d(2023, 3, 22), 40, 540, "long_term", "PSU banking"),
            ("LTIM", d(2023, 6, 14), 8, 4800, "long_term", "IT services"),
            ("TITAN", d(2023, 9, 3), 12, 3200, "long_term", "Consumer discretionary"),
            ("TATASTEEL", d(2023, 11, 20), 60, 128, "swing", "Commodity cycle"),
            ("NESTLEIND", d(2024, 2, 10), 3, 24500, "long_term", "FMCG stability"),
            ("ICICIBANK", d(2024, 5, 18), 20, 1120, "long_term", "Banking growth"),
            ("DMART", d(2024, 8, 7), 6, 3900, "long_term", "Retail growth story"),
            ("BHARTIARTL", d(2024, 11, 25), 15, 1580, "long_term", "Telecom monopoly"),
            ("ZOMATO", d(2025, 2, 14), 100, 185, "swing", "New-age tech bet"),
            ("RVNL", d(2025, 5, 10), 200, 280, "positional", "Railway capex theme"),
            ("JSWSTEEL", d(2025, 9, 15), 25, 850, "long_term", "Steel upcycle"),
            # IPO allocations
            ("TATATECH", d(2023, 11, 30), 15, 500, "ipo", "IPO allotment"),
            ("IREDA", d(2023, 11, 22), 100, 32, "ipo", "Green energy IPO"),
        ]
        for sym, bd, qty, price, itype, notes in stock_history:
            db.add(StockHolding(
                user_id=rahul.id, symbol=sym, exchange=Exchange.NSE,
                investment_type=InvestmentType(itype),
                quantity=qty, avg_buy_price=price, buy_date=bd,
                broker="Zerodha", notes=notes,
            ))
        print(f"Added {len(stock_history)} stock holdings for Rahul.")

        # ============ PRIYA'S MUTUAL FUNDS ============
        mf_holdings = [
            # (code, name, category, units, avg_nav, mode, buy_date, platform)
            ("119551", "Parag Parikh Flexi Cap Fund", "Flexi Cap", 1450.5, 42.80, "sip", d(2021, 4, 5), "Kuvera"),
            ("120503", "Mirae Asset Large Cap Fund", "Large Cap", 980.2, 68.50, "sip", d(2021, 4, 5), "Kuvera"),
            ("118989", "Axis Small Cap Fund", "Small Cap", 620.8, 52.30, "sip", d(2021, 6, 10), "Kuvera"),
            ("100356", "HDFC Mid-Cap Opportunities Fund", "Mid Cap", 412.6, 95.70, "sip", d(2022, 1, 5), "Groww"),
            ("112321", "SBI Blue Chip Fund", "Large Cap", 550.0, 52.10, "lumpsum", d(2022, 3, 15), "Kuvera"),
            ("108272", "Kotak Emerging Equity Fund", "Mid Cap", 280.4, 72.60, "sip", d(2022, 7, 5), "Kuvera"),
            ("120587", "Motilal Oswal Nasdaq 100 FoF", "International", 185.2, 24.80, "sip", d(2023, 1, 10), "Groww"),
            ("119597", "Quant Small Cap Fund", "Small Cap", 340.7, 145.50, "lumpsum", d(2023, 5, 20), "Kuvera"),
            ("100119", "ICICI Prudential Balanced Advantage", "Balanced", 890.3, 48.20, "sip", d(2023, 8, 5), "Groww"),
            ("145552", "Nippon India Liquid Fund", "Liquid", 120.0, 5450.0, "lumpsum", d(2024, 1, 10), "Kuvera"),
            # Priya also has an ELSS for tax saving
            ("120465", "Mirae Asset Tax Saver Fund", "ELSS", 720.5, 32.40, "sip", d(2021, 4, 5), "Kuvera"),
        ]
        for code, name, cat, units, nav, mode, bd, platform in mf_holdings:
            db.add(MFHolding(
                user_id=priya.id, scheme_code=code, scheme_name=name, category=cat,
                units=Decimal(str(units)), avg_nav=Decimal(str(nav)),
                investment_mode=MFInvestmentMode(mode), buy_date=bd, platform=platform,
            ))
        # Rahul also has some MFs
        rahul_mf = [
            ("120503", "Mirae Asset Large Cap Fund", "Large Cap", 320.5, 55.20, "lumpsum", d(2021, 9, 15), "Zerodha"),
            ("118989", "Axis Small Cap Fund", "Small Cap", 180.3, 48.90, "lumpsum", d(2022, 6, 20), "Zerodha"),
            ("119551", "Parag Parikh Flexi Cap Fund", "Flexi Cap", 250.0, 58.10, "sip", d(2023, 3, 5), "Zerodha"),
        ]
        for code, name, cat, units, nav, mode, bd, platform in rahul_mf:
            db.add(MFHolding(
                user_id=rahul.id, scheme_code=code, scheme_name=name, category=cat,
                units=Decimal(str(units)), avg_nav=Decimal(str(nav)),
                investment_mode=MFInvestmentMode(mode), buy_date=bd, platform=platform,
            ))
        print(f"Added {len(mf_holdings) + len(rahul_mf)} MF holdings.")

        # ============ SIPs (Active) ============
        sips = [
            (priya.id, "119551", "Parag Parikh Flexi Cap Fund", 10000, 5, d(2021, 4, 5), 10, True),
            (priya.id, "120503", "Mirae Asset Large Cap Fund", 8000, 5, d(2021, 4, 5), 10, True),
            (priya.id, "118989", "Axis Small Cap Fund", 5000, 10, d(2021, 6, 10), 10, True),
            (priya.id, "120465", "Mirae Asset Tax Saver Fund (ELSS)", 5000, 5, d(2021, 4, 5), None, True),
            (priya.id, "100356", "HDFC Mid-Cap Opportunities Fund", 7000, 5, d(2022, 1, 5), 10, True),
            (priya.id, "108272", "Kotak Emerging Equity Fund", 5000, 5, d(2022, 7, 5), None, True),
            (priya.id, "120587", "Motilal Oswal Nasdaq 100 FoF", 3000, 10, d(2023, 1, 10), None, True),
            (priya.id, "100119", "ICICI Prudential Balanced Advantage", 6000, 5, d(2023, 8, 5), None, True),
            (rahul.id, "119551", "Parag Parikh Flexi Cap Fund", 8000, 5, d(2023, 3, 5), 10, True),
            # Stopped SIP
            (priya.id, "119597", "Quant Small Cap Fund", 5000, 15, d(2023, 5, 20), None, False),
        ]
        for uid, code, name, amt, dom, sd, stepup, active in sips:
            sip = SIP(
                user_id=uid, scheme_code=code, scheme_name=name,
                amount=amt, day_of_month=dom, start_date=sd,
                step_up_percent=stepup, is_active=active,
            )
            db.add(sip)
            db.flush()
            # Generate installment history
            current = sd
            while current <= date(2026, 2, 1):
                if not active and current > date(2024, 6, 1):
                    break
                nav = round(random.uniform(30, 200), 2)
                units = round(amt / nav, 4)
                db.add(SIPInstallment(
                    sip_id=sip.id, date=current, amount=amt, nav=nav, units_bought=units,
                ))
                # Step-up annually
                if stepup and current.month == 4 and current.year > sd.year:
                    amt = round(amt * (1 + stepup / 100))
                if current.month == 12:
                    current = date(current.year + 1, 1, dom)
                else:
                    current = date(current.year, current.month + 1, min(dom, 28))
        print(f"Added {len(sips)} SIPs with installment history.")

        # ============ FIXED INCOME ============
        fixed = [
            # Rahul
            (rahul.id, "EPF", "Infosys EPF", 480000, 720000, 8.15, d(2018, 6, 1), None),
            (rahul.id, "NPS", "Rahul NPS Tier 1", 300000, 420000, 10.5, d(2021, 4, 1), None),
            (rahul.id, "FD", "SBI FD 5yr", 500000, 570000, 7.1, d(2022, 9, 1), d(2027, 9, 1)),
            # Priya
            (priya.id, "PPF", "Priya PPF Account", 750000, 1050000, 7.1, d(2018, 4, 1), d(2033, 4, 1)),
            (priya.id, "EPF", "Flipkart EPF", 350000, 510000, 8.15, d(2019, 7, 1), None),
            (priya.id, "SSY", "Ananya SSY (Daughter)", 150000, 175000, 8.2, d(2022, 12, 1), d(2043, 12, 1)),
            (priya.id, "FD", "HDFC FD 3yr", 300000, 330000, 7.25, d(2024, 1, 15), d(2027, 1, 15)),
            (priya.id, "FD", "ICICI FD 1yr", 200000, 215000, 7.0, d(2025, 6, 1), d(2026, 6, 1)),
        ]
        for uid, typ, name, invested, current, rate, start, maturity in fixed:
            db.add(FixedHolding(
                user_id=uid, type=FixedHoldingType(typ), name=name,
                invested_amount=invested, current_value=current,
                interest_rate=rate, start_date=start, maturity_date=maturity,
            ))
        print(f"Added {len(fixed)} fixed income holdings.")

        # ============ PROPERTY ============
        db.add(PropertyHolding(
            user_id=rahul.id, name="2BHK Whitefield, Bangalore",
            type=PropertyType.RESIDENTIAL, purchase_price=8500000,
            purchase_date=d(2022, 6, 15), estimated_current_value=11200000,
            last_valuation_date=d(2025, 12, 1), loan_outstanding=4200000,
            is_shared=True, notes="Joint property with Priya. Near ITPL.",
        ))
        db.add(PropertyHolding(
            user_id=priya.id, name="Plot in Mysore (Parents' gift)",
            type=PropertyType.LAND, purchase_price=1500000,
            purchase_date=d(2023, 3, 10), estimated_current_value=2200000,
            last_valuation_date=d(2025, 6, 1), is_shared=False,
            notes="Inherited plot near Ring Road, Mysore. Potential to build.",
        ))
        print("Added 2 properties.")

        # ============ GOLD ============
        gold_buys = [
            (priya.id, "physical", 20.0, 98000, d(2020, 11, 1)),    # Wedding gold
            (priya.id, "physical", 10.0, 55000, d(2022, 10, 25)),    # Diwali
            (priya.id, "SGB", 16.0, 76800, d(2021, 5, 15)),          # SGB Series IX
            (priya.id, "SGB", 8.0, 48000, d(2023, 3, 10)),           # SGB
            (rahul.id, "digital", 5.0, 30000, d(2024, 1, 20)),       # Digital gold
            (priya.id, "physical", 8.0, 52000, d(2024, 10, 15)),     # Diwali 2024
        ]
        for uid, typ, grams, price, bd in gold_buys:
            db.add(GoldHolding(
                user_id=uid, type=GoldType(typ), quantity_grams=grams,
                purchase_price=price, purchase_date=bd,
            ))
        print(f"Added {len(gold_buys)} gold holdings.")

        # ============ LIABILITIES ============
        db.add(Liability(
            user_id=rahul.id, type=LiabilityType.HOME_LOAN,
            name="SBI Home Loan - Whitefield 2BHK", principal=6000000,
            outstanding=4200000, interest_rate=8.5, emi_amount=52000,
            start_date=d(2022, 6, 15), end_date=d(2042, 6, 15), bank="SBI",
        ))
        db.add(Liability(
            user_id=rahul.id, type=LiabilityType.CAR_LOAN,
            name="Hyundai Creta Car Loan", principal=800000,
            outstanding=320000, interest_rate=9.0, emi_amount=17500,
            start_date=d(2023, 8, 1), end_date=d(2028, 8, 1), bank="HDFC Bank",
        ))
        db.add(Liability(
            user_id=priya.id, type=LiabilityType.EDUCATION_LOAN,
            name="MBA Education Loan (IIM)", principal=1200000,
            outstanding=180000, interest_rate=10.5, emi_amount=22000,
            start_date=d(2017, 7, 1), end_date=d(2026, 7, 1), bank="Axis Bank",
        ))
        print("Added 3 liabilities.")

        # ============ 5 YEARS OF INCOME (monthly) ============
        # Rahul salary growth: 14L(2021) -> 17L(2022) -> 20L(2023) -> 24L(2024) -> 26L(2025) -> 28L(2026)
        rahul_salaries = {2021: 116667, 2022: 141667, 2023: 166667, 2024: 200000, 2025: 216667, 2026: 233333}
        # Priya salary: 12L -> 14L -> 16.5L -> 19L -> 20.5L -> 22L
        priya_salaries = {2021: 100000, 2022: 116667, 2023: 137500, 2024: 158333, 2025: 170833, 2026: 183333}

        income_count = 0
        for year in range(2021, 2027):
            for month in range(1, 13):
                if year == 2026 and month > 2:
                    break
                dt = d(year, month, 1)
                # Rahul salary
                db.add(Income(user_id=rahul.id, date=dt, amount=rahul_salaries[year], source=IncomeSource.SALARY, earner=Earner.SELF, notes=f"Infosys salary {month}/{year}"))
                # Priya salary
                db.add(Income(user_id=priya.id, date=dt, amount=priya_salaries[year], source=IncomeSource.SALARY, earner=Earner.SELF, notes=f"Flipkart salary {month}/{year}"))
                income_count += 2

        # Bonus (annual, April)
        for year in [2021, 2022, 2023, 2024, 2025]:
            db.add(Income(user_id=rahul.id, date=d(year, 4, 15), amount=rahul_salaries[year] * 2, source=IncomeSource.OTHER, earner=Earner.SELF, notes=f"Annual bonus {year}"))
            db.add(Income(user_id=priya.id, date=d(year, 4, 15), amount=priya_salaries[year] * 1.5, source=IncomeSource.OTHER, earner=Earner.SELF, notes=f"Annual bonus {year}"))
            income_count += 2

        # Dividend income (quarterly from ITC, HDFCBANK etc.)
        for year in range(2022, 2027):
            for month in [3, 6, 9, 12]:
                if year == 2026 and month > 2:
                    break
                db.add(Income(user_id=rahul.id, date=d(year, month, 15), amount=random.randint(1500, 8000), source=IncomeSource.DIVIDEND, earner=Earner.SELF, notes="Stock dividends"))
                income_count += 1

        # Interest income from FDs
        for year in range(2023, 2027):
            for month in [6, 12]:
                if year == 2026 and month > 2:
                    break
                db.add(Income(user_id=priya.id, date=d(year, month, 1), amount=random.randint(8000, 15000), source=IncomeSource.INTEREST, earner=Earner.SELF, notes="FD interest payout"))
                income_count += 1

        # Rental income (from Priya's Mysore plot — leased for farming from 2024)
        for year in [2024, 2025]:
            for month in range(1, 13):
                db.add(Income(user_id=priya.id, date=d(year, month, 5), amount=8000, source=IncomeSource.RENTAL, earner=Earner.SELF, notes="Mysore plot lease"))
                income_count += 1
        for month in [1, 2]:
            db.add(Income(user_id=priya.id, date=d(2026, month, 5), amount=8000, source=IncomeSource.RENTAL, earner=Earner.SELF, notes="Mysore plot lease"))
            income_count += 1

        # Rahul freelance (occasional consulting)
        for bd in [d(2022, 8, 20), d(2023, 2, 10), d(2023, 11, 5), d(2024, 6, 15), d(2025, 3, 20)]:
            db.add(Income(user_id=rahul.id, date=bd, amount=random.randint(25000, 75000), source=IncomeSource.FREELANCE, earner=Earner.SELF, notes="Tech consulting"))
            income_count += 1

        print(f"Added {income_count} income entries across 5 years.")

        # ============ 5 YEARS OF EXPENSES (monthly patterns) ============
        expense_patterns = {
            # category: (min, max) monthly range
            "Housing": (18000, 55000),      # rent then EMI
            "Groceries": (8000, 15000),
            "Dining Out": (3000, 12000),
            "Transport": (3000, 8000),
            "Utilities": (3000, 7000),
            "Shopping": (2000, 20000),
            "Healthcare": (1000, 8000),
            "Entertainment": (1500, 8000),
            "Insurance": (0, 0),  # handled separately
            "EMI Payments": (0, 0),  # handled separately
            "Personal Care": (1000, 4000),
            "Misc": (500, 5000),
        }
        expense_count = 0
        for year in range(2021, 2027):
            for month in range(1, 13):
                if year == 2026 and month > 2:
                    break
                dt_base = d(year, month, 1)

                # Housing: rent before mid-2022, then EMI after
                if year < 2022 or (year == 2022 and month < 7):
                    housing = random.randint(22000, 28000)
                else:
                    housing = 52000  # EMI
                db.add(Expense(user_id=rahul.id, date=d(year, month, 1), amount=housing, category_id=cats["Housing"], description="Rent/EMI"))
                expense_count += 1

                # Regular expenses (split between both users)
                for cat_name, (lo, hi) in expense_patterns.items():
                    if cat_name in ("Housing", "Insurance", "EMI Payments") or lo == 0:
                        continue
                    # Seasonal adjustments
                    multiplier = 1.0
                    if cat_name == "Shopping" and month in (10, 11):  # Diwali/festive
                        multiplier = 2.5
                    if cat_name == "Dining Out" and month == 12:
                        multiplier = 1.8
                    if cat_name == "Healthcare" and month in (7, 8):  # monsoon
                        multiplier = 1.5
                    amt = int(random.randint(lo, hi) * multiplier)
                    user = random.choice([rahul, priya])
                    day = random.randint(1, 28)
                    db.add(Expense(user_id=user.id, date=d(year, month, day), amount=amt, category_id=cats[cat_name], description=f"{cat_name} - {month}/{year}"))
                    expense_count += 1

                # Childcare (from 2022 onwards)
                if year >= 2023:
                    db.add(Expense(user_id=priya.id, date=d(year, month, 10), amount=random.randint(5000, 18000), category_id=cats["Childcare"], description="Daycare/nanny"))
                    expense_count += 1

                # Car EMI (from Aug 2023)
                if year > 2023 or (year == 2023 and month >= 8):
                    db.add(Expense(user_id=rahul.id, date=d(year, month, 5), amount=17500, category_id=cats["EMI Payments"], description="Hyundai Creta EMI"))
                    expense_count += 1

                # Education loan EMI (Priya, until mid-2026)
                db.add(Expense(user_id=priya.id, date=d(year, month, 10), amount=22000, category_id=cats["EMI Payments"], description="IIM education loan EMI"))
                expense_count += 1

        # Big one-time expenses
        big_expenses = [
            (rahul.id, d(2021, 10, 25), 45000, "Shopping", "Diwali electronics"),
            (priya.id, d(2021, 12, 20), 80000, "Travel", "Goa trip"),
            (rahul.id, d(2022, 2, 14), 35000, "Gifts", "Anniversary jewelry"),
            (priya.id, d(2022, 5, 15), 120000, "Healthcare", "Delivery hospital bills"),
            (rahul.id, d(2022, 8, 10), 60000, "Shopping", "Baby furniture & supplies"),
            (priya.id, d(2022, 10, 20), 55000, "Shopping", "Diwali gold coin & clothes"),
            (rahul.id, d(2023, 1, 15), 95000, "Travel", "Kerala family vacation"),
            (priya.id, d(2023, 6, 8), 28000, "Healthcare", "Annual health checkup family"),
            (rahul.id, d(2023, 10, 28), 110000, "Shopping", "Diwali renovation"),
            (priya.id, d(2024, 3, 20), 45000, "Travel", "Mysore parents visit"),
            (rahul.id, d(2024, 5, 12), 200000, "Travel", "Bali family vacation"),
            (priya.id, d(2024, 8, 15), 35000, "Education", "Ananya preschool admission"),
            (rahul.id, d(2024, 10, 25), 75000, "Shopping", "Diwali gifts & clothes"),
            (priya.id, d(2025, 1, 10), 150000, "Travel", "Thailand trip"),
            (rahul.id, d(2025, 4, 5), 42000, "Healthcare", "Dental work"),
            (priya.id, d(2025, 7, 20), 55000, "Education", "Ananya school fees"),
            (rahul.id, d(2025, 10, 28), 90000, "Shopping", "Diwali festival expenses"),
            (priya.id, d(2025, 12, 25), 65000, "Gifts", "Christmas + New Year party"),
            (rahul.id, d(2026, 1, 15), 30000, "Healthcare", "Eye surgery (LASIK)"),
        ]
        for uid, dt, amt, cat_name, desc in big_expenses:
            db.add(Expense(user_id=uid, date=dt, amount=amt, category_id=cats[cat_name], description=desc))
            expense_count += 1

        print(f"Added {expense_count} expense entries across 5 years.")

        # ============ INSURANCE ============
        insurance_policies = [
            (rahul.id, "term", "ICICI Prudential", "ICT-2021-R001", 10000000, 12500, "annual", d(2021, 5, 1), d(2055, 5, 1), d(2026, 5, 1), None, "80C", "Priya Sharma"),
            (priya.id, "term", "HDFC Life", "HDT-2021-P002", 7500000, 9800, "annual", d(2021, 6, 1), d(2056, 6, 1), d(2026, 6, 1), None, "80C", "Rahul Sharma"),
            (rahul.id, "health", "Star Health", "SH-FAM-003", 1000000, 22000, "annual", d(2021, 4, 1), None, d(2026, 4, 1), None, "80D", "Family floater"),
            (priya.id, "health", "Niva Bupa", "NB-TOP-004", 500000, 15000, "annual", d(2023, 1, 1), None, d(2026, 1, 1), None, "80D", "Super top-up"),
            (priya.id, "ulip", "LIC", "LIC-UL-005", 2500000, 50000, "annual", d(2019, 8, 1), d(2029, 8, 1), d(2026, 8, 1), 850000, "80C", "Priya Sharma"),
            (rahul.id, "motor", "Bajaj Allianz", "BA-MOT-006", 500000, 18000, "annual", d(2023, 8, 15), None, d(2026, 8, 15), None, None, "Hyundai Creta"),
        ]
        for uid, typ, provider, pnum, sa, prem, freq, start, mat, npd, mv, tax, nom in insurance_policies:
            db.add(InsurancePolicy(
                user_id=uid, type=typ, provider=provider, policy_number=pnum,
                sum_assured=sa, annual_premium=prem, premium_frequency=freq,
                start_date=start, maturity_date=mat, next_premium_date=npd,
                maturity_value=mv, tax_section=tax, nominees=nom,
            ))
        print(f"Added {len(insurance_policies)} insurance policies.")

        # ============ ESOPs (Rahul — ex-Razorpay) ============
        db.add(ESOPHolding(
            user_id=rahul.id, company="Razorpay", type="esop",
            total_granted=2000, vested=1500, exercised=500,
            strike_price=120, current_fmv=1800,
            grant_date=d(2019, 3, 1), next_vesting_date=d(2026, 3, 1),
            vesting_schedule="25% per year over 4 years, fully vested. Remaining exercisable.",
            notes="Left Razorpay in 2021. 1000 shares exercisable at ₹120 each. FMV ~₹1800.",
        ))
        db.add(ESOPHolding(
            user_id=rahul.id, company="Infosys", type="rsu",
            total_granted=100, vested=50, exercised=25,
            strike_price=0, current_fmv=1850,
            grant_date=d(2022, 4, 1), next_vesting_date=d(2026, 4, 1),
            vesting_schedule="25 RSUs per year over 4 years",
            notes="Infosys RSU grant. 25 remaining to vest.",
        ))
        print("Added 2 ESOP/RSU holdings.")

        # ============ CRYPTO ============
        db.add(CryptoHolding(user_id=rahul.id, coin="BTC", quantity=Decimal("0.05"), avg_buy_price_inr=2800000, buy_date=d(2021, 11, 10), exchange="WazirX", notes="Bitcoin dip buy"))
        db.add(CryptoHolding(user_id=rahul.id, coin="ETH", quantity=Decimal("0.8"), avg_buy_price_inr=180000, buy_date=d(2022, 6, 20), exchange="CoinDCX", notes="Ethereum"))
        db.add(CryptoHolding(user_id=rahul.id, coin="SOL", quantity=Decimal("10"), avg_buy_price_inr=2500, buy_date=d(2023, 10, 5), exchange="WazirX", notes="Solana bet"))
        print("Added 3 crypto holdings.")

        # ============ FINANCIAL GOALS ============
        goals = [
            (rahul.id, "Retire at 50", "Build corpus of 5Cr+ by age 50 for early retirement", 50000000, 8500000, d(2042, 1, 1), "critical", "retirement", 12, 6),
            (priya.id, "Ananya's Education Fund", "College fund for daughter (engineering/abroad)", 25000000, 1200000, d(2040, 6, 1), "high", "education", 12, 7),
            (rahul.id, "Second Property", "Investment flat or villa in Bangalore outskirts", 15000000, 2500000, d(2030, 1, 1), "medium", "house", 10, 6),
            (priya.id, "Ananya's Marriage Fund", "Daughter's wedding fund", 5000000, 300000, d(2045, 6, 1), "medium", "marriage", 11, 6),
            (rahul.id, "Emergency Fund (6mo)", "6 months of family expenses in liquid assets", 900000, 650000, d(2026, 12, 1), "critical", "emergency", 5, 0),
            (priya.id, "Europe Trip 2027", "Family vacation to Europe", 600000, 150000, d(2027, 5, 1), "low", "travel", 8, 6),
            (rahul.id, "Tesla/EV Fund", "Save up for an electric car by 2028", 2500000, 400000, d(2028, 6, 1), "low", "car", 8, 6),
        ]
        for uid, name, desc, target, current, td, prio, cat, ret, inf in goals:
            db.add(FinancialGoal(
                user_id=uid, name=name, description=desc,
                target_amount=target, current_amount=current,
                target_date=td, priority=GoalPriority(prio), category=cat,
                expected_return_pct=ret, inflation_pct=inf,
            ))
        print(f"Added {len(goals)} financial goals.")

        # ============ TAX DEDUCTIONS (FY 2025-26) ============
        fy = "2025-26"
        deductions = [
            # Rahul
            (rahul.id, "80C", "EPF contribution", 72000, True),
            (rahul.id, "80C", "Home loan principal", 50000, True),
            (rahul.id, "80C", "ICICI Term Insurance premium", 12500, True),
            (rahul.id, "80CCD_1B", "NPS Tier 1 contribution", 50000, True),
            (rahul.id, "80D_self", "Star Health family floater", 22000, True),
            (rahul.id, "24B", "Home loan interest (SBI)", 200000, True),
            # Priya
            (priya.id, "80C", "EPF contribution", 60000, True),
            (priya.id, "80C", "PPF contribution", 75000, True),
            (priya.id, "80C", "ELSS (Mirae Asset Tax Saver)", 60000, True),
            (priya.id, "80C", "LIC ULIP premium", 50000, True),
            (priya.id, "80C", "Sukanya Samriddhi (SSY)", 50000, True),
            (priya.id, "80D_self", "Niva Bupa super top-up", 15000, True),
            (priya.id, "80E", "Education loan interest", 45000, True),
            (priya.id, "80G", "PM CARES Fund donation", 10000, True),
            (priya.id, "80G", "CRY NGO donation", 5000, False),
        ]
        for uid, section, desc, amt, proof in deductions:
            db.add(TaxDeduction(
                user_id=uid, financial_year=fy, section=section,
                description=desc, amount=amt, proof_available=proof,
                max_limit={"80C": 150000, "80CCD_1B": 50000, "80D_self": 25000, "24B": 200000, "80E": None, "80G": None}.get(section),
            ))
        print(f"Added {len(deductions)} tax deductions for FY {fy}.")

        # ============ AI MEMORIES (simulating past conversations) ============
        memories = [
            # Rahul
            (rahul.id, "risk_appetite", "Aggressive — comfortable with 70%+ equity allocation", "preference"),
            (rahul.id, "investment_style", "Prefers direct stocks over MFs. Enjoys stock picking.", "preference"),
            (rahul.id, "retirement_goal", "Wants to retire by 50 (2042) with 5 Cr corpus", "goal"),
            (rahul.id, "tax_regime", "Uses old tax regime due to heavy 80C/80D/NPS deductions", "fact"),
            (rahul.id, "esop_plan", "Plans to exercise Razorpay ESOPs post-IPO for max value", "plan"),
            (rahul.id, "second_property", "Looking at 2BHK in Sarjapur or Electronic City for 2028-30", "plan"),
            (rahul.id, "age", "34 years old, born 1992", "fact"),
            (rahul.id, "employer", "Senior Software Engineer at Infosys, Bangalore since 2021", "fact"),
            (rahul.id, "crypto_view", "Small allocation to crypto (2-3% of portfolio), mainly BTC", "preference"),
            # Priya
            (priya.id, "risk_appetite", "Moderate — prefers 60% equity, 40% debt/gold", "preference"),
            (priya.id, "investment_style", "Prefers SIP-based MF investing. Trusts Kuvera platform.", "preference"),
            (priya.id, "daughter_education", "Saving for Ananya's college abroad (target: US/UK university)", "goal"),
            (priya.id, "ppf_strategy", "Maxes out PPF every year. Views it as retirement safety net.", "plan"),
            (priya.id, "insurance_view", "Believes in adequate term + health coverage before investing", "preference"),
            (priya.id, "gold_view", "Likes SGB for investment, physical gold for sentiment", "preference"),
            (priya.id, "age", "31 years old, born 1995", "fact"),
            (priya.id, "employer", "Product Manager at Flipkart, Bangalore since 2019", "fact"),
            (priya.id, "education_loan", "IIM MBA loan almost paid off (180K remaining, ends Jul 2026)", "fact"),
        ]
        for uid, key, value, cat in memories:
            db.add(UserMemory(user_id=uid, key=key, value=value, category=MemoryCategory(cat)))
        print(f"Added {len(memories)} AI memory entries.")

        # ============ CHAT CONVERSATIONS (simulating past interactions) ============
        # Rahul's conversation
        conv1 = ChatConversation(user_id=rahul.id, title="Am I on track for retirement at 50?")
        db.add(conv1)
        db.flush()
        rahul_chat = [
            ("user", "Am I on track to retire at 50? I want at least 5 crores by then."),
            ("assistant", """Great question, Rahul! Let me analyze your retirement readiness.

**Current Position (Age 34, Target Age 50 = 16 years):**
- Stocks portfolio: ~₹18L invested across 22 holdings
- Mutual Funds: ~₹5.5L (you're lighter on MFs compared to Priya)
- EPF: ₹7.2L (growing at 8.15%)
- NPS: ₹4.2L (growing at ~10.5%)
- Razorpay ESOPs: 1000 exercisable shares @ ₹120, FMV ₹1800 = **₹18L potential**
- Property equity: ~₹70L (₹1.12Cr value - ₹42L loan)

**Total invested assets: ~₹52L (excluding property)**

**To reach ₹5 Cr in 16 years at 12% CAGR:**
You need to invest approximately **₹85,000/month** consistently.

**Current monthly investment:** ~₹8,000 SIP + stock purchases (irregular)

**Verdict: You're behind target.** The Razorpay ESOP exercise could add ₹18L which helps, but you need to significantly increase your monthly investments.

**Recommendations:**
1. Increase SIP to ₹40K/month minimum (add large cap + flexi cap)
2. Exercise Razorpay ESOPs and redeploy proceeds into diversified equity
3. Consider the Infosys RSUs as part of your equity allocation
4. Your stock portfolio is well-diversified but consider booking profits on swing trades and moving to SIPs for compounding

Shall I create a detailed month-by-month plan?"""),
            ("user", "What about the property equity? And yes, I want to exercise the Razorpay ESOPs after their IPO."),
            ("assistant", """**Property in your retirement calc:**
Your Whitefield 2BHK (₹1.12Cr, loan ₹42L) gives you ₹70L equity. If property appreciates at 5-6% p.a., by 2042 it could be worth ₹2.5-3Cr. However, I'd treat this as your "housing asset" rather than retirement corpus, since you'll need a place to live.

**Razorpay ESOP Strategy:**
Smart move waiting for IPO. Post-listing:
- Exercise 1000 shares at ₹120 = ₹1.2L cost
- At FMV of ₹1800/share = ₹18L value
- Tax: Perquisite tax on exercise (₹18L - ₹1.2L = ₹16.8L taxed as salary)
- LTCG exemption if you hold 1 year post-exercise

**Revised plan factoring ESOPs:**
If you exercise and reinvest ₹15L (post-tax) into index funds, that alone could compound to ₹90L+ by 2042 at 12%.

**Adjusted monthly SIP needed: ₹65,000/month** (down from ₹85K thanks to ESOPs).

This is very doable given your combined household income of ₹4L+/month. I'd suggest allocating post-EMI/expenses savings more aggressively to SIPs.

I've noted your ESOP exercise plan — I'll remind you about tax implications when Razorpay IPO news comes out."""),
        ]
        for role, content in rahul_chat:
            db.add(ChatMessage(conversation_id=conv1.id, role=role, content=content))

        # Priya's conversation
        conv2 = ChatConversation(user_id=priya.id, title="Daughter's education fund - how much do I need?")
        db.add(conv2)
        db.flush()
        priya_chat = [
            ("user", "Ananya is 3 now. If she wants to study engineering or MBA abroad, how much should I save?"),
            ("assistant", """Great forward planning, Priya! Let me calculate for Ananya's education.

**Assumptions:**
- Ananya is 3, college at 18 = **15 years to save**
- Target: US/UK university (4-year engineering or 2-year MBA)
- Current cost: ₹40-60L per year (tuition + living)
- Total current cost: ₹1.5 - 2.5 Cr
- With 7% inflation over 15 years: **₹4 - 7 Cr** (2040-41 prices)

**Let's plan for ₹5 Cr (middle estimate):**

**Your current education fund allocations:**
- Sukanya Samriddhi (SSY): ₹1.75L (growing at 8.2%)
- Your MF portfolio: ~₹28L invested across 11 schemes
- Part of these are earmarked for education

**Monthly SIP needed for ₹5 Cr in 15 years (at 12% return):**
~₹50,000/month

**Your current SIPs total: ₹49,000/month** — you're almost exactly on track!

**However, here's the nuance:**
Not all your SIPs are for education. You have retirement, emergency, and other goals too. I'd recommend:

1. **Earmark specific SIPs for education:** PPFAS Flexi + Mirae Large Cap (~₹18K/month)
2. **Add a dedicated international fund SIP:** You already have Motilal Nasdaq FoF (₹3K) — increase to ₹8K
3. **SSY will contribute ~₹6L by maturity** — helpful but small
4. **Consider a step-up of 10% annually** — your SIPs already have this!

**Bottom line:** With your current 10% step-up SIPs, you're likely to accumulate ₹4-5 Cr in 15 years. Stay consistent and you're golden!

Shall I also factor in a potential scholarship discount?"""),
            ("user", "That's reassuring. Should I also look at PPF for her education? My PPF matures in 2033."),
            ("assistant", """**PPF for Education — Smart Thinking!**

Your PPF account (opened 2018, matures 2033) currently has ₹10.5L. By 2033, at 7.1% it should grow to approximately **₹18-20L**.

**Timing alignment:**
- PPF matures: 2033 (Ananya will be 11)
- College starts: 2040 (Ananya will be 18)
- Gap: 7 years

**Strategy:**
1. **Withdraw PPF at maturity (2033):** ₹18-20L
2. **Reinvest in a balanced/equity MF:** For 7 more years at 12%
3. **By 2040:** This could become ₹40-45L — covering almost one year of abroad tuition!

**Alternatively:**
You can extend PPF in blocks of 5 years (2033 → 2038) with continued contributions. This keeps it tax-free and safe.

**My recommendation:** Withdraw at 2033 maturity and shift to equity MFs for higher returns, since you still have 7 years of runway and Ananya's education is a long-term goal.

I've noted this plan. When your PPF approaches maturity in 2032, I'll remind you to start planning the transition!"""),
        ]
        for role, content in priya_chat:
            db.add(ChatMessage(conversation_id=conv2.id, role=role, content=content))

        # Family financial review conversation (Rahul)
        conv3 = ChatConversation(user_id=rahul.id, title="Annual family financial review 2025")
        db.add(conv3)
        db.flush()
        family_chat = [
            ("user", "Can you do a full financial health check for our family? Both mine and Priya's portfolios combined."),
            ("assistant", """# The Sharma Family — Annual Financial Review 2025

## Net Worth Summary
| Asset Class | Rahul | Priya | Combined |
|---|---|---|---|
| Stocks | ₹18.2L | — | ₹18.2L |
| Mutual Funds | ₹5.5L | ₹28.4L | ₹33.9L |
| Fixed Income (EPF/PPF/NPS/FD) | ₹16.1L | ₹19.5L | ₹35.6L |
| Property | ₹1.12Cr (shared) | ₹22L plot | ₹1.34Cr |
| Gold | ₹0.3L | ₹3.3L | ₹3.6L |
| ESOPs | ₹18L (potential) | — | ₹18L |
| Crypto | ₹4.5L | — | ₹4.5L |
| **Total Assets** | | | **≈ ₹2.48 Cr** |
| Liabilities | ₹45.2L | ₹1.8L | ₹47L |
| **Net Worth** | | | **≈ ₹2.01 Cr** |

## What's Good
- **SIP discipline is excellent** — Priya's ₹49K/month with 10% step-up is textbook
- **Insurance coverage adequate** — ₹1.75Cr term life between both of you
- **Tax planning well-utilized** — Both using 80C, 80D, NPS benefits
- **Diversified across asset classes** — equity, debt, gold, property, even crypto

## Risks & Concerns
1. **Home loan EMI is 25% of take-home** — slightly high but manageable with dual income
2. **Rahul's stock portfolio is concentrated** — 22 stocks but heavy in IT sector (TCS, INFY, WIPRO, LTIM)
3. **Emergency fund is below 6 months** — ₹6.5L vs ₹9L target
4. **Crypto allocation is speculative** — 2% of portfolio, acceptable but monitor
5. **No will or succession planning** — critical with a young child

## Action Items for 2026
1. **Rahul:** Increase SIP by ₹15K/month (total ₹23K). You're too stock-heavy.
2. **Both:** Top up emergency fund to ₹9L — move ₹2.5L from savings to liquid fund
3. **Rahul:** Reduce IT sector concentration — consider booking profits on WIPRO
4. **Priya:** Your education loan ends in Jul 2026 — redirect that ₹22K EMI to daughter's education SIP
5. **Both:** Create a will and nominate each other on all investments
6. **Both:** Review health insurance — ₹15L family floater may be insufficient in 5 years

Overall Family Health Score: **72/100** — Good foundation, needs some optimization."""),
        ]
        for role, content in family_chat:
            db.add(ChatMessage(conversation_id=conv3.id, role=role, content=content))

        print("Added 3 AI chat conversations with detailed history.")

        # ============ NOTIFICATIONS ============
        notifications = [
            (rahul.id, "reminder", "SIP Due: Parag Parikh Flexi Cap", "₹8,000 SIP due on the 5th. Ensure sufficient balance in your bank account.", "/mutual-funds"),
            (priya.id, "reminder", "SIP Due: 6 SIPs this month", "₹49,000 total SIP outflow this month across 6 active SIPs.", "/mutual-funds"),
            (rahul.id, "warning", "Home Loan Rate Review", "SBI home loan rates have increased to 8.75%. Consider refinancing or prepayment.", "/fixed-income"),
            (priya.id, "alert", "ICICI FD Maturing Soon", "Your ₹2.15L ICICI FD matures on Jun 1, 2026. Plan reinvestment.", "/fixed-income"),
            (priya.id, "info", "Education Loan Almost Done!", "Only ₹1.8L remaining on your IIM education loan. Completes Jul 2026. Plan to redirect ₹22K EMI to investments.", "/expenses"),
            (rahul.id, "warning", "Emergency Fund Below Target", "Current: ₹6.5L. Target: ₹9L. Shortfall of ₹2.5L. Consider moving funds to liquid MF.", "/analytics"),
            (rahul.id, "info", "Tax Season Reminder", "FY 2025-26 ends March 31. You've utilized ₹1.85L of ₹1.5L 80C limit. NPS 80CCD(1B) ₹50K utilized. Review pending 80D.", "/tax"),
            (priya.id, "info", "Tax Season Reminder", "FY 2025-26 ends March 31. You've utilized ₹2.95L of ₹1.5L 80C limit. Well done! Verify all proofs uploaded.", "/tax"),
            (rahul.id, "alert", "ESOP Vesting: Infosys", "25 Infosys RSUs vesting on Apr 1, 2026. Review exercise strategy and tax implications.", "/more-assets"),
            (priya.id, "reminder", "Health Insurance Renewal", "Star Health family floater premium ₹22,000 due on Apr 1, 2026.", "/more-assets"),
            (rahul.id, "info", "Portfolio Sector Concentration", "IT sector is 35% of your stock portfolio (TCS, INFY, WIPRO, LTIM). Consider diversifying.", "/stocks"),
            (priya.id, "info", "Goal Progress: Ananya Education", "12% progress towards ₹2.5Cr education fund. On track with current SIPs.", "/goals"),
        ]
        for uid, typ, title, msg, url in notifications:
            db.add(Notification(user_id=uid, type=typ, title=title, message=msg, action_url=url))
        print(f"Added {len(notifications)} notifications.")

        # ============ COMMIT ============
        db.commit()
        print("\n✅ SEED COMPLETE!")
        print("=" * 60)
        print("FAMILY: The Sharmas")
        print(f"  Rahul: rahul@sharma.com / sharma2021 (id={rahul.id})")
        print(f"  Priya: priya@sharma.com / sharma2021 (id={priya.id})")
        print(f"  Family ID: {family.id}")
        print()
        print("DATA SUMMARY:")
        print(f"  Stocks: {len(stock_history)} holdings (Rahul)")
        print(f"  Mutual Funds: {len(mf_holdings) + len(rahul_mf)} holdings (both)")
        print(f"  SIPs: {len(sips)} ({sum(1 for s in sips if s[7])} active)")
        print(f"  Fixed Income: {len(fixed)} (EPF, PPF, NPS, FD, SSY)")
        print(f"  Properties: 2 (Whitefield flat + Mysore plot)")
        print(f"  Gold: {len(gold_buys)} purchases (physical + SGB + digital)")
        print(f"  Liabilities: 3 (home loan, car loan, education loan)")
        print(f"  Insurance: {len(insurance_policies)} policies (term, health, ULIP, motor)")
        print(f"  ESOPs: 2 (Razorpay + Infosys RSU)")
        print(f"  Crypto: 3 (BTC, ETH, SOL)")
        print(f"  Goals: {len(goals)}")
        print(f"  Tax Deductions: {len(deductions)} (FY 2025-26)")
        print(f"  Income entries: {income_count}")
        print(f"  Expense entries: {expense_count}")
        print(f"  AI Memories: {len(memories)}")
        print(f"  Chat Conversations: 3 (with detailed responses)")
        print(f"  Notifications: {len(notifications)}")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()
