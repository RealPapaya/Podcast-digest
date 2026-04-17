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


def _build_line_flex(digest: dict) -> dict:
    """
    建立 LINE Flex Message（仿照截圖卡片設計）
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

        # 個股清單（最多 15 檔）
    stock_rows = []
    for s in stocks[:15]:
        s_stance = s.get("stance", "觀望")
        s_color = {"看多": "#22c55e", "看空": "#ef4444", "觀望": "#f59e0b"}.get(s_stance, "#6b7280")
        stock_rows.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": f"{s.get('name','')} ({s.get('ticker','')}) ",
                    "size": "sm",
                    "color": "#111827",
                    "flex": 3,
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
            "paddingTop": "4px",
        })

            # 新聞標題（最多 8 條）
    news_items = []
    for n in news[:8]:
        news_items.append({
            "type": "text",
            "text": f"• {n.get('title','')}",
            "size": "sm",
            "color": "#374151",
            "wrap": True,
            "margin": "sm",
        })

    # Q&A 區塊（最多 5 個）
    qa_items = []
    for qa in qa_list[:5]:
        qa_title = qa.get("title", "")
        qa_question = qa.get("question", "")
        # 只顯示第一個 point 的內容（節省空間）
        points = qa.get("points", [])
        first_point = points[0].get("content", "")[:60] + "..." if points else ""
        
        qa_items.append({
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#f0f0ff",
            "cornerRadius": "8px",
            "paddingAll": "10px",
            "margin": "sm",
            "contents": [
                {
                    "type": "text",
                    "text": f"💡 {qa_title}",
                    "size": "sm",
                    "weight": "bold",
                    "color": "#4f46e5",
                    "wrap": True,
                },
                {
                    "type": "text",
                    "text": f"Q: {qa_question}",
                    "size": "xs",
                    "color": "#6b7280",
                    "wrap": True,
                    "margin": "sm",
                },
                {
                    "type": "text",
                    "text": first_point,
                    "size": "xs",
                    "color": "#374151",
                    "wrap": True,
                    "margin": "xs",
                } if first_point else {"type": "filler"},
            ],
        })

    flex_message = {
        "type": "flex",
        "altText": f"股癌 {ep} 投資筆記 {stance_emoji} {date}",
        "contents": {
            "type": "bubble",
            "size": "giga",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#111827",
                "paddingAll": "20px",
                "contents": [
                    {
                        "type": "text",
                        "text": f"🎙️ 股癌 {ep}",
                        "color": "#ffffff",
                        "size": "xl",
                        "weight": "bold",
                    },
                    {
                        "type": "text",
                        "text": f"AI 投資筆記 · {date}",
                        "color": "#9ca3af",
                        "size": "sm",
                        "margin": "sm",
                    },
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
                        "paddingAll": "12px",
                        "margin": "none",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"大盤觀點 {stance_emoji} {stance}",
                                "size": "md",
                                "weight": "bold",
                                "color": stance_color,
                            },
                            {
                                "type": "text",
                                "text": (market.get("description") or "—")[:80],
                                "size": "sm",
                                "color": "#374151",
                                "wrap": True,
                                "margin": "sm",
                            },
                        ],
                    },
                    # 分隔線
                    {"type": "separator", "margin": "lg", "color": "#e5e7eb"},
                    # 個股觀點
                    {
                        "type": "text",
                        "text": "📊 個股觀點",
                        "size": "md",
                        "weight": "bold",
                        "color": "#111827",
                        "margin": "lg",
                    },
                    *stock_rows,
                    # 分隔線
                    {"type": "separator", "margin": "lg", "color": "#e5e7eb"},
                    # 今日新聞
                    {
                        "type": "text",
                        "text": "📰 今日新聞",
                        "size": "md",
                        "weight": "bold",
                        "color": "#111827",
                        "margin": "lg",
                    },
                                        *news_items,
                    # Q&A 區塊
                    *([{"type": "separator", "margin": "lg", "color": "#e5e7eb"},
                       {"type": "text", "text": "💡 Q&A 投資心法", "size": "md", "weight": "bold", "color": "#111827", "margin": "lg"}] + qa_items if qa_items else []),
                    # 底部說明
                    {
                        "type": "text",
                        "text": "投資組合終端・僅供參考不構成投資建議",
                        "size": "xxs",
                        "color": "#9ca3af",
                        "margin": "xl",
                        "align": "center",
                    },
                ],
            },
        },
    }
    return flex_message


def send_line_message(digest: dict) -> bool:
    """
    透過 LINE Messaging API 推播 Flex Message
    需要環境變數：LINE_CHANNEL_ACCESS_TOKEN, LINE_USER_ID
    """
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")

    if not token or not user_id:
        log.warning("未設定 LINE 環境變數，略過 LINE 發送")
        return False

    flex_msg = _build_line_flex(digest)

    payload = {
        "to": user_id,
        "messages": [flex_msg],
    }

    try:
        log.info(f"📡 準備發送 LINE 訊息至 {user_id[:10]}...")
        resp = requests.post(
            LINE_API_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )

        if resp.status_code == 200:
            log.info("✅ LINE 訊息發送成功")
            return True
        elif resp.status_code == 401:
            log.error(f"LINE API 認證失敗：Token 可能無效或過期")
            log.error(f"請檢查 LINE_CHANNEL_ACCESS_TOKEN 是否正確")
            return False
        elif resp.status_code == 400:
            log.error(f"LINE API 請求錯誤：{resp.text}")
            log.error(f"可能是 User ID 或 Flex Message 格式有誤")
            return False
        else:
            log.error(f"LINE API 錯誤 {resp.status_code}：{resp.text}")
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
