import requests
from bs4 import BeautifulSoup
import re

def crawl_discadia(start_page=1, end_page=5, output_file="server_links.txt"):
    base_url = "https://discadia.com"
    found_links = set()

    for page in range(start_page, end_page + 1):
        url = f"{base_url}/?sort=members&page={page}"
        print(f"正在抓取：{url}")
        response = requests.get(url)
        if response.status_code != 200:
            print(f"無法抓取 {url} (狀態碼：{response.status_code})")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        # 找尋 href 以 "/" 開頭且 class 包含 server-join-button 的 <a> 標籤
        anchors = soup.find_all("a", href=re.compile("^/"), class_=re.compile("server-join-button"))
        for a in anchors:
            relative_link = a.get("href")
            full_link = base_url + relative_link
            found_links.add(full_link)

    # 將結果儲存到 .txt 文件中
    with open(output_file, "w", encoding='utf-8') as f:
        for link in found_links:
            f.write(link + "\n")
            
    print(f"完成，共找到 {len(found_links)} 個連結，儲存於 {output_file}")

if __name__ == "__main__":
    # 此處可以調整要檢查的頁數範圍
    crawl_discadia(start_page=15, end_page=100)
