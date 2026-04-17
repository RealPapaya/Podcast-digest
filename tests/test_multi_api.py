#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-API Test Script
快速測試所有配置的 AI API
"""

import os
import sys
import dotenv

dotenv.load_dotenv()

def test_api_keys():
    """檢查並顯示已配置的 API Keys"""
    print("=" * 60)
    print("🔍 檢查 AI API 配置")
    print("=" * 60)
    
    apis = [
        ("Claude (Anthropic)", "ANTHROPIC_API_KEY", "sk-ant-"),
        ("OpenAI", "OPENAI_API_KEY", "sk-"),
        ("Gemini (Google)", "GOOGLE_API_KEY", "AIza"),
    ]
    
    configured = []
    
    for name, env_var, prefix in apis:
        key = os.environ.get(env_var)
        if key and not key.startswith("your_"):
            print(f"✅ {name:25} : {key[:15]}...")
            configured.append(name)
        else:
            print(f"⏭️  {name:25} : 未設定")
    
    print("=" * 60)
    
    if not configured:
        print("❌ 沒有配置任何 API Key！")
        print("\n請在 .env 文件中至少設置一個 API Key：")
        print("  - ANTHROPIC_API_KEY (Claude)")
        print("  - OPENAI_API_KEY (GPT-4o-mini)")
        print("  - GOOGLE_API_KEY (Gemini)")
        return False
    
    print(f"✅ 已配置 {len(configured)} 個 API:")
    for api in configured:
        print(f"   • {api}")
    
    return True


def test_imports():
    """測試必要的庫是否已安裝"""
    print("\n" + "=" * 60)
    print("📦 檢查依賴庫")
    print("=" * 60)
    
    libs = [
        ("anthropic", "Claude SDK"),
        ("openai", "OpenAI SDK"),
        ("google.genai", "Gemini SDK"),
    ]
    
    all_ok = True
    
    for lib, desc in libs:
        try:
            __import__(lib)
            print(f"✅ {desc:20} : 已安裝")
        except ImportError:
            print(f"⚠️  {desc:20} : 未安裝")
            all_ok = False
    
    print("=" * 60)
    
    if not all_ok:
        print("\n⚠️  部分庫未安裝，建議運行：")
        print("   pip install anthropic openai google-genai")
    
    return all_ok


def test_analyze_function():
    """測試 analyze 函數"""
    print("\n" + "=" * 60)
    print("🧪 測試 AI 分析功能")
    print("=" * 60)
    
    try:
        from src.analyze import analyze_transcript
        
        # 簡單測試數據
        test_transcript = "這是一個測試逐字稿。"
        test_episode = {
            "ep_number": "TEST001",
            "date": "2026-04-17",
            "guid": "test-123",
        }
        
        print("📡 調用 analyze_transcript...")
        result = analyze_transcript(test_transcript, test_episode)
        
        if result:
            print("✅ 分析成功！")
            print(f"   新聞：{len(result.get('news', []))} 條")
            print(f"   個股：{len(result.get('stocks', []))} 檔")
            print(f"   Q&A：{len(result.get('qa', []))} 個")
            return True
        else:
            print("❌ 分析失敗")
            return False
            
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        return False


def main():
    print("\n🎯 多 AI API 配置測試工具")
    print()
    
    # Step 1: 檢查 API Keys
    if not test_api_keys():
        sys.exit(1)
    
    # Step 2: 檢查依賴
    test_imports()
    
    # Step 3: 測試功能（可選）
    if len(sys.argv) > 1 and sys.argv[1] == "--test-analyze":
        test_analyze_function()
    else:
        print("\n💡 提示：運行 'python test_multi_api.py --test-analyze' 測試完整功能")
    
    print("\n✅ 測試完成！")
    print()


if __name__ == "__main__":
    main()
