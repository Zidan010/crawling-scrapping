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
CSV_OUTPUT = "extracted_programs_testtttttt.csv"

# Headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)

# ----------------------------- HELPERS -----------------------------
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip() if text else ""

# ----------------------------- DYNAMIC EXTRACTION FUNCTION -----------------------------
def extract_programs_from_page(page_url, config):
    """
    Extract programs using a configurable selector setup.
    
    config keys:
        card_selector: str - CSS selector for each program card/container
        name_selector: dict - how to get program name (e.g., {"parent": "ancestor accordion", "elements": "span"})
        degree_selector: str or None - CSS selector for degree type
        campus_selector: str - CSS selector for campus/delivery tags
        link_selector: str - CSS selector for the detail page link
        accordion_button: str - CSS selector for accordion toggle buttons
        next_button: str - CSS selector for pagination "Next" button
    """
    driver.get(page_url)
    wait = WebDriverWait(driver, 30)

    programs = []

    # Wait for first card
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config["card_selector"])))

    # Expand accordions if needed
    if config.get("accordion_button"):
        while True:
            collapsed = driver.find_elements(By.CSS_SELECTOR, config["accordion_button"])
            if not collapsed:
                break
            for btn in collapsed:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(0.6)
                except:
                    pass
        time.sleep(2)

    page_num = 1
    while True:
        print(f"    Scraping page {page_num}...")
        cards = driver.find_elements(By.CSS_SELECTOR, config["card_selector"])

        for card in cards:
            try:
                # Program Name
                if config["name_selector"]["type"] == "accordion_header":
                    header = card.find_element(By.XPATH, "./ancestor::div[contains(@class,'accordion-item')]//h2//button")
                    name_elements = header.find_elements(By.TAG_NAME, "span")
                    program_name = clean_text(name_elements[0].text) if name_elements else ""
                    degree_type = clean_text(name_elements[1].text if len(name_elements) > 1 else "")
                else:
                    # Generic fallback
                    name_elem = card.find_element(By.CSS_SELECTOR, config["name_selector"]["selector"])
                    program_name = clean_text(name_elem.text)
                    degree_type = ""

                # Campuses / Delivery
                campuses = "Not specified"
                if config.get("campus_selector"):
                    tags = card.find_elements(By.CSS_SELECTOR, config["campus_selector"])
                    campuses = ", ".join([clean_text(t.text) for t in tags if t.text.strip()])

                # Program Link
                # link_elem = card.find_element(By.CSS_SELECTOR, config["link_selector"])
                # program_link = urljoin(page_url, link_elem.get_attribute("href"))

                # Program Link
                try:
                    if config["link_selector"] == ".explorer-card__anchor":
                        # Special case for UTulsa: the card itself is the link
                        program_link = card.get_attribute("href")
                    else:
                        link_elem = card.find_element(By.CSS_SELECTOR, config["link_selector"])
                        program_link = urljoin(page_url, link_elem.get_attribute("href"))
                    program_link = program_link or ""
                except:
                    program_link = ""


                programs.append({
                    "program_name": program_name,
                    "degree_type": degree_type,
                    "campuses": campuses,
                    "program_link": program_link
                })

            except Exception as e:
                print(f"      Card error: {e}")
                continue

        # Pagination
        if not config.get("next_button"):
            break

        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, config["next_button"])
            if "disabled" in next_btn.get_attribute("class") or not next_btn.is_enabled():
                break
            driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(4)
            page_num += 1
        except:
            break

    return programs

# ----------------------------- MAIN -----------------------------
def main():
    if not Path(CSV_INPUT).exists():
        print("CSV not found")
        return

    # Example configs — add more as needed
    UNIVERSITY_CONFIGS = {
        "utulsa.edu": {  # ← NEW: University of Tulsa
            "card_selector": ".explorer-card__anchor",
            "name_selector": {
                "type": "direct",
                "selector": "h3.explorer-card__section__entry-header"
            },
            "campus_selector": ".explorer-card__section__program-format",
            "link_selector": ".explorer-card__anchor",  # The card itself is the link
            "accordion_button": None,
            "next_button": None
        }
    # "uwyo.edu": {  # University of Wyoming
    #         "card_selector": ".program-card",
    #         "name_selector": {"type": "accordion_header"},
    #         "campus_selector": ".category-tag span",
    #         "link_selector": "a.hyperlink-arrow",
    #         "accordion_button": ".accordion-button.collapsed",
    #         "next_button": ".btn-next:not(.disabled) a"
    #     }
    }


    output_path = Path(CSV_OUTPUT)
    file_exists = output_path.exists()

    with open(CSV_INPUT, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = ["university_name", "degree_program_link", "program_name", "degree_type", "campuses", "program_link"]

        with open(output_path, 'a', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()

            batch = 0

            for row in reader:
                uni_name = row.get("university_name", "").strip()
                listing_url = row.get("degree_program_link", "").strip()
                if not listing_url:
                    continue

                # Auto-detect config by domain
                from urllib.parse import urlparse
                domain = urlparse(listing_url).netloc
                config = None
                for key in UNIVERSITY_CONFIGS:
                    if key in domain:
                        config = UNIVERSITY_CONFIGS[key]
                        break

                if not config:
                    print(f"No config for domain: {domain} — skipping {listing_url}")
                    continue

                print(f"\n=== {uni_name} ===\n{listing_url}")

                try:
                    programs = extract_programs_from_page(listing_url, config)

                    for p in programs:
                        writer.writerow({
                            "university_name": uni_name,
                            "degree_program_link": listing_url,
                            "program_name": p["program_name"],
                            "degree_type": p["degree_type"],
                            "campuses": p["campuses"],
                            "program_link": p["program_link"]
                        })
                        batch += 1
                        if batch >= 10:
                            outfile.flush()
                            print("  → Saved 10 programs")
                            batch = 0

                    print(f"→ Extracted {len(programs)} programs\n")

                except Exception as e:
                    print(f"Error: {e}")

    driver.quit()
    print("All done!")

if __name__ == "__main__":
    main()