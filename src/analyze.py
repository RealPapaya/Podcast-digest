# -*- coding: utf-8 -*-
"""
analyze.py
AI Analysis Module with Multi-Provider Fallback Chain
Priority: Claude (Anthropic) → GPT-4o-mini (OpenAI) → Gemini (Google)
Includes caching and retry mechanisms for maximum reliability
"""

import os
import json
import logging
import time
import hashlib
import sys
from pathlib import Path
from typing import Optional, Callable

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
  "intro": "本集導讀摘要（600-800字，需包含：本集重點議題、核心投資觀點、主要提及的股票或產業）",
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
      "insights": [
        {"label": "催化劑", "content": "CoWoS產能擴充"},
        {"label": "風險點", "content": "地緣政治"},
        {"label": "目標價", "content": "2800元"},
        {"label": "進場時機", "content": "回測月線支撐"}
      ],
      "source_time": "12-13"
    }
  ],
  "sector_analysis": [
    {
      "sector_name": "被動元件",
      "stance": "看多 | 觀望 | 看空",
      "description": "族群整體分析（150字以內）",
      "insights": [
        {"label": "催化劑", "content": "太陽誘電漲價"},
        {"label": "風險點", "content": "庫存調整"},
        {"label": "趨勢研判", "content": "產業週期向上"}
      ],
      "related_stocks": [
        {"name": "國巨", "ticker": "2327", "exchange": "台股"},
        {"name": "華新科", "ticker": "2492", "exchange": "台股"}
      ],
      "source_time": "15-20"
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
- sector_analysis 抓族群/產業分析（如被動元件、AI 概念股等），相關個股填在 related_stocks
- qa 抓 2–4 個 Q&A 問答
- source_time 填集內時間點（分鐘），如 "12-13" 或 "29"
- insights 為彈性欄位陣列，請根據內容性質智能選擇最精確的標籤：
  
  【正面驅動力】
  • 驅動因素 - 結構性改變（產能擴充、技術升級、市佔提升）
  • 觸發事件 - 短期催化劑（新品發表、財報公告、訂單獲取）
  • 產業紅利 - 總體趨勢（AI浪潮、政策扶植、供應鏈轉移）
  
  【風險評估】
  • 風險點 - 明確威脅（競爭加劇、法規限制、客戶流失）
  • 隱憂 - 潛在不確定性（產能過剩疑慮、技術路線分歧）
  
  【投資操作】
  • 目標價 - 價格預測（2800元、上看50美元）
  • 進場時機 - 時機判斷（回測月線支撐、突破季線後）
  • 操作策略 - 具體建議（分批布局、逢高減碼）
  
  【基本面分析】
  • 財務狀況 - 獲利能力（毛利率改善、EPS成長）
  • 訂單能見度 - 營收展望（Q2訂單滿載、下半年回溫）
  • 估值水位 - 本益比/淨值比判斷（本益比偏低、估值合理）
  
  【技術面/籌碼面】
  • 技術訊號 - 圖表形態（突破盤整、形成黃金交叉）
  • 籌碼動向 - 資金流向（外資連買、法人佈局）
  
  【其他常用】
  • 趨勢研判 - 產業週期判斷（景氣谷底、成長期初段）
  • 觀察重點 - 後續關注事項（月營收公告、法說會）
  
  只填寫 Podcast 中有明確提到的項目，每個股票/族群可以有 2-5 個 insights，非必填
  優先使用更精確的語義標籤，避免所有內容都用「催化劑」「風險點」等通用標籤
"""


# ═══════════════════════════════════════════════════════════════
# Cache Management
# ═══════════════════════════════════════════════════════════════

def _get_cache_key(transcript: str, episode: dict) -> str:
    """Generate cache key from transcript and episode info"""
    content = f"{episode.get('guid', '')}_{len(transcript)}"
    return hashlib.md5(content.encode()).hexdigest()


def _load_from_cache(cache_key: str) -> Optional[dict]:
    """Load cached result if exists"""
    if not config.ENABLE_CACHE:
        return None
        
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                log.info(f"💾 Loading from cache: {cache_key[:8]}...")
                return json.load(f)
        except Exception as e:
            log.warning(f"Cache read failed: {e}")
    return None


def _save_to_cache(cache_key: str, data: dict):
    """Save result to cache"""
    if not config.ENABLE_CACHE:
        return
        
    cache_file = CACHE_DIR / f"{cache_key}.json"
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        log.info(f"💾 Saved to cache: {cache_key[:8]}...")
    except Exception as e:
        log.warning(f"Cache write failed: {e}")


# ═══════════════════════════════════════════════════════════════
# JSON Parsing Helper
# ═══════════════════════════════════════════════════════════════

def _parse_json(raw: str) -> Optional[dict]:
    """Clean and parse JSON from AI response"""
    text = raw.strip()
    
    # Remove markdown code block wrapper
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1]
        if text.startswith("json"):
            text = text[4:]
    
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        log.error(f"JSON parsing failed: {e}")
        log.error(f"Raw text (first 500 chars): {text[:500]}")
        return None


# ═══════════════════════════════════════════════════════════════
# AI Provider Functions
# ═══════════════════════════════════════════════════════════════

def _build_user_message(transcript: str, episode: dict) -> str:
    """Build user message with transcript"""
    if len(transcript) > config.MAX_TRANSCRIPT_CHARS:
        log.warning(f"Transcript too long ({len(transcript)} chars), truncating to {config.MAX_TRANSCRIPT_CHARS}")
        transcript = transcript[:config.MAX_TRANSCRIPT_CHARS] + "\n\n[以上為前段內容，後續略]"

    return (
        f"以下是股癌 Podcast {episode['ep_number']}（{episode['date']}）的完整逐字稿，"
        f"請按格式輸出 JSON 筆記：\n\n"
        f"---逐字稿開始---\n{transcript}\n---逐字稿結束---\n\n請輸出 JSON："
    )


# ── Provider 1: Claude (Anthropic) ──────────────────────────────

def _try_claude(user_message: str) -> Optional[dict]:
    """Try Claude API with retry mechanism"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.info("  ⏭️  Claude: ANTHROPIC_API_KEY not set, skipping")
        return None

    try:
        import anthropic
    except ImportError:
        log.warning("  ⏭️  Claude: 'anthropic' package not installed, skipping")
        return None

    client = anthropic.Anthropic(api_key=api_key)
    
    for attempt in range(config.MAX_RETRIES):
        try:
            log.info(f"  📡 Claude: Sending request (attempt {attempt + 1}/{config.MAX_RETRIES})...")
            
            message = client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=config.CLAUDE_MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
            
            result = _parse_json(message.content[0].text)
            if result:
                log.info("  ✅ Claude: Success")
                return result
            else:
                log.warning("  ⚠️  Claude: Failed to parse JSON")
                
        except Exception as e:
            error_msg = str(e)
            log.warning(f"  ❌ Claude: {error_msg}")
            
            # Retry on rate limit
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                if attempt < config.MAX_RETRIES - 1:
                    delay = config.RETRY_DELAY * (config.RETRY_MULTIPLIER ** attempt)
                    log.info(f"  ⏳ Claude: Rate limited, waiting {delay}s...")
                    time.sleep(delay)
                    continue
            
            # Don't retry on other errors
            break
    
    return None


# ── Provider 2: OpenAI GPT-4o-mini ──────────────────────────────

def _try_openai(user_message: str) -> Optional[dict]:
    """Try OpenAI API with retry mechanism"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        log.info("  ⏭️  GPT-4o-mini: OPENAI_API_KEY not set, skipping")
        return None

    try:
        import openai
    except ImportError:
        log.warning("  ⏭️  GPT-4o-mini: 'openai' package not installed, skipping")
        return None

    client = openai.OpenAI(api_key=api_key)
    
    for attempt in range(config.MAX_RETRIES):
        try:
            log.info(f"  📡 GPT-4o-mini: Sending request (attempt {attempt + 1}/{config.MAX_RETRIES})...")
            
            response = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                max_tokens=config.OPENAI_MAX_TOKENS,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
            )
            
            result = _parse_json(response.choices[0].message.content)
            if result:
                log.info("  ✅ GPT-4o-mini: Success")
                return result
            else:
                log.warning("  ⚠️  GPT-4o-mini: Failed to parse JSON")
                
        except Exception as e:
            error_msg = str(e)
            log.warning(f"  ❌ GPT-4o-mini: {error_msg}")
            
            # Retry on rate limit
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                if attempt < config.MAX_RETRIES - 1:
                    delay = config.RETRY_DELAY * (config.RETRY_MULTIPLIER ** attempt)
                    log.info(f"  ⏳ GPT-4o-mini: Rate limited, waiting {delay}s...")
                    time.sleep(delay)
                    continue
            
            # Don't retry on other errors
            break
    
    return None


# ── Provider 3: Google Gemini ───────────────────────────────────

def _try_gemini(user_message: str) -> Optional[dict]:
    """Try Gemini API with retry and model fallback"""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        log.info("  ⏭️  Gemini: GOOGLE_API_KEY not set, skipping")
        return None

    try:
        from google import genai
    except ImportError:
        log.warning("  ⏭️  Gemini: 'google-genai' package not installed, skipping")
        return None

    client = genai.Client(api_key=api_key)
    
    # Try multiple Gemini models
    for model_name in config.GEMINI_MODELS:
        for attempt in range(config.MAX_RETRIES):
            try:
                log.info(f"  📡 Gemini ({model_name}): Sending request (attempt {attempt + 1}/{config.MAX_RETRIES})...")
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_message,
                    config=config.GENERATION_CONFIG
                )

                result = _parse_json(response.text)
                if result:
                    log.info(f"  ✅ Gemini ({model_name}): Success")
                    return result
                else:
                    log.warning(f"  ⚠️  Gemini ({model_name}): Failed to parse JSON")
                    
            except Exception as e:
                error_msg = str(e)
                
                # Quota exceeded - try next model
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    log.warning(f"  ⚠️  Gemini ({model_name}): Quota exceeded")
                    break  # Try next model
                
                # Rate limit - retry with backoff
                if "503" in error_msg or "UNAVAILABLE" in error_msg:
                    if attempt < config.MAX_RETRIES - 1:
                        delay = config.RETRY_DELAY * (config.RETRY_MULTIPLIER ** attempt)
                        log.info(f"  ⏳ Gemini ({model_name}): Rate limited, waiting {delay}s...")
                        time.sleep(delay)
                        continue
                
                # Other errors
                log.warning(f"  ❌ Gemini ({model_name}): {error_msg}")
                break  # Try next model
    
    return None


# ── Audio Analysis: Gemini direct audio ────────────────────────

def analyze_audio_gemini(audio_path: Path, episode: dict) -> Optional[dict]:
    """直接上傳音檔給 Gemini 分析，不需 Whisper 轉錄"""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        log.error("未設定 GOOGLE_API_KEY，無法進行音訊分析")
        return None

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        log.error("'google-genai' 套件未安裝，請執行 pip install google-genai")
        return None

    cache_key = _get_cache_key(str(audio_path), episode)
    cached = _load_from_cache(cache_key)
    if cached:
        log.info("  ✅ 從快取載入分析結果")
        return cached

    client = genai.Client(api_key=api_key)

    mime_map = {".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".wav": "audio/wav", ".ogg": "audio/ogg"}
    mime_type = mime_map.get(Path(audio_path).suffix.lower(), "audio/mpeg")

    log.info(f"📤 上傳音檔至 Gemini Files API：{audio_path}")
    try:
        uploaded = client.files.upload(file=str(audio_path), config={"mime_type": mime_type})
    except TypeError:
        # 舊版 SDK 使用不同參數名稱
        uploaded = client.files.upload(file=str(audio_path), mime_type=mime_type)

    # 等待 Gemini 處理完成
    while uploaded.state.name == "PROCESSING":
        time.sleep(3)
        uploaded = client.files.get(name=uploaded.name)

    if uploaded.state.name == "FAILED":
        log.error("Gemini Files API 處理音檔失敗")
        return None

    log.info(f"✅ 音檔上傳完成：{uploaded.uri}")

    prompt = (
        f"以下是股癌 Podcast {episode.get('ep_number', 'EP???')}（{episode.get('date', '')}）的完整音訊，"
        f"請仔細聆聽後，按格式輸出 JSON 筆記："
    )

    result = None
    for model_name in config.GEMINI_MODELS:
        for attempt in range(config.MAX_RETRIES):
            try:
                log.info(f"  📡 Gemini audio ({model_name}): attempt {attempt + 1}/{config.MAX_RETRIES}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        {"file_data": {"file_uri": uploaded.uri, "mime_type": mime_type}},
                        {"text": prompt},
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=config.GENERATION_CONFIG["temperature"],
                        max_output_tokens=65536,
                        top_p=config.GENERATION_CONFIG["top_p"],
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                    ),
                )
                result = _parse_json(response.text)
                if result:
                    log.info(f"  ✅ Gemini audio ({model_name}): 成功")
                    break
                else:
                    log.warning(f"  ⚠️  Gemini audio ({model_name}): JSON 解析失敗")
            except Exception as e:
                err = str(e)
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    log.warning(f"  ⚠️  Gemini ({model_name}): 配額超限，換下一個模型")
                    break
                if "503" in err or "UNAVAILABLE" in err:
                    if attempt < config.MAX_RETRIES - 1:
                        delay = config.RETRY_DELAY * (config.RETRY_MULTIPLIER ** attempt)
                        log.info(f"  ⏳ Gemini ({model_name}): 等待 {delay}s 後重試...")
                        time.sleep(delay)
                        continue
                log.warning(f"  ❌ Gemini audio ({model_name}): {err}")
                break
            if result:
                break

    try:
        client.files.delete(name=uploaded.name)
        log.info("🗑️  已清理 Gemini Files API 暫存檔")
    except Exception:
        pass

    if result:
        # Fill missing episode info (in case AI didn't include them)
        result.setdefault("ep_number", episode.get("ep_number", ""))
        result.setdefault("date", episode.get("date", ""))
        _save_to_cache(cache_key, result)
    return result


# ═══════════════════════════════════════════════════════════════
# Main Fallback Chain
# ═══════════════════════════════════════════════════════════════

PROVIDERS = [
    ("Claude (Anthropic)", _try_claude),
    ("GPT-4o-mini (OpenAI)", _try_openai),
    ("Gemini (Google)", _try_gemini),
]


def analyze_transcript(transcript: str, episode: dict) -> Optional[dict]:
    """
    Analyze transcript using multi-provider fallback chain with caching.
    
    Priority order:
    1. Claude (Anthropic) - Best quality
    2. GPT-4o-mini (OpenAI) - Fast and reliable
    3. Gemini (Google) - Fallback option
    
    Returns first successful result or None if all fail.
    """
    # Check cache first
    cache_key = _get_cache_key(transcript, episode)
    cached = _load_from_cache(cache_key)
    if cached:
        return cached

    # Build user message
    user_message = _build_user_message(transcript, episode)

    log.info("🤖 AI Analysis Fallback Chain Started")
    log.info("─" * 50)

    # Try each provider in order
    for provider_name, provider_fn in PROVIDERS:
        log.info(f"→ Trying {provider_name}...")
        
        try:
            result = provider_fn(user_message)
        except Exception as e:
            log.error(f"  ❌ Unexpected error: {e}")
            result = None

        if result is not None:
            # Fill missing episode info
            result.setdefault("ep_number", episode.get("ep_number", ""))
            result.setdefault("date", episode.get("date", ""))
            
            log.info("─" * 50)
            log.info(f"✅ Analysis completed by {provider_name}")
            log.info(
                f"   📊 News: {len(result.get('news', []))} / "
                f"Stocks: {len(result.get('stocks', []))} / "
                f"Q&A: {len(result.get('qa', []))}"
            )
            
            # Save to cache
            _save_to_cache(cache_key, result)
            
            return result
        
        log.info(f"  → {provider_name} failed, trying next provider...")

    # All providers failed
    log.info("─" * 50)
    log.error("❌ All AI providers failed")
    log.error("Please check:")
    log.error("  1. API keys are set correctly in .env")
    log.error("  2. API quotas are not exceeded")
    log.error("  3. Network connection is stable")
    
    return None
