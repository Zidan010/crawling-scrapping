import csv
import time
import re
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------------------- CONFIG -----------------------------
CSV_INPUT = "../crawling-scrapping/phase-1_input_files/ucflorida_input_latest_undergrad.csv"
CSV_OUTPUT = "../crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_ucflorida_latest_undergrad.csv"

WAIT_TIMEOUT = 40

# ----------------------------- DRIVER -----------------------------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
)
chrome_options.page_load_strategy = "eager"

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, WAIT_TIMEOUT)

# ----------------------------- HELPERS -----------------------------
def clean_text(text):
    return re.sub(r"\s+", " ", text).strip() if text else ""

def extract_degree_type(program_name):
    match = re.search(r'\((.*?)\)', program_name)
    return match.group(1) if match else ""

def make_absolute_url(href):
    if href.startswith("http"):
        return href
    return "https://www.ucf.edu" + href if href.startswith("/") else "https://www.ucf.edu/" + href

# ----------------------------- CORE SCRAPER -----------------------------
def extract_programs_from_page(page_url):
    print(f"    Loading page: {page_url}")
    driver.get(page_url)

    # Wait for degree-list-wrapper
    try:
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "degree-list-wrapper"))
        )
        print("    Found degree-list-wrapper")
    except:
        print("    ERROR: Degree list wrapper not found")
        return []

    time.sleep(2)  # Allow JS to fully render

    programs = []

    # Find all degree-list-group
    groups = driver.find_elements(By.CSS_SELECTOR, "div.degree-list-group")
    print(f"    Found {len(groups)} groups")

    for group in groups:
        # Department from h3
        department = ""
        try:
            h3 = group.find_element(By.CSS_SELECTOR, "h3.degree-list-heading")
            department = clean_text(h3.text)
        except:
            department = "Unknown"

        # Find ul > li
        lis = group.find_elements(By.CSS_SELECTOR, "ul.degree-list-twocol > li.degree-list-program")
        for li in lis:
            try:
                a = li.find_element(By.TAG_NAME, "a")
                program_name = clean_text(a.text)
                program_url = make_absolute_url(a.get_attribute("href"))
                degree_type = extract_degree_type(program_name)
                delivery_type = ""  # Not present in element

                if program_name and program_url:
                    programs.append({
                        "program_name": program_name,
                        "degree_type": degree_type,
                        "department": department,
                        "deliveryType": delivery_type,
                        "programUrl": program_url
                    })
            except Exception as e:
                print(f"    Skipped one program → {e}")
                continue

    return programs

# ----------------------------- MAIN PIPELINE -----------------------------
def main():
    input_path = Path(CSV_INPUT)
    output_path = Path(CSV_OUTPUT)

    if not input_path.exists():
        print(f"Input CSV not found: {CSV_INPUT}")
        return

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        input_fields = reader.fieldnames

    scraped_fields = ["program_name", "degree_type", "department", "deliveryType", "programUrl"]
    output_fields = input_fields + [f for f in scraped_fields if f not in input_fields]

    file_exists = output_path.exists()

    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "a", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)

        if not file_exists:
            writer.writeheader()

        for row in reader:
            listing_url = row.get("degree_program_link", "").strip()
            uni_name = row.get("university_name", "University of Central Florida")

            if not listing_url:
                print("Skipping row — no degree_program_link")
                continue

            print(f"\n=== {uni_name} ===")

            try:
                programs = extract_programs_from_page(listing_url)

                if not programs:
                    empty_row = row.copy()
                    for f in scraped_fields:
                        empty_row[f] = ""
                    writer.writerow(empty_row)
                else:
                    for prog in programs:
                        out = row.copy()
                        out.update(prog)
                        writer.writerow(out)

                print(f"  → Extracted {len(programs)} programs")

            except Exception as e:
                print(f"  CRITICAL ERROR: {e}")
                error_row = row.copy()
                for f in scraped_fields:
                    error_row[f] = ""
                writer.writerow(error_row)

    driver.quit()
    print(f"\n✅ Done. Saved to {CSV_OUTPUT}")

if __name__ == "__main__":
    main()