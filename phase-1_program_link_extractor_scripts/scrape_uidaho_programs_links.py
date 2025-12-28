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
CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/uidaho_input_latest.csv"
CSV_OUTPUT = "extracted_programs_uidaho_latest.csv"

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

def extract_programs_from_page(page_url):
    print(f"    Loading page: {page_url}")
    driver.get(page_url)

    # Wait for the main container
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.flex.divide-y")))
        print("    Found main program container")
    except:
        print("    ERROR: Could not find program container")
        return []

    # Expand all <details> sections
    print("    Expanding all program sections...")
    details_elements = driver.find_elements(By.TAG_NAME, "details")
    for detail in details_elements:
        if not detail.get_attribute("open"):
            try:
                summary = detail.find_element(By.TAG_NAME, "summary")
                driver.execute_script("arguments[0].scrollIntoView(true);", summary)
                driver.execute_script("arguments[0].click();", summary)
                time.sleep(0.5)
            except:
                pass
    time.sleep(2)

    # Scroll to ensure everything is loaded
    print("    Scrolling to load all content...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    time.sleep(2)

    # Find all program articles
    articles = driver.find_elements(By.CSS_SELECTOR, "article.relative")
    print(f"    Found {len(articles)} program articles")

    programs = []
    for article in articles:
        try:
            # Program name from summary
            summary_text_elem = article.find_element(By.CSS_SELECTOR, "summary p")
            full_name = clean_text(summary_text_elem.text)  # e.g., "Accountancy (M.Acct.)"

            # Extract degree type from parentheses
            degree_match = re.search(r'\(([^)]+)\)', full_name)
            degree_type = degree_match.group(1) if degree_match else ""

            # Clean program name (remove degree part)
            program_name = re.sub(r'\s*\([^)]+\)', '', full_name).strip()

            # Locations
            locations = ""
            try:
                loc_section = article.find_element(By.XPATH, ".//p[contains(text(), 'Locations:')]/following-sibling::div")
                loc_text = loc_section.text
                locations = clean_text(loc_text)
            except:
                pass

            # Program link (from "View degree details" button)
            program_link = ""
            try:
                link_elem = article.find_element(By.CSS_SELECTOR, "a.button.link-arrow")
                program_link = link_elem.get_attribute("href")
            except:
                pass

            if program_name and program_link:
                programs.append({
                    "program_name": program_name,
                    "degree_type": degree_type,
                    "campus_name": locations,
                    "programUrl": program_link
                })

        except Exception as e:
            print(f"      Warning: Failed to parse one program → {e}")
            continue

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

        scraped_fields = ["program_name", "degree_type", "campus_name", "programUrl"]
        output_fieldnames = input_fieldnames + [f for f in scraped_fields if f not in input_fieldnames]

    # Process the file
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        with open(output_path, 'a', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            if not file_exists:
                writer.writeheader()

            for row in reader:
                listing_url = row.get("degree_program_link", "").strip()
                uni_name = row.get("university_name", "University of Idaho")

                if not listing_url:
                    print("Skipping row — no degree_program_link")
                    continue

                print(f"\n=== {uni_name} ===")
                print(f"URL: {listing_url}")

                try:
                    programs = extract_programs_from_page(listing_url)

                    if not programs:
                        print("  → No programs extracted.")
                        output_row = row.copy()
                        for field in scraped_fields:
                            output_row[field] = ""
                        writer.writerow(output_row)
                    else:
                        for prog in programs:
                            output_row = row.copy()
                            output_row.update(prog)
                            writer.writerow(output_row)

                    print(f"  → Successfully extracted {len(programs)} programs")

                except Exception as e:
                    print(f"  → Critical error: {e}")
                    output_row = row.copy()
                    for field in scraped_fields:
                        output_row[field] = ""
                    writer.writerow(output_row)

    driver.quit()
    print(f"\nAll done! Saved to {CSV_OUTPUT}")

if __name__ == "__main__":
    main()