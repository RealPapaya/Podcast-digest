# -*- coding: utf-8 -*-
"""
render.py
將 digest dict 渲染成精美 HTML Email（對標截圖設計）
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)

# ── 顏色配置 ─────────────────────────────────────────────────────
STANCE_CONFIG = {
    "看多": {"dot": "#22c55e", "border": "#22c55e", "bg": "#f0fdf4", "text": "看多"},
    "觀望": {"dot": "#f59e0b", "border": "#f59e0b", "bg": "#fffbeb", "text": "觀望"},
    "看空": {"dot": "#ef4444", "border": "#ef4444", "bg": "#fef2f2", "text": "看空"},
    "中性": {"dot": "#6b7280", "border": "#6b7280", "bg": "#f9fafb", "text": "中性"},
}

RISK_CONFIG = {
    "低": {"color": "#166534", "bg": "#dcfce7"},
    "中": {"color": "#92400e", "bg": "#fef3c7"},
    "高": {"color": "#991b1b", "bg": "#fee2e2"},
}

CATEGORY_CONFIG = {
    "台股": {"color": "#1d4ed8", "bg": "#dbeafe"},
    "美股": {"color": "#7c3aed", "bg": "#ede9fe"},
    "半導體": {"color": "#0f766e", "bg": "#ccfbf1"},
    "總經": {"color": "#374151", "bg": "#f3f4f6"},
    "其他": {"color": "#374151", "bg": "#f3f4f6"},
}


def _stance_dot(stance: str) -> str:
    cfg = STANCE_CONFIG.get(stance, STANCE_CONFIG["中性"])
    return f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{cfg["dot"]};margin-right:6px;vertical-align:middle;"></span>'


def _badge(text: str, color: str, bg: str) -> str:
    return (
        f'<span style="display:inline-block;padding:2px 8px;border-radius:4px;'
        f'background:{bg};color:{color};font-size:12px;font-weight:600;">{text}</span>'
    )


def _render_stock_card(stock: dict) -> str:
    """
    Render a single stock card with market data (matching reference image format)
    """
    stance = stock.get("stance", "觀望")
    risk = stock.get("risk", "中")
    s_cfg = STANCE_CONFIG.get(stance, STANCE_CONFIG["觀望"])
    src = stock.get("source_time", "")

    ticker = stock.get("ticker", "")
    exchange = stock.get("exchange", "")
    sector = stock.get("sector", "")
    name = stock.get('name', '')
    
    # 右上角標籤
    if exchange == "美股":
        label = f"<span style='font-size:12px;color:#9ca3af;'>🇺🇸 美股{sector}</span>"
    elif not ticker and sector:  # 產業概述
        label = f"<span style='font-size:12px;color:#9ca3af;'>🏭 {sector}產業</span>"
    else:
        label = f"<span style='font-size:12px;color:#9ca3af;'>{exchange}{sector}</span>"
    
    # 股價資訊行（灰色背景、表格式）
    market_data = stock.get("market_data", {})
    price_row = ""
    if market_data and not market_data.get("error") and ticker:
        price = market_data.get("price")
        pe = market_data.get("pe")
        rsi = market_data.get("rsi")
        change_1m = market_data.get("change_1m")
        
        # 代號
        ticker_cell = f"{name}({ticker})"
        
        # 現價
        price_cell = f"${price:,.2f}" if price else "—"
        
        # P/E
        pe_cell = str(int(pe)) if pe else "—"
        
        # RSI
        rsi_cell = f"{rsi:.1f}" if rsi else "—"
        
        # 1M%
        if change_1m is not None:
            sign = "+" if change_1m > 0 else ""
            change_cell = f"{sign}{change_1m:.1f}%"
        else:
            change_cell = "—"
        
                # 評級（根據RSI和1M%，5種評級）
        rating = "—"
        if rsi and change_1m is not None:
            # 超賣區（RSI < 30 且跌幅大）
            if rsi < 30 and change_1m < -5:
                rating = "⭐超賣"
            # 強勢股（漲幅 > 30%）
            elif change_1m > 30:
                rating = "🚀爆發"
            # 熱門股（RSI > 70 且漲幅 > 10%）
            elif rsi > 70 and change_1m > 10:
                rating = "🔥熱門"
            # 穩健股（RSI 在 40-60 之間且小幅上漲）
            elif 40 <= rsi <= 60 and 0 < change_1m <= 10:
                rating = "✅穩健"
            # 弱勢股（跌幅 > 10% 但 RSI 未超賣）
            elif change_1m < -10 and rsi >= 30:
                rating = "⚠️弱勢"
        
        price_row = f"""
        <div style="margin:10px 0;">
          <table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;">
            <tr>
              <td style="padding:6px 8px 6px 14px;font-size:11px;color:#9ca3af;width:34%;">代號</td>
              <td style="padding:6px 8px;font-size:11px;color:#9ca3af;text-align:right;width:18%;">現價</td>
              <td style="padding:6px 8px;font-size:11px;color:#9ca3af;text-align:center;width:12%;">P/E</td>
              <td style="padding:6px 8px;font-size:11px;color:#9ca3af;text-align:center;width:12%;">RSI</td>
              <td style="padding:6px 8px;font-size:11px;color:#9ca3af;text-align:center;width:12%;">1M%</td>
              <td style="padding:6px 14px 6px 8px;font-size:11px;color:#9ca3af;text-align:center;width:12%;">評級</td>
            </tr>
            <tr style="background:#f9fafb;">
              <td style="padding:10px 8px 10px 14px;font-size:13px;font-weight:600;color:#374151;border-radius:6px 0 0 6px;">{ticker_cell}</td>
              <td style="padding:10px 8px;font-size:13px;font-weight:600;color:#111827;text-align:right;">{price_cell}</td>
              <td style="padding:10px 8px;font-size:13px;color:#6b7280;text-align:center;">{pe_cell}</td>
              <td style="padding:10px 8px;font-size:13px;color:#6b7280;text-align:center;">{rsi_cell}</td>
              <td style="padding:10px 8px;font-size:13px;color:#6b7280;text-align:center;">{change_cell}</td>
              <td style="padding:10px 14px 10px 8px;font-size:13px;color:#6b7280;text-align:center;border-radius:0 6px 6px 0;">{rating}</td>
            </tr>
          </table>
        </div>
        """

    return f"""
    <div style="border:1px solid #e5e7eb;border-left:4px solid {s_cfg['border']};border-radius:0 10px 10px 0;
                padding:18px 20px;margin-bottom:14px;background:#fff;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
        <div>
          <div style="display:inline-flex;align-items:center;gap:8px;margin-bottom:4px;">
            {_stance_dot(stance)}
            <span style="font-size:16px;font-weight:700;color:#111827;">{name}</span>
            <span style="display:inline-block;padding:2px 6px;background:{s_cfg['bg']};color:{s_cfg['dot']};border-radius:3px;font-size:11px;font-weight:600;">{stance}</span>
            {"<span style='font-size:11px;color:#9ca3af;'>來源 " + src + "</span>" if src else ""}
          </div>
        </div>
        <div>{label}</div>
      </div>
      {price_row}
            <div style="font-size:14px;color:#374151;line-height:1.7;margin-top:12px;">{stock.get('description','')}</div>
      
      <!-- 動態 insights 欄位 -->
      {"".join([
        f"<div style='margin-top:{6 if i == 0 else 4}px;font-size:13px;'>" +
        f"<span style='color:#2563eb;font-weight:600;'>{insight.get('label','')}：</span>" +
        f"<span style='color:#374151;'>{insight.get('content','')}</span>" +
        "</div>"
        for i, insight in enumerate(stock.get('insights', []))
      ]) if stock.get('insights') else ""}
    </div>
    """




def _render_sector_card(sector: dict) -> str:
    """
    Render a sector analysis card with multiple related stocks table
    """
    stance = sector.get("stance", "觀望")
    s_cfg = STANCE_CONFIG.get(stance, STANCE_CONFIG["觀望"])
    src = sector.get("source_time", "")
    sector_name = sector.get("sector_name", "")
    related_stocks = sector.get("related_stocks", [])
    
    # 建立族群股票表格
    stock_table = ""
    if related_stocks:
        # 獲取股價資料
        stock_rows = ""
        for stock in related_stocks:
            ticker = stock.get("ticker", "")
            name = stock.get("name", "")
            exchange = stock.get("exchange", "台股")
            
            # 如果有 market_data，顯示完整資訊
            market_data = stock.get("market_data", {})
            if market_data and not market_data.get("error"):
                price = market_data.get("price")
                pe = market_data.get("pe")
                rsi = market_data.get("rsi")
                change_1m = market_data.get("change_1m")
                
                ticker_cell = f"{name}({ticker})"
                price_cell = f"${price:,.2f}" if price else "—"
                pe_cell = f"{pe:.1f}" if pe else "—"
                rsi_cell = f"{rsi:.1f}" if rsi else "—"
                change_cell = f"+{change_1m:.1f}%" if change_1m and change_1m > 0 else f"{change_1m:.1f}%" if change_1m else "—"
                
                # 評級（5種評級）
                rating = "—"
                if rsi and change_1m is not None:
                    if rsi < 30 and change_1m < -5:
                        rating = "⭐超賣"
                    elif change_1m > 30:
                        rating = "🚀爆發"
                    elif rsi > 70 and change_1m > 10:
                        rating = "🔥熱門"
                    elif 40 <= rsi <= 60 and 0 < change_1m <= 10:
                        rating = "✅穩健"
                    elif change_1m < -10 and rsi >= 30:
                        rating = "⚠️弱勢"
                
                stock_rows += f"""
          <tr style="background:#f9fafb;">
            <td style="padding:10px 8px 10px 14px;font-size:13px;font-weight:600;color:#374151;border-radius:6px 0 0 6px;">{ticker_cell}</td>
            <td style="padding:10px 8px;font-size:13px;font-weight:600;color:#111827;text-align:right;">{price_cell}</td>
            <td style="padding:10px 8px;font-size:13px;color:#6b7280;text-align:center;">{pe_cell}</td>
            <td style="padding:10px 8px;font-size:13px;color:#6b7280;text-align:center;">{rsi_cell}</td>
            <td style="padding:10px 8px;font-size:13px;color:#6b7280;text-align:center;">{change_cell}</td>
            <td style="padding:10px 14px 10px 8px;font-size:13px;color:#6b7280;text-align:center;border-radius:0 6px 6px 0;">{rating}</td>
          </tr>
          <tr><td colspan="6" style="padding:4px 0;"></td></tr>"""
            else:
                # 沒有股價資料，只顯示名稱和代碼
                stock_rows += f"""
          <div style="padding:8px 14px;background:#f9fafb;border-radius:6px;font-size:13px;color:#6b7280;margin-bottom:8px;">
            <span style="font-weight:600;color:#374151;">{name}({ticker})</span>
          </div>"""
        
        stock_table = f"""
        <div style="margin:10px 0;">
          <table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;">
            <tr>
              <td style="padding:6px 8px 6px 14px;font-size:11px;color:#9ca3af;width:34%;">相關個股</td>
              <td style="padding:6px 8px;font-size:11px;color:#9ca3af;text-align:right;width:18%;">現價</td>
              <td style="padding:6px 8px;font-size:11px;color:#9ca3af;text-align:center;width:12%;">P/E</td>
              <td style="padding:6px 8px;font-size:11px;color:#9ca3af;text-align:center;width:12%;">RSI</td>
              <td style="padding:6px 8px;font-size:11px;color:#9ca3af;text-align:center;width:12%;">1M%</td>
              <td style="padding:6px 14px 6px 8px;font-size:11px;color:#9ca3af;text-align:center;width:12%;">評級</td>
            </tr>
            {stock_rows}
          </table>
        </div>
        """
    
    return f"""
    <div style="border:1px solid #e5e7eb;border-left:4px solid {s_cfg['border']};border-radius:0 10px 10px 0;
                padding:18px 20px;margin-bottom:14px;background:#fff;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
        <div>
          <div style="display:inline-flex;align-items:center;gap:8px;margin-bottom:4px;">
            {_stance_dot(stance)}
            <span style="font-size:16px;font-weight:700;color:#111827;">{sector_name}</span>
            <span style="display:inline-block;padding:2px 6px;background:{s_cfg['bg']};color:{s_cfg['dot']};border-radius:3px;font-size:11px;font-weight:600;">{stance}</span>
            {"<span style='font-size:11px;color:#9ca3af;'>來源 " + src + "</span>" if src else ""}
          </div>
        </div>
        <div><span style='font-size:12px;color:#9ca3af;'>🏭 族群分析</span></div>
      </div>
            {stock_table}
      <div style="font-size:14px;color:#374151;line-height:1.7;margin-top:12px;">{sector.get('description','')}</div>
      
      <!-- 動態 insights 欄位 -->
      {"".join([
        f"<div style='margin-top:{10 if i == 0 else 6}px;font-size:13px;'>" +
        f"<span style='color:#2563eb;font-weight:600;'>{insight.get('label','')}：</span>" +
        f"<span style='color:#374151;'>{insight.get('content','')}</span>" +
        "</div>"
        for i, insight in enumerate(sector.get('insights', []))
      ]) if sector.get('insights') else ""}
    </div>
    """


def render_email_html(digest: dict) -> str:
    ep = digest.get("ep_number", "")
    date = digest.get("date", "")
    intro = digest.get("intro", "")
    market = digest.get("market_outlook", {})
    news_list = digest.get("news", [])
    stocks = digest.get("stocks", [])
    sector_analysis = digest.get("sector_analysis", [])
    qa_list = digest.get("qa", [])

    market_stance = market.get("stance", "中性")
    market_cfg = STANCE_CONFIG.get(market_stance, STANCE_CONFIG["中性"])

        # ── 新聞區塊 ─────────────────────────────────────────────────
    news_html = ""
    for item in news_list:
        cat = item.get("category", "其他")
        cat_cfg = CATEGORY_CONFIG.get(cat, CATEGORY_CONFIG["其他"])
        src = item.get("source_time", "")
        news_html += f"""
        <div style="border:1px solid #e5e7eb;border-radius:10px;padding:20px;margin-bottom:14px;background:#fff;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
            <h3 style="font-size:16px;font-weight:700;color:#111827;margin:0;flex:1;">{item.get('title','')}</h3>
            <span style="display:inline-block;padding:4px 10px;background:{cat_cfg['bg']};color:{cat_cfg['color']};border-radius:4px;font-size:12px;font-weight:600;margin-left:12px;white-space:nowrap;">★ {cat}</span>
          </div>
          {"<div style='font-size:12px;color:#9ca3af;margin-bottom:12px;'>來源：" + src + "</div>" if src else ""}
          <div style="margin-bottom:10px;">
            <span style="color:#2563eb;font-weight:600;font-size:14px;">事件：</span>
            <span style="color:#374151;font-size:14px;line-height:1.6;">{item.get('event','')}</span>
          </div>
          <div>
            <span style="color:#16a34a;font-weight:600;font-size:14px;">觀點：</span>
            <span style="color:#374151;font-size:14px;line-height:1.6;">{item.get('perspective','')}</span>
          </div>
        </div>
        """

        # ── 個股區塊 ─────────────────────────────────────────────────
    stocks_html = ""
    for stock in stocks:
        stocks_html += _render_stock_card(stock)


        # ── 族群分析區塊 ──────────────────────────────────────────────
    sectors_html = ""
    for sector in sector_analysis:
        sectors_html += _render_sector_card(sector)

        # ── Q&A 區塊 ─────────────────────────────────────────────────
    qa_html = ""
    for i, qa in enumerate(qa_list):
        points_html = ""
        for pt in qa.get("points", []):
            points_html += f"""
            <div style="margin-bottom:10px;">
              <span style="color:#7c3aed;font-weight:600;font-size:14px;">{pt.get('label','')}：</span>
              <span style="color:#374151;font-size:14px;line-height:1.6;">{pt.get('content','')}</span>
            </div>
            """
        quote = qa.get("quote", "")
        quote_html = ""
        if quote:
            quote_html = f"""
            <div style="margin-top:14px;padding:14px 18px;background:#fefce8;border-left:3px solid #eab308;border-radius:0 8px 8px 0;">
              <span style="font-size:18px;margin-right:8px;">💡</span>
              <span style="font-size:13px;color:#854d0e;font-style:italic;line-height:1.6;">{quote}</span>
            </div>
            """
        src = qa.get("source_time", "")
        src_badge = f"<span style='font-size:11px;color:#9ca3af;background:#f3f4f6;padding:3px 8px;border-radius:12px;'>⏱️ {src}分</span>" if src else ""
        qa_html += f"""
        <div style="border:1px solid #e5e7eb;border-radius:10px;padding:20px;margin-bottom:16px;background:#fff;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <h3 style="font-size:16px;font-weight:700;color:#111827;margin:0;flex:1;">{qa.get('title','')}</h3>
            {src_badge}
          </div>
          <div style="background:#f3e8ff;border-left:3px solid #a855f7;padding:12px 16px;border-radius:0 6px 6px 0;margin-bottom:14px;">
            <span style="font-weight:600;color:#7c3aed;font-size:14px;">Q：</span>
            <span style="color:#374151;font-size:14px;line-height:1.6;">{qa.get('question','')}</span>
          </div>
          {points_html}
          {quote_html}
        </div>
        """

    # ── 完整 HTML ─────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>股癌 {ep} 投資筆記</title>
</head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang TC','Noto Sans TC',sans-serif;">

<div style="max-width:680px;margin:0 auto;padding:20px 12px;">

  <!-- Header -->
  <div style="text-align:center;padding:28px 20px 20px;">
    <div style="font-size:13px;color:#9ca3af;margin-bottom:6px;">🎙️ 股癮 Podcast · {date}</div>
    <div style="font-size:28px;font-weight:800;color:#111827;letter-spacing:-0.5px;">{ep}</div>
    <div style="display:inline-block;margin-top:8px;padding:4px 14px;background:#111827;color:#fff;border-radius:20px;font-size:12px;">AI 投資筆記</div>
  </div>

  <!-- 大盤觀點 -->
  <div style="background:{market_cfg['bg']};border:2px solid {market_cfg['border']};border-radius:12px;padding:16px 20px;margin-bottom:20px;">
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
      <span style="font-size:16px;">🎙️</span>
      <span style="font-size:16px;font-weight:700;color:{market_cfg['dot']};">大盤觀點 — {_stance_dot(market_stance)} {market_stance}</span>
    </div>
    <div style="font-size:14px;color:#374151;line-height:1.7;">{market.get('description','')}</div>
  </div>

  <!-- 本集導讀 -->
  <div style="background:#fff;border-radius:12px;padding:18px 20px;margin-bottom:20px;border:1px solid #e5e7eb;">
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
      <span style="font-size:18px;">📝</span>
      <span style="font-size:16px;font-weight:700;color:#111827;">本集導讀</span>
    </div>
    <div style="font-size:14px;color:#374151;line-height:1.8;">{intro}</div>
  </div>

  <!-- 今日新聞整理 -->
  <div style="margin-bottom:20px;">
    <div style="font-size:18px;font-weight:800;color:#111827;margin-bottom:14px;padding-bottom:8px;border-bottom:2px solid #e5e7eb;">
      今日新聞整理
    </div>
    {news_html}
  </div>

  <!-- 主題/標的觀點 -->
  <div style="margin-bottom:20px;">
    <div style="font-size:18px;font-weight:800;color:#111827;margin-bottom:14px;padding-bottom:8px;border-bottom:2px solid #e5e7eb;">
      主題／標的觀點
    </div>
    {stocks_html}
    {sectors_html}
  </div>

  <!-- Q&A -->
  {"<div style='margin-bottom:20px;'><div style='font-size:18px;font-weight:800;color:#111827;margin-bottom:14px;padding-bottom:8px;border-bottom:2px solid #e5e7eb;'>Q&amp;A 投資心法</div>" + qa_html + "</div>" if qa_html else ""}

  <!-- Footer -->
  <div style="text-align:center;padding:20px;font-size:12px;color:#9ca3af;">
    投資組合終端・僅供參考不構成投資建議<br>
    <span style="color:#d1d5db;">由 AI 自動生成 · {ep} · {date}</span>
  </div>

</div>
</body>
</html>"""

    return html
