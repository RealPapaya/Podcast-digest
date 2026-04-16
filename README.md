# 股癌 AI 每日投資筆記 🎙️

自動抓取「股癌 Gooaye」Podcast，用 AI 整理成結構化投資筆記，每天自動寄送到 Email 和 LINE。

---

## 成品預覽

每天自動產生以下四個區塊：

| 區塊 | 內容 |
|------|------|
| 📝 本集導讀 | 本集主要議題摘要 |
| 🎙️ 大盤觀點 | 看多 / 看空 / 觀望，附說明 |
| 📰 今日新聞 | 3–6 條新聞事件 + 主持人觀點 |
| 📊 主題/標的觀點 | 個股觀點、風險等級 |
| 💡 Q&A 心法 | 投資問答精華 |

---

## 快速開始（5 步驟）

### 步驟 1：Fork 這個 Repo

點 GitHub 右上角 **Fork** 按鈕，複製到你自己的帳號。

---

### 步驟 2：取得 API Keys

#### 🔑 Google Gemini API Key
1. 前往 https://aistudio.google.com/app/apikey
2. 建立新的 API Key
3. 複製金鑰

#### 📧 Gmail 應用程式密碼
1. Google 帳號 → 安全性 → 兩步驟驗證（需先開啟）
2. 搜尋「應用程式密碼」→ 建立新密碼
3. 複製 16 位密碼（格式：`xxxx xxxx xxxx xxxx`）

> ⚠️ 注意：是**應用程式密碼**，不是你的 Gmail 登入密碼

#### 📱 LINE Bot 設定
LINE Notify 已於 2025/4 停服，需改用 LINE Messaging API：

1. 前往 https://developers.line.biz → 建立 Provider
2. 建立 **Messaging API** Channel
3. 進入 Channel → **Messaging API** 分頁 → Issue **Long-lived channel access token**
4. 取得你的 LINE User ID：
   - 在 https://developers.line.biz/console 開啟 Channel
   - 用 LINE 掃描 Channel 的 QR Code，加好友
   - 傳送任何訊息給機器人
   - 在 Webhook 或使用下面的 curl 指令取得 User ID：
   ```bash
   curl -X GET "https://api.line.me/v2/bot/followers/ids" \
     -H "Authorization: Bearer YOUR_CHANNEL_ACCESS_TOKEN"
   ```
   - 從回傳的 `userIds` 陣列取得你的 ID

---

### 步驟 3：本地環境設定（選用）

如果你想在本機測試，而非使用 GitHub Actions：

1. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```

2. 建立 `.env` 檔案，填入你的 API Keys：
   ```bash
   cp .env.example .env  # 或手動建立
   # 編輯 .env 檔案，填入實際的金鑰
   ```

3. 執行腳本：
   ```bash
   python main.py
   ```

---

### 步驟 4：設定 GitHub Secrets

在你 Fork 的 Repo → Settings → Secrets and variables → Actions → **New repository secret**

| Secret 名稱 | 說明 | 範例 |
|-------------|------|------|
| `GOOGLE_API_KEY` | Google Gemini API 金鑰 | `AIzaSyD...` |
| `GMAIL_USER` | 你的 Gmail 帳號 | `yourname@gmail.com` |
| `GMAIL_APP_PASSWORD` | Gmail 應用程式密碼 | `abcd efgh ijkl mnop` |
| `RECIPIENT_EMAIL` | 收件 Email（可填自己） | `yourname@gmail.com` |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot Token | `eyJhbGciOiJIUzI1...` |
| `LINE_USER_ID` | 你的 LINE User ID | `Uxxxxxxxxxxxxxxxx` |

---

### 步驟 4：開啟 GitHub Actions 權限

Repo → Settings → Actions → General → 確認：
- **Allow all actions** ✅
- **Read and write permissions** ✅（讓 Actions 能更新 state.json）

---

### 步驟 5：手動測試

Repo → Actions → 股癌 AI 每日投資筆記 → **Run workflow**

觀察 log，確認：
- 成功下載音檔
- Whisper 轉錄完成（約 30–60 分鐘）
- Gemini 分析完成
- Email 和 LINE 收到筆記

之後每天 **台灣時間早上 10:00** 自動執行。

---

## 常見問題

### Q：Whisper 轉錄多久？
在 GitHub Actions（2-core CPU）上：
- `tiny` 模型：~15 分鐘（精度較低）
- `base` 模型：~30 分鐘（**預設，推薦**）
- `small` 模型：~60 分鐘（更好但較慢）

可在 `src/transcribe.py` 修改 `WHISPER_MODEL` 變數。

### Q：要付費嗎？
- **GitHub Actions**：免費（每月 2000 分鐘）。每次執行約 30–60 分鐘，一個月 30 集約需 900–1800 分鐘。
- **Google Gemini API**：每次分析約 $0.001–0.005 USD（使用 gemini-1.5-flash），每月約 $0.03–0.15 USD。
- **LINE Bot**：免費（每月 200 則推播訊息）。
- **Gmail**：免費。

### Q：如果當天沒有新集，會怎樣？
程式會比對上次處理的 GUID，若相同則自動跳過，不重複發送。

### Q：可以接收多個 Email / LINE 嗎？
目前 `RECIPIENT_EMAIL` 只支援單一收件人。可在 `src/notify.py` 的 `send_gmail` 函數改為多個收件人。

### Q：如何修改發送時間？
編輯 `.github/workflows/daily.yml`，修改 cron 設定：
```yaml
# 格式：分 時 日 月 星期（UTC 時間）
# 台灣時間 = UTC + 8
- cron: "0 2 * * *"    # UTC 02:00 = 台灣 10:00
- cron: "0 1 * * *"    # UTC 01:00 = 台灣 09:00
- cron: "30 23 * * *"  # UTC 23:30 = 台灣 07:30
```

---

## 專案架構

```
gooaye-digest/
├── .github/
│   └── workflows/
│       └── daily.yml          # GitHub Actions 排程
├── src/
│   ├── fetch_podcast.py       # RSS 抓取 + 音檔下載
│   ├── transcribe.py          # faster-whisper 轉錄
│   ├── analyze.py             # Google Gemini API 結構化分析
│   ├── render.py              # HTML Email 渲染
│   └── notify.py              # Gmail + LINE Bot 發送
├── main.py                    # 主程式入口
├── requirements.txt
├── state.json                 # 記錄已處理集數（自動更新）
└── README.md
```

---

## 免責聲明

本專案為個人學習用途。投資筆記由 AI 自動生成，**僅供參考，不構成投資建議**。投資有風險，請自行判斷。
