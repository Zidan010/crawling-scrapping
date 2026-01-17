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
# CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_input_files/uonnecticut_input_latest_undergrad_major.csv"
# CSV_OUTPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_uconnecticut_undergrad_latest.csv"


# # Headless Chrome setup
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36")

# driver = webdriver.Chrome(options=chrome_options)
# wait = WebDriverWait(driver, 30)

# # ----------------------------- HELPERS -----------------------------
# def clean_text(text):
#     return re.sub(r'\s+', ' ', text).strip() if text else ""

# def scroll_to_load_all():
#     print(" Scrolling to ensure all content is loaded...")
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     while True:
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)
#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             break
#         last_height = new_height
#     time.sleep(2)  # Final wait

# def extract_programs_from_listing(page_url):
#     print(f" Loading listing page: {page_url}")
#     driver.get(page_url)
    
#     # Wait for az_sitemap to appear
#     try:
#         wait.until(EC.presence_of_element_located((By.CLASS_NAME, "az_sitemap")))
#         print(" Found az_sitemap")
#     except:
#         print(" ERROR: Could not find az_sitemap — page structure changed or blocked?")
#         return []
    
#     scroll_to_load_all()
    
#     # Find the first div.az_sitemap
#     divs = driver.find_elements(By.CLASS_NAME, "az_sitemap")
#     if not divs:
#         return []
#     div = divs[0]
    
#     # Extract programs
#     programs = []
#     a_elems = div.find_elements(By.TAG_NAME, "a")
#     print(f" Found {len(a_elems)} links, filtering...")
#     for a in a_elems:
#         href = a.get_attribute("href")
#         if href and href.startswith(page_url.split('#')[0] + "/undergraduate"):  # Filter relevant hrefs
#             try:
#                 full_text = clean_text(a.text)
#                 if '(' in full_text and full_text.endswith(')'):
#                     parts = full_text.rsplit(' (', 1)
#                     program_name = parts[0].strip()
#                     degree_type = parts[1][:-1].strip()
#                 else:
#                     program_name = full_text
#                     degree_type = ""
                
#                 program_url = href  # Already full url? No, relative, but in html it's relative
#                 program_url = urljoin(page_url, href)
                
#                 if program_name and program_url:
#                     programs.append({
#                         "program_name": program_name,
#                         "degree_type": degree_type,
#                         "programUrl": program_url
#                     })
#             except Exception as e:
#                 print(f" Warning: Failed to parse one program link → {e}")
#                 continue
    
#     print(f" Extracted {len(programs)} programs")
#     return programs

# # ----------------------------- MAIN -----------------------------
# def main():
#     input_path = Path(CSV_INPUT)
#     output_path = Path(CSV_OUTPUT)
#     if not input_path.exists():
#         print(f"Input CSV not found: {CSV_INPUT}")
#         return
    
#     file_exists = output_path.exists()
    
#     # Read input to preserve original columns
#     with open(input_path, newline='', encoding='utf-8') as infile:
#         reader = csv.DictReader(infile)
#         input_fieldnames = reader.fieldnames  # All original columns
#         scraped_fields = ["program_name", "degree_type", "programUrl"]
#         # Preserve order: original first, then append new fields
#         output_fieldnames = input_fieldnames + [f for f in scraped_fields if f not in input_fieldnames]
    
#     # Now process
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
#                         # Still write original row with empty scraped fields
#                         output_row = row.copy()
#                         for field in scraped_fields:
#                             output_row[field] = ""
#                         writer.writerow(output_row)
#                     else:
#                         total_programs = 0
#                         for program in programs:
#                             output_row = row.copy()  # Keep ALL original input data
#                             output_row.update(program)  # Add program info
#                             writer.writerow(output_row)
#                             total_programs += 1
#                         if total_programs == 0:
#                             # If no programs at all, write originals
#                             output_row = row.copy()
#                             for field in scraped_fields:
#                                 output_row[field] = ""
#                             writer.writerow(output_row)
#                         print(f" → Successfully extracted {total_programs} programs")
#                 except Exception as e:
#                     print(f" → Critical error: {e}")
#                     # Write original row on error
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
# import re
# from pathlib import Path
# from urllib.parse import urljoin
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # ----------------------------- CONFIG -----------------------------
# CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_input_files/uonnecticut_input_latest_undergrad_minor.csv"
# CSV_OUTPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_uconnecticut_undergrad_minor_latest.csv"


# # Headless Chrome setup
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36")

# driver = webdriver.Chrome(options=chrome_options)
# wait = WebDriverWait(driver, 30)

# # ----------------------------- HELPERS -----------------------------
# def clean_text(text):
#     return re.sub(r'\s+', ' ', text).strip() if text else ""

# def scroll_to_load_all():
#     print(" Scrolling to ensure all content is loaded...")
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     while True:
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)
#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             break
#         last_height = new_height
#     time.sleep(2)  # Final wait

# def extract_programs_from_listing(page_url):
#     print(f" Loading listing page: {page_url}")
#     driver.get(page_url)
    
#     # Wait for az_sitemap to appear
#     try:
#         wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "az_sitemap")))
#         print(" Found az_sitemap(s)")
#     except:
#         print(" ERROR: Could not find az_sitemap — page structure changed or blocked?")
#         return []
    
#     scroll_to_load_all()
    
#     # Find all div.az_sitemap
#     divs = driver.find_elements(By.CLASS_NAME, "az_sitemap")
#     if len(divs) < 2:
#         return []
#     div = divs[1]  # Second one for minors
    
#     # Extract programs
#     programs = []
#     a_elems = div.find_elements(By.TAG_NAME, "a")
#     print(f" Found {len(a_elems)} links, filtering...")
#     for a in a_elems:
#         href = a.get_attribute("href")
#         if href and '#' not in href:
#             try:
#                 full_text = clean_text(a.text)
#                 if '(' in full_text and full_text.endswith(')'):
#                     parts = full_text.rsplit(' (', 1)
#                     program_name = parts[0].strip()
#                     degree_type = parts[1][:-1].strip()
#                 else:
#                     program_name = full_text.replace(' Minor', '') if ' Minor' in full_text else full_text
#                     degree_type = "Minor" if ' Minor' in full_text else ""
                
#                 program_url = urljoin(page_url, href)
                
#                 if program_name and program_url:
#                     programs.append({
#                         "program_name": program_name,
#                         "degree_type": degree_type,
#                         "programUrl": program_url
#                     })
#             except Exception as e:
#                 print(f" Warning: Failed to parse one program link → {e}")
#                 continue
    
#     print(f" Extracted {len(programs)} programs")
#     return programs

# # ----------------------------- MAIN -----------------------------
# def main():
#     input_path = Path(CSV_INPUT)
#     output_path = Path(CSV_OUTPUT)
#     if not input_path.exists():
#         print(f"Input CSV not found: {CSV_INPUT}")
#         return
    
#     file_exists = output_path.exists()
    
#     # Read input to preserve original columns
#     with open(input_path, newline='', encoding='utf-8') as infile:
#         reader = csv.DictReader(infile)
#         input_fieldnames = reader.fieldnames  # All original columns
#         scraped_fields = ["program_name", "degree_type", "programUrl"]
#         # Preserve order: original first, then append new fields
#         output_fieldnames = input_fieldnames + [f for f in scraped_fields if f not in input_fieldnames]
    
#     # Now process
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
#                         # Still write original row with empty scraped fields
#                         output_row = row.copy()
#                         for field in scraped_fields:
#                             output_row[field] = ""
#                         writer.writerow(output_row)
#                     else:
#                         total_programs = 0
#                         for program in programs:
#                             output_row = row.copy()  # Keep ALL original input data
#                             output_row.update(program)  # Add program info
#                             writer.writerow(output_row)
#                             total_programs += 1
#                         if total_programs == 0:
#                             # If no programs at all, write originals
#                             output_row = row.copy()
#                             for field in scraped_fields:
#                                 output_row[field] = ""
#                             writer.writerow(output_row)
#                         print(f" → Successfully extracted {total_programs} programs")
#                 except Exception as e:
#                     print(f" → Critical error: {e}")
#                     # Write original row on error
#                     output_row = row.copy()
#                     for field in scraped_fields:
#                         output_row[field] = ""
#                     writer.writerow(output_row)
#     driver.quit()
#     print(f"\nAll done! Saved to {CSV_OUTPUT}")

# if __name__ == "__main__":
#     main()




########### grad

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
# CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_input_files/uonnecticut_input_latest_grad_cert.csv"
# CSV_OUTPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_uconnecticut_grad_cert_latest.csv"

# # Headless Chrome setup
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36")

# driver = webdriver.Chrome(options=chrome_options)
# wait = WebDriverWait(driver, 30)

# # ----------------------------- HELPERS -----------------------------
# def clean_text(text):
#     return re.sub(r'\s+', ' ', text).strip() if text else ""

# def scroll_to_load_all():
#     print(" Scrolling to ensure all content is loaded...")
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     while True:
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)
#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             break
#         last_height = new_height
#     time.sleep(2)  # Final wait

# def extract_programs_from_listing(page_url):
#     print(f" Loading listing page: {page_url}")
#     driver.get(page_url)
    
#     # Wait for az_sitemap to appear
#     try:
#         wait.until(EC.presence_of_element_located((By.CLASS_NAME, "az_sitemap")))
#         print(" Found az_sitemap")
#     except:
#         print(" ERROR: Could not find az_sitemap — page structure changed or blocked?")
#         return []
    
#     scroll_to_load_all()
    
#     # Find the first div.az_sitemap for graduate programs
#     divs = driver.find_elements(By.CLASS_NAME, "az_sitemap")
#     if not divs:
#         return []
#     div = divs[1]  # First one for degree programs
    
#     # Extract programs
#     programs = []
#     a_elems = div.find_elements(By.TAG_NAME, "a")
#     print(f" Found {len(a_elems)} links, filtering...")
#     for a in a_elems:
#         href = a.get_attribute("href")
#         if href and '#' not in href:
#             try:
#                 full_text = clean_text(a.text)
#                 if '(' in full_text and full_text.endswith(')'):
#                     parts = full_text.rsplit(' (', 1)
#                     program_name = parts[0].strip()
#                     degree_type = parts[1][:-1].strip()
#                 else:
#                     program_name = full_text
#                     degree_type = ""
                
#                 program_url = urljoin(page_url, href)
                
#                 if program_name and program_url:
#                     programs.append({
#                         "program_name": program_name,
#                         "degree_type": degree_type,
#                         "programUrl": program_url
#                     })
#             except Exception as e:
#                 print(f" Warning: Failed to parse one program link → {e}")
#                 continue
    
#     print(f" Extracted {len(programs)} programs")
#     return programs

# # ----------------------------- MAIN -----------------------------
# def main():
#     input_path = Path(CSV_INPUT)
#     output_path = Path(CSV_OUTPUT)
#     if not input_path.exists():
#         print(f"Input CSV not found: {CSV_INPUT}")
#         return
    
#     file_exists = output_path.exists()
    
#     # Read input to preserve original columns
#     with open(input_path, newline='', encoding='utf-8') as infile:
#         reader = csv.DictReader(infile)
#         input_fieldnames = reader.fieldnames  # All original columns
#         scraped_fields = ["program_name", "degree_type", "programUrl"]
#         # Preserve order: original first, then append new fields
#         output_fieldnames = input_fieldnames + [f for f in scraped_fields if f not in input_fieldnames]
    
#     # Now process
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
#                         # Still write original row with empty scraped fields
#                         output_row = row.copy()
#                         for field in scraped_fields:
#                             output_row[field] = ""
#                         writer.writerow(output_row)
#                     else:
#                         total_programs = 0
#                         for program in programs:
#                             output_row = row.copy()  # Keep ALL original input data
#                             output_row.update(program)  # Add program info
#                             writer.writerow(output_row)
#                             total_programs += 1
#                         if total_programs == 0:
#                             # If no programs at all, write originals
#                             output_row = row.copy()
#                             for field in scraped_fields:
#                                 output_row[field] = ""
#                             writer.writerow(output_row)
#                         print(f" → Successfully extracted {total_programs} programs")
#                 except Exception as e:
#                     print(f" → Critical error: {e}")
#                     # Write original row on error
#                     output_row = row.copy()
#                     for field in scraped_fields:
#                         output_row[field] = ""
#                     writer.writerow(output_row)
#     driver.quit()
#     print(f"\nAll done! Saved to {CSV_OUTPUT}")

# if __name__ == "__main__":
#     main()











########################################

import csv
import time
import re
from pathlib import Path
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------------------- CONFIG -----------------------------
CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_input_files/uonnecticut_input_latest_grad_dual.csv"
CSV_OUTPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_uconnecticut_grad_dual_latest.csv"



# Headless Chrome setup
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)

# ----------------------------- HELPERS -----------------------------
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip() if text else ""

def scroll_to_load_all():
    print(" Scrolling to ensure all content is loaded...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    time.sleep(2)  # Final wait

def extract_programs_from_listing(page_url):
    print(f" Loading listing page: {page_url}")
    driver.get(page_url)
    
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sitemap")))
        print(" Found az_sitemap")
    except:
        print(" ERROR: Could not find az_sitemap — page structure changed or blocked?")
        return []
    
    scroll_to_load_all()
    
    # For CERTIFICATE programs → take the SECOND az_sitemap
    divs = driver.find_elements(By.CLASS_NAME, "sitemap")
    if len(divs) < 0:
        print(f" Only {len(divs)} az_sitemap found - expected at least 2 for certificates")
        return []
    div = divs[0] 
    
    # Extract programs
    programs = []
    a_elems = div.find_elements(By.TAG_NAME, "a")
    print(f" Found {len(a_elems)} links in the second az_sitemap, filtering...")
    for a in a_elems:
        href = a.get_attribute("href")
        if href and '#' not in href:
            try:
                full_text = clean_text(a.text)
                if '(' in full_text and full_text.endswith(')'):
                    parts = full_text.rsplit(' (', 1)
                    program_name = parts[0].strip()
                    degree_type = parts[1][:-1].strip()
                else:
                    program_name = full_text.strip()
                    degree_type = "Certificate"  # Default for certificates
                
                program_url = urljoin(page_url, href)
                
                if program_name and program_url:
                    programs.append({
                        "program_name": program_name,
                        "degree_type": degree_type,
                        "programUrl": program_url
                    })
            except Exception as e:
                print(f" Warning: Failed to parse one program link → {e}")
                continue
    
    print(f" Extracted {len(programs)} certificate programs")
    return programs

# ----------------------------- MAIN -----------------------------
def main():
    input_path = Path(CSV_INPUT)
    output_path = Path(CSV_OUTPUT)
    if not input_path.exists():
        print(f"Input CSV not found: {CSV_INPUT}")
        return
    
    file_exists = output_path.exists()
    
    # Read input to preserve original columns
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        input_fieldnames = reader.fieldnames
        scraped_fields = ["program_name", "degree_type", "programUrl"]
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
                        if total_programs == 0:
                            output_row = row.copy()
                            for field in scraped_fields:
                                output_row[field] = ""
                            writer.writerow(output_row)
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