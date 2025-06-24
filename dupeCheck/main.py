import requests
import json
import os
import time
from datetime import datetime

# 伺服器資料庫文件路徑
SERVER_DB_FILE = "server_database.json"

def get_user_info(token, max_retries=5):
    """
    使用提供的用戶令牌獲取用戶信息（包括用戶ID）。
    """
    headers = {"Authorization": token}
    for attempt in range(max_retries):
        try:
            response = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 1)
                print(f"Rate limited for get_user_info, waiting {retry_after} seconds...")
                time.sleep(float(retry_after))
            else:
                print(f"Failed to get user info: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    print("Max retries reached for get_user_info")
    return None

def get_user_guilds(token, max_retries=5):
    """
    使用提供的用戶令牌獲取用戶所在的伺服器列表。
    """
    headers = {"Authorization": token}
    for attempt in range(max_retries):
        try:
            response = requests.get("https://discord.com/api/v10/users/@me/guilds", headers=headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 1)
                print(f"Rate limited for get_user_guilds, waiting {retry_after} seconds...")
                time.sleep(float(retry_after))
            else:
                print(f"Failed to get user guilds: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Error getting user guilds: {e}")
            return []
    print("Max retries reached for get_user_guilds")
    return []

def leave_guild(token, guild_id, max_retries=5):
    """
    使用提供的用戶令牌讓用戶退出指定的伺服器。
    """
    headers = {"Authorization": token}
    for attempt in range(max_retries):
        try:
            response = requests.delete(f"https://discord.com/api/v10/users/@me/guilds/{guild_id}", headers=headers)
            if response.status_code == 204:
                print(f"Successfully left server {guild_id}")
                return True
            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 1)
                print(f"Rate limited for leave_guild, waiting {retry_after} seconds...")
                time.sleep(float(retry_after))
            else:
                print(f"Failed to leave server {guild_id}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Error leaving server {guild_id}: {e}")
            return False
    print(f"Max retries reached for leaving server {guild_id}")
    return False

def read_tokens_from_file(file_path="token.txt"):
    """
    從指定的檔案中讀取令牌列表。
    格式應為每行一個令牌，後面可跟逗號（例如：token1,）。
    """
    if not os.path.exists(file_path):
        print(f"Error: {file_path} file does not exist")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            tokens = [line.strip().rstrip(',') for line in file if line.strip()]
            if not tokens:
                print(f"Error: {file_path} is empty")
                return []
            print(f"Successfully read {len(tokens)} tokens: {[t[:10] + '...' for t in tokens]}")
            return tokens
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def load_server_database():
    """
    從檔案載入伺服器資料庫。
    """
    if os.path.exists(SERVER_DB_FILE):
        try:
            with open(SERVER_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading server database: {e}")
            return {}
    return {}

def save_server_database(database):
    """
    將伺服器資料庫保存到檔案。
    """
    try:
        with open(SERVER_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2)
        print(f"Server database saved with {len(database)} servers")
    except Exception as e:
        print(f"Error saving server database: {e}")

def deduplicate(tokens):
    """
    去重複伺服器，確保每個伺服器只有一個帳號。
    同時更新伺服器資料庫。
    """
    # 載入現有的伺服器資料庫
    server_database = load_server_database()
    print(f"\n== 已載入伺服器資料庫，包含 {len(server_database)} 個伺服器ID ==")
    
    user_data = {}
    token_guild_counts = {}  # 用於存儲每個token的伺服器數量
    total_left_servers = 0   # 用於統計總計退出伺服器數量
    
    print("\n== 取得所有帳號資訊與伺服器列表 ==")
    for i, token in enumerate(tokens):
        print(f"處理 Token #{i+1} (前10字元: {token[:10]}...)")
        user = get_user_info(token)
        if user:
            user_id = user["id"]
            user_name = user.get("username", "Unknown User")
            print(f"用戶 ID: {user_id}, 用戶名: {user_name}")
            guilds = get_user_guilds(token)
            
            # 更新伺服器資料庫
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for guild in guilds:
                guild_id = guild["id"]
                guild_name = guild.get("name", "Unknown Server")
                
                # 如果伺服器ID不在資料庫中，或者我們有更新的資訊，則更新
                if guild_id not in server_database:
                    server_database[guild_id] = {
                        "name": guild_name,
                        "first_discovered": current_time,
                        "last_updated": current_time
                    }
                else:
                    # 更新上次更新時間和名稱（如果有變化）
                    server_database[guild_id]["last_updated"] = current_time
                    if guild_name != "Unknown Server":
                        server_database[guild_id]["name"] = guild_name
            
            user_data[user_id] = {
                "token": token, 
                "guilds": [g["id"] for g in guilds],
                "username": user_name
            }
            guild_count = len(guilds) if guilds is not None else 0
            token_guild_counts[token] = guild_count
            print(f"此帳號目前有 {guild_count} 個伺服器")
        else:
            print(f"無法處理 Token #{i+1}")
        print("等待1秒後處理下一個令牌...")
        time.sleep(1)
    
    # 保存更新後的伺服器資料庫
    print(f"\n== 更新伺服器資料庫，現在共有 {len(server_database)} 個伺服器ID ==")
    save_server_database(server_database)

    print("\n== 顯示每個 Token 的伺服器數量 ==")
    for i, token in enumerate(tokens):
        count = token_guild_counts.get(token, "無法獲取")
        print(f"Token #{i+1} (前10字元: {token[:10]}...): {count} 個伺服器")
    
    print("\n== 開始去重複處理 ==")
    guild_to_users = {}
    for user_id, data in user_data.items():
        for guild_id in data["guilds"]:
            if guild_id not in guild_to_users:
                guild_to_users[guild_id] = []
            guild_to_users[guild_id].append(user_id)

    for guild_id, users in guild_to_users.items():
        if len(users) > 1:
            server_name = server_database.get(guild_id, {}).get("name", "Unknown Server")
            print(f"找到伺服器 {guild_id} ({server_name}) 有多個用戶: {users}")
            keep_user = users[0]
            keep_username = user_data[keep_user]["username"]
            print(f"保留用戶 {keep_user} ({keep_username}) 在伺服器 {guild_id}")
            
            for user in users[1:]:
                username = user_data[user]["username"]
                token = user_data[user]["token"]
                print(f"移除用戶 {user} ({username}) 從伺服器 {guild_id}")
                
                if leave_guild(token, guild_id):
                    total_left_servers += 1
                    # 更新此token的伺服器計數
                    if token in token_guild_counts:
                        token_guild_counts[token] -= 1
                    print("等待5秒後進行下一個退出操作...")
                    time.sleep(5)
                else:
                    print(f"無法讓用戶 {user} 退出伺服器 {guild_id}")

    print("\n== 去重複完成 ==")
    print(f"總計退出了 {total_left_servers} 個伺服器")
    
    print("\n== 更新後的每個 Token 的伺服器數量 ==")
    for i, token in enumerate(tokens):
        count = token_guild_counts.get(token, "無法獲取")
        print(f"Token #{i+1} (前10字元: {token[:10]}...): {count} 個伺服器")

def display_server_database():
    """
    顯示伺服器資料庫的內容。
    """
    server_database = load_server_database()
    if not server_database:
        print("伺服器資料庫為空或無法讀取")
        return
    
    print(f"\n===== 伺服器資料庫 (共 {len(server_database)} 個伺服器) =====")
    print("{:<24} {:<40} {:<20}".format("伺服器ID", "伺服器名稱", "發現日期"))
    print("-" * 85)
    
    for server_id, data in server_database.items():
        name = data.get("name", "Unknown Server")
        discovered = data.get("first_discovered", "Unknown")
        print("{:<24} {:<40} {:<20}".format(server_id, name[:39], discovered))

def main():
    """
    主函數，執行去重複操作。
    """
    print("=== Discord 帳號伺服器去重複工具 ===")
    print(f"現在時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 顯示資料庫中的伺服器數量
    server_database = load_server_database()
    print(f"資料庫中目前有 {len(server_database)} 個伺服器ID")
    
    tokens = read_tokens_from_file()
    if not tokens:
        print("沒有有效的令牌可處理，程式結束")
        return
    
    # 提供選項選單
    print("\n請選擇操作:")
    print("1. 執行伺服器去重複")
    print("2. 顯示伺服器資料庫")
    choice = input("請輸入選項 (1/2): ")
    
    if choice == "1":
        print("開始執行伺服器去重複...")
        deduplicate(tokens)
        print("處理完成!")
    elif choice == "2":
        display_server_database()
    else:
        print("無效的選擇，程式結束")

if __name__ == "__main__":
    main()