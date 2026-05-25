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
    "https://www.vancleefarpels.com/kr/ko/collections/jewelry/flora/frivole.html",
    "https://www.vancleefarpels.com/kr/ko/collections/jewelry/other-collections/zodiaque.html",
    "https://www.vancleefarpels.com/kr/ko/collections/jewelry/flora.html"
]

all_data = []
seen = set()

for url in urls:
    driver.get(url)

    WebDriverWait(driver, 20).until(
        lambda d: len(d.find_elements(By.CLASS_NAME, "product-tile")) > 0
    )

    time.sleep(2)

    # infinite scroll
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height

    # Load More
    while True:
        try:
            span = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(
                    (By.ID, "loadMore-aria-label")
                )
            )

            button = span.find_element(By.XPATH, "./ancestor::button")

            driver.execute_script(
                "arguments[0].scrollIntoView(true);",
                button
            )

            time.sleep(1)

            driver.execute_script(
                "arguments[0].click();",
                button
            )

            print(f"[LOAD MORE] {url}")

            time.sleep(3)

        except:
            print(f"[DONE] {url}")
            break

    collection_name = url.split("/")[-1].replace(".html", "")

    products = driver.find_elements(By.CLASS_NAME, "product-tile")

    print(f"{collection_name}: {len(products)} products")

    for p in products:
        raw = p.get_attribute("data-vue-stats-product")

        if raw:
            data = json.loads(raw)

            name = data.get("item_name", "").strip()

            price_value = data.get("price")

            # price 예외 처리
            try:
                price_raw = float(price_value)
                price = f"₩ {price_raw:,.0f}"
            except:
                price_raw = None
                price = "N/A"

            # 중복 방지
            item_id = data.get("item_id")
            key = item_id if item_id else (name + str(price))

            if key in seen:
                continue

            seen.add(key)

            all_data.append({
                "collection": collection_name,
                "name": name,
                "price": price
            })

#디버깅
print(f"RAW tiles: {len(products)}")
print(f"UNIQUE items: {len(all_data)}")            

driver.quit()

pd.set_option('display.max_rows', None)

df = pd.DataFrame(all_data)

df.to_csv(
    "../data/products.csv",
    index=False,
    encoding="utf-8-sig"
)

print(df)