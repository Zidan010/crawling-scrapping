import csv
import time
import re
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# ----------------------------- CONFIG -----------------------------
CSV_INPUT = "../crawling-scrapping/phase-1_input_files/indianau_input_latest.csv"
CSV_OUTPUT = "../crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_indianau_latest.csv"

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

def extract_delivery_type(program_name):
    if "(100% online)" in program_name.lower():
        return "Online"
    return "Offline"

def extract_degree_campus(eyebrow_text):
    parts = eyebrow_text.split("|")
    degree_type = clean_text(parts[0]) if parts else ""
    campus_name = clean_text(parts[1]) if len(parts) > 1 else ""
    return degree_type, campus_name

# ----------------------------- CORE SCRAPER -----------------------------
def extract_programs_from_page(page_url):
    print(f"    Loading base page: {page_url}")
    driver.get(page_url)

    # Wait for results
    try:
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.rvt-cols-9-md"))
        )
        print("    Found results wrapper")
    except:
        print("    ERROR: Results not found")
        return []

    programs = []
    current_page = 1
    max_pages = 123  # From element, 30 pages

    while current_page <= max_pages:
        time.sleep(2)  # Wait for page load

        # Extract programs on current page
        lis = driver.find_elements(By.CSS_SELECTOR, "ul.rvt-row > li.rvt-cols-6-md")
        for li in lis:
            try:
                eyebrow = ""
                try:
                    eyebrow_elem = li.find_element(By.CSS_SELECTOR, "div.rvt-card__eyebrow")
                    eyebrow = clean_text(eyebrow_elem.text)
                except:
                    pass

                degree_type, campus_name = extract_degree_campus(eyebrow)

                title_a = li.find_element(By.CSS_SELECTOR, "h2.rvt-card__title a")
                program_name = clean_text(title_a.text)
                program_url = title_a.get_attribute("href")

                department = ""
                try:
                    dept_div = li.find_element(By.CSS_SELECTOR, "div.rvt-m-left-sm.rvt-m-bottom-sm")
                    department = clean_text(dept_div.text)
                except:
                    pass

                delivery_type = extract_delivery_type(program_name)

                if program_name and program_url:
                    programs.append({
                        "program_name": program_name,
                        "degree_type": degree_type,
                        "campus_name": campus_name,
                        "department": department,
                        "deliveryType": delivery_type,
                        "programUrl": program_url
                    })
            except Exception as e:
                print(f"    Skipped one program on page {current_page} → {e}")
                continue

        print(f"    Extracted {len(lis)} programs from page {current_page}")

        # Go to next page
        try:
            next_li = driver.find_element(By.ID, "pagination-next").find_element(By.XPATH, "..")
            if "is-disabled" in next_li.get_attribute("class"):
                print("    No more pages")
                break

            next_button = driver.find_element(By.ID, "pagination-next")
            driver.execute_script("arguments[0].click();", next_button)
            wait.until(EC.staleness_of(next_button))  # Wait for page refresh
            current_page += 1
        except (NoSuchElementException, TimeoutException):
            print("    No next button or timeout")
            break

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

    scraped_fields = ["program_name", "degree_type", "campus_name", "department", "deliveryType", "programUrl"]
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
            uni_name = row.get("university_name", "Indiana University")

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

                print(f"  → Extracted {len(programs)} programs total")

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