# -*- coding: utf-8 -*-
"""
Configuration for Podcast Digest Pipeline
"""

# ═══════════════════════════════════════════════════════════════
# AI Provider Settings (Fallback Chain)
# Priority: Claude → OpenAI → Gemini
# ═══════════════════════════════════════════════════════════════

# Claude (Anthropic) - Highest priority
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # Latest Sonnet model
CLAUDE_MAX_TOKENS = 8192

# OpenAI - Second priority
OPENAI_MODEL = "gpt-4o-mini"  # Fast and cost-effective
OPENAI_MAX_TOKENS = 8192

# Gemini (Google) - Fallback, multiple models
GEMINI_MODELS = [
    "gemini-2.5-flash",          # Latest, fast, free tier: 5 RPM, 250K TPM
    "gemini-2.5-pro",            # Best quality (check your quota first)
    "gemini-2.0-flash",          # Fallback option
]

# API retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
RETRY_MULTIPLIER = 2  # exponential backoff

# Rate limiting
REQUESTS_PER_MINUTE = 10  # Conservative limit for free tier
MIN_REQUEST_INTERVAL = 60 / REQUESTS_PER_MINUTE  # 6 seconds

# Cache settings
ENABLE_CACHE = True
CACHE_DIR = ".cache"
CACHE_EXPIRY_DAYS = 7

# Transcript processing
MAX_TRANSCRIPT_CHARS = 800_000  # Conservative limit for free tier

# Gemini API generation config
GENERATION_CONFIG = {
    "temperature": 0.1,
    "max_output_tokens": 8192,  # Increased for complete JSON response
    "top_p": 0.95,
}

# AI Provider Fallback Chain
# Set to True to enable multi-provider fallback
ENABLE_MULTI_PROVIDER = True

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"
