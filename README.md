# Discord 伺服器邀請碼蒐集器

> ⚡ 本專案僅供**學術、測試、研發**用途，請依照 Discord 服務條款使用，若有違法行為後果需由你自己承擔。

---

## 🟣 檔案說明

- `invite.py`  
  依指定條件（比如依照成員人数）蒐集不同的Discord server邀請碼。
  
- `GetUrl.py`  
  依照整理出的邀請碼，批量處理獲取完整的加入URL。  

---

## 🟣 安裝

確保你已安裝以下依賴：
- Python 3.x
- `pip`
---

## 🟣 使用說明

### 🔹 1. 執行 `invite.py`

```bash
python invite.py
```

你可以依需要修改：
```python
# 第 72 行
crawl_discadia(start_page=1, end_page=2, output_file='server_links.txt', max_workers=5)
```

其中：
- `start_page` / `end_page` : 你希望蒐集幾頁
- `output_file` : 儲存結果的文件名稱
- `max_workers` : 依你的處理器效能調整工作執行緒数


你也可以修改：
```python
# 第 13 行
url = f"{base_url}/?sort=members&page={page}" 
# 你可以依需要修改 ?sort= 參数
# 目前是依 members (成員数) 由大到小列出
``` 


若執行後：
你會獲得一個 `server_links.txt` 檔案，每行就是一個 Discord 服務器的URL。

---

### 🔹 2. 執行 `GetUrl.py`

```bash
python GetUrl.py
```

你可以依需要修改：
```python
# 第 65 行
num_workers = 5
```

其中：
- `num_workers` : 依你處理器可以處理多少工作量。

此處**建議你在 Windows 系統上執行**，因為若在 Linux 可能會發生不同的平台問題。

執行後，你會獲取整理後的Discord伺服器邀請碼。
