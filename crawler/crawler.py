"""
Jewelry Price Crawler

1) Site structure:
- Infinite scroll + batch loading

2) Crawling Process
1. Manage collection URLs
2. Access pages with Selenium
3. Extract product-tile elements
4. Parse embedded JSON data
5. Store data using pandas
6. Visualize data with Streamlit
"""

import json
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

urls = [
    "https://www.vancleefarpels.com/kr/ko/collections/jewelry/alhambra.html",
    "https://www.vancleefarpels.com/kr/ko/collections/jewelry/perlee.html",
    "https://www.vancleefarpels.com/kr/ko/collections/jewelry/fauna.html",
    "https://www.vancleefarpels.com/kr/ko/collections/jewelry/flora/frivole.html"
]

all_data = []
seen = set()

for url in urls:
    driver.get(url)

    WebDriverWait(driver, 20).until(
        lambda d: len(d.find_elements(By.CLASS_NAME, "product-tile")) > 0
    )

    time.sleep(2)

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height

    collection_name = url.split("/")[-1].replace(".html", "")

    products = driver.find_elements(By.CLASS_NAME, "product-tile")

    for p in products:
        raw = p.get_attribute("data-vue-stats-product")

        if raw:
            data = json.loads(raw)

            name = data.get("item_name")

            price_raw = float(data.get("price"))
            price = f"₩ {price_raw:,.0f}"

            # 중복방지
            item_id = data.get("item_id")
            key = item_id if item_id else (name + str(price_raw))

            if key in seen:
                continue

            seen.add(key)

            all_data.append({
                "collection": collection_name,
                "name": name,
                "price": price
            })

driver.quit()

pd.set_option('display.max_rows', None)

df = pd.DataFrame(all_data)
print(df)