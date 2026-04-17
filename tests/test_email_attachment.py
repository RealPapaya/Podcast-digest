#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_email_attachment.py
測試 Email 是否正確附加 HTML 檔案

用法：
  python tests/test_email_attachment.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

# 測試用資料
TEST_DIGEST = {
    "ep_number": "EP999",
    "date": "2026-04-17",
    "market_outlook": {
        "stance": "看多",
        "description": "這是測試 HTML 附件功能"
    },
    "news": [
        {"title": "測試新聞 1", "description": "測試內容"},
    ],
    "stocks": [
        {"name": "測試股票", "ticker": "9999", "stance": "看多", "price": "999"}
    ],
    "qa": [{"question": "測試問題", "answer": "測試答案"}]
}

TEST_HTML = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>股癌 EP999 測試</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f3f4f6; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; 
                     border-radius: 12px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #667eea; }
        .section { margin: 20px 0; padding: 15px; background: #f9fafb; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ 股癌 EP999 投資筆記</h1>
        <p><strong>測試 HTML 附件功能</strong></p>
        
        <div class="section">
            <h2>🎯 大盤觀點 🟢 看多</h2>
            <p>這是測試 HTML 附件功能</p>
        </div>
        
        <div class="section">
            <h2>📰 今日新聞</h2>
            <p>• 測試新聞 1</p>
        </div>
        
        <div class="section">
            <h2>📊 個股觀點</h2>
            <p><strong>測試股票 (9999)</strong> - 看多 NT$ 999</p>
        </div>
        
        <p style="text-align: center; color: #6b7280; margin-top: 30px;">
            ⚠️ 本筆記由 AI 自動生成，僅供參考，不構成投資建議
        </p>
    </div>
</body>
</html>
"""

def main():
    print()
    print("=" * 70)
    print("📧 Email HTML 附件測試")
    print("=" * 70)
    print()
    
    # 檢查環境變數
    gmail_user = os.getenv("GMAIL_USER")
    gmail_pass = os.getenv("GMAIL_APP_PASSWORD")
    
    if not gmail_user or not gmail_pass:
        print("❌ 錯誤：未設定 Gmail 環境變數")
        print("   請在 .env 檔案中設定 GMAIL_USER 和 GMAIL_APP_PASSWORD")
        return
    
    if gmail_pass == "abcd efgh ijkl mnop":
        print("❌ 錯誤：GMAIL_APP_PASSWORD 仍是範例值")
        print("   請參考 docs/GMAIL_SETUP_GUIDE.md 設定真實密碼")
        return
    
    print(f"✅ Gmail 設定:")
    print(f"   寄件者: {gmail_user}")
    print(f"   收件者: {os.getenv('RECIPIENT_EMAIL', gmail_user)}")
    print()
    
    # 儲存 HTML 到本地
    with open("test_attachment_preview.html", "w", encoding="utf-8") as f:
        f.write(TEST_HTML)
    print("💾 已儲存測試 HTML 至: test_attachment_preview.html")
    print("   可用瀏覽器開啟預覽")
    print()
    
    print("📋 此次測試將會：")
    print("   1. 發送 Email 到你的信箱")
    print("   2. Email 內容會顯示 HTML（彩色排版）")
    print("   3. Email 會附加一個 stock_digest_EP999.html 檔案")
    print()
    
    confirm = input("🚀 確定要發送測試 Email 嗎？(y/N): ").strip().lower()
    
    if confirm != 'y':
        print("⏭️  已取消測試")
        return
    
    print()
    print("📧 正在發送測試 Email...")
    print()
    
    from src.notify import send_gmail
    
    success = send_gmail(TEST_HTML, TEST_DIGEST)
    
    print()
    print("=" * 70)
    
    if success:
        print("✅ 測試成功！Email 已發送")
        print("=" * 70)
        print()
        print("📬 請檢查你的信箱並確認以下事項：")
        print()
        print("   ✓ 信件主旨：股癌 EP999 投資筆記 🟢 2026-04-17")
        print("   ✓ 信件內容：顯示彩色 HTML 排版")
        print("   ✓ 附件：stock_digest_EP999.html（可下載）")
        print()
        print("💡 如果看不到附件，請檢查：")
        print("   - Gmail: 信件底部應顯示「1 個附件」")
        print("   - Outlook: 信件頂部應顯示迴紋針圖示")
        print("   - 垃圾郵件資料夾")
        print()
    else:
        print("❌ 測試失敗")
        print("=" * 70)
        print()
        print("請檢查上方的錯誤訊息")
        print()

if __name__ == "__main__":
    main()
