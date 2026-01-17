# import csv
# import time
# import re
# from pathlib import Path
# from urllib.parse import urljoin
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # ----------------------------- CONFIG -----------------------------
# CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_input_files/stevensit_input_latest.csv"
# CSV_OUTPUT = "../crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_stevensit_latest.csv"

# # Headless Chrome setup
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

# driver = webdriver.Chrome(options=chrome_options)
# wait = WebDriverWait(driver, 45)

# # ----------------------------- HELPERS -----------------------------
# def clean_text(text):
#     return re.sub(r'\s+', ' ', text).strip() if text else ""

# def scroll_to_load_all():
#     print("Scrolling to ensure all content is loaded...")
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     while True:
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(3)
#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             break
#         last_height = new_height
#     time.sleep(3)

# def extract_programs_from_listing(page_url):
#     print(f"Loading listing page: {page_url}")
#     driver.get(page_url)
    
#     # Wait for the first program item
#     try:
#         wait.until(EC.presence_of_element_located((By.CLASS_NAME, "listing-item__content")))
#         print("Found listing-item__content")
#     except:
#         print("ERROR: Could not find listing-item__content — page structure changed or blocked?")
#         return []
    
#     scroll_to_load_all()
    
#     programs = []
#     page_count = 1
#     while True:
#         print(f"Processing page {page_count}")
        
#         # Find all program blocks on current page
#         items = driver.find_elements(By.CLASS_NAME, "listing-item__content")
#         print(f"Found {len(items)} programs on this page")
        
#         for item in items:
#             try:
#                 # Get title link
#                 title_link = item.find_element(By.CSS_SELECTOR, ".listing-item__title-link")
#                 program_name = clean_text(title_link.text)
#                 program_url = title_link.get_attribute("href")
                
#                 # Optional: Get school/college
#                 school = ""
#                 try:
#                     school_elem = item.find_element(By.CLASS_NAME, "listing-item__body-block")
#                     school = clean_text(school_elem.text)
#                 except:
#                     pass
                
#                 # Optional: Get tags (degree type, format, department)
#                 tags = []
#                 try:
#                     tag_list = item.find_elements(By.CSS_SELECTOR, ".listing-item__tag")
#                     tags = [clean_text(t.text) for t in tag_list]
#                 except:
#                     pass
                
#                 if program_name and program_url:
#                     programs.append({
#                         "program_name": program_name,
#                         "programUrl": program_url,
#                         "school": school,
#                         "tags": ", ".join(tags) if tags else ""
#                     })
#             except Exception as e:
#                 print(f"Warning: Failed to parse one item → {e}")
#                 continue
        
#         # Try to go to next page
#         try:
#             next_button = driver.find_element(By.CSS_SELECTOR, "a.next, .pagination-next a")
#             if "disabled" in next_button.get_attribute("class") or not next_button.is_enabled():
#                 print("No more pages")
#                 break
#             next_button.click()
#             time.sleep(4)  # Wait for next page to load
#             page_count += 1
#         except:
#             print("No next button or end of pagination")
#             break
    
#     print(f"Total extracted: {len(programs)} programs")
#     return programs

# # ----------------------------- MAIN -----------------------------
# def main():
#     input_path = Path(CSV_INPUT)
#     output_path = Path(CSV_OUTPUT)
#     if not input_path.exists():
#         print(f"Input CSV not found: {CSV_INPUT}")
#         return
    
#     file_exists = output_path.exists()
    
#     with open(input_path, newline='', encoding='utf-8') as infile:
#         reader = csv.DictReader(infile)
#         input_fieldnames = reader.fieldnames
#         scraped_fields = ["program_name", "programUrl", "school", "tags"]
#         output_fieldnames = input_fieldnames + [f for f in scraped_fields if f not in input_fieldnames]
    
#     with open(input_path, newline='', encoding='utf-8') as infile:
#         reader = csv.DictReader(infile)
#         with open(output_path, 'a', newline='', encoding='utf-8') as outfile:
#             writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
#             if not file_exists:
#                 writer.writeheader()
#             for row in reader:
#                 listing_url = row.get("degree_program_link", "").strip()
#                 uni_name = row.get("university_name", "Unknown University")
#                 if not listing_url:
#                     print("Skipping row — no degree_program_link")
#                     continue
#                 print(f"\n=== {uni_name} ===")
#                 print(f"URL: {listing_url}")
#                 try:
#                     programs = extract_programs_from_listing(listing_url)
#                     if not programs:
#                         print(" → No programs extracted.")
#                         output_row = row.copy()
#                         for field in scraped_fields:
#                             output_row[field] = ""
#                         writer.writerow(output_row)
#                     else:
#                         total_programs = 0
#                         for program in programs:
#                             output_row = row.copy()
#                             output_row.update(program)
#                             writer.writerow(output_row)
#                             total_programs += 1
#                         print(f" → Successfully extracted {total_programs} programs")
#                 except Exception as e:
#                     print(f" → Critical error: {e}")
#                     output_row = row.copy()
#                     for field in scraped_fields:
#                         output_row[field] = ""
#                     writer.writerow(output_row)
#     driver.quit()
#     print(f"\nAll done! Saved to {CSV_OUTPUT}")

# if __name__ == "__main__":
#     main()




# import csv
# import time
# from pathlib import Path
# from urllib.parse import urljoin
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# import re
# # ----------------------------- CONFIG -----------------------------
# CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_input_files/stevensit_input_latest.csv"
# CSV_OUTPUT = "../crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_stevensit_latest_2.csv"


# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

# driver = webdriver.Chrome(options=chrome_options)
# wait = WebDriverWait(driver, 45)

# # ----------------------------- HELPERS -----------------------------
# def clean_text(text):
#     return re.sub(r'\s+', ' ', text).strip() if text else ""

# def scroll_to_load_all():
#     print("Scrolling to ensure all content is loaded...")
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     while True:
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(3)
#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             break
#         last_height = new_height
#     time.sleep(3)  # Final wait

# def extract_programs_from_listing(page_url):
#     print(f" Loading listing page: {page_url}")
#     driver.get(page_url)
    
#     # Wait for listing-item to appear
#     try:
#         wait.until(EC.presence_of_element_located((By.CLASS_NAME, "listing-item__content")))
#         print(" Found listing-item__content")
#     except:
#         print(" ERROR: Could not find listing-item__content — page structure changed or blocked?")
#         return []
    
#     programs = []
#     page_count = 1
#     max_pages = 30  # Safety limit
    
#     while page_count <= max_pages:
#         print(f"Processing page {page_count}")
#         scroll_to_load_all()
        
#         items = driver.find_elements(By.CLASS_NAME, "listing-item__content")
#         print(f" Found {len(items)} programs on this page")
        
#         for item in items:
#             try:
#                 title_link = item.find_element(By.CSS_SELECTOR, ".listing-item__title-link")
#                 program_name = clean_text(title_link.text)
#                 program_url = title_link.get_attribute("href")
                
#                 school = ""
#                 try:
#                     school_elem = item.find_element(By.CLASS_NAME, "listing-item__body-block")
#                     school = clean_text(school_elem.text)
#                 except:
#                     pass
                
#                 tags = []
#                 try:
#                     tag_elems = item.find_elements(By.CLASS_NAME, "listing-item__tag")
#                     tags = [clean_text(t.text) for t in tag_elems]
#                 except:
#                     pass
                
#                 if program_name and program_url:
#                     programs.append({
#                         "program_name": program_name,
#                         "programUrl": program_url,
#                         "school": school,
#                         "tags": ", ".join(tags)
#                     })
#             except Exception as e:
#                 print(f" Warning: Failed to parse one program → {e}")
#                 continue
        
#         # Find Next item and check if disabled
#         try:
#             next_item = driver.find_element(By.CSS_SELECTOR, ".pagination__item--next")
#             if "pagination__item--disabled" in next_item.get_attribute("class"):
#                 print(" Next item is disabled - end of pages")
#                 break
            
#             next_button = next_item.find_element(By.TAG_NAME, "a")
#             old_first_name = clean_text(driver.find_element(By.CSS_SELECTOR, ".listing-item__title-link").text)
            
#             next_button.click()
#             time.sleep(5)
            
#             # Wait for new content - check if first program name changed
#             wait.until(lambda d: clean_text(d.find_element(By.CSS_SELECTOR, ".listing-item__title-link").text) != old_first_name)
#             print(" New page loaded")
#             page_count += 1
#         except TimeoutException:
#             print(" Timeout waiting for new page - end of pagination?")
#             break
#         except NoSuchElementException:
#             print(" No Next item found - end of pagination?")
#             break
#         except Exception as e:
#             print(f" Pagination error: {e} - stopping")
#             break
    
#     print(f"Total extracted: {len(programs)} programs")
#     return programs

# # ----------------------------- MAIN -----------------------------
# def main():
#     input_path = Path(CSV_INPUT)
#     output_path = Path(CSV_OUTPUT)
#     if not input_path.exists():
#         print(f"Input CSV not found: {CSV_INPUT}")
#         return
    
#     file_exists = output_path.exists()
    
#     with open(input_path, newline='', encoding='utf-8') as infile:
#         reader = csv.DictReader(infile)
#         input_fieldnames = reader.fieldnames
#         scraped_fields = ["program_name", "programUrl", "school", "tags"]
#         output_fieldnames = input_fieldnames + [f for f in scraped_fields if f not in input_fieldnames]
    
#     with open(input_path, newline='', encoding='utf-8') as infile:
#         reader = csv.DictReader(infile)
#         with open(output_path, 'a', newline='', encoding='utf-8') as outfile:
#             writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
#             if not file_exists:
#                 writer.writeheader()
#             for row in reader:
#                 listing_url = row.get("degree_program_link", "").strip()
#                 uni_name = row.get("university_name", "Unknown University")
#                 if not listing_url:
#                     print("Skipping row — no degree_program_link")
#                     continue
#                 print(f"\n=== {uni_name} ===")
#                 print(f"URL: {listing_url}")
#                 try:
#                     programs = extract_programs_from_listing(listing_url)
#                     if not programs:
#                         print(" → No programs extracted.")
#                         output_row = row.copy()
#                         for field in scraped_fields:
#                             output_row[field] = ""
#                         writer.writerow(output_row)
#                     else:
#                         total_programs = 0
#                         for program in programs:
#                             output_row = row.copy()
#                             output_row.update(program)
#                             writer.writerow(output_row)
#                             total_programs += 1
#                         print(f" → Successfully extracted {total_programs} programs")
#                 except Exception as e:
#                     print(f" → Critical error: {e}")
#                     output_row = row.copy()
#                     for field in scraped_fields:
#                         output_row[field] = ""
#                     writer.writerow(output_row)
#     driver.quit()
#     print(f"\nAll done! Saved to {CSV_OUTPUT}")

# if __name__ == "__main__":
#     main()





import csv
import time
from pathlib import Path
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ----------------------------- CONFIG -----------------------------
CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_input_files/stevensit_input_latest.csv"
CSV_OUTPUT = "../crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_stevensit_latest_4.csv"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 45)

def clean_text(text):
    return ' '.join(text.split()).strip() if text else ""

def scroll_to_load_all():
    print("Scrolling to load content...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    time.sleep(3)

def extract_programs_from_listing(page_url):
    print(f"Loading: {page_url}")
    driver.get(page_url)
    
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "listing-item__content")))
        print("Found listing-item__content")
    except:
        print("ERROR: listing-item__content not found")
        return []
    
    programs = []
    page_count = 1
    max_pages = 22  # Safety net - you said only 22 pages
    
    while page_count <= max_pages:
        print(f"\nProcessing page {page_count}")
        scroll_to_load_all()
        
        items = driver.find_elements(By.CLASS_NAME, "listing-item__content")
        print(f"  Found {len(items)} programs on page {page_count}")
        
        for item in items:
            try:
                title_link = item.find_element(By.CSS_SELECTOR, ".listing-item__title-link")
                program_name = clean_text(title_link.text)
                if not program_name:
                    program_name = driver.execute_script("return arguments[0].textContent.trim();", title_link)
                
                program_url = title_link.get_attribute("data-live-url")  # Clean URL!
                if not program_url:
                    program_url = title_link.get_attribute("href")
                
                if program_name and program_url and "stevens.edu/program/" in program_url:
                    programs.append({
                        "program_name": program_name,
                        "programUrl": program_url
                    })
            except Exception as e:
                print(f"  Warning parsing item: {e}")
                continue
        
        # Try to find and click Next button (more selectors)
        next_selectors = [
            ".pagination__item--next a",
            "a.next",
            ".pagination-next a",
            ".btn-next",
            "a[rel='next']",
            ".pagination a:last-child:not(.disabled)",
            "button.next",
            ".next-page a"
        ]
        
        next_button = None
        for sel in next_selectors:
            try:
                candidates = driver.find_elements(By.CSS_SELECTOR, sel)
                for cand in candidates:
                    if cand.is_displayed() and cand.is_enabled():
                        next_button = cand
                        print(f"  Found Next button using selector: {sel}")
                        break
                if next_button:
                    break
            except:
                continue
        
        if not next_button:
            print("  No Next button found after trying all selectors - end of pagination")
            break
        
        # Click with JavaScript (most reliable)
        try:
            old_first_name = clean_text(driver.find_element(By.CSS_SELECTOR, ".listing-item__title-link").text)
            driver.execute_script("arguments[0].click();", next_button)
            print("  Clicked Next button")
            time.sleep(5)
            
            # Wait for page change (new first title different)
            wait.until(lambda d: clean_text(d.find_element(By.CSS_SELECTOR, ".listing-item__title-link").text) != old_first_name)
            print("  New page content loaded")
            page_count += 1
        except Exception as e:
            print(f"  Failed to load next page: {e}")
            break
    
    print(f"\nTotal extracted: {len(programs)} programs across {page_count-1} pages")
    return programs

# ----------------------------- MAIN -----------------------------
def main():
    input_path = Path(CSV_INPUT)
    output_path = Path(CSV_OUTPUT)
    if not input_path.exists():
        print(f"Input CSV not found: {CSV_INPUT}")
        return
    
    file_exists = output_path.exists()
    
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        input_fieldnames = reader.fieldnames
        scraped_fields = ["program_name", "programUrl"]
        output_fieldnames = input_fieldnames + [f for f in scraped_fields if f not in input_fieldnames]
    
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        with open(output_path, 'a', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            if not file_exists:
                writer.writeheader()
            for row in reader:
                listing_url = row.get("degree_program_link", "").strip()
                uni_name = row.get("university_name", "Unknown University")
                if not listing_url:
                    print("Skipping row — no degree_program_link")
                    continue
                print(f"\n=== {uni_name} ===")
                print(f"URL: {listing_url}")
                try:
                    programs = extract_programs_from_listing(listing_url)
                    if not programs:
                        print(" → No programs extracted.")
                        output_row = row.copy()
                        for field in scraped_fields:
                            output_row[field] = ""
                        writer.writerow(output_row)
                    else:
                        total_programs = 0
                        for program in programs:
                            output_row = row.copy()
                            output_row.update(program)
                            writer.writerow(output_row)
                            total_programs += 1
                        print(f" → Successfully extracted {total_programs} programs")
                except Exception as e:
                    print(f" → Critical error: {e}")
                    output_row = row.copy()
                    for field in scraped_fields:
                        output_row[field] = ""
                    writer.writerow(output_row)
    driver.quit()
    print(f"\nAll done! Saved to {CSV_OUTPUT}")

if __name__ == "__main__":
    main()