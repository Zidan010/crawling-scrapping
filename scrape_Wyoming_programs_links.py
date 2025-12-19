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
CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/input_test.csv"
CSV_OUTPUT = "extracted_programs_wyoming.csv"      # Will contain ALL input columns + scraped ones

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

    # Wait for initial content
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "accordion-item")))
    except:
        print("    No accordion items found — page might be empty or different structure")
        return []

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
        time.sleep(1)

    # Pagination loop
    while True:
        # Extract programs from current page
        cards = driver.find_elements(By.CLASS_NAME, "program-card")
        for card in cards:
            try:
                # Program name and degree from accordion header
                accordion_header = card.find_element(By.XPATH, "./ancestor::div[contains(@class,'accordion-item')]//h2//button")
                name_parts = accordion_header.find_elements(By.TAG_NAME, "span")
                program_name = clean_text(name_parts[0].text) if name_parts else ""
                degree_type = clean_text(name_parts[1].text if len(name_parts) > 1 else "")

                # Campus/delivery tags
                tags = card.find_elements(By.CSS_SELECTOR, ".category-tag span")
                campuses = ", ".join([clean_text(t.text) for t in tags if t.text.strip()])

                # Program detail link
                link_elem = card.find_element(By.CSS_SELECTOR, "a.hyperlink-arrow")
                relative_href = link_elem.get_attribute("href")
                full_link = urljoin(page_url, relative_href) if relative_href else ""

                programs.append({
                    "program_name": program_name,
                    "degree_type": degree_type,
                    "campuses": campuses,
                    "program_link": full_link
                })
            except Exception as e:
                print(f"      Card extraction error: {e}")
                continue

        # Try next page
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, ".btn-next:not(.disabled), .btn-next a:not(.disabled)")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(4)

            # Re-expand new accordions after pagination
            collapsed = driver.find_elements(By.CSS_SELECTOR, ".accordion-button.collapsed")
            for b in collapsed:
                try:
                    driver.execute_script("arguments[0].click();", b)
                    time.sleep(0.3)
                except:
                    pass
        except Exception as e:
            # No more pages or button not clickable
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

    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        input_fieldnames = reader.fieldnames

        # Define scraped fields to add
        scraped_fields = ["program_name", "degree_type", "campuses", "program_link"]

        # Final output columns: all input + scraped (avoid duplicates)
        output_fieldnames = input_fieldnames + [f for f in scraped_fields if f not in input_fieldnames]

        with open(output_path, 'a', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            if not file_exists:
                writer.writeheader()

            batch_count = 0

            for row in reader:
                listing_url = row.get("degree_program_link", "").strip()
                uni_name = row.get("university_name", "Unknown University")

                if not listing_url:
                    print(f"Skipping row — no degree_program_link: {row.get('university_name', '')}")
                    continue

                print(f"\nProcessing: {uni_name}")
                print(f"URL: {listing_url}")

                try:
                    programs = extract_programs_from_page(listing_url)

                    if not programs:
                        print("  → No programs found on this page.")
                        # Still write one row with empty scraped fields to preserve input data
                        empty_row = row.copy()
                        for field in scraped_fields:
                            empty_row[field] = ""
                        writer.writerow(empty_row)
                    else:
                        for prog in programs:
                            output_row = row.copy()  # Preserve ALL original columns
                            output_row.update({
                                "program_name": prog["program_name"],
                                "degree_type": prog["degree_type"],
                                "campuses": prog["campuses"],
                                "program_link": prog["program_link"]
                            })
                            writer.writerow(output_row)
                            batch_count += 1

                    print(f"  → Extracted {len(programs)} programs")

                    # Flush every 10 programs
                    if batch_count >= 10:
                        outfile.flush()
                        batch_count = 0

                except Exception as e:
                    print(f"  → Failed to process {listing_url}: {e}")
                    # Optionally still write row with empty fields
                    empty_row = row.copy()
                    for field in scraped_fields:
                        empty_row[field] = ""
                    writer.writerow(empty_row)

    driver.quit()
    print(f"\nAll done! Results saved to: {CSV_OUTPUT}")

if __name__ == "__main__":
    main()