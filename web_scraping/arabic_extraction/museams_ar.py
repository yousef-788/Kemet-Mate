import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Start the browser and go to the MUSEUMS directory
driver = webdriver.Chrome()
driver.get("https://mota.gov.eg/ar/%D8%A7%D9%84%D8%A2%D8%AB%D8%A7%D8%B1-%D9%88%D8%A7%D9%84%D9%85%D8%AA%D8%A7%D8%AD%D9%81/%D8%A7%D9%84%D9%85%D8%AC%D9%84%D8%B3-%D8%A7%D9%84%D8%A3%D8%B9%D9%84%D9%89-%D9%84%D9%84%D8%A2%D8%AB%D8%A7%D8%B1/%D8%AF%D9%84%D9%8A%D9%84-%D9%85%D8%AA%D8%A7%D8%AD%D9%81-%D8%A7%D9%84%D8%A2%D8%AB%D8%A7%D8%B1-%D8%A7%D9%84%D9%85%D9%81%D8%AA%D9%88%D8%AD%D8%A9-%D9%84%D9%84%D8%B2%D9%8A%D8%A7%D8%B1%D8%A9-%D8%AC%D8%AF%D9%8A%D8%AF/")

# Wait for the initial DOM to load properly
time.sleep(5) 

print("Initiating patient scrolling protocol with Strike System...")

# ==========================================
# 1. THE "STRIKE SYSTEM" SCROLL LOGIC
# ==========================================
body = driver.find_element(By.TAG_NAME, 'body')
previous_count = 0
strikes = 0

while strikes < 3:
    # Press the "Page Down" key 8 times in a row to simulate human scrolling
    for _ in range(8):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)
        
    # Give the network 3 seconds to fetch the new governorate data
    time.sleep(3)
    
    # Count how many links we have successfully exposed so far
    current_links = driver.find_elements(By.CSS_SELECTOR, 'section.ministry__reference_listing div.row a')
    current_count = len(current_links)
    
    print(f"Currently found {current_count} total museum links...")
    
    # If the count hasn't gone up, we issue a strike
    if current_count == previous_count:
        strikes += 1
        print(f"No new links found. Strike {strikes} of 3. Waiting longer for server...")
        
        # Extra wait time in case of a slow server connection
        time.sleep(4) 
        
        # "Wiggle" the page up and down using the keyboard to bump the lazy-load trigger
        body.send_keys(Keys.PAGE_UP)
        time.sleep(1)
        body.send_keys(Keys.PAGE_DOWN)
        body.send_keys(Keys.PAGE_DOWN)
    else:
        # If we found new links, reset the strikes back to 0!
        strikes = 0 
        
    previous_count = current_count

print("Reached the absolute end of the page! Proceeding to scrape...")

# ==========================================
# GRAB AND CLEAN THE LINKS
# ==========================================
urls = [link.get_attribute('href') for link in current_links if link.get_attribute('href')]
urls = list(set(urls)) # Remove duplicates

print(f"\nFinal Count: {len(urls)} UNIQUE museums to scrape. Starting data extraction...\n")

data = []

# ==========================================
# VISIT EACH URL AND EXTRACT DATA
# ==========================================
for url in urls:
    driver.get(url)
    time.sleep(5)
    
    # Set defaults for the current museum
    name = "Not Found"
    desc = "Not Found"
    opening_time = "Not Found"
    closing_time = "Not Found"
    location = "Not Found"
    ticket_url = "None"
    price_adult = "N/A"
    price_student = "N/A"
    
    #  Get Museum Name
    try:
        name_element = driver.find_element(By.CSS_SELECTOR, 'div.generic-banner__content')
        name = name_element.text.strip()
    except:
        pass
    
    # Get and Clean Description
    try:
        paragraphs = driver.find_elements(By.CSS_SELECTOR, 'div.article__text p')
        clean_desc_lines = []
        for p in paragraphs:
            p_text = p.text.strip()
            # Stop grabbing text if we hit the standard contact/ticket footer
            if "للحصول على تجربة" in p_text or "لشراء تذكرة" in p_text or "لمزيد من المعلومات" in p_text:
                break
            if p_text: 
                clean_desc_lines.append(p_text)
        desc = "\n".join(clean_desc_lines)
    except:
        pass
        
    #  Get and Split Time
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

    #  Get Location
    try:
        location = driver.find_element(By.CSS_SELECTOR, 'body > div.container > div > div > div:nth-child(4)').text
    except:
        pass

    #  Find Online Reservation Link
    try:
        ticket_element = driver.find_element(By.CSS_SELECTOR, 'div.article__text a[href*="egymonuments.com"]')
        ticket_url = ticket_element.get_attribute('href')
    except:
        pass 

    #  If Ticket Link Exists, Visit and Scrape Prices
    if ticket_url != "None":
        driver.get(ticket_url)
        time.sleep(4) 
        
        try:
            price_rows = driver.find_elements(By.CSS_SELECTOR, '#pills-OtherNationality table.table tbody tr')
            
            for row in price_rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 2:
                    visitor_type = cols[0].text.strip().lower()
                    price = cols[1].text.strip()
                    
                    if 'adult' in visitor_type:
                        price_adult = price
                    elif 'student' in visitor_type:
                        price_student = price
        except:
            pass 

    # G. Append all data to our list
    data.append({
        'name': name,
        'url': url,
        'description': desc,
        'opening_time': opening_time,
        'closing_time': closing_time,
        'location': location,
        'reservation_link': ticket_url,
        'price_adult_foreign': price_adult,
        'price_student_foreign': price_student
    }) 
    
    print(f"Successfully scraped: {name} | Tickets: {price_adult}")

# Close the browser when the loop finishes
driver.quit()

# ==========================================
# EXPORT TO CSV
# ==========================================
df = pd.DataFrame(data)

df = df[['name', 'location', 'opening_time', 'closing_time', 'price_adult_foreign', 'price_student_foreign', 'reservation_link', 'description', 'url']] 

df.to_csv("museums_ar.csv", index=False, encoding='utf-8-sig')
print("All done!  data saved to museums_ar.csv")