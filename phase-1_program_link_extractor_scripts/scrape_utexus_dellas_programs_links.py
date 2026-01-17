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
CSV_INPUT = "../crawling-scrapping/phase-1_input_files/utexus_dellas_input_latest.csv"
CSV_OUTPUT = "../crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_utexus_dellas_latest.csv"

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

# ----------------------------- CORE SCRAPER -----------------------------
def extract_programs_from_page(page_url):
    print(f"    Loading page: {page_url}")
    driver.get(page_url)

    # Wait for program-listings
    try:
        wait.until(
            EC.presence_of_element_located((By.ID, "fact-sheet-listing"))
        )
        print("    Found program-listings")
    except:
        print("    ERROR: Program listings not found")
        return []

    time.sleep(2)  # Allow JS to fully render

    programs = []

    # Find all element-item
    items = driver.find_elements(By.CSS_SELECTOR, "div.element-item")
    print(f"    Found {len(items)} items")

    for item in items:
        try:
            # Program name
            program_name = ""
            try:
                h3 = item.find_element(By.TAG_NAME, "h3")
                program_name = clean_text(h3.text)
            except:
                continue

            # Department
            department = ""
            try:
                school_div = item.find_element(By.CLASS_NAME, "school")
                dept_as = school_div.find_elements(By.TAG_NAME, "a")
                depts = [clean_text(a.text) for a in dept_as]
                department = ", ".join(depts)
            except:
                pass

            # Degrees
            degrees_div = item.find_element(By.CLASS_NAME, "degrees")
            degree_as = degrees_div.find_elements(By.TAG_NAME, "a")
            for deg_a in degree_as:
                try:
                    program_url = deg_a.get_attribute("href")

                    degree_div = deg_a.find_element(By.CLASS_NAME, "degree")
                    degree_text = clean_text(degree_div.text)
                    degree_type = degree_text.split('<')[0].strip() if '<' in degree_text else degree_text.strip()

                    footnote = ""
                    try:
                        fn_div = deg_a.find_element(By.CLASS_NAME, "footnote")
                        footnote = clean_text(fn_div.text)
                    except:
                        pass

                    delivery_type = "Offline"  # Default

                    if program_name and program_url:
                        programs.append({
                            "program_name": program_name,
                            "degree_type": degree_type,
                            "department": department,
                            "deliveryType": delivery_type,
                            "programUrl": program_url
                        })
                except Exception as e:
                    print(f"    Skipped one degree → {e}")
                    continue

        except Exception as e:
            print(f"    Skipped one item → {e}")
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
            uni_name = row.get("university_name", "University of Texas at Dallas")

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