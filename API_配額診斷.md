# ⚠️ Google Gemini API 配額診斷報告

## 🔴 偵測到的問題

測試結果：
```
ERROR: gemini-2.0-flash - 429 RESOURCE_EXHAUSTED
```

**這表示：你的 Google Gemini API 已經達到當前配額限制**

---

## 📊 API 額度限制信息

根據 Google 官方文檔，Gemini API 有以下限制：

| 限制類型 | 免費層限制 |
|--------|----------|
| **每分鐘請求數** | 15 requests/minute |
| **每分鐘輸入 tokens** | 1,000,000 tokens/minute |
| **每分鐘輸出 tokens** | 30,000 tokens/minute |
| **日限額** | 每天最多 1,500 request |

⚠️ 如果超過這些限制，會返回 **429 RESOURCE_EXHAUSTED** 錯誤

---

## ✅ 解決方案

### 方案 1：等待限制重置（推薦）
- **時間**：等待 1–60 分鐘後重試（取決於限制類型）
- **成本**：免費，但需要等待
- **適用**：短期測試

### 方案 2：升級到付費層
1. 前往 [Google Cloud Console](https://console.cloud.google.com)
2. 進入 **Billing** → **Upgrade Account**
3. 設定信用卡信息
4. 配額限制會自動提升

**費用**：
- 免費額度：每月前 10,000 個 request（gemini-2.0-flash）
- 超出部分：約 $0.075 per 1M input tokens（非常便宜）

### 方案 3：控制請求頻率
修改 `src/analyze.py`，添加延遲和重試機制：

```python
import time
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(3)
)
def analyze_transcript(transcript: str, episode: dict):
    # ... existing code ...
    time.sleep(2)  # 請求前等待 2 秒
```

---

## 🔍 檢查 API 配額使用情況

1. 前往 [Google Cloud Console](https://console.cloud.google.com)
2. 選擇正確的 **Project**
3. 進入 **APIs & Services** → **Quotas**
4. 搜尋 **"Generative Language API"**
5. 查看當前的 usage 百分比

---

## 🚀 立即要做的事

1. **現在**：等待 5–10 分鐘讓額度重置
2. **然後**：再執行一次測試
   ```bash
   python test_api_key.py
   ```

3. **如果還是失敗**：考慮升級到付費層或聯絡 Google Support

---

## 💡 預防措施

### 為生產環境設定最佳實踐

1. **添加延遲**
   ```python
   import time
   time.sleep(2)  # 每個請求間隔 2 秒
   ```

2. **設定重試機制**
   ```bash
   pip install tenacity
   ```

3. **監控 API 使用量**
   - 定期檢查 Google Cloud Console 的 quotas
   - 設定 alerts（當達到 80% 配額時通知）

4. **緩存結果**
   - 保存已分析的結果到 `test_digest.json`
   - 避免重複分析同一集

---

## 📝 相關文件

- 📖 [Google Gemini API 官方文檔](https://ai.google.dev/docs)
- 💰 [Google Cloud 定價](https://cloud.google.com/generative-ai/pricing)
- ⚙️ [配額和限制](https://cloud.google.com/docs/quotas)

---

**更新時間**：2026-04-17  
**API 版本**：google-genai 0.1.73+
