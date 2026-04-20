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
        # Also try .TWO for OTC stocks if .TW fails
        fallback_ticker = f"{ticker}.TWO"
    elif exchange == "美股":
        yf_ticker = ticker
        fallback_ticker = None
    else:
        result["error"] = f"Unknown exchange: {exchange}"
        return result
    
    def _try_fetch_ticker(ticker_symbol: str) -> bool:
        """Try to fetch data for a ticker symbol. Returns True if successful."""
        try:
            log.info(f"📊 Fetching data for {ticker_symbol}...")
            stock = yf.Ticker(ticker_symbol)
            
            # Get basic info
            info = stock.info
            
            # Check if ticker is valid (yfinance returns empty dict for invalid tickers)
            if not info or len(info) < 5:
                log.warning(f"⚠️  {ticker_symbol}: No data available (possibly delisted or invalid)")
                return False
            
            # Current price
            result["price"] = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
            
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
            
            # Check if we got any useful data
            if result["price"] is None and hist.empty:
                log.warning(f"⚠️  {ticker_symbol}: No price or historical data")
                return False
            
            log.info(f"✅ {ticker_symbol}: ${result['price']}, P/E={result['pe']}, RSI={result['rsi']}, 1M={result['change_1m']}%")
            return True
            
        except Exception as e:
            error_msg = str(e)
            # Don't log as ERROR for 404 (stock not found) - it's expected for delisted stocks
            if "404" in error_msg or "Not Found" in error_msg:
                log.warning(f"⚠️  {ticker_symbol}: Stock not found (possibly delisted)")
            else:
                log.error(f"❌ {ticker_symbol}: {error_msg}")
            return False
    
    # Try primary ticker
    success = _try_fetch_ticker(yf_ticker)
    
    # If failed and we have a fallback (TW -> TWO for OTC stocks), try it
    if not success and fallback_ticker:
        log.info(f"🔄 Trying fallback ticker {fallback_ticker}...")
        success = _try_fetch_ticker(fallback_ticker)
    
    # Set error if no data was retrieved
    if not success:
        result["error"] = "Stock data unavailable (possibly delisted or invalid ticker)"
    
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
        name = stock.get("name", "")
        
        # Skip if no ticker (e.g., sector overview)
        if not ticker:
            enriched.append(stock)
            continue
        
        # Skip invalid tickers (AI parsing errors)
        invalid_tickers = ["無", "N/A", "—", "-", "待確認", "未知", "TBD", "?", "？"]
        if ticker.strip() in invalid_tickers:
            log.warning(f"⚠️ 跳過無效 ticker: {name} (ticker={ticker})")
            stock["market_data"] = {"error": "Invalid ticker", "price": None, "pe": None, "rsi": None, "change_1m": None}
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
