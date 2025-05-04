import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.plugins": 2,
        "profile.managed_default_content_settings.popups": 2
    })
    driver = uc.Chrome(options=options)
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setBlockedURLs", {
        "urls": ["*.css", "*.png", "*.jpg", "*.jpeg", "*.svg", "*.woff", "*.ttf", "*.gif", "*.webp", "*.js"]
    })
    return driver

def scrape_player_urls(page):
    driver = create_driver()
    try:
        url = f"https://www.fifaindex.com/players/?page={page}"
        driver.get(url)
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "figure > a")))
        links = driver.find_elements(By.CSS_SELECTOR, "figure > a")
        urls = list(set(link.get_attribute("href") for link in links if link.get_attribute("href")))
        print(f"[PAGE {page}] Found {len(urls)} player URLs")
        return urls
    except Exception as e:
        print(f"[ERROR] Failed on page {page}: {e}")
        return []
    finally:
        driver.quit()

def scrape_player_data(player_url):
    driver = create_driver()
    try:
        driver.get(player_url)
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        stats = {}
        stats["name"] = driver.execute_script("return arguments[0].childNodes[0].nodeValue.trim();", driver.find_element(By.TAG_NAME, "h1"))
        stats["age"] = driver.find_element(By.XPATH, "//p[contains(text(),'Age')]").text.split()[-1]
        
        for p in driver.find_elements(By.CSS_SELECTOR, "div.card-body p"):
            spans = p.find_elements(By.TAG_NAME, "span")
            if spans:
                stat_value = spans[-1].text.strip()
                stat_name = p.text.strip().replace(stat_value, "").strip()
                if stat_value != "None":
                    stats[stat_name] = stat_value

        stats["value"] = driver.find_element(By.CSS_SELECTOR, "p.data-currency-euro").text.replace("Value", "").strip()[1:].replace(".", "")
        print(f"[OK] Scraped: {stats['name']}")
        return list(stats.values())
    except Exception as e:
        print(f"[ERROR] Failed to scrape {player_url}: {e}")
        return None
    finally:
        driver.quit()

# Collect all player URLs from 608 pages in parallel
all_player_urls = []
with ThreadPoolExecutor(max_workers=6) as executor:
    futures = [executor.submit(scrape_player_urls, page) for page in range(1, 2)]
    for future in as_completed(futures):
        urls = future.result()
        all_player_urls.extend(urls)

print(f"[INFO] Total collected player URLs: {len(all_player_urls)}")

# Scrape each player page in parallel
scraped_data = []
with ThreadPoolExecutor(max_workers=6) as executor:
    futures = [executor.submit(scrape_player_data, url) for url in all_player_urls[:3]]
    for future in as_completed(futures):
        row = future.result()
        if row:
            scraped_data.append(row)

# Save all data to CSV
with open("ratings.csv", "a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    for row in scraped_data:
        writer.writerow(row)

print("✅ All data saved to ratings.csv")
