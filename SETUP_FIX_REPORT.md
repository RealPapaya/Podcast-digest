# 🔧 Google Gemini SDK 更新修復報告

## 📋 更新摘要

你的項目已成功從舊版 `google-generativeai` SDK 遷移到新版 `google-genai` SDK。

---

## ✅ 已完成的修復

### 1. **SDK 更新**
- ❌ 舊版本：`google.generativeai` 
- ✅ 新版本：`google.genai`
- **檔案修改**：`requirements.txt`

### 2. **API 呼叫更新**
- **檔案修改**：`src/analyze.py`
- **主要改變**：
  ```python
  # 舊寫法
  import google.generativeai as genai
  genai.configure(api_key=api_key)
  model = genai.GenerativeModel('gemini-1.5-flash')
  response = model.generate_content(
      user_message,
      generation_config=genai.types.GenerationConfig(...)
  )
  
  # 新寫法
  from google import genai
  client = genai.Client(api_key=api_key)
  response = client.models.generate_content(
      model="gemini-1.5-flash",
      contents=user_message,
      config={...}
  )
  ```

### 3. **環境變數修正**
- **檔案修改**：`.env`
- **修正內容**：
  - 新增 `GMAIL_USER` 變數（原本缺少）
  - 改正 `LINE_ACCESS_TOKEN` → `LINE_CHANNEL_ACCESS_TOKEN`

### 4. **新增測試工具**
- **新檔案**：`test_api_key.py`
- **功能**：驗證所有 API 金鑰和環境變數設定是否正確

---

## 🚀 接下來要做什麼

### 第 1 步：設定 API 金鑰

#### 1a. Google Gemini API 金鑰
1. 前往 https://aistudio.google.com/app/apikey
2. 點「**Create API Key**」
3. 複製金鑰
4. 編輯 `.env` 檔案，將 `GOOGLE_API_KEY=your_google_api_key_here` 改成實際金鑰

#### 1b. Gmail 設定（可選，但推薦）
1. Google 帳號 → 安全性設定 → [啟用兩步驟驗證](https://support.google.com/accounts/answer/185839)
2. 搜尋「**應用程式密碼**」→ 建立新密碼
3. 編輯 `.env`：
   ```
   GMAIL_USER=your.email@gmail.com
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

#### 1c. LINE Bot 設定（可選，但推薦）
1. 前往 https://developers.line.biz
2. 建立新的 Provider → 建立 **Messaging API** Channel
3. 在 Channel 設定中點「**Issue channel access token**」
4. 取得 User ID（詳見 README 第 49–58 行）
5. 編輯 `.env`：
   ```
   LINE_CHANNEL_ACCESS_TOKEN=eyJhbGci...
   LINE_USER_ID=Uxxxxxxxx...
   ```

### 第 2 步：本地測試

```bash
# 測試所有 API 金鑰是否有效
python test_api_key.py

# 如果上面通過，測試完整流程（需要 Google API 金鑰）
python test_pipeline.py --step analyze
```

### 第 3 步：設定 GitHub Actions（可選）

如果要自動執行：

1. Fork 這個 Repo 到你的 GitHub 帳號
2. 進入 **Settings** → **Secrets and variables** → **Actions**
3. 新增以下 Secrets：
   | 名稱 | 值 |
   |------|-----|
   | `GOOGLE_API_KEY` | 你的 Gemini API 金鑰 |
   | `GMAIL_USER` | 你的 Gmail 帳號 |
   | `GMAIL_APP_PASSWORD` | Gmail 應用程式密碼 |
   | `RECIPIENT_EMAIL` | 收件信箱 |
   | `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot Token |
   | `LINE_USER_ID` | 你的 LINE User ID |

4. 進入 **Settings** → **Actions** → **General** → 確認：
   - ☑️ **Allow all actions**
   - ☑️ **Read and write permissions**

5. 在 **Actions** 標籤 → 點 **🧪 測試 Pipeline（跳過轉錄）** → **Run workflow**

---

## 🐛 故障排除

### 問題：「缺少環境變數：GOOGLE_API_KEY」

**原因**：
- `.env` 檔案中的 API 金鑰仍是佔位符（`your_google_api_key_here`）
- GitHub Actions 的 Secret 未設定

**解決**：
1. 檢查 `.env` 中是否有實際的金鑰（不是佔位符）
2. 確認 GitHub Secrets 中已新增 `GOOGLE_API_KEY`

### 問題：「Gemini API 錯誤」

可能原因：
1. API 金鑰無效或已過期 → 重新生成
2. API 配額用盡 → 檢查 [Google Console](https://console.cloud.google.com)
3. 網路連線問題 → 檢查防火牆設定

### 問題：Email 發送失敗

確認：
1. ☑️ 已開啟 Gmail 兩步驟驗證
2. ☑️ 使用的是**應用程式密碼**（16 位），不是登入密碼
3. ☑️ Gmail 帳號允許「安全性較低的應用程式」（新版 Gmail 用應用程式密碼代替）

### 問題：LINE 訊息發送失敗

確認：
1. ☑️ 已取得 **Long-lived channel access token**（不是舊的 Bot 金鑰）
2. ☑️ User ID 以 `U` 開頭（例：`Uxxxxxxxxxxxxxxxx`）
3. ☑️ 已在 LINE 上加這個機器人為好友

---

## 📚 相關文件

- 📖 [README.md](./README.md) - 完整使用說明
- 🧪 [test_pipeline.py](./test_pipeline.py) - 詳細的測試流程
- 📝 [test_api_key.py](./test_api_key.py) - 快速驗證 API 設定

---

## 📊 檔案更動清單

| 檔案 | 修改內容 |
|------|---------|
| `src/analyze.py` | 更新為新版 Gemini SDK API 呼叫 |
| `requirements.txt` | `google-generativeai` → `google-genai` |
| `.env` | 新增 `GMAIL_USER`，修正 `LINE_ACCESS_TOKEN` |
| `test_api_key.py` | ✨ 新檔案 - API 金鑰驗證工具 |

---

## ✨ 接下來的建議

1. **立即測試**：執行 `python test_api_key.py` 驗證設定
2. **本地測試**：執行 `python test_pipeline.py` 測試完整流程
3. **GitHub Actions**：設定 Secrets 並手動觸發 workflow
4. **監控運行**：檢查日誌確保每日自動執行正常

---

**更新完成於** 2026-04-17  
**SDK 版本**: google-genai 0.1.0+
