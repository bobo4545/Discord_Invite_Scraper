import time
import threading
import concurrent.futures
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

# A lock for thread-safe file writes.
file_lock = threading.Lock()

def process_url(driver, url, timeout=15, check_interval=1):
    """
    Process a single URL using the given driver instance.
    Loads the URL with a page load strategy of 'none', then polls until
    the current URL contains "https://discord.com/invite/" or until timeout.
    Returns True and logs the URL only if successful, else returns False.
    """
    try:
        driver.get(url)
        elapsed = 0
        final_url = driver.current_url
        # Poll until "https://discord.com/invite/" is found or timeout is reached.
        while "https://discord.com/invite/" not in final_url and elapsed < timeout:
            time.sleep(check_interval)
            elapsed += check_interval
            final_url = driver.current_url

        # If the final URL contains the Discord invite substring, log it.
        if "https://discord.com/invite/" in final_url:
            with file_lock:
                with open("results.txt", "a", encoding="utf-8") as f:
                    f.write(final_url + "\n")
            print(f"Processed {url} -> {final_url}")
            return True
        else:
            print(f"Processed {url} -> No successful jump (timeout)")
            return False

    except WebDriverException as e:
        print(f"Error processing {url}: {e}")
        return False

def process_url_group(urls):
    """
    Initializes a browser instance and processes a list of URLs sequentially
    using the same browser instance. The browser remains open between URL loads.
    """
    options = webdriver.ChromeOptions()
    # Uncomment to run in headless mode if desired.
    # options.add_argument("--headless")
    options.page_load_strategy = 'none'
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(300, 400)  # Limit the window size to conserve resources.

    for url in urls:
        process_url(driver, url)
    
    driver.quit()

def main():
    # Read URLs from "server_links.txt".
    with open("server_links.txt", "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    # Number of concurrent browser instances.
    num_workers = 5  # Adjust based on your system capabilities.

    # Partition the URLs evenly among the workers.
    groups = [[] for _ in range(num_workers)]
    for index, url in enumerate(urls):
        groups[index % num_workers].append(url)
    
    # Process each group concurrently.
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        executor.map(process_url_group, groups)

if __name__ == "__main__":
    main()
