# 專案開發記錄

## 2026-04-20：添加強制重新處理功能

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
