# -*- coding: utf-8 -*-
"""
notify.py
發送 Gmail 和 LINE Bot 推播通知
"""

import os
import json
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional

import requests

log = logging.getLogger(__name__)


# ╔══════════════════════════════════════════════╗
# ║                  GMAIL                       ║
# ╚══════════════════════════════════════════════╝

def send_gmail(html_content: str, digest: dict) -> bool:
    """
    使用 Gmail SMTP 發送 HTML Email
    需要環境變數：GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL
    """
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("RECIPIENT_EMAIL", gmail_user)

    if not gmail_user or not gmail_pass:
        log.warning("未設定 Gmail 環境變數，略過 Email 發送")
        return False

    ep = digest.get("ep_number", "EP???")
    date = digest.get("date", "")
    market = digest.get("market_outlook", {})
    stance_emoji = {"看多": "🟢", "看空": "🔴", "觀望": "🟡", "中性": "⚪"}.get(
        market.get("stance", "中性"), "⚪"
    )

    subject = f"股癌 {ep} 投資筆記 {stance_emoji} {date}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"股癌 AI 筆記 <{gmail_user}>"
    msg["To"] = recipient

    # 純文字備用版本
    plain_text = f"""股癌 {ep} 投資筆記
日期：{date}
大盤觀點：{market.get('stance','')} — {market.get('description','')}

完整筆記請查看 HTML 版本。

投資組合終端・僅供參考不構成投資建議"""

    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    # 附加 HTML 檔案
    html_filename = f"stock_digest_{ep}.html"
    html_attachment = MIMEBase("text", "html")
    html_attachment.set_payload(html_content.encode("utf-8"))
    encoders.encode_base64(html_attachment)
    html_attachment.add_header(
        "Content-Disposition",
        f"attachment; filename={html_filename}"
    )
    msg.attach(html_attachment)
    log.info(f"📎 附加 HTML 檔案: {html_filename}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, recipient, msg.as_string())
        log.info(f"✅ Email 已發送至 {recipient}")
        return True
    except smtplib.SMTPAuthenticationError:
        log.error("Gmail 登入失敗！請確認是否已開啟「應用程式密碼」")
        return False
    except Exception as e:
        log.error(f"Email 發送失敗：{e}")
        return False


# ╔══════════════════════════════════════════════╗
# ║              LINE Messaging API              ║
# ╚══════════════════════════════════════════════╝

LINE_API_URL = "https://api.line.me/v2/bot/message/push"


def _build_line_summary_card(digest: dict) -> dict:
    """
    建立 LINE 摘要卡片（訊息1：精華摘要）
    包含：大盤觀點、導讀摘要、重點統計
    """
    ep = digest.get("ep_number", "EP???")
    date = digest.get("date", "")
    intro = digest.get("intro", "")[:280] + "..." if len(digest.get("intro", "")) > 280 else digest.get("intro", "")
    market = digest.get("market_outlook", {})
    stance = market.get("stance", "中性")
    stocks = digest.get("stocks", [])
    news = digest.get("news", [])
    sector_analysis = digest.get("sector_analysis", [])
    
    stance_color = {"看多": "#22c55e", "看空": "#ef4444", "觀望": "#f59e0b", "中性": "#6b7280"}.get(stance, "#6b7280")
    stance_emoji = {"看多": "🟢", "看空": "🔴", "觀望": "🟡", "中性": "⚪"}.get(stance, "⚪")
    
    # 統計看多/看空股票
    bullish = sum(1 for s in stocks if s.get("stance") == "看多")
    bearish = sum(1 for s in stocks if s.get("stance") == "看空")
    neutral = len(stocks) - bullish - bearish
    
    return {
        "type": "flex",
        "altText": f"股癌 {ep} 投資筆記 {stance_emoji}",
        "contents": {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#111827",
                "paddingAll": "20px",
                "contents": [
                    {"type": "text", "text": f"🎙️ 股癌 {ep}", "color": "#ffffff", "size": "xl", "weight": "bold"},
                    {"type": "text", "text": f"AI 投資筆記 · {date}", "color": "#9ca3af", "size": "sm", "margin": "sm"},
                ],
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "contents": [
                    # 大盤觀點
                    {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": "#f9fafb",
                        "cornerRadius": "8px",
                        "paddingAll": "14px",
                        "contents": [
                            {"type": "text", "text": f"大盤觀點 {stance_emoji} {stance}", "size": "md", "weight": "bold", "color": stance_color},
                            {"type": "text", "text": market.get("description", "")[:100], "size": "sm", "color": "#374151", "wrap": True, "margin": "sm"},
                        ],
                    },
                    {"type": "separator", "margin": "lg", "color": "#e5e7eb"},
                    # 本集導讀
                    {"type": "text", "text": "📝 本集導讀", "size": "md", "weight": "bold", "color": "#111827", "margin": "lg"},
                    {"type": "text", "text": intro, "size": "sm", "color": "#374151", "wrap": True, "margin": "sm"},
                    {"type": "separator", "margin": "lg", "color": "#e5e7eb"},
                    # 統計摘要
                    {"type": "text", "text": "📊 本集重點", "size": "md", "weight": "bold", "color": "#111827", "margin": "lg"},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "spacing": "sm",
                        "contents": [
                            {"type": "text", "text": f"🟢 看多 {bullish}檔", "size": "sm", "color": "#22c55e", "flex": 1},
                            {"type": "text", "text": f"🔴 看空 {bearish}檔", "size": "sm", "color": "#ef4444", "flex": 1},
                            {"type": "text", "text": f"📰 新聞 {len(news)}則", "size": "sm", "color": "#6b7280", "flex": 1},
                        ],
                    },
                    {"type": "text", "text": f"🏭 族群分析 {len(sector_analysis)}個" if sector_analysis else "", "size": "sm", "color": "#6b7280", "margin": "sm"} if sector_analysis else {"type": "filler"},
                    {"type": "text", "text": "詳細內容請看下一則訊息 👇", "size": "xs", "color": "#9ca3af", "margin": "xl", "align": "center"},
                ],
            },
        },
    }


def _build_line_stocks_card(digest: dict) -> dict:
    """
    建立 LINE 個股卡片（訊息2：個股列表）
    包含：前8檔個股 + 新聞標題
    """
    ep = digest.get("ep_number", "EP???")
    date = digest.get("date", "")
    market = digest.get("market_outlook", {})
    stance = market.get("stance", "中性")
    stocks = digest.get("stocks", [])
    news = digest.get("news", [])
    qa_list = digest.get("qa", [])

    stance_color = {"看多": "#22c55e", "看空": "#ef4444", "觀望": "#f59e0b", "中性": "#6b7280"}.get(
        stance, "#6b7280"
    )
    stance_emoji = {"看多": "🟢", "看空": "🔴", "觀望": "🟡", "中性": "⚪"}.get(stance, "⚪")

                    # 個股清單（最多 6 檔，精簡版）
    stock_rows = []
    for s in stocks[:6]:
        s_stance = s.get("stance", "觀望")
        s_color = {"看多": "#22c55e", "看空": "#ef4444", "觀望": "#f59e0b"}.get(s_stance, "#6b7280")
        
        # 美股標示
        name = s.get('name', '')
        ticker = s.get('ticker', '')
        exchange = s.get('exchange', '')
        if exchange == "美股":
            name = f"🇺🇸 {name}"
        
        # 股價資訊（僅顯示價格和1M%）
        market_data = s.get("market_data", {})
        price_text = ""
        if market_data and not market_data.get("error"):
            price = market_data.get("price")
            change_1m = market_data.get("change_1m")
            if price:
                price_text = f"${price:,.0f}"
            if change_1m is not None:
                sign = "+" if change_1m > 0 else ""
                price_text += f" ({sign}{change_1m}%)"
        
        # 股票卡片
        stock_box = {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"{name} ({ticker})",
                            "size": "sm",
                            "color": "#111827",
                            "flex": 3,
                            "weight": "bold",
                        },
                        {
                            "type": "text",
                            "text": s_stance,
                            "size": "sm",
                            "color": s_color,
                            "flex": 1,
                            "align": "end",
                            "weight": "bold",
                        },
                    ],
                },
            ],
            "paddingTop": "4px",
        }
        
        # 如果有價格資訊，加上第二行
        if price_text:
            stock_box["contents"].append({
                "type": "text",
                "text": price_text,
                "size": "xs",
                "color": "#6b7280",
                "margin": "xs",
            })
        
        stock_rows.append(stock_box)

                # 新聞標題（最多 5 條）
    news_items = []
    for n in news[:5]:
        news_items.append({
            "type": "text",
            "text": f"• {n.get('title','')}",
            "size": "sm",
            "color": "#374151",
            "wrap": True,
            "margin": "sm",
        })

        # 返回核心資訊卡片
    return {
        "type": "flex",
        "altText": f"股癌 {ep} 個股列表",
        "contents": {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#1e3a8a",
                "paddingAll": "16px",
                "contents": [
                    {"type": "text", "text": "📊 個股列表 & 新聞", "color": "#ffffff", "size": "lg", "weight": "bold"},
                ],
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "16px",
                "contents": [
                    {"type": "text", "text": "📈 重點個股", "size": "md", "weight": "bold", "color": "#111827"},
                    *stock_rows,
                    {"type": "separator", "margin": "lg", "color": "#e5e7eb"},
                    {"type": "text", "text": "📰 今日新聞", "size": "md", "weight": "bold", "color": "#111827", "margin": "lg"},
                    *news_items,
                    {"type": "text", "text": "完整內容請查看 Email 📧", "size": "xs", "color": "#9ca3af", "margin": "xl", "align": "center"},
                ],
            },
        },
    }


def send_line_message(digest: dict) -> bool:
    """
    透過 LINE Messaging API 推播 Flex Message
    發送兩則訊息：1. 摘要卡片  2. 個股列表
    需要環境變數：LINE_CHANNEL_ACCESS_TOKEN, LINE_USER_ID
    """
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")

    if not token or not user_id:
        log.warning("未設定 LINE 環境變數，略過 LINE 發送")
        return False

    # 建立兩張卡片
    summary_card = _build_line_summary_card(digest)
    stocks_card = _build_line_stocks_card(digest)

    payload = {
        "to": user_id,
        "messages": [summary_card, stocks_card],
    }

    try:
        log.info(f"📡 準備發送 LINE 訊息（共 2 則）至 {user_id[:10]}...")
        log.debug(f"LINE Token (first 20 chars): {token[:20]}...")
        payload_size = len(json.dumps(payload, ensure_ascii=False))
        log.debug(f"Total payload size: {payload_size:,} bytes")
        log.debug(f"Message 1 (Summary): {len(json.dumps(summary_card, ensure_ascii=False)):,} bytes")
        log.debug(f"Message 2 (Stocks): {len(json.dumps(stocks_card, ensure_ascii=False)):,} bytes")
        
        resp = requests.post(
            LINE_API_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
                )
        
        log.info(f"🔍 LINE API Response Status: {resp.status_code}")

        if resp.status_code == 200:
            log.info("✅ LINE 訊息發送成功（共 2 則）")
            return True
        elif resp.status_code == 401:
            log.error(f"❌ LINE API 認證失敗：Token 可能無效或過期")
            log.error(f"Response: {resp.text}")
            log.error(f"🔧 解決方法：")
            log.error(f"  1. 前往 LINE Developers Console: https://developers.line.biz/console/")
            log.error(f"  2. 點選你的 Channel")
            log.error(f"  3. 到 'Messaging API' 頁籤")
            log.error(f"  4. 重新發行 Channel Access Token")
            log.error(f"  5. 更新 .env 中的 LINE_CHANNEL_ACCESS_TOKEN")
            return False
        elif resp.status_code == 400:
            log.error(f"❌ LINE API 請求錯誤：{resp.text}")
            log.error(f"🔍 Payload preview (first 500 chars):")
            log.error(json.dumps(payload, ensure_ascii=False, indent=2)[:500])
            log.error(f"🔧 可能原因：")
            log.error(f"  1. LINE_USER_ID 錯誤 (當前: {user_id})")
            log.error(f"  2. Flex Message 格式無效 (超過 LINE 限制)")
            log.error(f"  3. 某個字段內容過長")
            return False
        else:
            log.error(f"❌ LINE API 未知錯誤 {resp.status_code}：{resp.text}")
            return False

    except requests.exceptions.ConnectionError as e:
        log.error(f"LINE 連線錯誤：{e}")
        log.error("請檢查：")
        log.error("  1. 網路連線是否正常")
        log.error("  2. LINE_CHANNEL_ACCESS_TOKEN 是否正確")
        log.error("  3. Token 是否已過期（需重新產生）")
        return False
    except Exception as e:
        log.error(f"LINE 發送失敗：{e}")
        return False
