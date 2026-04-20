#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股癌 Podcast Digest Pipeline
自動抓取、轉錄、分析並發送每日投資筆記
"""

import os
import sys
import json
import logging
from pathlib import Path

import dotenv

from src.fetch_podcast import fetch_latest_episode, download_audio
from src.transcribe import transcribe_audio
from src.analyze import analyze_audio_gemini, analyze_transcript
from src.stock_data import enrich_stocks_with_data
from src.render import render_email_html
from src.notify import send_gmail, send_line_message

dotenv.load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

STATE_FILE = Path("state.json")
AUDIO_DIR = Path("audio")
AUDIO_DIR.mkdir(exist_ok=True)


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"last_processed_guid": None, "last_processed_title": None}


def save_state(state: dict):
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main():
    log.info("🎙️  股癌 Digest Pipeline 啟動")

    # ── 1. 載入上次狀態 ──────────────────────────────────────────
    state = load_state()
    last_guid = state.get("last_processed_guid")

    # ── 2. 抓最新集資訊 ──────────────────────────────────────────
    log.info("📡 抓取最新集資訊...")
    episode = fetch_latest_episode()
    if not episode:
        log.error("無法取得 Podcast 資訊，結束")
        sys.exit(1)

    log.info(f"📻 最新集：{episode['title']} ({episode['date']})")

    # ── 3. 檢查是否已處理過 ───────────────────────────────────────
    if episode["guid"] == last_guid:
        log.info("✅ 此集已處理過，略過")
        sys.exit(0)

    # ── 4. 下載音檔 ───────────────────────────────────────────────
    log.info("⬇️  下載音檔...")
    audio_path = download_audio(episode["audio_url"], AUDIO_DIR)
    if not audio_path:
        log.error("音檔下載失敗，結束")
        sys.exit(1)

            # ── 5. AI 分析（多重備援）───────────────────────────────────
    digest = None
    
    # 嘗試 1: Gemini 直接聆聽音檔（最快但不穩定）
    if os.environ.get("GOOGLE_API_KEY"):
        log.info("🎧 嘗試 Gemini 直接聆聽音檔分析...")
        digest = analyze_audio_gemini(audio_path, episode)
    
    # 嘗試 2: Whisper 轉錄 + 多 AI fallback（Claude → OpenAI → Gemini）
    if not digest:
        log.info("🎤 Gemini 音訊分析失敗，改用 Whisper 轉錄...")
        transcript = transcribe_audio(audio_path)
        if transcript:
            log.info("🤖 使用多 AI fallback 分析逐字稿 (Claude → OpenAI → Gemini)...")
            digest = analyze_transcript(transcript, episode)
    
    if not digest:
        log.error("❌ 所有 AI 分析方式都失敗，結束")
        audio_path.unlink(missing_ok=True)
        sys.exit(1)
    
        log.info("✅ AI 分析完成")

    # ── 6. 獲取股價數據 ──────────────────────────────────────────
    log.info("📊 獲取股價數據 (Price, P/E, RSI, 1M%)...")
    
    # Individual stocks
    stocks = digest.get("stocks", [])
    if stocks:
        digest["stocks"] = enrich_stocks_with_data(stocks)
        log.info(f"✅ 已獲取 {len(stocks)} 檔個股數據")
    
    # Sector analysis stocks
    sector_analysis = digest.get("sector_analysis", [])
    sector_stock_count = 0
    for sector in sector_analysis:
        related_stocks = sector.get("related_stocks", [])
        if related_stocks:
            sector["related_stocks"] = enrich_stocks_with_data(related_stocks)
            sector_stock_count += len(related_stocks)
    if sector_stock_count > 0:
        log.info(f"✅ 已獲取 {sector_stock_count} 檔族群股票數據")

    # ── 7. 渲染 HTML ──────────────────────────────────────────────
    log.info("🎨 渲染 Email HTML...")
    html_content = render_email_html(digest)

    # ── 8. 發送通知 ───────────────────────────────────────────────
    log.info("📧 發送 Email...")
    send_gmail(html_content, digest)

    log.info("📱 發送 LINE 訊息...")
    send_line_message(digest)

    # ── 9. 更新狀態 ───────────────────────────────────────────────
    state["last_processed_guid"] = episode["guid"]
    state["last_processed_title"] = episode["title"]
    save_state(state)

    # 清理音檔（避免佔空間）
    audio_path.unlink(missing_ok=True)

    log.info("🎉 完成！")


if __name__ == "__main__":
    main()
