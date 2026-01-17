import csv
import time
from pathlib import Path
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_input_files/uniflorida_input_latest.csv"
# CSV_OUTPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_uniflorida_latest_2.csv"

# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

# driver = webdriver.Chrome(options=chrome_options)
# wait = WebDriverWait(driver, 45)



# def scroll_to_load_all():
#     print("Scrolling to load all programs...")
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
#     print(f"Loading UF Catalog: {page_url}")
#     driver.get(page_url)
    
#     try:
#         # Wait for the exact class: filter-items list
#         wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".filter-items.list")))
#         print("Found .filter-items.list container")
#     except:
#         print("ERROR: .filter-items.list not found")
#         return []
    
#     scroll_to_load_all()
    
#     programs = []
#     # Target all <a> inside .filter-items.list
#     a_elems = driver.find_elements(By.CSS_SELECTOR, ".filter-items.list a")
#     print(f"Found {len(a_elems)} program links")
    
#     seen = set()
#     for a in a_elems:
#         try:
#             href = a.get_attribute("href")
#             if not href or href in seen or '#' in href or not href.strip():
#                 continue
#             seen.add(href)
            
#             name = a.text.strip()
#             if not name:
#                 # Fallback: use textContent if .text is empty
#                 name = driver.execute_script("return arguments[0].textContent.trim();", a)
#                 if not name:
#                     continue
            
#             url = urljoin(page_url, href)
            
#             programs.append({
#                 "program_name": name,
#                 "programUrl": url
#             })
#         except Exception as e:
#             print(f"Warning: {e}")
#             continue
    
#     print(f"Successfully extracted {len(programs)} programs")
#     return programs

# # ----------------------------- MAIN -----------------------------
# def main():
#     input_path = Path(CSV_INPUT)
#     output_path = Path(CSV_OUTPUT)
#     if not input_path.exists():
#         print(f"Input not found: {CSV_INPUT}")
#         return
    
#     file_exists = output_path.exists()
    
#     with open(input_path, newline='', encoding='utf-8') as infile:
#         reader = csv.DictReader(infile)
#         input_fieldnames = reader.fieldnames
#         scraped_fields = ["program_name", "programUrl"]
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
#                     continue
#                 print(f"\n=== {uni_name} ===")
#                 print(f"URL: {listing_url}")
#                 try:
#                     programs = extract_programs_from_listing(listing_url)
#                     if not programs:
#                         print(" → No programs extracted.")
#                         output_row = row.copy()
#                         for f in scraped_fields:
#                             output_row[f] = ""
#                         writer.writerow(output_row)
#                     else:
#                         count = 0
#                         for p in programs:
#                             output_row = row.copy()
#                             output_row.update(p)
#                             writer.writerow(output_row)
#                             count += 1
#                         print(f" → Successfully saved {count} programs")
#                 except Exception as e:
#                     print(f" → Error: {e}")
#                     output_row = row.copy()
#                     for f in scraped_fields:
#                         output_row[f] = ""
#                     writer.writerow(output_row)
#     driver.quit()
#     print(f"\nDone! Output: {CSV_OUTPUT}")

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

# ----------------------------- CONFIG -----------------------------
CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_input_files/uniflorida_grad_input_latest.csv"
CSV_OUTPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_uniflorida_grad_latest.csv"


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 45)

def scroll_to_load_all():
    print("Scrolling to ensure full load...")
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
    print(f"Loading UF Graduate Catalog: {page_url}")
    driver.get(page_url)
    
    try:
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "sitemap")))
        print("Found az_sitemap classes")
    except:
        print("ERROR: Could not find az_sitemap")
        return []
    
    scroll_to_load_all()
    
    programs = []
    # Get ALL .az_sitemap divs (there are multiple, each with program data)
    sitemaps = driver.find_elements(By.CLASS_NAME, "sitemap")
    print(f"Found {len(sitemaps)} az_sitemap divs")
    
    seen = set()
    for sitemap in sitemaps:
        a_elems = sitemap.find_elements(By.TAG_NAME, "a")
        for a in a_elems:
            try:
                href = a.get_attribute("href")
                if not href or href in seen or '#' in href or not href.strip():
                    continue
                seen.add(href)
                
                name = a.text.strip()
                if not name:
                    name = driver.execute_script("return arguments[0].textContent.trim();", a)
                    if not name:
                        continue
                
                url = urljoin(page_url, href)
                
                programs.append({
                    "program_name": name,
                    "programUrl": url
                })
            except Exception as e:
                print(f"Warning on link: {e}")
                continue
    
    print(f"Successfully extracted {len(programs)} graduate programs from all az_sitemap")
    return programs

# ----------------------------- MAIN -----------------------------
def main():
    input_path = Path(CSV_INPUT)
    output_path = Path(CSV_OUTPUT)
    if not input_path.exists():
        print(f"Input not found: {CSV_INPUT}")
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
                    continue
                print(f"\n=== {uni_name} ===")
                print(f"URL: {listing_url}")
                try:
                    programs = extract_programs_from_listing(listing_url)
                    if not programs:
                        print(" → No programs extracted.")
                        output_row = row.copy()
                        for f in scraped_fields:
                            output_row[f] = ""
                        writer.writerow(output_row)
                    else:
                        count = 0
                        for p in programs:
                            output_row = row.copy()
                            output_row.update(p)
                            writer.writerow(output_row)
                            count += 1
                        print(f" → Successfully saved {count} programs")
                except Exception as e:
                    print(f" → Error: {e}")
                    output_row = row.copy()
                    for f in scraped_fields:
                        output_row[f] = ""
                    writer.writerow(output_row)
    driver.quit()
    print(f"\nDone! Output: {CSV_OUTPUT}")

if __name__ == "__main__":
    main()