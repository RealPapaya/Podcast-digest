# 📁 專案檔案結構

```
Podcast-digest/
│
├── 📁 .github/                      # GitHub Actions 設定
│   └── workflows/
│       └── daily.yml                # 每日自動執行排程
│
├── 📁 src/                          # 核心程式碼
│   ├── fetch_podcast.py             # RSS 抓取 + 音檔下載
│   ├── transcribe.py                # Faster-Whisper 語音轉文字
│   ├── analyze.py                   # AI 分析（Claude/OpenAI/Gemini 三重容錯）
│   ├── render.py                    # HTML Email 渲染
│   └── notify.py                    # Gmail + LINE Bot 推送
│
├── 📁 docs/                         # 所有文檔
│   ├── CHANGELOG.md                 # 版本更新記錄
│   ├── MULTI_API_GUIDE.md           # 多 AI API 使用指南
│   ├── GMAIL_SETUP_GUIDE.md         # Gmail 應用程式密碼設定教學
│   ├── UPGRADE_SUMMARY.md           # v3.0 升級總結
│   └── GEMINI_API_OPTIMIZATION.md   # Gemini API 優化文檔
│
├── 📁 tests/                        # 測試工具
│   ├── test_pipeline.py             # 完整 Pipeline 測試（可跳過 Whisper）
│   ├── test_api_key.py              # API Key 驗證工具
│   ├── test_multi_api.py            # 多 AI 提供商測試
│   └── check_env.py                 # 環境變數檢查工具
│
├── 📄 main.py                       # 主程式入口
├── 📄 config.py                     # 全域配置（模型、重試、緩存）
├── 📄 requirements.txt              # Python 依賴套件
├── 📄 .env.example                  # 環境變數範例檔案
├── 📄 .gitignore                    # Git 忽略清單
├── 📄 README.md                     # 專案主要說明文件
├── 📄 PROJECT_STRUCTURE.md          # 本檔案（專案結構說明）
└── 📄 state.json                    # 已處理集數記錄（自動生成）
```

---

## 📂 核心資料夾說明

### 🔧 `src/` - 核心功能模組

| 檔案 | 功能 | 主要技術 |
|------|------|----------|
| `fetch_podcast.py` | 抓取 RSS 並下載音檔 | `feedparser`, `requests` |
| `transcribe.py` | 語音轉文字 | `faster-whisper` |
| `analyze.py` | AI 結構化分析 | `anthropic`, `openai`, `google-genai` |
| `render.py` | 渲染 HTML Email | Jinja2 模板 |
| `notify.py` | 發送通知 | SMTP (Gmail), LINE Messaging API |

### 📚 `docs/` - 完整文檔

| 檔案 | 內容 | 適用對象 |
|------|------|----------|
| `CHANGELOG.md` | 版本更新歷史 | 所有用戶 |
| `MULTI_API_GUIDE.md` | 多 AI API 詳細教學 | 進階用戶 |
| `GMAIL_SETUP_GUIDE.md` | Gmail 應用程式密碼設定步驟 | 新手用戶 |
| `UPGRADE_SUMMARY.md` | v3.0 新特性與遷移指南 | 舊版用戶 |
| `GEMINI_API_OPTIMIZATION.md` | Gemini API 優化紀錄 | 開發者 |

### 🧪 `tests/` - 測試工具集

| 檔案 | 用途 | 命令範例 |
|------|------|----------|
| `test_pipeline.py` | 測試完整流程（可跳過 Whisper） | `python tests/test_pipeline.py --step analyze` |
| `test_api_key.py` | 快速驗證 API Key 有效性 | `python tests/test_api_key.py` |
| `test_multi_api.py` | 測試多 AI 提供商容錯 | `python tests/test_multi_api.py` |
| `check_env.py` | 檢查 `.env` 環境變數設定 | `python tests/check_env.py` |

---

## 🔑 重要檔案說明

### `main.py` - 主程式入口

完整執行流程：
1. 抓取最新 Podcast RSS
2. 下載音檔
3. Whisper 轉錄（30-60 分鐘）
4. AI 分析（Claude → OpenAI → Gemini）
5. 渲染 HTML
6. 發送 Email + LINE 通知

**執行命令：**
```bash
python main.py
```

---

### `config.py` - 全域配置

集中管理所有設定：

```python
# AI Provider 設定
CLAUDE_MODEL = "claude-sonnet-4-20250514"
OPENAI_MODEL = "gpt-4o-mini"
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"]

# 重試設定
MAX_RETRIES = 3
RETRY_DELAY = 2

# 緩存設定
ENABLE_CACHE = True
CACHE_DIR = ".cache"
```

---

### `.env` - 環境變數（機敏資訊）

**⚠️ 絕對不要上傳到 GitHub！**

包含所有 API Keys：
```bash
# AI API Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIzaSyD...

# Gmail 設定
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN=eyJhbGc...
LINE_USER_ID=Uxxxxxxxx...
```

**設定方式：**
```bash
# 複製範例檔案
cp .env.example .env

# 編輯並填入真實 API Keys
# Windows: notepad .env
# Mac/Linux: nano .env
```

---

### `state.json` - 執行狀態記錄

自動生成，記錄已處理的集數 GUID，避免重複處理。

```json
{
  "last_processed_guid": "https://feeds.soundon.fm/podcasts/xxx",
  "last_run": "2026-04-17T10:00:00Z"
}
```

**清除方式：**
```bash
# 刪除後會重新處理最新一集
rm state.json   # Mac/Linux
del state.json  # Windows
```

---

## 🚀 快速上手

### 1️⃣ 首次設定

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 設定環境變數
cp .env.example .env
# 編輯 .env 填入 API Keys

# 3. 檢查環境
python tests/check_env.py
```

### 2️⃣ 測試運行

```bash
# 測試 AI 分析（不轉錄，使用假資料）
python tests/test_pipeline.py --step analyze

# 測試 Email 發送
python tests/test_pipeline.py --step email

# 測試 LINE 發送
python tests/test_pipeline.py --step line
```

### 3️⃣ 完整執行

```bash
# 抓取最新 Podcast 並處理
python main.py
```

---

## 📊 資料流程圖

```
┌─────────────┐
│  RSS Feed   │
│ (SoundOn)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ fetch_      │
│ podcast.py  │  下載音檔 (.mp3)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ transcribe. │
│ py          │  Whisper 轉錄 → 逐字稿
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ analyze.py  │  AI 分析 (Claude/OpenAI/Gemini)
└──────┬──────┘     │
       │            ├─► 緩存檢查 (.cache/)
       │            └─► 三重容錯鏈
       ▼
┌─────────────┐
│ render.py   │  渲染 HTML Email
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ notify.py   │  發送通知
└─────┬───┬───┘
      │   │
      │   └────► LINE Bot
      │
      └────────► Gmail SMTP
```

---

## 🛠️ 開發指南

### 新增功能流程

1. **修改核心邏輯** → 編輯 `src/` 中對應模組
2. **調整配置** → 修改 `config.py`
3. **更新環境變數** → 編輯 `.env.example`（不要直接改 `.env`）
4. **撰寫測試** → 在 `tests/` 新增測試腳本
5. **更新文檔** → 修改 `docs/` 相關 Markdown

### 常用開發命令

```bash
# 查看目前結構
tree /F  # Windows
tree     # Mac/Linux

# 清除緩存
Remove-Item -Recurse -Force .cache  # PowerShell
rm -rf .cache/                      # Mac/Linux

# 檢查依賴
pip list | findstr -i "anthropic openai google"  # Windows
pip list | grep -i "anthropic\|openai\|google"  # Mac/Linux
```

---

## 📝 版本資訊

- **當前版本**: v3.0.0
- **更新時間**: 2026-04-17
- **主要特性**: 三重 AI API 容錯、智能緩存、詳細日誌

**版本歷史請參考**: [docs/CHANGELOG.md](docs/CHANGELOG.md)

---

## 🤝 貢獻指南

1. Fork 本專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 遵循現有檔案結構
4. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
5. 推送到分支 (`git push origin feature/AmazingFeature`)
6. 開啟 Pull Request

---

## 📞 需要幫助？

- 📖 **查看文檔**: [docs/](docs/)
- 🐛 **回報問題**: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 **討論交流**: [GitHub Discussions](https://github.com/your-repo/discussions)

---

**最後更新**: 2026-04-17  
**維護者**: [Your Name]
