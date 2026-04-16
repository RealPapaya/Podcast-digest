#!/usr/bin/env python3
"""
股癌 Podcast Digest Pipeline
自動抓取、轉錄、分析並發送每日投資筆記
"""

import os
import sys
import json
import logging
from pathlib import Path

from src.fetch_podcast import fetch_latest_episode, download_audio
from src.transcribe import transcribe_audio
from src.analyze import analyze_transcript
from src.render import render_email_html
from src.notify import send_gmail, send_line_message

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

    # ── 5. Whisper 轉錄 ───────────────────────────────────────────
    log.info("🎯 開始轉錄（可能需要 20–60 分鐘）...")
    transcript = transcribe_audio(audio_path)
    if not transcript:
        log.error("轉錄失敗，結束")
        sys.exit(1)
    log.info(f"📝 轉錄完成，共 {len(transcript)} 字")

    # ── 6. Claude 分析 ────────────────────────────────────────────
    log.info("🤖 Claude 分析中...")
    digest = analyze_transcript(transcript, episode)
    if not digest:
        log.error("Claude 分析失敗，結束")
        sys.exit(1)

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
