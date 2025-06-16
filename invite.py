import requests
from bs4 import BeautifulSoup
import re
import concurrent.futures
import threading

# 建立全域鎖來保護共享資源: found_links 和檔案寫入
found_links_lock = threading.Lock()
file_lock = threading.Lock()
found_links = set()

def process_page(page, base_url):
    url = f"{base_url}/?sort=members&page={page}"
    print(f"正在抓取：{url}")
    try:
        response = requests.get(url)
    except Exception as e:
        print(f"無法抓取 {url} (例外錯誤：{e})")
        return set()
    
    if response.status_code != 200:
        print(f"無法抓取 {url} (狀態碼：{response.status_code})")
        return set()

    soup = BeautifulSoup(response.text, "html.parser")
    # 找尋 href 以 "/" 開頭且 class 包含 server-join-button 的 <a> 標籤
    anchors = soup.find_all("a", href=re.compile("^/"), class_=re.compile("server-join-button"))
    # 每頁第一個通常是贊助商的連結，故跳過
    if anchors:
        anchors = anchors[1:]
    
    new_links = set()
    for a in anchors:
        relative_link = a.get("href")
        full_link = base_url + relative_link
        # 使用全域鎖確保不會寫入重複的連結
        with found_links_lock:
            if full_link not in found_links:
                found_links.add(full_link)
                new_links.add(full_link)
    if new_links:
        print(f"頁面 {page} 完成，共找到 {len(new_links)} 個新連結")
    else:
        print(f"頁面 {page} 未發現新的連結")
    return new_links

def crawl_discadia(start_page=1, end_page=5, output_file="server_links.txt", max_workers=5):
    base_url = "https://discadia.com"
    all_new_links = set()

    # 使用 ThreadPoolExecutor 同時處理多個頁面 (2-5個緒)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_page, page, base_url): page for page in range(start_page, end_page + 1)}
        for future in concurrent.futures.as_completed(futures):
            page = futures[future]
            try:
                new_links = future.result()
                all_new_links.update(new_links)
                # 寫入檔案，確保 thread-safe 以 file_lock 保護
                if new_links:
                    with file_lock:
                        with open(output_file, "a", encoding='utf-8') as f:
                            for link in new_links:
                                f.write(link + "\n")
            except Exception as exc:
                print(f"頁面 {page} 產生錯誤: {exc}")

    print(f"完成，共找到 {len(found_links)} 個不重複的連結，儲存於 {output_file}")

if __name__ == "__main__":
    # 依需求調整要檢查的頁數範圍與緒數 (max_workers 可設定為 2-5)
    crawl_discadia(start_page=1, end_page=2, output_file="server_links.txt", max_workers=5)
