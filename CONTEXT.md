# Finance Tracker — Context Paper for Claude

## What Is This?

A **self-hosted personal & family finance platform** for Indian households. It tracks daily income and expenses, investments across every asset class available in India, and provides AI-powered financial insights — all running on a laptop with zero external dependencies.

---

## Who Is It For?

Dual-income Indian families (25-45 age group) who:
- Invest in stocks (NSE/BSE), mutual funds, PPF, EPF, NPS, FDs, gold, crypto, ESOPs
- Want one place to see their complete net worth instead of checking 10 apps
- Need to plan for goals (retirement, children's education, home purchase)
- Want to optimize taxes under Indian tax law (Old vs New regime, 80C/80D/80CCD)
- Want AI to analyze their portfolio and answer financial questions

---

## Core Domains

### 1. Daily Expense & Income Tracking
- **Manual expense entry** with date, amount, category, and optional notes
- **Axio CSV import** — bulk upload from the Axio personal finance app with auto-categorization and duplicate detection
- **Income tracking** by source: salary, rental, dividends, interest, freelance
- **Earner identification** — self or spouse, so family income is properly attributed
- **Monthly trends** — income vs expenses over time, savings rate calculation
- **Category breakdown** — where money goes each month (groceries, housing, dining, transport, utilities, shopping, healthcare, entertainment, childcare, EMIs, etc.)

### 2. Investment & Savings Tracking (India-specific)

**Equity**
- Stocks: NSE & BSE with investment type classification (long-term, swing, positional, intraday, IPO)
- Mutual Funds: scheme code, NAV tracking, units held, lumpsum vs SIP mode
- SIPs: monthly/quarterly, day-of-month, step-up percentage, pause/resume, installment history

**Fixed Income**
- PPF, EPF, VPF — with interest rates and maturity
- NPS — tier-1 contributions
- FDs — bank, interest rate, maturity date
- SSY (Sukanya Samriddhi Yojana) — for daughters
- Bonds — corporate and government

**Real Assets**
- Property — residential, commercial, land. Purchase price, current valuation, rental income, loan linkage
- Gold — physical, digital, Sovereign Gold Bonds (SGB). Weight in grams, purchase price

**Alternative**
- Crypto — BTC, ETH, altcoins. Exchange, quantity, avg buy price in INR
- ESOP/RSU — grants, vesting schedules, exercised shares, strike vs FMV, potential value calculation

**Protection**
- Insurance — term, health, ULIP, endowment, motor, travel. Sum assured, premium frequency, next premium date, maturity tracking

**Liabilities**
- Home loan, car loan, personal loan, education loan. Principal, outstanding, EMI, interest rate

### 3. Financial Goal Planning
- Named goals with target amount, current amount, target date, priority (critical/high/medium/low)
- **SIP calculator** — auto-calculates the monthly SIP needed to reach the goal, factoring in:
  - Inflation (default 6%)
  - Expected return (default 12% equity, 7% debt)
  - Current savings already allocated
- Categories: retirement, education, home purchase, marriage, emergency fund, travel, vehicle
- **On-track indicator** — compares progress percentage vs timeline percentage
- Inflation-adjusted target display

### 4. Tax Planning (Indian Tax Law)
- **Deduction tracking** by section with statutory limits:
  - 80C (₹1.5L) — PPF, ELSS, LIC, tuition fees
  - 80D — health insurance premiums (self, family, parents, senior citizen limits)
  - 80CCD(1B) — NPS additional ₹50K
  - 80G — donations
  - 80E — education loan interest
  - 80TTA/80TTB — savings/FD interest
  - HRA — house rent allowance
  - 24(b) — home loan interest (₹2L limit)
- **Old vs New regime comparison** — computes tax under both regimes and recommends the better one
- Financial year auto-detection (April 1 – March 31)
- Proof-of-documentation tracking per deduction

### 5. Portfolio Analytics
- **XIRR calculation** — Extended Internal Rate of Return using Newton-Raphson algorithm, per-stock and per-fund
- **Net worth snapshot** — total assets minus total liabilities, with allocation percentages
- **Asset allocation** — equity / fixed income / real estate / gold / crypto breakdown
- **Stock returns** — per-holding P&L with absolute gain, percentage return, and XIRR
- **MF returns** — per-fund performance
- **Monthly income/expense trends** — time-series data for charting
- **Expense breakdown by category** — for any given month
- **Portfolio export** — full JSON export for backup or external analysis

### 6. Smart Notifications & Alerts
- Auto-generated alerts for:
  - SIP due dates (next 3 days)
  - Insurance premiums (within 15 days)
  - FD/bond maturity (within 30 days)
  - Goal deadlines (<80% progress with <6 months remaining)
  - ESOP vesting dates
  - Tax season reminders (January–March)
- 7-day deduplication to avoid alert spam
- Mark as read, mark all read, notification types (alert, warning, reminder, info)

### 7. AI-Powered Features (Claude API)
- **Portfolio analysis** — AI reads actual portfolio data and provides health score, strengths, weaknesses, alerts, and suggestions
- **Financial chatbot** — multi-turn conversations where AI sees the user's holdings, income, expenses, and goals for personalized advice
- **Conversation memory** — past chats are stored and retrievable
- **User memory** — key facts (goals, preferences, plans) extracted and stored for context across sessions
- **Suggested prompts** — pre-built questions like "Am I on track for retirement?", "Where should I invest ₹50K?", "How can I save more tax?"
- **Graceful degradation** — all features work without an API key; AI features simply show a prompt to add the key in Settings

### 8. Family / Multi-User
- **Family unit** — owner creates family, invites members by email
- **Combined net worth** — aggregated view across all family members
- **Per-member breakdown** — each member's contribution as a percentage bar
- **Role-based access** — owner vs member permissions
- **Individual privacy** — each member manages their own holdings data

---

## Live Price Data Sources
- **Stocks & Gold**: yfinance — NSE/BSE symbols (e.g., RELIANCE.NS, TCS.BO), gold price in INR
- **Mutual Fund NAVs**: MFapi.in — free public API, no auth required
- **Index values**: Nifty 50, Sensex via yfinance
- **Price caching**: SQLite table with symbol, price, day_change_pct, last_updated — avoids repeated API calls

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript 5.9, Vite 7, TailwindCSS 4, TanStack Query, Recharts, React Router 7, Lucide Icons |
| Backend | Python 3.11+, FastAPI, Uvicorn, SQLAlchemy 2, Pydantic v2, python-jose (JWT), passlib+bcrypt |
| Database | SQLite (default, zero-config) or PostgreSQL (production) |
| AI | Anthropic Claude API (user provides own key) |
| Prices | yfinance, MFapi.in (free) |
| Import | Axio CSV parser |

---

## Architecture

```
Finance-Tracker/
├── start.sh                    # One-command launcher
├── seed_data.py                # 5-year sample data for "The Sharma Family"
├── demo.html                   # Animated product presentation (17 slides)
│
├── backend/
│   ├── pyproject.toml          # Python dependencies
│   └── app/
│       ├── main.py             # FastAPI app with lifespan (auto-creates 24 tables)
│       ├── core/
│       │   ├── config.py       # Settings from env vars (DATABASE_URL, API key, etc.)
│       │   ├── database.py     # SQLAlchemy engine, session, Base, init_db()
│       │   └── security.py     # JWT creation/verification, password hashing
│       ├── api/
│       │   ├── deps.py         # get_current_user dependency
│       │   └── routes/
│       │       ├── auth.py     # Register, login, refresh, family management
│       │       ├── dashboard.py# Net worth summary, family summary
│       │       ├── holdings.py # CRUD for stocks, MFs, SIPs, fixed, property, gold, liabilities
│       │       ├── expenses.py # Expenses, income, Axio CSV import
│       │       ├── portfolio.py# Analytics, AI analysis, chat, prices, settings
│       │       └── extended.py # Goals, insurance, ESOP, crypto, tax, notifications
│       ├── models/
│       │   ├── user.py         # User, Family
│       │   ├── holdings.py     # StockHolding, MFHolding, SIP, FixedHolding, PropertyHolding, GoldHolding, Liability
│       │   ├── expense.py      # Expense, ExpenseCategory, Income
│       │   ├── extended.py     # FinancialGoal, InsurancePolicy, ESOPHolding, CryptoHolding, TaxDeduction, Notification
│       │   ├── settings.py     # UserSettings
│       │   └── ai_memory.py    # UserMemory, ChatConversation, ChatMessage, PriceCache
│       ├── schemas/            # Pydantic request/response models
│       └── services/
│           ├── ai/engine.py    # Claude API integration (analysis + chat)
│           └── portfolio/
│               ├── analytics.py# XIRR, returns, trends, net worth calculation
│               └── price_service.py # yfinance + MFapi.in with caching
│
└── frontend/
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx             # Routes (15 pages, 13 authenticated)
        ├── lib/api.ts          # Axios client with JWT interceptor
        ├── hooks/useAuth.ts    # Auth context hook
        ├── types/api.ts        # TypeScript interfaces
        ├── components/layout/
        │   ├── AuthProvider.tsx # JWT auth context
        │   ├── AppLayout.tsx   # Sidebar + content wrapper
        │   └── Sidebar.tsx     # Navigation with notification badge
        └── pages/
            ├── DashboardPage.tsx
            ├── StocksPage.tsx
            ├── MutualFundsPage.tsx
            ├── FixedIncomePage.tsx
            ├── MoreAssetsPage.tsx   # Crypto, ESOP, Insurance
            ├── ExpensesPage.tsx
            ├── GoalsPage.tsx
            ├── TaxPage.tsx
            ├── AnalyticsPage.tsx
            ├── FamilyPage.tsx
            ├── ChatPage.tsx
            ├── NotificationsPage.tsx
            ├── SettingsPage.tsx
            ├── LoginPage.tsx
            └── RegisterPage.tsx
```

---

## Database Schema (24 Tables)

| Table | Key Fields |
|-------|-----------|
| users | email, name, password_hash, family_id, family_role |
| families | name |
| holdings_stocks | symbol, exchange, investment_type, quantity, avg_buy_price, buy_date, broker |
| holdings_mf | scheme_code, scheme_name, category, units, avg_nav, investment_mode |
| sips | scheme_code, amount, day_of_month, frequency, step_up_percent, is_active |
| sip_installments | sip_id, date, amount, nav, units_bought, status |
| holdings_fixed | type (EPF/PPF/NPS/FD/SSY/bonds), invested_amount, current_value, interest_rate, maturity_date |
| holdings_property | type, purchase_price, estimated_current_value, loan_outstanding |
| holdings_gold | type (physical/digital/SGB), quantity_grams, purchase_price |
| liabilities | type, principal, outstanding, interest_rate, emi_amount |
| expenses | date, amount, category_id, description, import_source |
| expense_categories | name, parent_id, icon, axio_category_name |
| incomes | date, amount, source, earner |
| user_settings | anthropic_api_key, currency, theme, monthly_budget, emergency_fund_target, risk_profile |
| chat_conversations | user_id, title |
| chat_messages | conversation_id, role, content |
| user_memory | key, value, category (goal/preference/fact/plan) |
| price_cache | symbol, asset_type, price, day_change_pct, last_updated |
| financial_goals | name, target_amount, current_amount, target_date, priority, status, monthly_sip_needed |
| insurance_policies | type, provider, sum_assured, annual_premium, next_premium_date, maturity_value |
| esop_holdings | company, type, total_granted, vested, exercised, strike_price, current_fmv |
| crypto_holdings | coin, quantity, avg_buy_price_inr, exchange |
| tax_deductions | financial_year, section, amount, max_limit, proof_available |
| notifications | type, title, message, is_read, action_url |

---

## API Endpoints (50+)

### Auth (7)
- POST `/auth/register`, `/auth/login`, `/auth/refresh`
- GET `/auth/me`, `/auth/family`
- POST `/auth/family`, `/auth/family/invite`

### Holdings CRUD (19)
- Stocks: GET, POST, PUT, DELETE `/holdings/stocks`
- Mutual Funds: GET, POST, DELETE `/holdings/mf`
- SIPs: GET, POST, PUT (pause), DELETE `/holdings/sips`
- Fixed Income: GET, POST, DELETE `/holdings/fixed`
- Property: GET, POST, DELETE `/holdings/property`
- Gold: GET, POST, DELETE `/holdings/gold`
- Liabilities: GET, POST, DELETE `/holdings/liabilities`

### Dashboard (2)
- GET `/dashboard/summary` — personal net worth & asset breakdown
- GET `/dashboard/family-summary` — combined family view

### Expenses & Income (7)
- GET, POST, DELETE `/expenses` + GET `/expense-categories`
- POST `/expenses/import/axio` — CSV upload
- GET, POST, DELETE `/income`

### Analytics (6)
- GET `/portfolio/net-worth`, `/portfolio/stock-returns`, `/portfolio/mf-returns`
- GET `/portfolio/trends`, `/portfolio/expense-breakdown`, `/portfolio/export`

### AI & Prices (7)
- GET `/portfolio/analysis` — AI portfolio health
- POST `/chat`, GET `/conversations`, GET `/conversations/{id}/messages`
- POST `/prices/refresh`, GET `/prices/stock/{symbol}`, `/prices/mf/{code}`, `/prices/gold`, `/prices/index/{name}`

### Goals, Tax, Insurance, ESOP, Crypto, Notifications (17)
- Goals: GET, POST, PUT, DELETE `/goals`
- Insurance: GET, POST, DELETE `/insurance`
- ESOP: GET, POST, DELETE `/esop`
- Crypto: GET, POST, DELETE `/crypto`
- Tax: GET, POST, DELETE `/tax/deductions` + GET `/tax/regime-comparison`
- Notifications: GET, PUT (read), PUT (read-all), POST (generate) `/notifications`

### Settings & Misc (4)
- GET, PUT `/settings` + DELETE `/settings/api-key`
- GET `/properties/rental-summary`, `/emergency-fund`

---

## Sample Data Available

The `seed_data.py` script creates 5 years of realistic data for **The Sharma Family**:
- **Rahul** (34, Sr Software Engineer @ Infosys) — aggressive investor, ₹28L salary
- **Priya** (31, Product Manager @ Flipkart) — moderate investor, ₹22L salary
- **Ananya** (3, daughter) — has SSY account

Includes: 22 stocks, 14 MFs, 10 SIPs with installment history, 8 fixed income, 2 properties, 6 gold purchases, 3 liabilities, 6 insurance policies, 2 ESOPs, 3 crypto, 7 goals, 15 tax deductions, 300+ expenses (with seasonal patterns), 150+ income entries, 19 AI memories, 3 chat conversations, 12 notifications.

---

## How to Run

```bash
git clone <repo> && cd Finance-Tracker
chmod +x start.sh && ./start.sh
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/api/docs (Swagger)
# AI: Add your Anthropic API key in Settings page
```

**Prerequisites**: Python 3.11+ and Node.js 18+ (that's it).

---

## What to Build Next (Suggested)

Here are areas where this prototype can be extended:

1. **Recurring transactions** — auto-create monthly salary income and fixed expenses (rent, EMIs)
2. **Budget management** — set category-wise monthly budgets, track actual vs budget, alert on overspend
3. **Mutual fund SIP installment auto-tracking** — record actual NAV and units for each SIP execution
4. **Bank statement import** — parse CSV/PDF from major Indian banks (SBI, HDFC, ICICI, Axis)
5. **Capital gains report** — LTCG/STCG calculation for stocks and MFs per Indian tax rules
6. **Dividend tracking** — record dividends per stock/MF and show dividend yield
7. **Rebalancing suggestions** — compare current allocation vs target allocation, suggest trades
8. **Mobile responsive polish** — the frontend uses TailwindCSS so it's mobile-friendly, but needs testing
9. **PDF report generation** — monthly/quarterly financial summary as downloadable PDF
10. **Multi-currency support** — for NRIs tracking investments in India + abroad
11. **Dark/light theme toggle** — settings already has a theme field, just needs frontend implementation
12. **Data encryption at rest** — encrypt sensitive fields (API key, account numbers) in SQLite
