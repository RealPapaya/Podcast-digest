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
    Render a single stock card with market data
    """
    stance = stock.get("stance", "觀望")
    risk = stock.get("risk", "中")
    s_cfg = STANCE_CONFIG.get(stance, STANCE_CONFIG["觀望"])
    r_cfg = RISK_CONFIG.get(risk, RISK_CONFIG["中"])
    src = stock.get("source_time", "")

    ticker = stock.get("ticker", "")
    exchange = stock.get("exchange", "")
    sector = stock.get("sector", "")
    
    # 美股與產業概述使用不同顏色
    if exchange == "美股":
        label_style = "background:#ede9fe;color:#7c3aed;padding:3px 8px;border-radius:4px;font-size:12px;font-weight:600;"
        label = f"<span style='{label_style}'>🇺🇸 美股 {sector}</span>" if sector else f"<span style='{label_style}'>🇺🇸 美股</span>"
    elif not ticker and sector:  # 產業概述（沒有ticker）
        label_style = "background:#fef3c7;color:#92400e;padding:3px 8px;border-radius:4px;font-size:12px;font-weight:600;"
        label = f"<span style='{label_style}'>🏭 {sector}產業</span>"
    else:
        label_style = "font-size:13px;color:#6b7280;"
        label = f"<span style='{label_style}'>{exchange} {sector}</span>" if sector else f"<span style='{label_style}'>{exchange}</span>"
    
        # 股價數據（用於底部代號區）
    market_data = stock.get("market_data", {})
    market_info_parts = []
    if market_data and not market_data.get("error"):
        price = market_data.get("price")
        pe = market_data.get("pe")
        rsi = market_data.get("rsi")
        change_1m = market_data.get("change_1m")
        
        if price:
            market_info_parts.append(f"${price:,.2f}")
        if pe:
            market_info_parts.append(f"P/E {pe}")
        if rsi:
            market_info_parts.append(f"RSI {rsi}")
        if change_1m is not None:
            sign = "+" if change_1m > 0 else ""
            market_info_parts.append(f"1M {sign}{change_1m}%")

    return f"""
    <div style="border:1px solid #e5e7eb;border-left:4px solid {s_cfg['border']};border-radius:0 10px 10px 0;
                padding:18px 20px;margin-bottom:14px;background:{s_cfg['bg']};">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <div style="font-size:18px;font-weight:700;color:#111827;">{stock.get('name','')}</div>
        <div>{label}</div>
      </div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
        {_stance_dot(stance)}
        <span style="font-weight:600;color:{s_cfg['dot']};font-size:14px;">{stance}</span>
        {_badge('風險：' + risk, r_cfg['color'], r_cfg['bg'])}
        {"<span style='font-size:12px;color:#9ca3af;'>來源：" + src + "</span>" if src else ""}
      </div>
      <div style="font-size:14px;color:#374151;line-height:1.7;margin-bottom:10px;">{stock.get('description','')}</div>
      {"<div style='font-size:13px;margin-top:6px;'><span style='color:#2563eb;font-weight:600;'>催化劑：</span><span style='color:#374151;'>" + stock.get('catalyst','') + "</span></div>" if stock.get('catalyst') else ""}
      {"<div style='font-size:13px;margin-top:4px;'><span style='color:#dc2626;font-weight:600;'>風險點：</span><span style='color:#374151;'>" + stock.get('key_risk','') + "</span></div>" if stock.get('key_risk') else ""}
      {"<div style='display:flex;gap:24px;margin-top:12px;padding-top:12px;border-top:1px solid #e5e7eb;'><span style='font-size:13px;color:#6b7280;'>代號：<strong>" + (exchange + " " + ticker if ticker else "—") + "</strong></span>" + ("<span style='font-size:13px;color:#6b7280;'>" + " · ".join(market_info_parts) + "</span>" if market_info_parts else "") + "</div>" if ticker or market_info_parts else ""}
    </div>
    """


def render_email_html(digest: dict) -> str:
    ep = digest.get("ep_number", "")
    date = digest.get("date", "")
    intro = digest.get("intro", "")
    market = digest.get("market_outlook", {})
    news_list = digest.get("news", [])
    stocks = digest.get("stocks", [])
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
        <div style="border:1px solid #e5e7eb;border-radius:10px;padding:18px 20px;margin-bottom:14px;background:#fff;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
            <div style="font-size:16px;font-weight:700;color:#111827;flex:1;">{item.get('title','')}</div>
            <div style="display:flex;gap:8px;align-items:center;flex-shrink:0;margin-left:12px;">
              {_badge('★ ' + cat, cat_cfg['color'], cat_cfg['bg'])}
            </div>
          </div>
          {"<div style='font-size:12px;color:#9ca3af;margin-bottom:8px;'>來源：" + src + "</div>" if src else ""}
          <div style="margin-bottom:8px;">
            <span style="color:#2563eb;font-weight:600;font-size:13px;">事件：</span>
            <span style="color:#374151;font-size:14px;">{item.get('event','')}</span>
          </div>
          <div>
            <span style="color:#16a34a;font-weight:600;font-size:13px;">觀點：</span>
            <span style="color:#374151;font-size:14px;">{item.get('perspective','')}</span>
          </div>
        </div>
        """

    # ── 個股區塊 ─────────────────────────────────────────────────
        stocks_html = ""
    for stock in stocks:
        stocks_html += _render_stock_card(stock)

    # ── Q&A 區塊 ─────────────────────────────────────────────────
    qa_html = ""
    for i, qa in enumerate(qa_list):
        points_html = ""
        for pt in qa.get("points", []):
            points_html += f"""
            <div style="margin-bottom:8px;">
              <span style="color:#7c3aed;font-weight:600;font-size:13px;">{pt.get('label','')}：</span>
              <span style="color:#374151;font-size:14px;">{pt.get('content','')}</span>
            </div>
            """
        quote = qa.get("quote", "")
        quote_html = ""
        if quote:
            quote_html = f"""
            <div style="margin-top:14px;padding:12px 16px;background:#fefce8;border-radius:8px;">
              <span style="font-size:18px;margin-right:8px;">💡</span>
              <span style="font-size:13px;color:#92400e;font-style:italic;">{quote}</span>
                        </div>
            """
        src = qa.get("source_time", "")
        src_badge = f"<span style='font-size:11px;color:#9ca3af;background:#f3f4f6;padding:3px 8px;border-radius:12px;'>⏱️ {src}分</span>" if src else ""
        qa_html += f"""
        <div style="border:1px solid #e5e7eb;border-radius:10px;padding:18px 20px;margin-bottom:14px;background:#fff;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <div style="font-size:15px;font-weight:700;color:#111827;flex:1;">{qa.get('title','')}</div>
            {src_badge}
          </div>
          <div style="background:#f0f0ff;border-left:3px solid #6366f1;padding:10px 14px;border-radius:0 6px 6px 0;margin-bottom:14px;">
            <span style="font-weight:600;color:#4f46e5;">Q：</span>
            <span style="color:#374151;font-size:14px;">{qa.get('question','')}</span>
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
