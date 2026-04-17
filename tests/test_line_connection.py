# -*- coding: utf-8 -*-
"""
LINE API 連線測試工具
用於診斷 LINE Channel Access Token 和 User ID 是否正確
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# 載入 .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

LINE_API_URL = "https://api.line.me/v2/bot/message/push"

def test_line_connection():
    """測試 LINE API 連線"""
    print("=" * 60)
    print("🔍 LINE API 連線測試")
    print("=" * 60)
    
    # 1. 檢查環境變數
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")
    
    print("\n1️⃣ 環境變數檢查：")
    if not token:
        print("   ❌ LINE_CHANNEL_ACCESS_TOKEN 未設定")
        return
    else:
        print(f"   ✅ LINE_CHANNEL_ACCESS_TOKEN: {token[:20]}...{token[-10:]}")
    
    if not user_id:
        print("   ❌ LINE_USER_ID 未設定")
        return
    else:
        print(f"   ✅ LINE_USER_ID: {user_id}")
    
    # 2. 測試最簡單的文字訊息
    print("\n2️⃣ 測試傳送純文字訊息...")
    simple_payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": "🧪 這是測試訊息，如果你收到了，表示 LINE API 連線正常！"
            }
        ]
    }
    
    try:
        resp = requests.post(
            LINE_API_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=simple_payload,
            timeout=30,
        )
        
        print(f"   HTTP Status: {resp.status_code}")
        print(f"   Response: {resp.text}")
        
        if resp.status_code == 200:
            print("\n✅ 成功！請檢查 LINE 是否收到測試訊息")
            print("\n📌 如果沒收到訊息，可能原因：")
            print("   1. 尚未加機器人為好友")
            print("   2. User ID 不正確")
            print("   3. LINE Bot 未啟用 Push Message 功能")
        elif resp.status_code == 401:
            print("\n❌ 認證失敗！")
            print("   可能原因：")
            print("   1. Channel Access Token 錯誤")
            print("   2. Token 已過期（長期 Token 不會過期，短期 Token 會）")
            print("   3. Channel 已被停用")
            print("\n🔧 解決方法：")
            print("   1. 前往 LINE Developers Console")
            print("   2. 重新產生 Channel Access Token")
            print("   3. 更新 .env 中的 LINE_CHANNEL_ACCESS_TOKEN")
        elif resp.status_code == 400:
            print("\n❌ 請求格式錯誤！")
            print(f"   錯誤詳情：{resp.text}")
            print("   可能原因：")
            print("   1. User ID 格式錯誤（應為 U 開頭的 33 字元）")
            print("   2. 訊息格式不正確")
        elif resp.status_code == 403:
            print("\n❌ 權限不足！")
            print("   可能原因：")
            print("   1. Channel 未開啟 Push Message 權限")
            print("   2. 該 User 已封鎖機器人")
        else:
            print(f"\n❌ 未知錯誤 ({resp.status_code})")
            print(f"   Response: {resp.text}")
    
    except requests.exceptions.ConnectionError as e:
        print("\n❌ 連線錯誤！")
        print(f"   錯誤訊息：{e}")
        print("\n可能原因：")
        print("   1. 網路連線問題")
        print("   2. 防火牆阻擋")
        print("   3. LINE API 服務暫時無法連線")
        print("   4. Token 格式錯誤導致 SSL 握手失敗")
        print("\n🔧 建議檢查：")
        print("   1. 確認可以訪問 https://api.line.me")
        print("   2. 檢查是否使用 VPN 或代理伺服器")
        print("   3. 確認 Channel Access Token 沒有特殊字元或換行")
    
    except requests.exceptions.Timeout:
        print("\n❌ 連線逾時！")
        print("   LINE API 伺服器可能忙碌，請稍後再試")
    
    except Exception as e:
        print(f"\n❌ 發生錯誤：{type(e).__name__}")
        print(f"   詳情：{e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_line_connection()
