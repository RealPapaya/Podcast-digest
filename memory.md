# 專案開發記錄

## 2026-04-20-2：優化股票數據抓取錯誤處理

### 問題
1. 部分台股（如 6187）無法抓取數據，顯示 404 錯誤
2. 錯誤訊息過於嚴重（ERROR level），但其實是預期行為
3. 台股上櫃股票（OTC）使用 `.TWO` 後綴，而非 `.TW`

### 解決方案
改進 `src/stock_data.py` 的錯誤處理機制：
- 添加 `.TW` → `.TWO` 的 fallback 機制（上市 → 上櫃）
- 將 404 錯誤降級為 WARNING（因為下市股票是預期情況）
- 檢查 yfinance 返回的數據有效性
- 優化錯誤訊息，提供更清晰的說明

### 修改內容

#### src/stock_data.py
1. **添加 fallback ticker 機制**
   ```python
   if exchange == "台股":
       yf_ticker = f"{ticker}.TW"
       fallback_ticker = f"{ticker}.TWO"  # 上櫃股票
   ```

2. **改進數據驗證**
   - 檢查 `info` 是否有效（非空且有足夠字段）
   - 檢查是否有價格或歷史數據
   - 在沒有數據時嘗試 fallback ticker

3. **優化錯誤處理**
   - 404 錯誤 → WARNING（預期行為）
   - 其他錯誤 → ERROR
   - 統一錯誤訊息："Stock data unavailable (possibly delisted or invalid ticker)"

### 測試結果
```bash
# 6187（上櫃股票）- 成功 fallback 到 .TWO
⚠️  6187.TW: No data available (possibly delisted or invalid)
✅ 6187.TWO: $1215.0, P/E=40.7, RSI=66.24, 1M=+73.57%

# 2330（上市股票）- 直接成功
✅ 2330.TW: $2030.0, P/E=17.01, RSI=66.67, 1M=+6.56%
```

### 效果
- ✅ 上櫃股票（OTC）可正常抓取
- ✅ 錯誤訊息更友善，不會誤導為嚴重錯誤
- ✅ 日誌更清晰，易於 debug
- ✅ 下市股票會優雅地返回 error，不會中斷流程

---

## 2026-04-20-1：添加強制重新處理功能

### 問題
用戶無法檢查已處理過的集數成果，因為程式會自動跳過已處理的集數。

### 解決方案
添加 `--force` 參數支援，允許強制重新處理已處理過的集數。

### 修改內容

#### 1. main.py
- 新增 `argparse` 模組導入
- 添加命令列參數解析：
  - `--force`：強制重新處理已處理過的集數（忽略 state.json）
- 修改已處理檢查邏輯：
  ```python
  if not args.force and episode["guid"] == last_guid:
      log.info("✅ 此集已處理過，略過")
      log.info("💡 提示：使用 --force 參數可強制重新處理")
      sys.exit(0)
  ```

#### 2. .github/workflows/daily.yml
- 在 `workflow_dispatch` 添加輸入參數：
  ```yaml
  inputs:
    force:
      description: '強制重新處理已處理過的集數'
      required: false
      type: boolean
      default: false
  ```
- 修改執行命令，根據參數傳遞 `--force`：
  ```yaml
  run: python main.py ${{ github.event.inputs.force == 'true' && '--force' || '' }}
  ```

### 使用方式

#### 本地測試
```bash
# 正常執行（會跳過已處理集數）
python main.py

# 強制重新處理
python main.py --force
```

#### GitHub Actions
1. 進入 GitHub repo 的 Actions 頁面
2. 選擇「股癌 AI 每日投資筆記」workflow
3. 點擊「Run workflow」
4. 勾選「強制重新處理已處理過的集數」選項
5. 點擊綠色「Run workflow」按鈕

### 效果
- ✅ 保留原有自動跳過邏輯（避免重複處理）
- ✅ 提供手動強制重新處理選項（方便檢查成果）
- ✅ 本地和 CI/CD 都支援
