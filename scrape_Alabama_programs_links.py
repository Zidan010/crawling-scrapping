# import csv
# import time
# import re

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # ----------------------------- CONFIG -----------------------------
# TARGET_URL = "https://catalog.uah.edu/#/programs"
# BASE_URL = "https://catalog.uah.edu/"
# CSV_OUTPUT = "uah_programs_by_college.csv"

# PAGE_LOAD_TIMEOUT = 180
# SCRIPT_TIMEOUT = 180
# WAIT_TIMEOUT = 40

# # ----------------------------- DRIVER SETUP -----------------------------
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # disable once for debugging
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--disable-software-rasterizer")
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_argument("--disable-features=VizDisplayCompositor")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument(
#     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
# )

# chrome_options.page_load_strategy = "eager"

# driver = webdriver.Chrome(options=chrome_options)
# driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
# driver.set_script_timeout(SCRIPT_TIMEOUT)

# wait = WebDriverWait(driver, WAIT_TIMEOUT)

# # ----------------------------- HELPERS -----------------------------
# def clean_text(text):
#     return re.sub(r"\s+", " ", text).strip() if text else ""

# def normalize_link(href):
#     if href.startswith("#/"):
#         return BASE_URL + href
#     return href

# def extract_degree(program_name):
#     """
#     Extract degree from parentheses if present
#     Example: "Computer Science (BS)" → BS
#     """
#     match = re.search(r"\(([^)]+)\)", program_name)
#     return match.group(1).strip() if match else ""

# # ----------------------------- SCRAPER -----------------------------
# def extract_programs_by_college():
#     print(f"Loading page: {TARGET_URL}")
#     driver.get(TARGET_URL)
#     time.sleep(6)

#     # Wait for colleges to appear
#     wait.until(
#         EC.presence_of_element_located(
#             (By.CSS_SELECTOR, "div[class*='collapsibleBox']")
#         )
#     )

#     colleges = driver.find_elements(
#         By.CSS_SELECTOR, "div[class*='collapsibleBox']"
#     )

#     print(f"Colleges found: {len(colleges)}")

#     results = []

#     for idx, college in enumerate(colleges, start=1):
#         try:
#             # College name
#             college_name = clean_text(
#                 college.find_element(By.CSS_SELECTOR, "h2").text
#             )

#             print(f"\n[{idx}] College: {college_name}")

#             # Expand college if collapsed
#             try:
#                 collapse_btn = college.find_element(
#                     By.CSS_SELECTOR, "button[class*='collapseButton']"
#                 )
#                 aria_expanded = collapse_btn.get_attribute("aria-expanded")

#                 if aria_expanded == "false":
#                     driver.execute_script("arguments[0].click();", collapse_btn)
#                     time.sleep(1.5)
#             except:
#                 pass

#             # Find programs inside this college
#             program_links = college.find_elements(
#                 By.CSS_SELECTOR,
#                 "li[class*='style__item'] a[href^='#/programs/']"
#             )

#             print(f"  Programs found: {len(program_links)}")

#             for a in program_links:
#                 try:
#                     program_name = clean_text(a.text)
#                     program_name = re.sub(r"^-+\s*", "", program_name)

#                     program_link = normalize_link(a.get_attribute("href"))
#                     degree = extract_degree(program_name)

#                     results.append({
#                         "college_name": college_name,
#                         "program_name": program_name,
#                         "degree": degree,
#                         "program_link": program_link
#                     })

#                 except Exception:
#                     continue

#         except Exception as e:
#             print(f"Skipping college due to error: {e}")
#             continue

#     return results

# # ----------------------------- MAIN -----------------------------
# def main():
#     try:
#         data = extract_programs_by_college()

#         if not data:
#             print("❌ No programs extracted.")
#             return

#         with open(CSV_OUTPUT, "w", newline="", encoding="utf-8") as f:
#             writer = csv.DictWriter(
#                 f,
#                 fieldnames=[
#                     "college_name",
#                     "program_name",
#                     "degree",
#                     "program_link"
#                 ]
#             )
#             writer.writeheader()
#             writer.writerows(data)

#         print(f"\n✅ Saved {len(data)} programs to {CSV_OUTPUT}")

#     finally:
#         driver.quit()
#         print("Browser closed.")

# # ----------------------------- ENTRY -----------------------------
# if __name__ == "__main__":
#     main()






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
CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/ualabama_input_latest.csv"
CSV_OUTPUT = "extracted_programs_ualabama_latest.csv"

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

def normalize_program_link(href):
    if href.startswith("#/"):
        return "https://catalog.uah.edu/" + href
    return href

# ----------------------------- CORE SCRAPER -----------------------------
def extract_programs_from_page(page_url):
    print(f"    Loading page: {page_url}")
    driver.get(page_url)

    # Wait for college containers
    try:
        wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div[class*='style__collapsibleBox']")
            )
        )
    except:
        print("    ERROR: College containers not found")
        return []

    time.sleep(2)  # Allow JS to fully render

    colleges = driver.find_elements(By.CSS_SELECTOR, "div[class*='style__collapsibleBox']")
    print(f"    Found {len(colleges)} colleges")

    programs = []

    for college in colleges:
        # Expand college if collapsed
        try:
            toggle_btn = college.find_element(By.CSS_SELECTOR, "button[aria-expanded]")
            if toggle_btn.get_attribute("aria-expanded") == "false":
                driver.execute_script("arguments[0].click();", toggle_btn)
                time.sleep(0.5)
        except:
            pass

        # College name
        college_name = ""
        try:
            college_name = clean_text(college.find_element(By.CSS_SELECTOR, "h2").text)
        except:
            college_name = ""

        # STRICT selector: only top-level programs inside style__columns___K01Hv
        program_anchors = college.find_elements(
            By.CSS_SELECTOR,
            "div.style__columns___K01Hv > h3 > div:not([class*='indented']) > a[href^='#/programs/']"
        )

        for a in program_anchors:
            try:
                degree_type = clean_text(a.text)  # e.g., "Art (BA)"
                program_link = normalize_program_link(a.get_attribute("href"))

                # If campuses info exists somewhere, you can extract it. 
                # For now, leave empty or add parsing later
                campuses = ""

                programs.append({
                    "degree_type": degree_type,
                    "campus_name": campuses,
                    "programUrl": program_link
                })

            except Exception as e:
                print(f"  Skipped one program → {e}")


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

    scraped_fields = ["degree_type", "campus_name", "programUrl"]
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
            uni_name = row.get("university_name", "UAH")

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

# ----------------------------- ENTRY -----------------------------
if __name__ == "__main__":
    main()
