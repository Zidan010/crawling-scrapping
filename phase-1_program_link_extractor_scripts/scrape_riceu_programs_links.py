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
CSV_INPUT = "../crawling-scrapping/phase-1_input_files/riceu_input_latest.csv"  # Update with your actual input CSV path
CSV_OUTPUT = "../crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_riceu_latest.csv"

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

def make_absolute_url(href):
    if not href or href == "-" or href.startswith("#"):
        return ""
    if href.startswith("http"):
        return href
    return "https://ga.rice.edu" + href if href.startswith("/") else "https://ga.rice.edu/" + href

# ----------------------------- CORE SCRAPER -----------------------------
def extract_programs_from_page(page_url):
    print(f"    Loading page: {page_url}")
    driver.get(page_url)

    # Wait for the table to load
    try:
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.grid.academic-program-view"))
        )
        print("    Found academic programs table")
    except Exception as e:
        print(f"    ERROR: Table not found → {e}")
        return []

    time.sleep(3)  # Allow any dynamic content to settle

    programs = []

    # Get all rows in tbody
    rows = driver.find_elements(By.CSS_SELECTOR, "table.grid.academic-program-view tbody tr")
    print(f"    Found {len(rows)} program rows")

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) != 5:
            continue  # Skip malformed rows

        # Program name (first column, inside the inner <span>)
        program_name = ""
        try:
            program_name = clean_text(cells[0].find_element(By.XPATH, ".//span[not(@class)]").text)
        except:
            pass
        if not program_name:
            continue

        # Department name and link (second column)
        department_name = ""
        department_url = ""
        try:
            dept_a = cells[1].find_element(By.TAG_NAME, "a")
            department_name = clean_text(dept_a.text)
            department_url = make_absolute_url(dept_a.get_attribute("href"))
        except:
            pass

        # Undergraduate links (fourth column)
        ug_links = cells[3].find_elements(By.TAG_NAME, "a")
        ug_programs = []
        for a in ug_links:
            title = clean_text(a.text) or "Undergraduate Program"
            url = make_absolute_url(a.get_attribute("href"))
            if url:
                ug_programs.append({"program_name": f"{program_name} ({title})", "programUrl": url, "level": "Undergraduate"})

        # Graduate links (fifth column)
        grad_links = cells[4].find_elements(By.TAG_NAME, "a")
        grad_programs = []
        for a in grad_links:
            title = clean_text(a.text) or "Graduate Program"
            url = make_absolute_url(a.get_attribute("href"))
            if url:
                grad_programs.append({"program_name": f"{program_name} ({title})", "programUrl": url, "level": "Graduate"})

        # Combine all programs (each link becomes a separate row, same department)
        all_programs = ug_programs + grad_programs
        if not all_programs:
            # If no links, still record the program (optional)
            all_programs.append({"program_name": program_name, "programUrl": "", "level": ""})

        for prog in all_programs:
            programs.append({
                "program_name": prog["program_name"],
                "department": department_name,
                "department_url": department_url,
                "programUrl": prog["programUrl"],
                "level": prog["level"]
            })

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

    scraped_fields = ["program_name", "department", "department_url", "programUrl", "level"]
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
            uni_name = row.get("university_name", "Rice University")

            if not listing_url:
                print("Skipping row — no degree_program_link")
                continue

            print(f"\n=== {uni_name} ===")
            print(f"URL: {listing_url}")

            try:
                programs = extract_programs_from_page(listing_url)

                if not programs:
                    empty_row = row.copy()
                    for f in scraped_fields:
                        empty_row[f] = ""
                    writer.writerow(empty_row)
                    print("  → No programs extracted")
                else:
                    for prog in programs:
                        out_row = row.copy()
                        out_row.update(prog)
                        writer.writerow(out_row)

                    print(f"  → Extracted {len(programs)} program entries (multiple per row if multiple links)")

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