# -*- coding: utf-8 -*-
"""
fetch_podcast.py
抓取股癌 Podcast RSS，取得最新集資訊並下載音檔
"""

import re
import time
import logging
import requests
import feedparser
from pathlib import Path
from datetime import datetime
from typing import Optional

log = logging.getLogger(__name__)

# Apple Podcasts ID → feedUrl 查詢
APPLE_LOOKUP_URL = "https://itunes.apple.com/lookup?id=1500839292&entity=podcast"
# 備用 RSS（若 Apple API 失敗）
FALLBACK_RSS = "https://feed.firstory.me/rss/user/ckf1r1aze1bgh0873p38u1pb7"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GooayeDigestBot/1.0)"
}


def get_rss_url() -> str:
    """透過 Apple iTunes API 取得 RSS Feed URL"""
    try:
        resp = requests.get(APPLE_LOOKUP_URL, timeout=15)
        data = resp.json()
        if data.get("resultCount", 0) > 0:
            feed_url = data["results"][0].get("feedUrl", "")
            if feed_url:
                log.info(f"RSS URL: {feed_url}")
                return feed_url
    except Exception as e:
        log.warning(f"Apple API 查詢失敗：{e}，使用備用 RSS")
    return FALLBACK_RSS


def fetch_latest_episode() -> Optional[dict]:
    """
    解析 RSS 取得最新集資訊
    回傳 dict: {title, guid, date, audio_url, duration, description}
    """
    rss_url = get_rss_url()

    try:
        feed = feedparser.parse(rss_url)
    except Exception as e:
        log.error(f"RSS 解析錯誤：{e}")
        return None

    if not feed.entries:
        log.error("RSS 無內容")
        return None

    entry = feed.entries[0]  # 最新一集

    # 取得音檔 URL
    audio_url = None
    for link in entry.get("links", []):
        if link.get("type", "").startswith("audio"):
            audio_url = link["href"]
            break
    if not audio_url and hasattr(entry, "enclosures"):
        for enc in entry.enclosures:
            if "audio" in enc.get("type", ""):
                audio_url = enc.href
                break

    if not audio_url:
        log.error("找不到音檔 URL")
        return None

    # 解析日期
    pub_date = entry.get("published_parsed") or entry.get("updated_parsed")
    if pub_date:
        date_str = datetime(*pub_date[:6]).strftime("%Y-%m-%d")
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")

    # 取得集數編號（如 EP653）
    ep_match = re.search(r"EP\s*\d+", entry.title, re.IGNORECASE)
    ep_number = ep_match.group(0).upper() if ep_match else "EP???"

    return {
        "title": entry.title,
        "ep_number": ep_number,
        "guid": entry.get("id", audio_url),
        "date": date_str,
        "audio_url": audio_url,
        "description": entry.get("summary", "")[:500],
    }


def download_audio(url: str, output_dir: Path) -> Optional[Path]:
    """
    串流下載音檔，顯示進度
    回傳本地路徑
    """
    filename = output_dir / "episode.mp3"

    try:
        log.info(f"下載：{url}")
        with requests.get(url, stream=True, headers=HEADERS, timeout=60) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0
            last_log = 0

            with open(filename, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                    f.write(chunk)
                    downloaded += len(chunk)
                    pct = (downloaded / total * 100) if total else 0
                    if pct - last_log >= 10:
                        log.info(f"  下載進度：{pct:.0f}% ({downloaded // 1024 // 1024}MB)")
                        last_log = pct

        log.info(f"✅ 音檔儲存至：{filename}")
        return filename

    except Exception as e:
        log.error(f"下載失敗：{e}")
        return None
