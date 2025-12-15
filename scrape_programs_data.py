import csv
import time
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin

# ----------------------------- CONFIG -----------------------------
CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/input_test.csv"          # Your CSV with degree_program_link column
CSV_OUTPUT = "extracted_programs.csv"      # Output CSV
CHROME_DRIVER_PATH = None                 # Optional: set if not in PATH

# Headless Chrome setup
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)

# ----------------------------- HELPERS -----------------------------
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip() if text else ""

def extract_programs_from_page(page_url):
    driver.get(page_url)
    wait = WebDriverWait(driver, 20)

    programs = []

    # Wait for initial load
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "accordion-item")))

    # Expand all accordions
    while True:
        collapsed_buttons = driver.find_elements(By.CSS_SELECTOR, ".accordion-button.collapsed")
        if not collapsed_buttons:
            break
        for btn in collapsed_buttons:
            try:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.5)
            except:
                pass

    # Pagination loop
    while True:
        # Extract current page programs
        cards = driver.find_elements(By.CLASS_NAME, "program-card")
        for card in cards:
            try:
                # Program name (main bold title from parent accordion)
                accordion_header = card.find_element(By.XPATH, "./ancestor::div[contains(@class,'accordion-item')]//h2//button")
                name_parts = accordion_header.find_elements(By.TAG_NAME, "span")
                program_name = clean_text(name_parts[0].text) if name_parts else ""
                degree_type = clean_text(name_parts[1].text if len(name_parts) > 1 else "")

                # Campus/delivery tags
                tags = card.find_elements(By.CSS_SELECTOR, ".category-tag span")
                campuses = ", ".join([clean_text(t.text) for t in tags])

                # Explore Program link
                link_elem = card.find_element(By.CSS_SELECTOR, "a.hyperlink-arrow")
                relative_href = link_elem.get_attribute("href")
                full_link = urljoin(page_url, relative_href)

                programs.append({
                    "program_name": program_name,
                    "degree_type": degree_type,
                    "campuses": campuses,
                    "program_link": full_link
                })
            except Exception as e:
                print(f"Error extracting card: {e}")
                continue

        # Try to go to next page
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, ".btn-next:not(.disabled), .btn-next a:not(.disabled)")
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(3)  # Wait for new content
            # Re-expand accordions after page change
            collapsed = driver.find_elements(By.CSS_SELECTOR, ".accordion-button.collapsed")
            for b in collapsed:
                driver.execute_script("arguments[0].click();", b)
                time.sleep(0.3)
        except:
            break  # No more pages

    return programs

# ----------------------------- MAIN -----------------------------
def main():
    if not Path(CSV_INPUT).exists():
        print(f"Input CSV not found: {CSV_INPUT}")
        return

    output_path = Path(CSV_OUTPUT)
    with open(CSV_INPUT, newline='', encoding='utf-8') as infile, \
         open(output_path, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = ["university_name", "degree_program_link", "program_name", "degree_type", "campuses", "program_link"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            uni_name = row.get("university_name", "").strip()
            listing_url = row.get("degree_program_link", "").strip()

            if not listing_url:
                print(f"Skipping row - no degree_program_link")
                continue

            print(f"\nProcessing: {uni_name} — {listing_url}")
            try:
                programs = extract_programs_from_page(listing_url)

                for prog in programs:
                    writer.writerow({
                        "university_name": uni_name,
                        "degree_program_link": listing_url,
                        "program_name": prog["program_name"],
                        "degree_type": prog["degree_type"],
                        "campuses": prog["campuses"],
                        "program_link": prog["program_link"]
                    })

                print(f"  → Extracted {len(programs)} programs")
            except Exception as e:
                print(f"  → Error processing {listing_url}: {e}")

    driver.quit()
    print(f"\nDone! All programs saved to {CSV_OUTPUT}")

if __name__ == "__main__":
    main()