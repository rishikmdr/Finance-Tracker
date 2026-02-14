# Finance Tracker — Project Plan

## 1. What Are We Building?

A personal finance dashboard for a dual-income household that:
- Tracks **income & expenses** (yours + wife's)
- Tracks **all investments** — shares, mutual funds, PF, NPS, property, gold
- Shows **live market prices** for stocks and MF NAVs
- Pulls expense data from **Axio** (or a workaround, since Axio has no API)
- Gives a **consolidated net worth** view at any point in time

---

## 2. Scope — What Gets Tracked

| Category | Details | Data Source |
|----------|---------|-------------|
| **Income** | Salary (you + wife), rental, dividends, interest | Manual entry / bank statement import |
| **Expenses** | Daily spends, bills, EMIs, subscriptions | Axio workaround (see below), manual |
| **Shares** | NSE/BSE holdings | Manual holdings + yfinance for live prices |
| **Mutual Funds** | SIPs, lumpsum, all schemes | Manual holdings + MFapi.in for NAV |
| **Provident Fund** | EPF + VPF balances | Manual entry (EPFO has no API) |
| **NPS** | Tier 1 & 2 contributions | Manual entry + Arthgyaan API for NAV |
| **Property** | Purchase price, current estimated value | Manual entry |
| **Fixed Deposits** | Bank FDs, corporate FDs | Manual entry |
| **Gold** | Physical, digital, SGBs | Manual entry + yfinance for gold price |
| **Other** | PPF, SSY, bonds, crypto, etc. | Manual entry |

---

## 3. The Axio Problem & Solution

**Problem:** Axio (formerly Walnut) has **no public API, no data export, and no third-party integrations**. It reads SMS to auto-categorize expenses.

**Workaround options (pick one or combine):**

| Option | How | Effort |
|--------|-----|--------|
| **A. SMS parsing (recommended)** | Build our own SMS parser that reads the same bank/UPI SMS that Axio reads. Run it on a simple Android companion app or use Tasker/MacroDroid to forward SMS to our backend. | Medium |
| **B. Manual CSV import** | User exports bank statements (most banks offer CSV/XLS download) and imports into our tracker monthly. | Low |
| **C. Manual entry** | Simple form to log expenses. Defeats the purpose if Axio already does this. | Low |
| **D. Screenshot/OCR** | Take screenshots of Axio's reports, OCR them into structured data. Hacky but works. | Medium |
| **E. Bank statement email parsing** | Many banks email monthly statements. Auto-parse these via an email integration. | Medium |

**Recommendation:** Start with **Option B (CSV import)** for quick wins, then build **Option A (SMS parsing)** or **Option E (email parsing)** as a Phase 2 enhancement.

---

## 4. Tech Stack (Proposed)

### Backend
- **Python 3.12+** with **FastAPI** — lightweight, async, great for APIs
- **SQLite** (start simple) → migrate to **PostgreSQL** if needed later
- **SQLAlchemy** — ORM
- **Celery + Redis** — for scheduled jobs (price refresh, etc.)

### Frontend
- **React** (Vite + TypeScript) — modern, fast
- **Recharts or Chart.js** — for portfolio graphs, expense charts
- **TailwindCSS** — styling

### Data Sources / Integrations
- **yfinance** (Python) — live stock prices, gold prices, index values
- **MFapi.in** — mutual fund NAV (free, no auth)
- **Arthgyaan API** — NPS NAV data
- **CSV parser** — for bank statement imports

### Infrastructure (local-first)
- Runs locally or on a home server (Raspberry Pi, NAS, etc.)
- Optional: Deploy to a cheap VPS or Railway/Render later
- Docker Compose for easy setup

---

## 5. Architecture

```
┌─────────────────────────────────────────────────┐
│                  React Frontend                  │
│  Dashboard │ Portfolio │ Expenses │ Net Worth    │
└──────────────────────┬──────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────┐
│                 FastAPI Backend                   │
│                                                  │
│  ┌─────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ Auth    │ │ Portfolio │ │ Expense Manager  │  │
│  │ Module  │ │ Manager  │ │ (CSV import etc) │  │
│  └─────────┘ └──────────┘ └──────────────────┘  │
│                                                  │
│  ┌─────────────────────────────────────────────┐ │
│  │         Price Refresh Service (Celery)      │ │
│  │  yfinance │ MFapi.in │ Arthgyaan │ Gold     │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────┘
                       │
              ┌────────▼────────┐
              │   SQLite / PG   │
              │   Database      │
              └─────────────────┘
```

---

## 6. Database Schema (High Level)

### Core Tables

```
users
  - id, name, email, password_hash

accounts (bank accounts, wallets)
  - id, user_id, name, type (savings/current/wallet), bank_name

income
  - id, user_id, date, amount, source, category, notes

expenses
  - id, user_id, account_id, date, amount, category, subcategory,
    description, import_source (manual/csv/sms)

holdings_stocks
  - id, user_id, symbol, exchange (NSE/BSE), quantity, avg_buy_price,
    buy_date, broker

holdings_mutual_funds
  - id, user_id, scheme_code (AMFI code), units, avg_nav,
    buy_date, folio_number, platform

holdings_fixed
  - id, user_id, type (EPF/VPF/PPF/NPS/FD/SSY/bonds),
    invested_amount, current_value, interest_rate,
    start_date, maturity_date, notes

holdings_property
  - id, user_id, name, purchase_price, purchase_date,
    estimated_current_value, last_valuation_date, notes

holdings_gold
  - id, user_id, type (physical/digital/SGB), quantity_grams,
    purchase_price, purchase_date

price_cache
  - symbol, price, last_updated, source
```

---

## 7. Key Features by Screen

### Dashboard (Home)
- Total net worth (all assets combined)
- Net worth trend chart (monthly)
- Monthly income vs expenses summary
- Asset allocation pie chart (equity / debt / real estate / gold / cash)

### Portfolio — Stocks
- Holdings table with live prices, P&L, day change
- Sector-wise breakdown
- Add/edit/delete holdings
- Auto-refresh prices every 15 mins (market hours)

### Portfolio — Mutual Funds
- Holdings with latest NAV, current value, returns (XIRR)
- SIP tracker
- Fund-wise and category-wise (large cap, mid cap, debt, etc.) breakdown

### Portfolio — Fixed Income
- EPF, VPF, PPF, NPS, FDs — all in one view
- Maturity calendar
- Interest accrual tracking

### Portfolio — Property & Gold
- Properties with estimated appreciation
- Gold holdings with live gold price

### Income Tracker
- Monthly/yearly income view
- Income by source (salary, rental, dividends, etc.)
- You vs wife split view

### Expense Tracker
- Category-wise expense breakdown
- Monthly trend
- CSV import from bank statements
- Manual entry form
- Budget vs actual

### Net Worth
- Consolidated view across ALL asset classes
- Historical net worth growth chart
- Liabilities tracking (loans, EMIs)
- Assets minus liabilities = true net worth

---

## 8. Build Phases

### Phase 1 — Foundation (MVP)
- [ ] Project setup (Python backend + React frontend + Docker)
- [ ] Database schema & migrations
- [ ] User auth (simple, single user is fine for now)
- [ ] Manual entry for all holding types (stocks, MF, FD, property, gold, PF, NPS)
- [ ] yfinance integration for live stock prices
- [ ] MFapi.in integration for MF NAV
- [ ] Basic dashboard with net worth calculation
- [ ] Portfolio views for each asset class

### Phase 2 — Expense & Income Tracking
- [ ] Income entry and tracking
- [ ] Expense entry (manual)
- [ ] CSV bank statement import & parser (support SBI, HDFC, ICICI, Kotak formats)
- [ ] Expense categorization (auto + manual)
- [ ] Monthly income vs expense views
- [ ] Budget setting and tracking

### Phase 3 — Advanced Integrations
- [ ] NPS NAV via Arthgyaan API
- [ ] Gold price tracking (via yfinance or commodity API)
- [ ] SMS forwarding + parsing for auto expense capture (Axio replacement)
- [ ] Email statement parser
- [ ] Scheduled price refresh (Celery jobs)

### Phase 4 — Analytics & Polish
- [ ] XIRR calculation for MF and stock returns
- [ ] Asset allocation analysis & rebalancing suggestions
- [ ] Net worth historical trend
- [ ] Tax-related views (LTCG, STCG, dividend income)
- [ ] Mobile-responsive design
- [ ] Data backup & export (CSV/JSON)

### Phase 5 — Optional / Future
- [ ] Multi-user (wife gets her own login)
- [ ] Mobile app (React Native or PWA)
- [ ] CAS (Consolidated Account Statement) parser for auto MF import
- [ ] EPFO passbook scraper
- [ ] Notifications (SIP reminders, FD maturity alerts)
- [ ] Goal-based planning (retirement, house, education)

---

## 9. Open Questions to Decide Before Building

1. **Local-only or cloud-hosted?**
   - Local (more private, your data stays with you) vs hosted (accessible from phone anywhere)

2. **Single user or multi-user from day 1?**
   - Can start single-user and add wife's login later

3. **Which bank statement formats to prioritize?**
   - Which banks do you and your wife use? (SBI, HDFC, ICICI, Kotak, etc.)

4. **Expense categories** — want to match Axio's categories or define your own?

5. **How do you currently track investments?**
   - Any existing spreadsheet/data we can import to bootstrap?

6. **Do you want this as a web app, desktop app, or both?**

---

## 10. Data Source Summary

| Data | Source | Cost | Auth Required |
|------|--------|------|---------------|
| Stock prices (NSE/BSE) | [yfinance](https://github.com/ranaroussi/yfinance) | Free | No |
| Mutual Fund NAV | [MFapi.in](https://www.mfapi.in/) | Free | No |
| NPS NAV | [Arthgyaan API](https://arthgyaan.com/blog/nps-nav-api.html) | Free | No |
| Gold price | yfinance (`GC=F` or `GOLDBEES.NS`) | Free | No |
| Expense data | CSV bank statement import | Free | No |
| Income data | Manual entry | Free | No |
| Property value | Manual entry | Free | No |
| EPF/PPF balance | Manual entry (no API available) | Free | No |
