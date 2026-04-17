# -*- coding: utf-8 -*-
"""
Test stock data enrichment in render pipeline
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stock_data import enrich_stocks_with_data
from src.render import render_email_html

print("=" * 60)
print("🧪 Testing Stock Data Enrichment in HTML Rendering")
print("=" * 60)

# Load test digest
test_digest_path = Path(__file__).parent.parent / "test_digest.json"
with open(test_digest_path, "r", encoding="utf-8") as f:
    digest = json.load(f)

print(f"\n📊 Original digest has {len(digest.get('stocks', []))} stocks")

# Enrich with real stock data
print("\n⏳ Fetching real stock data...")
digest["stocks"] = enrich_stocks_with_data(digest.get("stocks", []))

print("\n✅ Enrichment complete!")
print("\n📝 Stock data summary:")
for stock in digest["stocks"]:
    name = stock.get("name")
    md = stock.get("market_data", {})
    if md.get("error"):
        print(f"   ❌ {name}: {md['error']}")
    else:
        print(f"   ✅ {name}: ${md.get('price')}, P/E={md.get('pe')}, RSI={md.get('rsi')}, 1M={md.get('change_1m')}%")

# Render HTML
print("\n🎨 Rendering HTML with stock data...")
html = render_email_html(digest)

# Save to file
output_path = Path(__file__).parent.parent / "test_output_with_stock_data.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n💾 Saved to: {output_path}")
print("\n🌐 Open in browser to see:")
print("   - 🇺🇸 US stocks with purple badge")
print("   - 🏭 Industry overview with yellow badge  ")
print("   - 📊 Stock prices, P/E, RSI, 1M% data")
print("\n" + "=" * 60)
