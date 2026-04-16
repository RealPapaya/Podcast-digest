"""
analyze.py
將逐字稿送入 Gemini，產出結構化 JSON 筆記
"""

import os
import json
import logging
from typing import Optional

from google import genai

log = logging.getLogger(__name__)

# 逐字稿太長時截斷（Gemini 上下文限制保護）
MAX_TRANSCRIPT_CHARS = 1_000_000  # Gemini 支援較長上下文

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


def analyze_transcript(transcript: str, episode: dict) -> Optional[dict]:
    """
    呼叫 Gemini API 分析逐字稿，回傳結構化 dict
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        log.error("缺少環境變數：GOOGLE_API_KEY")
        return None

    # 截斷過長的逐字稿
    if len(transcript) > MAX_TRANSCRIPT_CHARS:
        log.warning(f"逐字稿過長（{len(transcript)} 字），截斷至 {MAX_TRANSCRIPT_CHARS} 字")
        transcript = transcript[:MAX_TRANSCRIPT_CHARS] + "\n\n[以上為前段內容，後續略]"

    client = genai.Client(api_key=api_key)

    user_message = f"""{SYSTEM_PROMPT}

以下是股癌 Podcast {episode['ep_number']}（{episode['date']}）的完整逐字稿，請按格式輸出 JSON 筆記：

---逐字稿開始---
{transcript}
---逐字稿結束---

請輸出 JSON："""

    try:
        log.info("送出 Gemini API 請求...")
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=user_message,
            config={
                "temperature": 0.1,
                "max_output_tokens": 4096,
            }
        )

        raw = response.text.strip()
        log.info(f"Gemini 回應長度：{len(raw)} 字")

        # 清理可能的 markdown 包裝
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        digest = json.loads(raw)

        # 補齊 episode 資訊（如果 Gemini 沒填）
        digest.setdefault("ep_number", episode.get("ep_number", ""))
        digest.setdefault("date", episode.get("date", ""))

        log.info(
            f"解析成功：{len(digest.get('news', []))} 條新聞，"
            f"{len(digest.get('stocks', []))} 檔個股，"
            f"{len(digest.get('qa', []))} 個 Q&A"
        )
        return digest

    except json.JSONDecodeError as e:
        log.error(f"JSON 解析失敗：{e}")
        log.error(f"原始回應：{raw[:500]}")
        return None
    except Exception as e:
        log.error(f"Gemini API 錯誤：{e}")
        return None
