# 多 AI API 容錯機制使用指南

## 🎯 概述

本項目現在支持**三重容錯機制**，按以下優先順序自動嘗試不同的 AI 提供商：

```
1️⃣ Claude (Anthropic)    ← 品質最佳，推薦首選
    ↓ 失敗/未設定
2️⃣ GPT-4o-mini (OpenAI)  ← 快速穩定，成本效益高
    ↓ 失敗/未設定
3️⃣ Gemini (Google)       ← 免費方案，最後備用
    ↓ 失敗
❌ 全部失敗，返回錯誤
```

**只要其中一個成功，就會立即返回結果！**

---

## 📋 快速設置

### 方法 1：設置單一 API（最簡單）

選擇以下任一選項，複製到 `.env` 文件：

#### 選項 A：使用 Gemini（免費）
```bash
GOOGLE_API_KEY=AIzaSyD...
```
👉 獲取：https://aistudio.google.com/app/apikey

#### 選項 B：使用 Claude（推薦，品質最佳）
```bash
ANTHROPIC_API_KEY=sk-ant-...
```
👉 獲取：https://console.anthropic.com/settings/keys

#### 選項 C：使用 OpenAI（穩定可靠）
```bash
OPENAI_API_KEY=sk-proj-...
```
👉 獲取：https://platform.openai.com/api-keys

---

### 方法 2：設置多個 API（最穩定）

在 `.env` 中同時設置多個 API Key，提高可靠性：

```bash
# 推薦配置：同時設置三個
ANTHROPIC_API_KEY=sk-ant-api03-xxx
OPENAI_API_KEY=sk-proj-xxx
GOOGLE_API_KEY=AIzaSyD...
```

**優勢：**
- ✅ 任一 API 配額用盡自動切換
- ✅ 任一 API 故障不影響使用
- ✅ 最大化系統可用性

---

## 🔍 工作原理

### 容錯流程示例

**場景 1：Claude 配額用盡**
```
10:30:23 [INFO] → Trying Claude (Anthropic)...
10:30:24 [WARNING]   ❌ Claude: rate_limit_error
10:30:24 [INFO]   → Claude (Anthropic) failed, trying next provider...
10:30:24 [INFO] → Trying GPT-4o-mini (OpenAI)...
10:30:26 [INFO]   ✅ GPT-4o-mini: Success
10:30:26 [INFO] ✅ Analysis completed by GPT-4o-mini (OpenAI)
```

**場景 2：只設置 Gemini**
```
10:29:49 [INFO] → Trying Claude (Anthropic)...
10:29:49 [INFO]   ⏭️  Claude: ANTHROPIC_API_KEY not set, skipping
10:29:49 [INFO] → Trying GPT-4o-mini (OpenAI)...
10:29:49 [INFO]   ⏭️  GPT-4o-mini: OPENAI_API_KEY not set, skipping
10:29:49 [INFO] → Trying Gemini (Google)...
10:30:23 [INFO]   ✅ Gemini (gemini-2.5-flash): Success
```

---

## ⚙️ 配置選項

### `config.py` - AI 提供商設定

```python
# Claude (Anthropic) - Highest priority
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 8192

# OpenAI - Second priority
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_MAX_TOKENS = 8192

# Gemini (Google) - Fallback
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
]

# Retry settings (適用於所有提供商)
MAX_RETRIES = 3
RETRY_DELAY = 2
RETRY_MULTIPLIER = 2
```

### 關閉多提供商模式（僅使用單一 API）

如果只想使用某一個 AI，可以直接設定對應的環境變數，其他留空即可。

---

## 💰 成本比較

| 提供商 | 模型 | 輸入價格 | 輸出價格 | 免費額度 |
|--------|------|---------|---------|---------|
| **Claude** | Sonnet 4 | $3/1M tokens | $15/1M tokens | $5 免費額度 |
| **OpenAI** | GPT-4o-mini | $0.15/1M tokens | $0.6/1M tokens | $5 免費額度 |
| **Gemini** | 2.5 Flash | 免費 | 免費 | 5 RPM, 20 RPD |

**估算（單次分析約 10K 輸入 + 2K 輸出）：**
- Claude: ~$0.06 / 次
- OpenAI: ~$0.003 / 次 ⭐ 最便宜
- Gemini: 免費（有配額限制）

---

## 📊 各提供商特點

### 🥇 Claude (Anthropic)
**優點：**
- ✅ 分析品質最佳
- ✅ 理解繁體中文優秀
- ✅ 遵循指令準確

**缺點：**
- ❌ 成本較高
- ❌ 免費額度有限

**推薦場景：** 正式環境、要求高品質輸出

---

### 🥈 GPT-4o-mini (OpenAI)
**優點：**
- ✅ 速度快
- ✅ 成本低
- ✅ 穩定可靠

**缺點：**
- ⚠️ 品質略低於 Claude
- ⚠️ 偶爾會有格式錯誤

**推薦場景：** 日常測試、大量處理

---

### 🥉 Gemini (Google)
**優點：**
- ✅ 完全免費
- ✅ 配額充足（5 RPM）

**缺點：**
- ❌ 品質不穩定
- ❌ 配額限制嚴格
- ❌ 經常觸發 429 錯誤

**推薦場景：** 測試開發、預算有限

---

## 🚀 使用建議

### 1. **開發測試階段**
```bash
# 只設置 Gemini（免費）
GOOGLE_API_KEY=your_key
```

### 2. **生產環境**
```bash
# 設置 Claude + OpenAI 雙保險
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key
```

### 3. **最大穩定性**
```bash
# 三個都設置
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_gemini_key
```

---

## 🔧 故障排除

### 問題 1：所有 API 都失敗

**錯誤信息：**
```
❌ All AI providers failed
Please check:
  1. API keys are set correctly in .env
  2. API quotas are not exceeded
  3. Network connection is stable
```

**解決方案：**
1. 檢查 `.env` 文件中的 API Key 是否正確
2. 訪問對應的控制台檢查配額：
   - Claude: https://console.anthropic.com/settings/usage
   - OpenAI: https://platform.openai.com/usage
   - Gemini: https://aistudio.google.com/rate-limit
3. 確認網絡連接正常

---

### 問題 2：想強制使用特定 API

**方法 1：只設置該 API 的 Key**
```bash
# 只保留 OpenAI
OPENAI_API_KEY=sk-proj-...
# ANTHROPIC_API_KEY=  # 留空
# GOOGLE_API_KEY=      # 留空
```

**方法 2：修改 `src/analyze.py` 中的 PROVIDERS 順序**
```python
PROVIDERS = [
    ("GPT-4o-mini (OpenAI)", _try_openai),  # 移到第一位
    ("Claude (Anthropic)", _try_claude),
    ("Gemini (Google)", _try_gemini),
]
```

---

## 📈 性能優化

### 緩存機制

系統會自動緩存 API 響應，相同內容不會重複調用：

```bash
# 第一次執行：調用 AI API
10:30:23 [INFO] 📡 Sending request to Gemini...
10:30:26 [INFO] ✅ Response received
10:30:26 [INFO] 💾 Saved to cache: 265c6e6c...

# 第二次執行：從緩存讀取
10:31:15 [INFO] 💾 Loading from cache: 265c6e6c...
# 0.1 秒即返回！
```

**清除緩存：**
```bash
# Windows
Remove-Item -Recurse -Force .cache

# Linux/Mac
rm -rf .cache/
```

---

## 📝 完整示例

### 示例 1：使用 Claude 分析

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-xxx

# 運行
python test_pipeline.py --step analyze
```

**輸出：**
```
🤖 AI Analysis Fallback Chain Started
──────────────────────────────────────────────────
→ Trying Claude (Anthropic)...
  📡 Claude: Sending request (attempt 1/3)...
  ✅ Claude: Success
──────────────────────────────────────────────────
✅ Analysis completed by Claude (Anthropic)
   📊 News: 3 / Stocks: 7 / Q&A: 2
💾 Saved to cache: abc12345...
```

---

### 示例 2：容錯切換

```bash
# .env (Claude 配額用盡，自動切到 OpenAI)
ANTHROPIC_API_KEY=sk-ant-api03-xxx  # 配額已用完
OPENAI_API_KEY=sk-proj-xxx          # 有配額
```

**輸出：**
```
→ Trying Claude (Anthropic)...
  ❌ Claude: rate_limit_error
  → Claude (Anthropic) failed, trying next provider...
→ Trying GPT-4o-mini (OpenAI)...
  ✅ GPT-4o-mini: Success
✅ Analysis completed by GPT-4o-mini (OpenAI)
```

---

## 🎓 最佳實踐

1. **測試時用 Gemini**（免費）
2. **生產環境用 Claude 或 OpenAI**（品質穩定）
3. **設置多個 API Key**（最高可靠性）
4. **利用緩存**（節省成本和時間）
5. **定期檢查配額**（避免突然失敗）

---

**更新時間：** 2026-04-17  
**版本：** 3.0.0  
**狀態：** ✅ 生產就緒
