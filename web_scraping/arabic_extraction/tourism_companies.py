import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://mota.gov.eg/ar/%D8%A7%D9%84%D8%B4%D8%B1%D9%83%D8%A7%D8%AA-%D9%88%D8%A7%D9%84%D9%85%D9%86%D8%B4%D8%A2%D8%AA-%D8%A7%D9%84%D9%81%D9%86%D8%AF%D9%82%D9%8A%D8%A9-%D9%88%D8%A7%D9%84%D8%B3%D9%8A%D8%A7%D8%AD%D9%8A%D8%A9/%D8%AF%D9%84%D9%8A%D9%84-%D8%B4%D8%B1%D9%83%D8%A7%D8%AA-%D8%A7%D9%84%D8%B3%D9%8A%D8%A7%D8%AD%D8%A9/")
time.sleep(5) 

data = []
current_page = 1

while True:
    print(f"Scraping Page {current_page}...")
    
    # Extract table rows
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, 'table.custom__info__table tbody tr')
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            if len(cols) >= 5:
                data.append({
                    'company_ar': cols[0].text.strip(),
                    'company_en': cols[1].text.strip(),
                    'license_no': cols[2].text.strip(),
                    'governorate': cols[3].text.strip(),
                    'email': cols[4].text.strip()
                })
    except Exception:
        pass

    # Pagination logic
    try:
        # 1. Target the very last <li> in the pagination container
        next_li = driver.find_element(By.CSS_SELECTOR, 'ul.pagination li:last-child')
        
        # 2. Check if that <li> has the disabled class (meaning we hit the end)
        if "disabled" in next_li.get_attribute("class"):
            break
            
        # 3. Find the clickable link inside that <li>
        next_link = next_li.find_element(By.TAG_NAME, 'a')
        
        # Scroll to it and click
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_link)
        time.sleep(0.5) 
        driver.execute_script("arguments[0].click();", next_link)
        
        current_page += 1
        time.sleep(3)
    except Exception as e:
        print(f"Pagination stopped: {e}")
        break

driver.quit()

pd.DataFrame(data).to_csv("tourism_companies.csv", index=False, encoding='utf-8-sig')
print(f" Saved {len(data)} companies.")