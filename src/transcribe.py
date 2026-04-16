"""
transcribe.py
使用 faster-whisper 進行語音轉文字（中文優化）
"""

import logging
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

# 模型選擇建議：
#   tiny   → 最快（~15min/hr），精度較低
#   base   → 平衡（~30min/hr），推薦 GitHub Actions
#   small  → 較佳（~45min/hr），建議本機 CPU 使用
#   medium → 最佳（~90min/hr），建議本機 GPU 使用
WHISPER_MODEL = "base"
LANGUAGE = "zh"  # 強制中文，避免誤判為日文


def transcribe_audio(audio_path: Path) -> Optional[str]:
    """
    轉錄音檔，回傳完整逐字稿字串
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        log.error("請安裝 faster-whisper：pip install faster-whisper")
        return None

    log.info(f"載入 Whisper 模型：{WHISPER_MODEL}")

    model = WhisperModel(
        WHISPER_MODEL,
        device="cpu",
        compute_type="int8",  # CPU 最佳化
        cpu_threads=4,
        num_workers=2,
    )

    log.info(f"開始轉錄：{audio_path}")

    try:
        segments, info = model.transcribe(
            str(audio_path),
            language=LANGUAGE,
            beam_size=5,
            vad_filter=True,            # 過濾靜音片段
            vad_parameters=dict(
                min_silence_duration_ms=500
            ),
            word_timestamps=False,
        )

        log.info(
            f"音訊長度：{info.duration:.0f}s，"
            f"偵測語言：{info.language}（信心度 {info.language_probability:.2%}）"
        )

        # 組合所有片段
        transcript_parts = []
        segment_count = 0
        for segment in segments:
            transcript_parts.append(segment.text.strip())
            segment_count += 1
            if segment_count % 100 == 0:
                log.info(f"  已處理 {segment_count} 段，時間軸：{segment.end:.0f}s")

        transcript = " ".join(transcript_parts)
        log.info(f"轉錄完成：{segment_count} 段，{len(transcript)} 字")
        return transcript

    except Exception as e:
        log.error(f"轉錄失敗：{e}")
        return None
