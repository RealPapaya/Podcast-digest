#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_env.py
環境變數檢查工具 - 診斷 .env 設定是否正確

用法：
  python check_env.py
"""

import os
from dotenv import load_dotenv

# 載入 .env
load_dotenv()

print("=" * 60)
print("🔍 環境變數檢查工具")
print("=" * 60)
print()

# 檢查 AI API Keys
print("📌 AI API Keys（至少需要一個）")
print("-" * 60)

anthropic_key = os.getenv("ANTHROPIC_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")
google_key = os.getenv("GOOGLE_API_KEY")

ai_providers = []

if anthropic_key:
    if anthropic_key.startswith("sk-ant-"):
        print("✅ ANTHROPIC_API_KEY: 已設定（格式正確）")
        ai_providers.append("Claude")
    else:
        print("⚠️  ANTHROPIC_API_KEY: 已設定但格式可能錯誤（應以 sk-ant- 開頭）")
else:
    print("⏭️  ANTHROPIC_API_KEY: 未設定")

if openai_key:
    if openai_key.startswith("sk-"):
        print("✅ OPENAI_API_KEY: 已設定（格式正確）")
        ai_providers.append("OpenAI")
    else:
        print("⚠️  OPENAI_API_KEY: 已設定但格式可能錯誤（應以 sk- 開頭）")
else:
    print("⏭️  OPENAI_API_KEY: 未設定")

if google_key:
    if len(google_key) > 30:
        print("✅ GOOGLE_API_KEY: 已設定（格式正確）")
        ai_providers.append("Gemini")
    else:
        print("⚠️  GOOGLE_API_KEY: 已設定但長度異常（可能錯誤）")
else:
    print("⏭️  GOOGLE_API_KEY: 未設定")

print()
if ai_providers:
    print(f"✅ AI 分析可用的 Provider: {', '.join(ai_providers)}")
else:
    print("❌ 錯誤：至少需要設定一個 AI API Key")
    print("   請參考 .env.example 或 MULTI_API_GUIDE.md")

print()

# 檢查 Gmail 設定
print("📌 Gmail 設定（可選）")
print("-" * 60)

gmail_user = os.getenv("GMAIL_USER")
gmail_pass = os.getenv("GMAIL_APP_PASSWORD")
recipient = os.getenv("RECIPIENT_EMAIL")

gmail_ok = True

if gmail_user:
    if "@" in gmail_user and "gmail.com" in gmail_user.lower():
        print(f"✅ GMAIL_USER: {gmail_user}")
    else:
        print(f"⚠️  GMAIL_USER: {gmail_user}（不是 Gmail 地址？）")
        gmail_ok = False
else:
    print("⏭️  GMAIL_USER: 未設定（將跳過 Email 發送）")
    gmail_ok = False

if gmail_pass:
    # 移除空格檢查長度
    clean_pass = gmail_pass.replace(" ", "")
    if len(clean_pass) == 16 and clean_pass.isalnum():
        print(f"✅ GMAIL_APP_PASSWORD: 已設定（16 字元）")
    elif gmail_pass == "abcd efgh ijkl mnop":
        print(f"❌ GMAIL_APP_PASSWORD: 仍是範例值，請替換成真實的應用程式密碼")
        print("   → 參考 GMAIL_SETUP_GUIDE.md 取得真實密碼")
        gmail_ok = False
    else:
        print(f"⚠️  GMAIL_APP_PASSWORD: 已設定但格式可能錯誤")
        print(f"   → 應為 16 字元英數字（可含空格）")
        print(f"   → 目前長度：{len(clean_pass)} 字元")
        gmail_ok = False
else:
    print("⏭️  GMAIL_APP_PASSWORD: 未設定（將跳過 Email 發送）")
    gmail_ok = False

if recipient:
    print(f"✅ RECIPIENT_EMAIL: {recipient}")
else:
    if gmail_user:
        print(f"ℹ️  RECIPIENT_EMAIL: 未設定（預設使用 GMAIL_USER）")
    else:
        print("⏭️  RECIPIENT_EMAIL: 未設定")

print()
if gmail_ok:
    print("✅ Gmail 設定完整，可以發送 Email")
else:
    print("⏭️  Gmail 設定不完整，將跳過 Email 發送")
    if not gmail_user or not gmail_pass:
        print("   → 如需啟用，請參考 GMAIL_SETUP_GUIDE.md")

print()

# 檢查 LINE 設定
print("📌 LINE Bot 設定（可選）")
print("-" * 60)

line_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_user = os.getenv("LINE_USER_ID")

line_ok = True

if line_token:
    if len(line_token) > 100:
        print(f"✅ LINE_CHANNEL_ACCESS_TOKEN: 已設定（{len(line_token)} 字元）")
    elif "eyJhbGciOiJIUzI1" in line_token:
        print(f"❌ LINE_CHANNEL_ACCESS_TOKEN: 仍是範例值，請替換成真實 Token")
        line_ok = False
    else:
        print(f"⚠️  LINE_CHANNEL_ACCESS_TOKEN: 已設定但長度異常")
        line_ok = False
else:
    print("⏭️  LINE_CHANNEL_ACCESS_TOKEN: 未設定（將跳過 LINE 發送）")
    line_ok = False

if line_user:
    if line_user.startswith("U") and len(line_user) == 33:
        print(f"✅ LINE_USER_ID: {line_user}")
    elif line_user.startswith("Uxxxxxxxx"):
        print(f"❌ LINE_USER_ID: 仍是範例值，請替換成真實 User ID")
        line_ok = False
    else:
        print(f"⚠️  LINE_USER_ID: {line_user}（格式可能錯誤，應為 U 開頭 33 字元）")
        line_ok = False
else:
    print("⏭️  LINE_USER_ID: 未設定（將跳過 LINE 發送）")
    line_ok = False

print()
if line_ok:
    print("✅ LINE 設定完整，可以發送訊息")
else:
    print("⏭️  LINE 設定不完整，將跳過 LINE 發送")

print()
print("=" * 60)
print("📋 總結")
print("=" * 60)

summary = []
if ai_providers:
    summary.append(f"✅ AI 分析: {', '.join(ai_providers)}")
else:
    summary.append("❌ AI 分析: 未設定任何 API Key")

if gmail_ok:
    summary.append(f"✅ Email 通知: {gmail_user}")
else:
    summary.append("⏭️  Email 通知: 已停用")

if line_ok:
    summary.append("✅ LINE 通知: 已啟用")
else:
    summary.append("⏭️  LINE 通知: 已停用")

for item in summary:
    print(item)

print()

# 給出建議
if not ai_providers:
    print("⚠️  警告：至少需要一個 AI API Key 才能執行分析")
    print("   → 推薦：GOOGLE_API_KEY（免費）")
    print("   → 進階：ANTHROPIC_API_KEY 或 OPENAI_API_KEY（付費但更穩定）")
    print()

if not gmail_ok and not line_ok:
    print("ℹ️  提示：目前沒有啟用任何通知方式")
    print("   → 分析結果會儲存為 HTML 檔案（可手動檢視）")
    print("   → 如需自動通知，請設定 Gmail 或 LINE")
    print()

print("💡 下一步：")
if ai_providers:
    print("   python tests/test_pipeline.py          # 完整測試")
    print("   python tests/test_pipeline.py --step analyze   # 只測試 AI 分析")
    if gmail_ok:
        print("   python tests/test_pipeline.py --step email     # 只測試 Email")
    if line_ok:
        print("   python tests/test_pipeline.py --step line      # 只測試 LINE")
else:
    print("   1. 編輯 .env 檔案，設定至少一個 AI API Key")
    print("   2. 執行 python tests/check_env.py 再次檢查")
    print("   3. 執行 python tests/test_pipeline.py 開始測試")

print()
print("=" * 60)
