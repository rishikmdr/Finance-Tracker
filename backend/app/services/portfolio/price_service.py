"""Live price fetching for stocks, mutual funds, gold, and NPS."""
import logging
from datetime import datetime, timezone, timedelta
from decimal import Decimal

import httpx
import yfinance as yf
from sqlalchemy.orm import Session

from app.models.ai_memory import PriceCache

logger = logging.getLogger(__name__)

CACHE_TTL_MINUTES = 15


def _is_cache_fresh(cached: PriceCache | None) -> bool:
    if not cached:
        return False
    age = datetime.now(timezone.utc) - cached.last_updated.replace(tzinfo=timezone.utc)
    return age < timedelta(minutes=CACHE_TTL_MINUTES)


def get_stock_price(symbol: str, exchange: str, db: Session) -> dict:
    """Fetch live stock price from yfinance with cache."""
    ticker_symbol = f"{symbol}.{'NS' if exchange == 'NSE' else 'BO'}"

    cached = db.query(PriceCache).filter(PriceCache.symbol == ticker_symbol).first()
    if _is_cache_fresh(cached):
        return {"price": cached.price, "day_change_pct": cached.day_change_pct}

    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.fast_info
        price = float(info.last_price) if hasattr(info, "last_price") else None
        prev_close = float(info.previous_close) if hasattr(info, "previous_close") else None

        if price is None:
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])

        day_change = None
        if price and prev_close and prev_close > 0:
            day_change = round((price - prev_close) / prev_close * 100, 2)

        if price:
            _update_cache(db, ticker_symbol, "stock", price, day_change, "yfinance")

        return {"price": price, "day_change_pct": day_change}
    except Exception as e:
        logger.warning(f"Failed to fetch stock price for {ticker_symbol}: {e}")
        if cached:
            return {"price": cached.price, "day_change_pct": cached.day_change_pct}
        return {"price": None, "day_change_pct": None}


def get_mf_nav(scheme_code: str, db: Session) -> dict:
    """Fetch latest MF NAV from mfapi.in with cache."""
    cache_key = f"MF:{scheme_code}"

    cached = db.query(PriceCache).filter(PriceCache.symbol == cache_key).first()
    if _is_cache_fresh(cached):
        return {"nav": cached.price}

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"https://api.mfapi.in/mf/{scheme_code}/latest")
            resp.raise_for_status()
            data = resp.json()

        if data.get("data") and len(data["data"]) > 0:
            nav = float(data["data"][0]["nav"])
            _update_cache(db, cache_key, "mf", nav, None, "mfapi.in")
            return {"nav": nav}
    except Exception as e:
        logger.warning(f"Failed to fetch MF NAV for {scheme_code}: {e}")

    if cached:
        return {"nav": cached.price}
    return {"nav": None}


def get_gold_price(db: Session) -> dict:
    """Fetch gold price in INR per gram."""
    cache_key = "GOLD:INR_PER_GRAM"

    cached = db.query(PriceCache).filter(PriceCache.symbol == cache_key).first()
    if _is_cache_fresh(cached):
        return {"price_per_gram": cached.price, "day_change_pct": cached.day_change_pct}

    try:
        ticker = yf.Ticker("GOLDBEES.NS")
        hist = ticker.history(period="2d")
        if not hist.empty:
            price = float(hist["Close"].iloc[-1])
            # GOLDBEES price ≈ 1/100th of 10g gold price, so price * 10 ≈ per gram
            price_per_gram = round(price * 10, 2)
            prev = float(hist["Close"].iloc[0]) if len(hist) > 1 else None
            day_change = round((price - prev) / prev * 100, 2) if prev else None
            _update_cache(db, cache_key, "gold", price_per_gram, day_change, "yfinance")
            return {"price_per_gram": price_per_gram, "day_change_pct": day_change}
    except Exception as e:
        logger.warning(f"Failed to fetch gold price: {e}")

    if cached:
        return {"price_per_gram": cached.price, "day_change_pct": cached.day_change_pct}
    return {"price_per_gram": None, "day_change_pct": None}


def get_nps_nav(scheme_code: str, db: Session) -> dict:
    """Fetch NPS NAV (placeholder — Arthgyaan API or fallback)."""
    cache_key = f"NPS:{scheme_code}"
    cached = db.query(PriceCache).filter(PriceCache.symbol == cache_key).first()
    if cached:
        return {"nav": cached.price}
    return {"nav": None}


def get_index_value(index: str, db: Session) -> dict:
    """Fetch index value (NIFTY50, SENSEX)."""
    symbols = {"NIFTY50": "^NSEI", "SENSEX": "^BSESN", "NIFTY_BANK": "^NSEBANK"}
    yf_symbol = symbols.get(index, index)
    cache_key = f"INDEX:{index}"

    cached = db.query(PriceCache).filter(PriceCache.symbol == cache_key).first()
    if _is_cache_fresh(cached):
        return {"value": cached.price, "day_change_pct": cached.day_change_pct}

    try:
        ticker = yf.Ticker(yf_symbol)
        hist = ticker.history(period="2d")
        if not hist.empty:
            value = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[0]) if len(hist) > 1 else None
            day_change = round((value - prev) / prev * 100, 2) if prev else None
            _update_cache(db, cache_key, "index", value, day_change, "yfinance")
            return {"value": value, "day_change_pct": day_change}
    except Exception as e:
        logger.warning(f"Failed to fetch index {index}: {e}")

    if cached:
        return {"value": cached.price, "day_change_pct": cached.day_change_pct}
    return {"value": None, "day_change_pct": None}


def refresh_all_prices(db: Session, user_id: int) -> dict:
    """Refresh all prices for a user's holdings. Returns summary."""
    from app.models.holdings import StockHolding, MFHolding

    stocks = db.query(StockHolding).filter(StockHolding.user_id == user_id).all()
    mfs = db.query(MFHolding).filter(MFHolding.user_id == user_id).all()

    updated = {"stocks": 0, "mf": 0, "gold": False}

    for stock in stocks:
        result = get_stock_price(stock.symbol, stock.exchange.value, db)
        if result["price"]:
            updated["stocks"] += 1

    for mf in mfs:
        result = get_mf_nav(mf.scheme_code, db)
        if result["nav"]:
            updated["mf"] += 1

    gold = get_gold_price(db)
    updated["gold"] = gold["price_per_gram"] is not None

    return updated


def _update_cache(
    db: Session, symbol: str, asset_type: str, price: float,
    day_change: float | None, source: str
):
    cached = db.query(PriceCache).filter(PriceCache.symbol == symbol).first()
    if cached:
        cached.price = price
        cached.day_change_pct = day_change
        cached.last_updated = datetime.now(timezone.utc)
        cached.source = source
    else:
        cached = PriceCache(
            symbol=symbol, asset_type=asset_type, price=price,
            day_change_pct=day_change, source=source,
            last_updated=datetime.now(timezone.utc),
        )
        db.add(cached)
    db.commit()
