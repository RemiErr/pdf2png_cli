# PDF to PNG 

本專案是一個使用 **Python + PyMuPDF** 實作的工具，用來將 **PDF 每一頁轉換成 PNG 圖檔**，並搭配 **pytest 單元測試**確保功能正確。

專案採用 **uv** 作為 Python 版本與套件管理工具，具有速度快、環境乾淨、適合 CI 與個人專案等優點。

---

## 功能說明

* 將 PDF 每一頁轉換為 PNG 圖檔
* 可設定：

  * DPI（解析度）
  * 輸出資料夾
  * 檔名格式（例如 `page_001.png`）
  * 指定頁碼範圍
* 提供 CLI 指令介面
* 內含完整 pytest 單元測試
* 使用 uv 管理 Python 環境與相依套件

---

## 專案結構

```text
pdf-to-png/
├─ pyproject.toml
├─ uv.lock
├─ pdf_to_png.py
├─ test_pdf_to_png.py
└─ README.md
```

---

## 環境需求

* 作業系統：macOS / Linux / Windows
* Python：3.10 以上（由 uv 管理）
* 套件管理工具：uv

---

## 安裝 uv

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows（PowerShell）

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

確認安裝成功：

```bash
uv --version
```

---

## 同步環境設定

在專案根目錄執行：

```bash
uv sync
```

該指令會自動安裝相依套件並同步環境設定，若環境未被正確安裝可嘗試手動安裝。

### 手動安裝相依套件

```bash
uv add pymupdf pillow reportlab pytest
```

說明：

* `pymupdf`：PDF 轉圖核心套件（匯入名稱為 `fitz`）
* `pillow`：驗證輸出 PNG
* `reportlab`：單元測試用來動態產生測試 PDF
* `pytest`：單元測試框架

---

## 使用方式

### 將 PDF 轉成 PNG

```bash
uv run python pdf_to_png.py input.pdf -o output --dpi 200
```

常用參數說明：

| 參數                | 說明              |
| ------------------- | ----------------- |
| `-o / --output-dir` | 輸出資料夾        |
| `--dpi`             | 圖片解析度        |
| `--prefix`          | 輸出檔名前綴      |
| `--start-page`      | 起始頁（1-based） |
| `--end-page`        | 結束頁（1-based） |
| `--pwd`             | PDF 檔案密碼      |

範例：

```bash
uv run python pdf_to_png.py sample.pdf -o out --dpi 150 --prefix page_
```

---

## 執行單元測試

```bash
uv run pytest -q
```

測試內容包含：

* 動態建立測試 PDF
* 驗證輸出 PNG 數量
* 驗證檔名格式
* 確認 PNG 可被 PIL 正常開啟
