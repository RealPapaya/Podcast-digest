# Gmail 設定完整指南

## 為什麼 Gmail 沒有寄送？

如果你看到以下錯誤訊息：
```
未設定 Gmail 環境變數，略過 Email 發送
```

或者：
```
Gmail 登入失敗！請確認是否已開啟「應用程式密碼」
```

這表示你的 `.env` 檔案中的 Gmail 設定不正確。

---

## 完整設定步驟

### 步驟 1：啟用兩步驟驗證

Gmail 的「應用程式密碼」功能需要先啟用兩步驟驗證。

1. 前往 Google 帳戶安全性設定：https://myaccount.google.com/security
2. 找到「登入 Google」區塊
3. 點擊「兩步驟驗證」
4. 按照指示完成設定（通常是簡訊驗證或 Google Authenticator）

✅ 完成後應該會看到「兩步驟驗證：**已開啟**」

---

### 步驟 2：產生應用程式密碼

1. 回到安全性頁面：https://myaccount.google.com/security
2. 在「登入 Google」區塊中，找到「應用程式密碼」（App Passwords）
   - 如果看不到這個選項，請確認兩步驟驗證已開啟
3. 點擊「應用程式密碼」
4. 選擇應用程式：「郵件」
5. 選擇裝置：「其他（自訂名稱）」
6. 輸入名稱：`股癌 Podcast Digest`
7. 點擊「產生」

✅ **畫面會顯示一組 16 字元的密碼**，例如：`abcd efgh ijkl mnop`

**⚠️ 重要：這個密碼只會顯示一次，請立即複製！**

---

### 步驟 3：更新 .env 檔案

打開 `.env` 檔案，修改以下三行：

```bash
# Your Gmail address（你的 Gmail 地址）
GMAIL_USER=your.email@gmail.com

# Gmail app password（剛剛產生的 16 字元密碼）
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop

# Recipient email address（收件人，預設同寄件人）
RECIPIENT_EMAIL=your.email@gmail.com
```

**範例（假設你的 Gmail 是 `morris199895@gmail.com`）：**

```bash
GMAIL_USER=morris199895@gmail.com
GMAIL_APP_PASSWORD=xmkp qrst uvwx yzab  # ← 替換成你產生的密碼
RECIPIENT_EMAIL=morris199895@gmail.com
```

⚠️ **不是你的 Gmail 登入密碼！而是步驟 2 產生的 16 字元密碼**

---

### 步驟 4：測試 Gmail 發送

執行測試命令：

```bash
# 只測試 Email 發送（會使用 test_digest.json 的內容）
python test_pipeline.py --step email
```

成功的輸出應該是：
```
📧 測試 Gmail 發送...
✅ Email 已發送至 morris199895@gmail.com
✅ Email 發送成功！請檢查收件匣
```

---

## 常見問題排解

### ❌ 錯誤 1：未設定 Gmail 環境變數

**錯誤訊息：**
```
未設定 Gmail 環境變數，略過 Email 發送
```

**原因：**
- `.env` 檔案中 `GMAIL_USER` 或 `GMAIL_APP_PASSWORD` 為空
- `.env` 檔案路徑不對

**解決方法：**
1. 確認 `.env` 檔案在專案根目錄（與 `test_pipeline.py` 同層）
2. 確認 `GMAIL_USER` 和 `GMAIL_APP_PASSWORD` 都有填寫
3. 確認沒有多餘的空格或註解符號 `#`

---

### ❌ 錯誤 2：Gmail 登入失敗

**錯誤訊息：**
```
Gmail 登入失敗！請確認是否已開啟「應用程式密碼」
SMTPAuthenticationError
```

**原因：**
- 使用了 Gmail 登入密碼（錯誤），而非應用程式密碼
- 應用程式密碼格式錯誤（多了或少了字元）
- 兩步驟驗證未啟用

**解決方法：**
1. 確認已啟用兩步驟驗證
2. 重新產生應用程式密碼
3. 複製時不要有額外空格（可以包含或移除空格，系統會自動處理）
4. 確認 `.env` 中沒有多餘的引號

**正確格式範例：**
```bash
GMAIL_APP_PASSWORD=abcdefghijklmnop           # ✅ 正確（無空格）
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop        # ✅ 正確（有空格）
GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"      # ❌ 錯誤（有引號）
GMAIL_APP_PASSWORD= abcd efgh ijkl mnop       # ❌ 錯誤（等號後有空格）
```

---

### ❌ 錯誤 3：收不到信

**可能原因：**
1. 信件被歸類到「促銷內容」或「垃圾郵件」
2. Gmail 信箱容量已滿
3. 收件人地址錯誤

**解決方法：**
1. 檢查 Gmail 的所有分類標籤（促銷內容、社交網路、論壇）
2. 搜尋「股癌」關鍵字
3. 確認 `RECIPIENT_EMAIL` 地址正確

---

## 測試流程總覽

```bash
# 1. 完整測試（Gemini 分析 + 渲染 + Email + LINE）
python test_pipeline.py

# 2. 只測試 Gemini 分析
python test_pipeline.py --step analyze

# 3. 只測試 HTML 渲染（輸出到 test_output.html）
python test_pipeline.py --step render

# 4. 只測試 Gmail 發送（需先有 test_digest.json）
python test_pipeline.py --step email

# 5. 只測試 LINE 發送（需先有 test_digest.json）
python test_pipeline.py --step line

# 6. 使用快取的分析結果（跳過 Gemini）
python test_pipeline.py --use-cached
```

---

## 安全性建議

1. **不要把 `.env` 檔案上傳到 GitHub**
   - 專案已包含 `.gitignore` 會自動排除 `.env`
   - 確認 `git status` 不會列出 `.env`

2. **應用程式密碼管理**
   - 如果密碼洩漏，立即到 Google 帳戶刪除該密碼
   - 定期更換應用程式密碼

3. **收件人設定**
   - `RECIPIENT_EMAIL` 可以設定為不同的信箱
   - 例如工作信箱發送到個人信箱

---

## 進階設定

### 寄送給多人

目前程式只支援單一收件人，如果要寄給多人：

1. 方案一：設定 Gmail 自動轉寄規則
2. 方案二：修改 `src/notify.py` 的 `send_gmail()` 函數

### 客製化信件標題

修改 `src/notify.py` 第 36-38 行：

```python
subject = f"股癌 {ep} 投資筆記 {stance_emoji} {date}"
```

可以改成：
```python
subject = f"[每日股癌] {ep} | {stance} | {date}"
```

### 關閉 Email 發送

如果只想用 LINE 通知，可以：

1. 方案一：註解掉 `test_pipeline.py` 中的 `step_email()`
2. 方案二：清空 `.env` 中的 `GMAIL_USER` 和 `GMAIL_APP_PASSWORD`

---

## 還是有問題？

執行以下命令檢查環境變數：

```bash
# Windows PowerShell
python -c "import os; print('GMAIL_USER:', os.getenv('GMAIL_USER')); print('GMAIL_APP_PASSWORD:', '***' if os.getenv('GMAIL_APP_PASSWORD') else None)"

# 輸出應該像這樣：
# GMAIL_USER: morris199895@gmail.com
# GMAIL_APP_PASSWORD: ***
```

如果輸出是 `None`，表示 `.env` 沒有正確載入。

---

**設定完成後，執行 `python test_pipeline.py --step email` 即可測試！** 🚀
