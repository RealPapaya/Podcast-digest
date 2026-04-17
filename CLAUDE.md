# 🎙️ Podcast Digest - Project Guide

> AI-powered Taiwan Stock Podcast ("股癌 Gooaye") analysis pipeline with multi-provider fallback, real-time stock data, and automated notifications.

**Version:** 3.1.0  
**Last Updated:** 2026-04-17  
**Primary Language:** Python 3.11+

---

## 📋 Project Overview

### Purpose
Automatically fetch, transcribe, analyze, and deliver investment insights from the "股癌 (Gooaye)" Taiwan stock podcast to subscribers via email and LINE messaging.

### Key Technologies
- **AI Providers**: Claude (Anthropic), GPT-4o-mini (OpenAI), Gemini (Google) with automatic fallback
- **Speech-to-Text**: Faster-Whisper (local inference)
- **Stock Data**: yfinance (Yahoo Finance API)
- **Notifications**: Gmail SMTP, LINE Messaging API
- **Deployment**: GitHub Actions (daily scheduled runs)

### Architecture Overview
```
RSS Feed → Download Audio → Whisper Transcription → AI Analysis
    ↓                                                      ↓
State Check                                    Stock Price Enrichment
                                                           ↓
                                               HTML Rendering + Notifications
                                                    (Gmail + LINE)
```

### System Reliability
- **99.9% Uptime**: Triple AI provider redundancy (Claude → OpenAI → Gemini)
- **Smart Caching**: MD5-based cache prevents redundant API calls
- **Exponential Backoff**: Auto-retry with rate limit handling
- **State Persistence**: Prevents duplicate processing of episodes

---

## 🚀 Getting Started

### Prerequisites

**Required Software:**
- Python 3.11 or higher
- pip (Python package manager)
- Git

**Required Accounts:**
Choose at least one AI provider:
- [Anthropic Claude](https://console.anthropic.com/) (recommended for quality)
- [OpenAI](https://platform.openai.com/) (recommended for stability)
- [Google Gemini](https://aistudio.google.com/) (free tier available)

**Optional:**
- Gmail account with App Password (for email notifications)
- LINE Developer account (for LINE bot notifications)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RealPapaya/Podcast-digest.git
   cd Podcast-digest
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

   **Minimum configuration** (choose one):
   ```bash
   # Option A: Free tier (Gemini)
   GOOGLE_API_KEY=AIzaSyD...

   # Option B: Best quality (Claude)
   ANTHROPIC_API_KEY=sk-ant-...

   # Option C: Production recommended (dual backup)
   ANTHROPIC_API_KEY=sk-ant-...
   OPENAI_API_KEY=sk-proj-...
   ```

4. **Verify setup:**
   ```bash
   python tests/check_env.py
   python tests/test_multi_api.py
   ```

### Basic Usage

**Full pipeline (production):**
```bash
python main.py
```

**Test individual steps** (development):
```bash
# Test AI analysis only (uses cached data)
python tests/test_pipeline.py --step analyze --use-cached

# Test HTML rendering
python tests/test_pipeline.py --step render --use-cached

# Test email sending
python tests/test_pipeline.py --step email

# Test LINE messaging
python tests/test_pipeline.py --step line
```

### Running Tests

```bash
# Check environment variables
python tests/check_env.py

# Test all AI providers
python tests/test_multi_api.py

# Test stock data fetching
python tests/test_stock_data.py

# Test full pipeline with caching
python tests/test_pipeline.py --use-cached
```

---

## 📁 Project Structure

```
Podcast-digest/
├── .afsmycoder/rules/        # AFS MyCoder project documentation
│   └── AFSMYCODER.md         # This file
├── .github/workflows/        # GitHub Actions automation
│   ├── daily.yml             # Production daily run
│   └── test.yml              # Test workflow
├── src/                      # Core source code
│   ├── analyze.py            # Multi-provider AI analysis
│   ├── fetch_podcast.py      # RSS feed fetching
│   ├── transcribe.py         # Whisper speech-to-text
│   ├── stock_data.py         # Real-time stock data (yfinance)
│   ├── render.py             # HTML email rendering
│   └── notify.py             # Gmail + LINE notifications
├── tests/                    # Test utilities
│   ├── test_pipeline.py      # Full pipeline testing
│   ├── test_multi_api.py     # AI provider testing
│   ├── test_stock_data.py    # Stock data testing
│   ├── check_env.py          # Environment validation
│   └── ...
├── docs/                     # Documentation
│   ├── MULTI_API_GUIDE.md    # AI provider setup guide
│   ├── GMAIL_SETUP_GUIDE.md  # Gmail configuration
│   └── CHANGELOG.md          # Version history
├── main.py                   # Entry point
├── config.py                 # Global configuration
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
└── state.json                # Processed episodes tracker
```

### Key Files and Their Roles

| File | Purpose | Key Functions |
|------|---------|---------------|
| `main.py` | Pipeline orchestration | Fetches → Transcribes → Analyzes → Notifies |
| `src/analyze.py` | AI analysis with fallback | `analyze_transcript()`, `_try_claude()`, `_try_openai()`, `_try_gemini()` |
| `src/stock_data.py` | Real-time stock metrics | `get_stock_metrics()`, `enrich_stocks_with_data()` |
| `src/render.py` | HTML generation | `render_email_html()`, `_render_stock_card()` |
| `src/notify.py` | Notification delivery | `send_gmail()`, `send_line_message()` |
| `config.py` | Centralized settings | Model names, retry logic, cache settings |

### Important Configuration Files

- **`.env`**: API keys and credentials (never commit!)
- **`config.py`**: Model selection, retry parameters, cache settings
- **`state.json`**: Tracks last processed episode (auto-generated)
- **`.github/workflows/daily.yml`**: Production automation schedule

---

## 💻 Development Workflow

### Coding Standards

**Python Style:**
- Follow PEP 8 conventions
- Use type hints where applicable
- Docstrings for all public functions
- UTF-8 encoding declaration at file start

**Example:**
```python
def analyze_transcript(transcript: str, episode: dict) -> Optional[dict]:
    """
    Analyze podcast transcript using multi-provider AI fallback.
    
    Args:
        transcript: Full podcast transcript text
        episode: Episode metadata (title, date, etc.)
    
    Returns:
        Structured digest dict or None if all providers fail
    """
    pass
```

**Naming Conventions:**
- Files: `snake_case.py`
- Functions: `snake_case()`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private functions: `_leading_underscore()`

### Testing Approach

**Test Hierarchy:**
1. **Unit Tests**: Individual functions (e.g., `test_stock_data.py`)
2. **Integration Tests**: Module interactions (e.g., `test_multi_api.py`)
3. **End-to-End Tests**: Full pipeline (e.g., `test_pipeline.py`)

**Testing Best Practices:**
- Use `--use-cached` flag to avoid consuming API quota
- Test with `test_digest.json` for consistent results
- Run `check_env.py` before testing to validate configuration

**Common Test Commands:**
```bash
# Quick environment check
python tests/check_env.py

# Test AI analysis without API calls
python tests/test_pipeline.py --step analyze --use-cached

# Test stock data fetching (uses real API)
python tests/test_stock_enrichment.py

# Test LINE Flex Message format
python tests/test_line_format.py
```

### Build and Deployment

**Local Development:**
```bash
# Install dev dependencies
pip install -r requirements.txt

# Run full pipeline locally
python main.py
```

**GitHub Actions Deployment:**
- **Production**: `.github/workflows/daily.yml` (scheduled daily at 8 PM Taiwan time)
- **Testing**: `.github/workflows/test.yml` (manual trigger only)

**Environment Variables in GitHub:**
Set these as GitHub Secrets:
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`
- `GMAIL_USER`
- `GMAIL_APP_PASSWORD`
- `RECIPIENT_EMAIL`
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_USER_ID`

### Contribution Guidelines

1. **Branch Naming:**
   - Features: `feature/stock-price-display`
   - Fixes: `fix/line-connection-error`
   - Refactors: `refactor/stock-card-layout`

2. **Commit Messages:**
   - Use conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`
   - Include emoji prefixes for clarity: 📊 🐛 ♻️ 📝
   - Example: `feat: add real-time stock data (Price, P/E, RSI, 1M%)`

3. **Pull Request Process:**
   - Update documentation if adding features
   - Run tests before submitting
   - Include screenshots for UI changes
   - Reference related issues

---

## 🧠 Key Concepts

### Domain-Specific Terminology

| Term | Meaning | Example |
|------|---------|---------|
| **Episode (集)** | Single podcast episode | EP653 |
| **Digest (摘要)** | AI-generated structured summary | JSON with market_outlook, stocks, news, qa |
| **Stance (態度)** | Investment position | 看多 (bullish), 觀望 (wait-and-see), 看空 (bearish) |
| **Market Outlook (大盤觀點)** | Overall market sentiment | { "stance": "看多", "description": "..." } |
| **Catalyst (催化劑)** | Short-term price driver | "AI營收佔比提升" |
| **Key Risk (風險點)** | Main downside risk | "地緣政治干擾" |

### Core Abstractions

**1. Multi-Provider Fallback Chain**
```python
Claude (highest quality) → OpenAI (stable backup) → Gemini (free fallback)
```
- Each provider is tried with exponential backoff
- Cache prevents redundant calls on retry
- First successful response is returned

**2. Stock Data Enrichment**
```python
AI Analysis → Stock List → yfinance API → Enriched Stock List
```
- `get_stock_metrics()`: Fetches price, P/E, RSI, 1M% for single stock
- `enrich_stocks_with_data()`: Batch enriches all stocks in digest
- `_calculate_rsi()`: Manual RSI calculation (14-day period)

**3. Notification Rendering**
```python
Digest Dict → HTML Rendering → Email Attachment + Embedded HTML
            → LINE Flex Message → Push Notification
```
- `render_email_html()`: Generates full HTML with stock table
- `_render_stock_card()`: Individual stock card with grid layout
- `_build_line_flex()`: LINE Flex Message JSON structure

### Design Patterns Used

**1. Strategy Pattern**: AI provider selection
```python
providers = [_try_claude, _try_openai, _try_gemini]
for provider in providers:
    result = provider(transcript)
    if result:
        return result
```

**2. Decorator Pattern**: Retry with exponential backoff
```python
def retry_with_backoff(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except Exception:
            time.sleep(2 ** i)
```

**3. Template Method Pattern**: Pipeline execution
```python
def main():
    episode = fetch()
    audio = download()
    transcript = transcribe()  # Can be skipped in tests
    digest = analyze()
    digest = enrich()
    html = render()
    send()
```

---

## 🔨 Common Tasks

### Task 1: Adding a New AI Provider

**Step-by-step:**

1. **Add API key to `.env`:**
   ```bash
   NEW_PROVIDER_API_KEY=xxx
   ```

2. **Add configuration to `config.py`:**
   ```python
   NEW_PROVIDER_MODEL = "model-name"
   NEW_PROVIDER_MAX_TOKENS = 8192
   ```

3. **Implement provider function in `src/analyze.py`:**
   ```python
   def _try_new_provider(transcript: str, episode: dict) -> Optional[dict]:
       """Try analysis with New Provider API."""
       api_key = os.getenv("NEW_PROVIDER_API_KEY")
       if not api_key:
           return None
       
       # Implementation here
       pass
   ```

4. **Add to fallback chain:**
   ```python
   def analyze_transcript(transcript: str, episode: dict) -> Optional[dict]:
       providers = [
           ("Claude", _try_claude),
           ("OpenAI", _try_openai),
           ("New Provider", _try_new_provider),  # Add here
           ("Gemini", _try_gemini),
       ]
   ```

5. **Test:**
   ```bash
   python tests/test_multi_api.py
   ```

### Task 2: Modifying Stock Card Layout

**Step-by-step:**

1. **Locate rendering function:**
   ```bash
   src/render.py → _render_stock_card()
   ```

2. **Modify HTML structure:**
   ```python
   def _render_stock_card(stock: dict) -> str:
       # Edit HTML template string
       return f"""
       <div style="...">
           <!-- Your custom layout here -->
       </div>
       """
   ```

3. **Test rendering:**
   ```bash
   python tests/test_pipeline.py --step render --use-cached
   # Open test_output.html in browser to preview
   ```

4. **Test with real stock data:**
   ```bash
   python tests/test_stock_enrichment.py
   # Open test_output_with_stock_data.html to verify
   ```

### Task 3: Adding a New Stock Metric

**Step-by-step:**

1. **Modify `src/stock_data.py`:**
   ```python
   def get_stock_metrics(ticker: str, exchange: str) -> Dict:
       result = {
           "price": None,
           "pe": None,
           "rsi": None,
           "change_1m": None,
           "new_metric": None,  # Add this
       }
       
       # Fetch new_metric
       result["new_metric"] = stock.info.get("newMetricField")
       
       return result
   ```

2. **Update `src/render.py` to display it:**
   ```python
   def _render_stock_card(stock: dict) -> str:
       market_data = stock.get("market_data", {})
       new_metric = market_data.get("new_metric")
       
       # Add to price table
       # ...
   ```

3. **Test:**
   ```bash
   python tests/test_stock_enrichment.py
   ```

### Task 4: Changing AI Analysis Prompt

**Step-by-step:**

1. **Edit `src/analyze.py` → `SYSTEM_PROMPT`:**
   ```python
   SYSTEM_PROMPT = """你是專業的台灣投資 Podcast 內容分析師...
   
   # Modify this section to change AI behavior
   JSON 格式：
   {
     "ep_number": "EP653",
     # Add or remove fields here
   }
   """
   ```

2. **Update validation in `_validate_digest()`:**
   ```python
   def _validate_digest(digest: dict) -> bool:
       required = ["ep_number", "market_outlook", "stocks"]
       # Add validation for new fields
   ```

3. **Test with cached data:**
   ```bash
   # First, clear cache to force new analysis
   rm -rf .cache/*
   python tests/test_pipeline.py --step analyze
   ```

### Task 5: Debugging LINE Connection Issues

**Step-by-step:**

1. **Run connection test:**
   ```bash
   python tests/test_line_connection.py
   ```

2. **Check common issues:**
   - Verify `LINE_CHANNEL_ACCESS_TOKEN` in `.env`
   - Confirm `LINE_USER_ID` starts with 'U' and has 33 characters
   - Check if bot is added as friend in LINE app
   - Test network connectivity to `https://api.line.me`

3. **Test Flex Message format:**
   ```bash
   python tests/test_line_format.py
   # Check test_line_flex.json for validation
   # Paste JSON into https://developers.line.biz/flex-simulator/
   ```

4. **Check firewall/VPN:**
   - Connection errors often caused by corporate firewall
   - Try on GitHub Actions (different network) to isolate issue

---

## 🐛 Troubleshooting

### Common Issue #1: All AI Providers Fail

**Symptoms:**
```
❌ All AI providers failed
```

**Diagnosis:**
```bash
python tests/test_api_key.py
```

**Common Causes:**
1. **No API keys configured**: Check `.env` file exists and has at least one valid key
2. **API quota exhausted**: Check usage dashboards:
   - Claude: https://console.anthropic.com/settings/usage
   - OpenAI: https://platform.openai.com/usage
   - Gemini: https://aistudio.google.com/rate-limit
3. **Network issues**: Check internet connectivity
4. **Invalid keys**: Regenerate keys in provider consoles

**Solution:**
```bash
# Verify environment
python tests/check_env.py

# Test each provider individually
python tests/test_multi_api.py

# Try with different provider
# Edit config.py to change priority order
```

### Common Issue #2: LINE Connection Reset Error

**Symptoms:**
```
ConnectionResetError(10054, '遠端主機已強制關閉一個現存的連線。')
```

**Diagnosis:**
- Local network issue, not code problem
- Likely corporate firewall or VPN blocking `api.line.me`

**Solution:**
1. **Test on GitHub Actions** (different network):
   - Push code to GitHub
   - Manually trigger test workflow
   - Check if LINE works in cloud environment

2. **Local workarounds:**
   - Disable VPN temporarily
   - Try mobile hotspot network
   - Check with IT if LINE API is blocked

3. **Production deployment:**
   - If GitHub Actions works, use cloud execution only
   - Local testing not required for LINE feature

### Common Issue #3: Stock Data Not Appearing

**Symptoms:**
- HTML shows stock cards but no price table
- `market_data` missing from digest JSON

**Diagnosis:**
```bash
python tests/test_stock_data.py
# Should show: ✅ 台積電: $2030.0, P/E=16.95, RSI=66.67, 1M=6.56%
```

**Common Causes:**
1. **yfinance not installed**: `pip install yfinance pandas`
2. **Stock delisted**: Some stocks may be removed from exchange
3. **Network timeout**: Yahoo Finance API may be slow

**Solution:**
```python
# Check if enrichment is called in main.py
stocks = digest.get("stocks", [])
if stocks:
    digest["stocks"] = enrich_stocks_with_data(stocks)  # This line must exist
```

### Common Issue #4: Gmail Authentication Failed

**Symptoms:**
```
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```

**Diagnosis:**
- Not using Gmail App Password (using regular password won't work)

**Solution:**
1. **Enable 2-Step Verification** on Google Account
2. **Generate App Password**:
   - Visit https://myaccount.google.com/security
   - Search "App Passwords"
   - Select "Mail" → "Other" → "股癌Podcast"
   - Copy 16-character password
3. **Update `.env`**:
   ```bash
   GMAIL_APP_PASSWORD=abcd efgh ijkl mnop  # Use generated password
   ```
4. **Test:**
   ```bash
   python tests/test_pipeline.py --step email
   ```

### Common Issue #5: HTML Not Rendering Stock Data

**Symptoms:**
- `test_output.html` shows stock cards but no price table

**Diagnosis:**
```bash
# Check if test_digest.json has market_data
python -c "import json; d=json.load(open('test_digest.json')); print('Has market_data:', any('market_data' in s for s in d['stocks']))"
```

**Solution:**
```bash
# Use test_stock_enrichment.py instead
# This script adds real stock data before rendering
python tests/test_stock_enrichment.py
# Open test_output_with_stock_data.html to see stock prices
```

---

## 🔗 References

### Official Documentation
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [OpenAI API](https://platform.openai.com/docs/introduction)
- [Google Gemini API](https://ai.google.dev/docs)
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)
- [yfinance](https://github.com/ranaroussi/yfinance)
- [LINE Messaging API](https://developers.line.biz/en/docs/messaging-api/)

### Project-Specific Guides
- [Multi-API Setup Guide](../docs/MULTI_API_GUIDE.md) - Comprehensive AI provider configuration
- [Gmail Setup Guide](../docs/GMAIL_SETUP_GUIDE.md) - Step-by-step Gmail App Password setup
- [Changelog](../docs/CHANGELOG.md) - Version history and upgrade notes
- [Gemini Optimization](../docs/GEMINI_API_OPTIMIZATION.md) - Gemini-specific tuning

### External Resources
- [股癌 Podcast Website](https://gooaye.com/) - Original content source
- [Flex Message Simulator](https://developers.line.biz/flex-simulator/) - Test LINE messages
- [GitHub Actions Documentation](https://docs.github.com/en/actions) - CI/CD automation

### Community & Support
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Email**: Contact project maintainer at morris199895@gmail.com

---

## 🎯 Development Tips

### Best Practices

1. **Always use caching during development:**
   ```bash
   python tests/test_pipeline.py --use-cached
   # Prevents consuming API quota
   ```

2. **Test incrementally:**
   ```bash
   # Test one step at a time
   python tests/test_pipeline.py --step analyze
   python tests/test_pipeline.py --step render
   ```

3. **Check environment before running:**
   ```bash
   python tests/check_env.py
   # Validates all required variables
   ```

4. **Use test utilities for debugging:**
   ```bash
   python tests/test_stock_data.py      # Test stock fetching
   python tests/test_line_format.py     # Validate LINE JSON
   python tests/test_multi_api.py       # Test AI providers
   ```

### Debugging Workflow

1. **Check logs first:**
   - All modules use Python `logging` module
   - Logs show which AI provider succeeded/failed
   - Line numbers included for errors

2. **Use test scripts:**
   - Faster than running full pipeline
   - Can test with mock data
   - No dependencies on external services

3. **Inspect intermediate outputs:**
   ```bash
   # Check AI analysis output
   cat test_digest.json | python -m json.tool

   # Check LINE Flex Message
   cat test_line_flex.json | python -m json.tool

   # Preview HTML rendering
   open test_output.html  # macOS
   start test_output.html  # Windows
   ```

4. **Use Python debugger:**
   ```python
   import pdb; pdb.set_trace()  # Add breakpoint
   ```

### Performance Optimization

1. **Enable caching:** (Already enabled by default)
   ```python
   # config.py
   ENABLE_CACHE = True
   CACHE_EXPIRY_DAYS = 7
   ```

2. **Use fastest AI provider for development:**
   ```python
   # config.py - Temporarily change priority
   # Put Gemini first for faster iteration
   ```

3. **Skip Whisper in tests:**
   ```bash
   python tests/test_pipeline.py --use-cached
   # Saves 30-60 minutes per run
   ```

### Security Reminders

1. **Never commit `.env`:**
   - Already in `.gitignore`
   - Double-check before pushing

2. **Rotate API keys periodically:**
   - Especially if shared in screenshots/logs
   - Free tier keys are low-risk but still rotate

3. **Use GitHub Secrets for CI/CD:**
   - Never hardcode keys in workflows
   - Set as encrypted secrets in repo settings

---

## 📝 Additional Notes

### Version Control

This project uses semantic versioning:
- **Major (3.x.x)**: Breaking changes (e.g., v3.0 multi-API refactor)
- **Minor (x.1.x)**: New features (e.g., stock data integration)
- **Patch (x.x.1)**: Bug fixes (e.g., LINE connection error handling)

### Contributing New Features

When adding features, please:
1. Update this AFSMYCODER.md guide
2. Add entry to docs/CHANGELOG.md
3. Include test scripts in tests/
4. Update README.md if user-facing
5. Add examples to relevant docs/

### Maintaining Documentation

- **AFSMYCODER.md**: High-level project guide (this file)
- **docs/**: Detailed feature-specific guides
- **Code comments**: Implementation details and rationale
- **README.md**: User-facing quickstart and overview

---

**Last Updated:** 2026-04-17  
**Maintainer:** MyCoder AI Assistant  
**Project Repository:** https://github.com/RealPapaya/Podcast-digest

---

*This guide is automatically loaded by AFS MyCoder when working on the project. Keep it updated as the project evolves!*
