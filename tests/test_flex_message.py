# -*- coding: utf-8 -*-
"""
本地測試：驗證 _build_line_flex 產生的 Flex Message 不含空 text 欄位
不需要實際呼叫 LINE API
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from notify import _build_line_flex


def collect_texts(obj, path=""):
    """遞迴收集所有 text 欄位及其路徑"""
    issues = []
    if isinstance(obj, dict):
        if obj.get("type") in ("text",) and "text" in obj:
            val = obj["text"]
            if not val or not str(val).strip():
                issues.append(f"空 text 欄位 at {path}")
        for k, v in obj.items():
            issues.extend(collect_texts(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            issues.extend(collect_texts(item, f"{path}[{i}]"))
    return issues


def run(label, digest):
    print(f"\n{'─'*50}")
    print(f"📋 {label}")
    flex = _build_line_flex(digest)
    issues = collect_texts(flex)
    if issues:
        print("  ❌ 發現空 text 欄位：")
        for i in issues:
            print(f"     {i}")
    else:
        print("  ✅ 所有 text 欄位均非空")
    return len(issues) == 0


def main():
    ok = True

    # Case 1: 正常完整資料
    ok &= run("正常完整資料", {
        "ep_number": "EP500",
        "date": "2026-04-17",
        "market_outlook": {"stance": "看多", "description": "Fed 降息預期升溫，科技股走強"},
        "stocks": [
            {"name": "台積電", "ticker": "2330", "stance": "看多"},
            {"name": "聯發科", "ticker": "2454", "stance": "觀望"},
        ],
        "news": [
            {"title": "Fed 官員暗示年底前降息"},
            {"title": "AI 伺服器需求持續強勁"},
        ],
    })

    # Case 2: description 為空字串（原本會觸發 LINE API 錯誤）
    ok &= run("description 為空字串", {
        "ep_number": "EP501",
        "date": "2026-04-17",
        "market_outlook": {"stance": "中性", "description": ""},
        "stocks": [],
        "news": [],
    })

    # Case 3: description 為 None
    ok &= run("description 為 None", {
        "ep_number": "EP502",
        "date": "2026-04-17",
        "market_outlook": {"stance": "看空"},
        "stocks": [],
        "news": [],
    })

    # Case 4: 完全空的 digest
    ok &= run("完全空的 digest", {})

    print(f"\n{'='*50}")
    print("✅ 全部通過" if ok else "❌ 有測試失敗")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
