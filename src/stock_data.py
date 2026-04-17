# -*- coding: utf-8 -*-
"""
stock_data.py
Fetch real-time stock data (price, P/E, RSI, 1M%) using yfinance
"""

import logging
import yfinance as yf
import pandas as pd
from typing import Optional, Dict
from datetime import datetime, timedelta

log = logging.getLogger(__name__)

def _calculate_rsi(prices: pd.Series, period: int = 14) -> Optional[float]:
    """
    Calculate RSI (Relative Strength Index) manually
    Args:
        prices: Series of closing prices
        period: RSI period (default 14 days)
    Returns:
        RSI value (0-100) or None if insufficient data
    """
    if len(prices) < period + 1:
        return None
    
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi.iloc[-1], 2) if not pd.isna(rsi.iloc[-1]) else None


def get_stock_metrics(ticker: str, exchange: str = "台股") -> Dict:
    """
    Get stock metrics: current price, P/E, RSI, 1M%
    
    Args:
        ticker: Stock ticker symbol (e.g., "2330", "AAPL")
        exchange: "台股" or "美股"
    
    Returns:
        Dict with keys: price, pe, rsi, change_1m, error
    """
    result = {
        "price": None,
        "pe": None,
        "rsi": None,
        "change_1m": None,
        "error": None
    }
    
    # Format ticker for yfinance
    if exchange == "台股":
        yf_ticker = f"{ticker}.TW"
        if ticker.startswith("6"):  # OTC stocks
            yf_ticker = f"{ticker}.TWO"
    elif exchange == "美股":
        yf_ticker = ticker
    else:
        result["error"] = f"Unknown exchange: {exchange}"
        return result
    
    try:
        log.info(f"📊 Fetching data for {yf_ticker}...")
        stock = yf.Ticker(yf_ticker)
        
        # Get basic info
        info = stock.info
        
        # Current price
        result["price"] = info.get("currentPrice") or info.get("regularMarketPrice")
        
        # P/E ratio (prefer forward P/E, fallback to trailing P/E)
        result["pe"] = info.get("forwardPE") or info.get("trailingPE")
        if result["pe"]:
            result["pe"] = round(result["pe"], 2)
        
        # Get historical data for RSI and 1M% calculation
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)  # Get 60 days for RSI calculation
        
        hist = stock.history(start=start_date, end=end_date)
        
        if not hist.empty:
            # Calculate RSI
            result["rsi"] = _calculate_rsi(hist['Close'])
            
            # Calculate 1 month % change
            if len(hist) >= 20:  # At least 20 trading days (~1 month)
                price_1m_ago = hist['Close'].iloc[-21]  # 21 days ago (1 month)
                current_price = hist['Close'].iloc[-1]
                result["change_1m"] = round(((current_price - price_1m_ago) / price_1m_ago) * 100, 2)
        
        log.info(f"✅ {yf_ticker}: ${result['price']}, P/E={result['pe']}, RSI={result['rsi']}, 1M={result['change_1m']}%")
        
    except Exception as e:
        log.error(f"❌ Failed to fetch {yf_ticker}: {e}")
        result["error"] = str(e)
    
    return result


def enrich_stocks_with_data(stocks: list) -> list:
    """
    Enrich stock list with real-time market data
    
    Args:
        stocks: List of stock dicts from AI analysis
    
    Returns:
        Same list with added market_data field
    """
    enriched = []
    
    for stock in stocks:
        ticker = stock.get("ticker")
        exchange = stock.get("exchange", "台股")
        
        # Skip if no ticker (e.g., sector overview)
        if not ticker:
            enriched.append(stock)
            continue
        
        # Fetch market data
        market_data = get_stock_metrics(ticker, exchange)
        
        # Add to stock dict
        stock["market_data"] = market_data
        enriched.append(stock)
    
    return enriched


def format_stock_badge(stock: dict) -> str:
    """
    Generate HTML badge string for stock display
    Returns formatted string like: "$1,234 | P/E 25.3 | RSI 67 | 1M +12.5%"
    """
    data = stock.get("market_data", {})
    
    if not data or data.get("error"):
        return ""
    
    parts = []
    
    # Price
    price = data.get("price")
    if price:
        parts.append(f"${price:,.2f}" if price >= 100 else f"${price:.2f}")
    
    # P/E
    pe = data.get("pe")
    if pe:
        parts.append(f"P/E {pe}")
    
    # RSI
    rsi = data.get("rsi")
    if rsi:
        parts.append(f"RSI {rsi}")
    
    # 1M %
    change = data.get("change_1m")
    if change is not None:
        sign = "+" if change > 0 else ""
        parts.append(f"1M {sign}{change}%")
    
    return " | ".join(parts)
