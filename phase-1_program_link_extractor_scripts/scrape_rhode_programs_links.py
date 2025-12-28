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
CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_input_files/rhode_input_latest.csv"
CSV_OUTPUT = "../crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_rhode_latest.csv"

# Headless Chrome setup
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)

# ----------------------------- HELPERS -----------------------------
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip() if text else ""

def extract_programs_from_page(page_url):
    print(f"    Loading page: {page_url}")
    driver.get(page_url)
    
    # Wait for the results container
    try:
        wait.until(EC.presence_of_element_located((By.ID, "program-results")))
        print("    Found #program-results container")
    except:
        print("    ERROR: Could not find #program-results — page structure changed?")
        return []

    # Scroll slowly to trigger lazy loading of all cards
    print("    Scrolling to load all programs...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Small extra scroll up/down to ensure everything renders
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 500);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # Now extract all cards
    cards = driver.find_elements(By.CSS_SELECTOR, "a.cl-card")
    print(f"    Found {len(cards)} program cards")

    programs = []
    for card in cards:
        try:
            # Program name from h3
            name_elem = card.find_element(By.CSS_SELECTOR, ".cl-card-text h3")
            program_name = clean_text(name_elem.text)

            # Degree type (from program-type badge title)
            degree_type = ""
            degree_badges = card.find_elements(By.CSS_SELECTOR, ".badges li.program-type")
            if degree_badges:
                degree_type = clean_text(degree_badges[0].get_attribute("title"))

            # All badges (delivery, online, etc.)
            badge_elems = card.find_elements(By.CSS_SELECTOR, ".badges li")
            badge_list = []
            for b in badge_elems:
                title = b.get_attribute("title")
                if title:
                    badge_list.append(clean_text(title))
            campuses = ", ".join(badge_list) if badge_list else "Not specified"

            # Program link (the card's href)
            program_link = card.get_attribute("href")

            if program_name and program_link:
                programs.append({
                    "program_name": program_name,
                    "degree_type": degree_type,
                    "campus_name": campuses,
                    "programUrl": program_link
                })

        except Exception as e:
            print(f"      Warning: Failed to parse one card → {e}")
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

    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        input_fieldnames = reader.fieldnames

        scraped_fields = ["program_name", "degree_type", "campus_name", "programUrl"]
        output_fieldnames = input_fieldnames + [f for f in scraped_fields if f not in input_fieldnames]

        with open(output_path, 'a', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            if not file_exists:
                writer.writeheader()

            for row in reader:
                listing_url = row.get("degree_program_link", "").strip()
                uni_name = row.get("university_name", "Unknown University")

                if not listing_url:
                    print("Skipping empty URL row")
                    continue

                print(f"\n=== {uni_name} ===")
                print(f"URL: {listing_url}")

                try:
                    programs = extract_programs_from_page(listing_url)

                    if not programs:
                        print("  → No programs extracted — check if page loaded correctly.")
                    else:
                        for prog in programs:
                            output_row = row.copy()
                            output_row.update(prog)
                            writer.writerow(output_row)

                    print(f"  → Successfully extracted {len(programs)} programs")

                except Exception as e:
                    print(f"  → Critical error: {e}")

    driver.quit()
    print(f"\nAll done! Saved to {CSV_OUTPUT}")

if __name__ == "__main__":
    main()