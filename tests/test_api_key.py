#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試 API 金鑰是否有效
"""

import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

def test_google_api():
    """測試 Google Gemini API"""
    log.info("=" * 50)
    log.info("🔍 測試 Google Gemini API...")
    log.info("=" * 50)

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        log.error("❌ 找不到 GOOGLE_API_KEY 環境變數")
        return False

    if api_key.startswith("your_"):
        log.error("❌ GOOGLE_API_KEY 仍是佔位符，請設定實際的 API 金鑰")
        return False

    log.info(f"✅ 找到 API Key: {api_key[:20]}...")

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        # 簡單的測試請求
        log.info("📡 發送測試請求到 Gemini...")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="簡單測試：回答 '成功' 就好"
        )

        log.info(f"✅ Gemini API 測試成功！回應：{response.text[:50]}")
        return True

    except Exception as e:
        log.error(f"❌ Gemini API 錯誤：{e}")
        return False


def test_gmail():
    """測試 Gmail 設定"""
    log.info("\n" + "=" * 50)
    log.info("🔍 測試 Gmail 設定...")
    log.info("=" * 50)

    gmail_user = os.environ.get("GMAIL_USER")
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD")

    if not gmail_user:
        log.warning("⚠️  GMAIL_USER 未設定（可選）")
        return None

    if not gmail_pass:
        log.warning("⚠️  GMAIL_APP_PASSWORD 未設定（可選）")
        return None

    if gmail_pass.startswith("your_"):
        log.warning("⚠️  GMAIL_APP_PASSWORD 仍是佔位符")
        return None

    log.info(f"✅ Gmail 帳號已設定：{gmail_user}")
    log.info(f"✅ Gmail 應用程式密碼已設定（前 4 字：{gmail_pass[:4]}...）")
    return True


def test_line():
    """測試 LINE 設定"""
    log.info("\n" + "=" * 50)
    log.info("🔍 測試 LINE 設定...")
    log.info("=" * 50)

    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")

    if not token:
        log.warning("⚠️  LINE_CHANNEL_ACCESS_TOKEN 未設定（可選）")
        return None

    if not user_id:
        log.warning("⚠️  LINE_USER_ID 未設定（可選）")
        return None

    if token.startswith("your_"):
        log.warning("⚠️  LINE_CHANNEL_ACCESS_TOKEN 仍是佔位符")
        return None

    if user_id.startswith("your_"):
        log.warning("⚠️  LINE_USER_ID 仍是佔位符")
        return None

    log.info(f"✅ LINE Token 已設定（前 10 字：{token[:10]}...）")
    log.info(f"✅ LINE User ID 已設定：{user_id}")
    return True


if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()

    results = []
    results.append(("Google Gemini API", test_google_api()))
    results.append(("Gmail", test_gmail()))
    results.append(("LINE", test_line()))

    log.info("\n" + "=" * 50)
    log.info("📋 測試結果摘要")
    log.info("=" * 50)

    for name, result in results:
        if result is True:
            log.info(f"✅ {name}: 已設定且有效")
        elif result is False:
            log.error(f"❌ {name}: 設定有誤")
        else:
            log.warning(f"⚠️  {name}: 未設定（可選）")

    # 如果 Google API 測試失敗，終止
    if results[0][1] is False:
        log.error("\n❌ Google Gemini API 設定有誤，無法繼續")
        sys.exit(1)

    log.info("\n✅ 基本測試完成！可以開始使用了")
