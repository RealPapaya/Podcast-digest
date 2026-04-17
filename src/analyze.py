# -*- coding: utf-8 -*-
"""
analyze.py
將逐字稿送入 Gemini，產出結構化 JSON 筆記
"""

import os
import json
import logging
import time
import hashlib
import sys
from pathlib import Path
from typing import Optional

from google import genai

# Import config from project root
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

log = logging.getLogger(__name__)

# Setup cache directory
CACHE_DIR = Path(config.CACHE_DIR)
CACHE_DIR.mkdir(exist_ok=True)

SYSTEM_PROMPT = """你是專業的台灣投資 Podcast 內容分析師，專門整理「股癌」(Gooaye) Podcast 的投資觀點。

你的任務是分析逐字稿，輸出一份結構化 JSON 筆記，格式如下。請確保：
1. 完全使用繁體中文
2. 準確反映主持人孟恭的原話觀點，不要自行添加
3. 股票代號與名稱要準確
4. 只輸出合法 JSON，不要加 markdown 符號或說明文字

JSON 格式：
{
  "ep_number": "EP653",
  "date": "2026-04-15",
  "intro": "本集導讀摘要（200字以內）",
  "market_outlook": {
    "stance": "看多 | 看空 | 中性 | 觀望",
    "description": "大盤觀點說明（100字以內）"
  },
  "news": [
    {
      "title": "新聞標題（10字以內）",
      "category": "台股 | 美股 | 總經 | 半導體 | 其他",
      "event": "事件描述（100字以內）",
      "perspective": "主持人觀點（100字以內）",
      "source_time": "12-13"
    }
  ],
  "stocks": [
    {
      "name": "台積電",
      "ticker": "2330",
      "exchange": "台股",
      "sector": "半導體",
      "stance": "看多 | 觀望 | 看空",
      "risk": "低 | 中 | 高",
      "description": "個股分析（150字以內）",
      "catalyst": "短線催化劑",
      "key_risk": "主要風險",
      "source_time": "12-13"
    }
  ],
  "qa": [
    {
      "title": "Q&A 主題標題",
      "question": "聽眾問題",
      "points": [
        {"label": "重點標題", "content": "說明內容"}
      ],
      "quote": "主持人金句（選填）",
      "source_time": "29"
    }
  ]
}

注意：
- news 抓 3–6 條最重要新聞
- stocks 抓所有提到有明確觀點的個股（通常 3–8 檔）
- qa 抓 2–4 個 Q&A 問答
- source_time 填集內時間點（分鐘），如 "12-13" 或 "29"
"""


def _get_cache_key(transcript: str, episode: dict) -> str:
    """Generate cache key from transcript and episode info"""
    content = f"{episode.get('guid', '')}_{len(transcript)}"
    return hashlib.md5(content.encode()).hexdigest()


def _load_from_cache(cache_key: str) -> Optional[dict]:
    """Load cached result if exists"""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                log.info(f"✅ Loading from cache: {cache_key[:8]}...")
                return json.load(f)
        except Exception as e:
            log.warning(f"Cache read failed: {e}")
    return None


def _save_to_cache(cache_key: str, data: dict):
    """Save result to cache"""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        log.info(f"💾 Saved to cache: {cache_key[:8]}...")
    except Exception as e:
        log.warning(f"Cache write failed: {e}")


def analyze_transcript(transcript: str, episode: dict) -> Optional[dict]:
    """
    Analyze transcript using Gemini API with retry and cache
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        log.error("Missing environment variable: GOOGLE_API_KEY")
        return None

    # Check cache first
    cache_key = _get_cache_key(transcript, episode)
    cached = _load_from_cache(cache_key)
    if cached:
        return cached

    # Truncate long transcript
    if len(transcript) > config.MAX_TRANSCRIPT_CHARS:
        log.warning(f"Transcript too long ({len(transcript)} chars), truncating to {config.MAX_TRANSCRIPT_CHARS}")
        transcript = transcript[:config.MAX_TRANSCRIPT_CHARS] + "\n\n[Content truncated]"

    client = genai.Client(api_key=api_key)

    user_message = f"""{SYSTEM_PROMPT}

以下是股癌 Podcast {episode['ep_number']}（{episode['date']}）的完整逐字稿，請按格式輸出 JSON 筆記：

---逐字稿開始---
{transcript}
---逐字稿結束---

請輸出 JSON："""

    # Try with retry mechanism
    models_to_try = config.GEMINI_MODELS
    
    last_error = None
    raw = None
    
    for model_name in models_to_try:
        for attempt in range(config.MAX_RETRIES):
            try:
                log.info(f"📡 Sending request to {model_name} (attempt {attempt + 1}/{config.MAX_RETRIES})...")
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_message,
                    config=config.GENERATION_CONFIG
                )

                raw = response.text.strip()
                log.info(f"✅ Response received: {len(raw)} chars from {model_name}")
                break  # Success, exit retry loop
                
            except Exception as e:
                last_error = e
                error_msg = str(e)
                
                # Check if quota exceeded
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    log.warning(f"⚠️ Quota exceeded for {model_name}, trying next model...")
                    break  # Try next model
                
                # Check if rate limit
                if "503" in error_msg or "UNAVAILABLE" in error_msg:
                    delay = config.RETRY_DELAY * (config.RETRY_MULTIPLIER ** attempt)
                    log.warning(f"⏳ Rate limited, waiting {delay}s before retry...")
                    time.sleep(delay)
                    continue  # Retry same model
                
                # Other errors
                log.error(f"❌ API error: {error_msg}")
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(config.RETRY_DELAY)
                    continue
                else:
                    break  # Try next model
        else:
            continue  # Retry loop completed without break, continue to next model
        break  # Successfully got response, exit model loop
    
    if raw is None:
        # All models failed
        log.error(f"❌ All models failed. Last error: {last_error}")
        return None
    
    try:
        # Clean markdown wrapper if exists
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        digest = json.loads(raw)

        # Fill missing episode info
        digest.setdefault("ep_number", episode.get("ep_number", ""))
        digest.setdefault("date", episode.get("date", ""))

        log.info(
            f"✅ Parsing successful: {len(digest.get('news', []))} news, "
            f"{len(digest.get('stocks', []))} stocks, "
            f"{len(digest.get('qa', []))} Q&A"
        )
        
        # Save to cache
        _save_to_cache(cache_key, digest)
        
        return digest

    except json.JSONDecodeError as e:
        log.error(f"❌ JSON parsing failed: {e}")
        log.error(f"Raw response (first 500 chars): {raw[:500]}")
        return None
