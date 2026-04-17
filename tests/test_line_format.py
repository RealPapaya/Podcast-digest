# -*- coding: utf-8 -*-
"""
測試 LINE Flex Message JSON 格式是否正確
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.notify import _build_line_flex

# 載入測試資料
test_digest_path = Path(__file__).parent.parent / "test_digest.json"
with open(test_digest_path, "r", encoding="utf-8") as f:
    digest = json.load(f)

print("=" * 60)
print("🧪 LINE Flex Message 格式測試")
print("=" * 60)

try:
    flex_msg = _build_line_flex(digest)
    
    # 驗證 JSON 格式
    json_str = json.dumps(flex_msg, ensure_ascii=False, indent=2)
    
    print("\n✅ JSON 格式有效！")
    print(f"\n📊 統計資訊：")
    print(f"   - JSON 大小: {len(json_str):,} 字元")
    print(f"   - 訊息類型: {flex_msg.get('type')}")
    print(f"   - 替代文字: {flex_msg.get('altText')}")
    
    # 檢查內容區塊數量
    body_contents = flex_msg.get("contents", {}).get("body", {}).get("contents", [])
    print(f"   - Body 區塊數: {len(body_contents)}")
    
    # 儲存到檔案供檢查
    output_path = Path(__file__).parent.parent / "test_line_flex.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json_str)
    
    print(f"\n💾 已儲存至: {output_path}")
    print("\n📝 可複製此 JSON 到 LINE Flex Message Simulator 測試：")
    print("   https://developers.line.biz/flex-simulator/")
    
    # 檢查 LINE 限制（10,000 字元）
    if len(json_str) > 10000:
        print(f"\n⚠️  警告：JSON 超過 LINE 限制 (10,000 字元)")
        print(f"   目前大小：{len(json_str):,} 字元")
        print(f"   超出：{len(json_str) - 10000:,} 字元")
    else:
        print(f"\n✅ JSON 大小符合 LINE 限制 (< 10,000 字元)")
    
except Exception as e:
    print(f"\n❌ 錯誤：{type(e).__name__}")
    print(f"   詳情：{e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
