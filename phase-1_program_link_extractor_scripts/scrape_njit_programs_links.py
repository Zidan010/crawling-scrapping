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
CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_input_files/njit_input_latest.csv"
CSV_OUTPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_njit_latest_2.csv"

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

def extract_programs_from_listing(page_url):
    print(f" Loading listing page: {page_url}")
    driver.get(page_url)
    
    # Wait for degree-finder-result-item to appear
    try:
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "degree-finder-result-item")))
        print(" Found degree-finder-result-item")
    except:
        print(" ERROR: Could not find degree-finder-result-item — page structure changed or blocked?")
        return []
    
    # Try to set items per page to 90
    try:
        ipp_select = driver.find_element(By.CSS_SELECTOR, "#degree-finder-sorts-and-ipp .w3-select:nth-of-type(2) select")
        driver.execute_script("arguments[0].classList.remove('fs-select-disabled');", ipp_select)
        driver.execute_script("arguments[0].value = '90';", ipp_select)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", ipp_select)
        time.sleep(5)
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "degree-finder-result-item")))
        print(" Set items per page to 90")
    except Exception as e:
        print(f" Could not set items per page: {e}")
    
    programs = []
    previous_first_title = None
    while True:
        items = driver.find_elements(By.CLASS_NAME, "degree-finder-result-item")
        if not items:
            break
        
        current_first_title = clean_text(items[0].find_element(By.CLASS_NAME, "title").text) if items else None
        if previous_first_title is not None and current_first_title == previous_first_title:
            print(" No change in content, stopping")
            break
        previous_first_title = current_first_title
        
        print(f" Found {len(items)} program links on this page")
        for item in items:
            try:
                full_text = clean_text(item.find_element(By.CLASS_NAME, "title").text)
                # Improved regex to handle Ph.D., etc.
                match = re.match(r'^(Online\s+)?([A-Z][a-zA-Z\.]+)(?:\s+in)?\s+(.*)$', full_text)
                if match:
                    degree_type = match.group(2).strip()
                    program_name = match.group(3).strip()
                    if match.group(1):
                        program_name = match.group(1).strip() + program_name
                else:
                    # Fallback
                    parts = full_text.split(' ', 1)
                    if len(parts) > 1 and '.' in parts[0] and parts[0].replace('.', '').isupper():
                        degree_type = parts[0]
                        program_name = parts[1].strip()
                    else:
                        program_name = full_text
                        degree_type = ""
                
                href = item.find_element(By.CSS_SELECTOR, ".link a").get_attribute("href")
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
        
        # Try to go to next page
        try:
            next_li = driver.find_element(By.XPATH, "//ul[contains(@class, 'pagination')]//li[a[text()='Next'] and not(contains(@class, 'disabled'))]")
            next_btn = next_li.find_element(By.TAG_NAME, "a")
            first_item = items[0]
            driver.execute_script("arguments[0].click();", next_btn)
            wait.until(EC.staleness_of(first_item))
            time.sleep(3)  # Additional wait
        except:
            print(" No more pages")
            break
    
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
        input_fieldnames = reader.fieldnames  # All original columns
        scraped_fields = ["program_name", "degree_type", "programUrl"]
        # Preserve order: original first, then append new fields
        output_fieldnames = input_fieldnames + [f for f in scraped_fields if f not in input_fieldnames]
    
    # Now process
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
                        # Still write original row with empty scraped fields
                        output_row = row.copy()
                        for field in scraped_fields:
                            output_row[field] = ""
                        writer.writerow(output_row)
                    else:
                        total_programs = 0
                        for program in programs:
                            output_row = row.copy()  # Keep ALL original input data
                            output_row.update(program)  # Add program info
                            writer.writerow(output_row)
                            total_programs += 1
                        if total_programs == 0:
                            # If no programs at all, write originals
                            output_row = row.copy()
                            for field in scraped_fields:
                                output_row[field] = ""
                            writer.writerow(output_row)
                        print(f" → Successfully extracted {total_programs} programs")
                except Exception as e:
                    print(f" → Critical error: {e}")
                    # Write original row on error
                    output_row = row.copy()
                    for field in scraped_fields:
                        output_row[field] = ""
                    writer.writerow(output_row)
    driver.quit()
    print(f"\nAll done! Saved to {CSV_OUTPUT}")

if __name__ == "__main__":
    main()