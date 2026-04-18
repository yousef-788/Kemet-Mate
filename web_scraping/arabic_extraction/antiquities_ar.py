import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Start the browser
driver = webdriver.Chrome()
driver.get("https://mota.gov.eg/ar/%D8%A7%D9%84%D8%A2%D8%AB%D8%A7%D8%B1-%D9%88%D8%A7%D9%84%D9%85%D8%AA%D8%A7%D8%AD%D9%81/%D8%A7%D9%84%D9%85%D8%AC%D9%84%D8%B3-%D8%A7%D9%84%D8%A3%D8%B9%D9%84%D9%89-%D9%84%D9%84%D8%A2%D8%AB%D8%A7%D8%B1/%D8%AF%D9%84%D9%8A%D9%84-%D8%A7%D9%84%D9%85%D9%88%D8%A7%D9%82%D8%B9-%D8%A7%D9%84%D8%A3%D8%AB%D8%B1%D9%8A%D8%A9-%D8%A7%D9%84%D9%85%D9%81%D8%AA%D9%88%D8%AD%D8%A9-%D9%84%D9%84%D8%B2%D9%8A%D8%A7%D8%B1%D8%A9-%D8%AC%D8%AF%D9%8A%D8%AF/")

time.sleep(5) 

print("Initiating patient scrolling protocol with Strike System...")

# ==========================================
# "STRIKE SYSTEM" SCROLL LOGIC
# ==========================================
body = driver.find_element(By.TAG_NAME, 'body')
previous_count = 0
strikes = 0

while strikes < 3:
    for _ in range(8):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)
        
    time.sleep(3)
    
    current_links = driver.find_elements(By.CSS_SELECTOR, 'section.ministry__reference_listing div.row a')
    current_count = len(current_links)
    
    print(f"Currently found {current_count} total links...")
    
    if current_count == previous_count:
        strikes += 1
        print(f"No new links found. Strike {strikes} of 3. Waiting longer for server...")
        time.sleep(4) 
        body.send_keys(Keys.PAGE_UP)
        time.sleep(1)
        body.send_keys(Keys.PAGE_DOWN)
        body.send_keys(Keys.PAGE_DOWN)
    else:
        strikes = 0 
        
    previous_count = current_count

print("Reached the absolute end of the page! Proceeding to scrape...")

# ==========================================
# GRAB AND CLEAN THE LINKS
# ==========================================
urls = [link.get_attribute('href') for link in current_links if link.get_attribute('href')]
urls = list(set(urls)) 

print(f"\nFinal Count: {len(urls)} UNIQUE sites to scrape. Starting data extraction...\n")

data = []

# ==========================================
# VISIT EACH URL AND EXTRACT DATA
# ==========================================
for url in urls:
    driver.get(url)
    time.sleep(5)
    
    name = "Not Found"
    desc = "Not Found"
    opening_time = "Not Found"
    closing_time = "Not Found"
    location = "Not Found"
    ticket_url = "None"
    
    # New variables for all 4 price types
    price_adult_foreign = "N/A"
    price_student_foreign = "N/A"
    price_adult_egyptian = "N/A"
    price_student_egyptian = "N/A"
    
    try:
        name_element = driver.find_element(By.CSS_SELECTOR, 'div.generic-banner__content')
        name = name_element.text.strip()
    except:
        pass
    
    try:
        paragraphs = driver.find_elements(By.CSS_SELECTOR, 'div.article__text p')
        clean_desc_lines = []
        for p in paragraphs:
            p_text = p.text.strip()
            if "للحصول على تجربة" in p_text or "لشراء تذكرة" in p_text or "لمزيد من المعلومات" in p_text:
                break
            if p_text: 
                clean_desc_lines.append(p_text)
        desc = "\n".join(clean_desc_lines)
    except:
        pass
        
    try:
        raw_time_text = driver.find_element(By.CSS_SELECTOR, 'body > div.container > div > div > div:nth-child(2) > div.section__text').text
        if "من" in raw_time_text and "إلى" in raw_time_text:
            parts = raw_time_text.split("إلى")
            opening_time = parts[0].replace("من", "").strip()
            closing_time = parts[1].strip()
        else:
            opening_time = raw_time_text
            closing_time = raw_time_text
    except:
        pass

    try:
        location = driver.find_element(By.CSS_SELECTOR, 'body > div.container > div > div > div:nth-child(4)').text
    except:
        pass

    try:
        ticket_element = driver.find_element(By.CSS_SELECTOR, 'div.article__text a[href*="egymonuments.com"]')
        ticket_url = ticket_element.get_attribute('href')
    except:
        pass 

    # ==========================================
    # BULLETPROOF TICKET SCRAPING LOGIC
    # ==========================================
    if ticket_url != "None":
        try:
            # This outer Try/Except catches the broken links!
            driver.get(ticket_url)
            time.sleep(4) 
            
            # 1. Scrape Foreign Prices
            try:
                foreign_rows = driver.find_elements(By.CSS_SELECTOR, '#pills-OtherNationality table.table tbody tr')
                for row in foreign_rows:
                    cols = row.find_elements(By.TAG_NAME, 'td')
                    if len(cols) >= 2:
                        v_type = cols[0].text.strip().lower()
                        price = cols[1].text.strip()
                        if 'adult' in v_type:
                            price_adult_foreign = price
                        elif 'student' in v_type:
                            price_student_foreign = price
            except:
                pass 

            # 2. Scrape Egyptian Prices (Using their exact HTML spelling: pills-Egyption)
            try:
                egyptian_rows = driver.find_elements(By.CSS_SELECTOR, '#pills-Egyption table.table tbody tr')
                for row in egyptian_rows:
                    cols = row.find_elements(By.TAG_NAME, 'td')
                    if len(cols) >= 2:
                        v_type = cols[0].text.strip().lower()
                        price = cols[1].text.strip()
                        if 'adult' in v_type:
                            price_adult_egyptian = price
                        elif 'student' in v_type:
                            price_student_egyptian = price
            except:
                pass 
                
        except Exception as e:
            print(f" [!] Warning: Broken ticket link provided by website for {name}")

    data.append({
        'name': name,
        'url': url,
        'description': desc,
        'opening_time': opening_time,
        'closing_time': closing_time,
        'location': location,
        'reservation_link': ticket_url,
        'price_adult_foreign': price_adult_foreign,
        'price_student_foreign': price_student_foreign,
        'price_adult_egyptian': price_adult_egyptian,
        'price_student_egyptian': price_student_egyptian
    }) 
    
    print(f"Successfully scraped: {name} | F. Adult: {price_adult_foreign} | E. Adult: {price_adult_egyptian}")

driver.quit()

# ==========================================
# EXPORT TO CSV
# ==========================================
df = pd.DataFrame(data)

df = df[['name', 'location', 'opening_time', 'closing_time', 'price_adult_foreign', 'price_student_foreign', 'price_adult_egyptian', 'price_student_egyptian', 'reservation_link', 'description', 'url']] 

df.to_csv("kemet_mate_antiquities_Ar_final.csv", index=False, encoding='utf-8-sig')
print("Data saved successfully!")