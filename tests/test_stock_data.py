# -*- coding: utf-8 -*-
"""
Test stock_data.py module
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stock_data import get_stock_metrics, enrich_stocks_with_data

print("=" * 60)
print("🧪 Stock Data Module Test")
print("=" * 60)

# Test 1: Taiwan stock
print("\n1️⃣ Testing Taiwan stock (台積電 2330)...")
tsmc_data = get_stock_metrics("2330", "台股")
print(f"   Price: ${tsmc_data.get('price')}")
print(f"   P/E: {tsmc_data.get('pe')}")
print(f"   RSI: {tsmc_data.get('rsi')}")
print(f"   1M%: {tsmc_data.get('change_1m')}%")
print(f"   Error: {tsmc_data.get('error')}")

# Test 2: US stock
print("\n2️⃣ Testing US stock (NVIDIA NVDA)...")
nvda_data = get_stock_metrics("NVDA", "美股")
print(f"   Price: ${nvda_data.get('price')}")
print(f"   P/E: {nvda_data.get('pe')}")
print(f"   RSI: {nvda_data.get('rsi')}")
print(f"   1M%: {nvda_data.get('change_1m')}%")
print(f"   Error: {nvda_data.get('error')}")

# Test 3: Enrich stock list (like in main.py)
print("\n3️⃣ Testing enrich_stocks_with_data()...")
test_stocks = [
    {"name": "台積電", "ticker": "2330", "exchange": "台股"},
    {"name": "Marvell", "ticker": "MRVL", "exchange": "美股"},
]

enriched = enrich_stocks_with_data(test_stocks)

for stock in enriched:
    print(f"\n   {stock['name']} ({stock['ticker']}):")
    md = stock.get("market_data", {})
    if md.get("error"):
        print(f"      ❌ Error: {md['error']}")
    else:
        print(f"      Price: ${md.get('price')}")
        print(f"      P/E: {md.get('pe')}")
        print(f"      RSI: {md.get('rsi')}")
        print(f"      1M%: {md.get('change_1m')}%")

print("\n" + "=" * 60)
print("✅ Test complete!")
print("=" * 60)
