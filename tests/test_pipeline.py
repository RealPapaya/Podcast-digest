#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_pipeline.py
快速測試腳本 — 跳過 Whisper 轉錄，用假逐字稿測試後半段流程

用法：
  python test_pipeline.py          # 測試全部（Gemini + Email + LINE）
  python test_pipeline.py --step analyze   # 只測試 Gemini 分析
  python test_pipeline.py --step email     # 只測試 Email 發送
  python test_pipeline.py --step line      # 只測試 LINE 發送
  python test_pipeline.py --step render    # 只輸出 HTML 到 test_output.html
"""

import os
import sys
import json
import argparse
import logging
from typing import Optional

import dotenv

dotenv.load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── 假逐字稿（模擬股癌 EP653 內容）───────────────────────────────
MOCK_TRANSCRIPT = """
各位好，我是孟恭，歡迎來到股癌 Podcast EP653。
今天是 2026 年 4 月 15 日，市場最近真的好到讓人懷疑人生，
美股從之前的低點大幅反彈，台股也跟著各路標股持續向前衝。

先講台積電，2330，目前股價在 2080 左右。
市場共識今年 EPS 約 90 幾元，但更重要的是明年，
預期可以跳升到 130 到 140 元，若給予 20 倍本益比，
2800 元的目標價在 AI 族群中其實並不誇張。
AI 晶片對先進製程與封裝的需求持續爆發，短線催化劑是 AI 營收佔比提升。
主要風險在於地緣政治干擾或半導體週期性波動。我個人是看多的。

聯發科，2454，現在 1790，我也是看多。
聯發科正從手機晶片商轉型為 AI 運算大廠。
與 Google 合作的 TPU 晶片，Zebra Fish 是 V8，Humu Fish 是 V9，
已在台積電確保關鍵產能。雖然手機市場疲軟，
但 AI 業務的成長動能足以支撐評價重估，也就是所謂的 Re-rate。
短線需觀察 TPU 晶片的出貨表現，風險在於手機業務衰退超乎預期。

再來講 Marvell，MRVL，美股，現在 133 塊多。
Marvell 成功切入 Google 供應鏈，負責推論晶片與記憶體處理單元的設計。
AI 運算中記憶體頻寬是瓶頸，Marvell 的技術正好解決這痛點。
目前我給觀望評級，因為股價已部分反映利多，需觀察後續訂單量級。
風險在於 Broadcom 的競爭壓力及研發成本高昂。

被動元件產業，太陽誘電宣布全系列產品漲價，
原因說是貴金屬成本上升，但業界認為主因是 AI 伺服器需求。
鋁電容，SP-Cap，缺貨情況最為明顯。
國巨 2327 現在 322，華新科 2492 現在 144，我給觀望。

啟基 6285，現在 243，我看多。
啟基受惠於低軌衛星大客戶 SpaceX Starlink 的強勁訂單。
單一客戶的訂單金額佔其市值比例極高，顯示基本面支撐強。

Q&A 時間。有人問我美股前五大持股是什麼。
目前主要持股包含 CPU 類，就是 INTC、ARM、AMD，
然後是 Marvell MRVL、光通訊 LITE、COHR、
Cloudflare NET 還有 Tesla TSLA。
抱住股票需要愛與信仰，必須深入了解公司的業務邏輯，
否則單靠技術面很難在波動中留存。
會傷到你的人，都是你最相信、最愛的人；投資也是，最深的傷害往往來自你最有信仰的持股。

還有人問判斷趨勢是看幾天的日 K。
不要只看 3 到 5 天的短線震盪，應該結合日線與周線觀察。
最簡單的基準點就是創新高，創新高的股票沒有套牢壓力，趨勢最為明確。
投資是相對值而非絕對值，當手中股票不漲而有更強的標的出現時，應果斷換股，這就是機會成本的思考。

最後給畢業生三句真心話，長輩與其在台上講一堆心靈雞湯，不如直接給年輕人錢最實在。
要送年輕人三句話，不如送他錢，實質的資源永遠比口頭的鼓勵更有力。

大盤觀點：市場走勢極佳，美股大復活且台股標股持續衝刺，我的大盤觀點是看多。
"""

MOCK_EPISODE = {
    "title": "EP653 | 行情好到懷疑人生，台積電2800不是夢？",
    "ep_number": "EP653",
    "guid": "test-guid-ep653",
    "date": "2026-04-15",
    "audio_url": "https://example.com/ep653.mp3",
    "description": "測試用假資料",
}


def step_analyze() -> Optional[dict]:
    log.info("🤖 測試 Gemini 分析...")
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from src.analyze import analyze_transcript

    digest = analyze_transcript(MOCK_TRANSCRIPT, MOCK_EPISODE)
    if digest:
        log.info("✅ Gemini 分析成功！")
        log.info(f"   → 新聞：{len(digest.get('news', []))} 條")
        log.info(f"   → 個股：{len(digest.get('stocks', []))} 檔")
        log.info(f"   → Q&A：{len(digest.get('qa', []))} 個")
        # 儲存到檔案方便檢查
        with open("test_digest.json", "w", encoding="utf-8") as f:
            json.dump(digest, f, ensure_ascii=False, indent=2)
        log.info("   → 已儲存至 test_digest.json")
    else:
        log.error("❌ Gemini 分析失敗，請檢查 GOOGLE_API_KEY 是否正確")
    return digest


def step_render(digest: dict) -> str:
    log.info("🎨 測試 HTML 渲染...")
    from src.render import render_email_html

    html = render_email_html(digest)
    with open("test_output.html", "w", encoding="utf-8") as f:
        f.write(html)
    log.info("✅ HTML 已輸出至 test_output.html（用瀏覽器開啟預覽）")
    return html


def step_email(html: str, digest: dict):
    log.info("📧 測試 Gmail 發送...")
    from src.notify import send_gmail

    ok = send_gmail(html, digest)
    if ok:
        log.info("✅ Email 發送成功！請檢查收件匣")
    else:
        log.error("❌ Email 發送失敗，請確認：")
        log.error("   1. GMAIL_USER 環境變數是否設定")
        log.error("   2. GMAIL_APP_PASSWORD 是否正確（不是登入密碼！）")
        log.error("   3. Google 帳號是否開啟兩步驟驗證")


def step_line(digest: dict):
    log.info("📱 測試 LINE 發送...")
    from src.notify import send_line_message

    ok = send_line_message(digest)
    if ok:
        log.info("✅ LINE 訊息發送成功！請檢查 LINE")
    else:
        log.error("❌ LINE 發送失敗，請確認：")
        log.error("   1. LINE_CHANNEL_ACCESS_TOKEN 是否設定")
        log.error("   2. LINE_USER_ID 是否正確（以 U 開頭）")
        log.error("   3. 是否已加機器人為好友")


def main():
    parser = argparse.ArgumentParser(description="股癌 Digest 測試腳本")
    parser.add_argument(
        "--step",
        choices=["analyze", "render", "email", "line", "all"],
        default="all",
        help="要測試的步驟（預設：all）",
    )
    parser.add_argument(
        "--use-cached",
        action="store_true",
        help="使用上次儲存的 test_digest.json，跳過 Gemini 分析",
    )
    args = parser.parse_args()

    log.info("=" * 50)
    log.info("🧪 股癌 Digest 測試模式（跳過 Whisper 轉錄）")
    log.info("=" * 50)

    # 載入或產生 digest
    digest = None

    if args.use_cached and os.path.exists("test_digest.json"):
        log.info("📂 使用快取的 test_digest.json（跳過 Gemini）")
        with open("test_digest.json", encoding="utf-8") as f:
            digest = json.load(f)
    elif args.step in ("all", "analyze", "render", "email", "line"):
        if args.step == "render" and os.path.exists("test_digest.json"):
            log.info("📂 render 模式：載入 test_digest.json")
            with open("test_digest.json", encoding="utf-8") as f:
                digest = json.load(f)
        elif args.step == "email" and os.path.exists("test_digest.json"):
            log.info("📂 email 模式：載入 test_digest.json")
            with open("test_digest.json", encoding="utf-8") as f:
                digest = json.load(f)
        elif args.step == "line" and os.path.exists("test_digest.json"):
            log.info("📂 line 模式：載入 test_digest.json")
            with open("test_digest.json", encoding="utf-8") as f:
                digest = json.load(f)
        else:
            digest = step_analyze()

    if not digest:
        log.error("無法取得 digest，結束")
        sys.exit(1)

    # 渲染 HTML
    html = None
    if args.step in ("all", "render", "email"):
        html = step_render(digest)

    # 發送 Email
    if args.step in ("all", "email"):
        if not html:
            from src.render import render_email_html
            html = render_email_html(digest)
        step_email(html, digest)

    # 發送 LINE
    if args.step in ("all", "line"):
        step_line(digest)

    log.info("=" * 50)
    log.info("🏁 測試完成")
    log.info("=" * 50)


if __name__ == "__main__":
    main()
