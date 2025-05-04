import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

# Setup optimized Chrome
options = uc.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-plugins")
options.add_argument("--disable-background-tasks")
options.add_argument("--disable-webgl")
options.add_argument("--disable-prediction-service")
options.add_argument("about:blank")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-infobars")
options.add_argument("--disable-notifications")
options.add_argument("--disable-translate")
options.add_argument("--disable-background-networking")

prefs = {
    "profile.managed_default_content_settings.images": 2,
    "profile.managed_default_content_settings.stylesheets": 2,
    "profile.managed_default_content_settings.plugins": 2,
    "profile.managed_default_content_settings.popups": 2,
}
options.add_experimental_option("prefs", prefs)

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 4)

# Block unnecessary resources
driver.execute_cdp_cmd("Network.enable", {})
driver.execute_cdp_cmd("Network.setBlockedURLs", {
    "urls": ["*.css", "*.png", "*.jpg", "*.jpeg", "*.svg", "*.woff", "*.ttf", "*.gif", "*.webp", "*.ico", "*.bmp",
             "*.webm", "*.mp4", "*.mp3", "*.wav", "*.ogg", "*.flac", "*.aac", "*.m4a", "*.opus", "*.avi", "*.mov",
             "*.wmv", "*.mkv", "*.webp", "gtm.js?id=GTM-PWRSC6S", "ads.adthrive.com/*"]
})

base_url = "https://www.fifaindex.com"
player_urls = []

# Step 1: Collect all player URLs from paginated listing
for page in range(1,300):
    url = f"{base_url}/players/?page={page}"
    driver.get(url)

    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "figure > a")))
    links = driver.find_elements(By.CSS_SELECTOR, "figure > a")
    for link in links:
        href = link.get_attribute("href")
        if href and href not in player_urls:
            player_urls.append(href)

    print(f"[INFO] Collected links from page {page}")

    with open("ratings.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        for player_url in player_urls:
            try:
                driver.get(player_url)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

                stats = {}

                name_el = driver.find_element(By.TAG_NAME, "h1")
                name = driver.execute_script("return arguments[0].childNodes[0].nodeValue.trim();", name_el)
                stats["name"] = name

                age_el = wait.until(EC.presence_of_element_located((By.XPATH, "//p[contains(text(),'Age')]")))
                stats["age"] = age_el.text.split()[-1]

                value_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.data-currency-euro")))
                value = value_el.text.replace("Value", "").strip()[1:].replace(".", "")

                items = driver.find_elements(By.CSS_SELECTOR, "div.item")
                for item in items:
                    paragraphs = item.find_elements(By.CSS_SELECTOR, "div.card-body p")
                    for p in paragraphs:
                        spans = p.find_elements(By.TAG_NAME, "span")
                        if spans:
                            full_text = p.text.strip()
                            stat_value = spans[-1].text.strip()
                            stat_name = full_text.replace(stat_value, "").strip()
                            if stat_value != "None":
                                stats[stat_name] = stat_value

                stats["value"] = value
                writer.writerow(stats.values())
                print(f"[OK] Scraped {stats['name']}")

            except Exception as e:
                print(f"[ERROR] Failed to scrape {player_url}: {e}")
                continue

    player_urls = []

driver.quit()
print("✅ All data saved to ratings.csv")
