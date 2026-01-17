# import csv
# import time
# import re
# from pathlib import Path
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # ----------------------------- CONFIG -----------------------------
# CSV_INPUT = "../crawling-scrapping/phase-1_input_files/utulsa_input_latest.csv"
# CSV_OUTPUT = "../crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_utulsa_latest_v3.csv"

# # Headless Chrome setup
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36")
# driver = webdriver.Chrome(options=chrome_options)
# wait = WebDriverWait(driver, 30)

# # ----------------------------- HELPERS -----------------------------
# def clean_text(text):
#     return re.sub(r'\s+', ' ', text).strip() if text else ""

# def scroll_to_load_all():
#     print(" Scrolling to ensure all content is loaded...")
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     while True:
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)
#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             break
#         last_height = new_height
#     time.sleep(2)  # Final wait

# def extract_categories_from_listing(page_url):
#     print(f" Loading listing page: {page_url}")
#     driver.get(page_url)
    
#     # Wait for category cards to appear
#     try:
#         wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".explorer-card__anchor")))
#         print(" Found category cards (.explorer-card__anchor)")
#     except:
#         print(" ERROR: Could not find category cards — page structure changed or blocked?")
#         return []
    
#     scroll_to_load_all()
    
#     # Extract all category cards
#     cards = driver.find_elements(By.CSS_SELECTOR, ".explorer-card__anchor")
#     print(f" Found {len(cards)} category cards")
#     categories = []
#     for card in cards:
#         try:
#             # Category name
#             name_elem = card.find_element(By.CSS_SELECTOR, "h3.explorer-card__section__entry-header")
#             category_name = clean_text(name_elem.text)
            
#             # Degree type — not explicitly marked, so leave empty or infer if needed
#             degree_type = ""
            
#             # Campus / Delivery format
#             campuses = "Not specified"
#             format_elems = card.find_elements(By.CSS_SELECTOR, ".explorer-card__section__program-format")
#             if format_elems:
#                 campuses = ", ".join([clean_text(e.text) for e in format_elems if e.text.strip()])
            
#             # Category link — the card itself is the <a>
#             category_link = card.get_attribute("href")
            
#             if category_name and category_link:
#                 categories.append({
#                     "category_name": category_name,  # Renamed to distinguish from sub-program_name
#                     "degree_type": degree_type,
#                     "campus_name": campuses,
#                     "first_layer": category_link
#                 })
#         except Exception as e:
#             print(f" Warning: Failed to parse one category card → {e}")
#             continue
#     return categories

# def extract_sub_programs_from_first_layer(first_layer_url):
#     print(f" Loading first-layer page: {first_layer_url}")
#     driver.get(first_layer_url)
    
#     try:
#         wait.until(EC.presence_of_element_located((By.CLASS_NAME, "entry-content")))
#         print(" Found entry-content divs")
#     except:
#         print(" ERROR: Could not find entry-content — page structure changed?")
#         return []
    
#     scroll_to_load_all()
    
#     # Extract program_overview from the second div.entry-content
#     entry_contents = driver.find_elements(By.CLASS_NAME, "entry-content")
#     program_overview = ""
#     if len(entry_contents) >= 2:
#         program_overview = clean_text(entry_contents[0].text)
#         print(f" Extracted program_overview (length: {len(program_overview)} chars)")
#     else:
#         print(" Warning: Fewer than 2 entry-content divs found")
    
#     # Extract sub-programs from the first div.ut_cards__grid.grid-x.grid-margin-x.align-center
#     sub_programs = []
#     grid_divs = driver.find_elements(By.CSS_SELECTOR, "div.ut_cards__grid.grid-x.grid-margin-x.align-center")
#     if grid_divs:
#         first_grid = grid_divs[0]
#         # Find all <a> tags inside the grid
#         links = first_grid.find_elements(By.TAG_NAME, "a")
#         print(f" Found {len(links)} potential sub-program links in grid")
#         for link in links:
#             try:
#                 sub_name = clean_text(link.text)
#                 sub_url = link.get_attribute("href")
#                 if sub_name and sub_url:
#                     sub_programs.append({
#                         "program_name": sub_name,
#                         "programUrl": sub_url,
#                         "program_overview": program_overview  # Shared for all subs
#                     })
#             except Exception as e:
#                 print(f" Warning: Failed to parse one sub-link → {e}")
#                 continue
#     else:
#         print(" Warning: No ut_cards__grid div found — using first_layer as fallback?")
#         # Optional fallback: If no subs, treat as single program
#         sub_programs.append({
#             "program_name": "",  # Will use category_name later if needed
#             "programUrl": first_layer_url,
#             "program_overview": program_overview
#         })
    
#     return sub_programs

# # ----------------------------- MAIN -----------------------------
# def main():
#     input_path = Path(CSV_INPUT)
#     output_path = Path(CSV_OUTPUT)
#     if not input_path.exists():
#         print(f"Input CSV not found: {CSV_INPUT}")
#         return
    
#     file_exists = output_path.exists()
    
#     # Read input to preserve original columns
#     with open(input_path, newline='', encoding='utf-8') as infile:
#         reader = csv.DictReader(infile)
#         input_fieldnames = reader.fieldnames  # All original columns
#         scraped_fields = ["category_name", "program_name", "degree_type", "campus_name", "first_layer", "program_overview", "programUrl"]
#         output_fieldnames = list(set(input_fieldnames + scraped_fields))  # Unique, preserve order if needed
    
#     # Now process
#     with open(input_path, newline='', encoding='utf-8') as infile:
#         reader = csv.DictReader(infile)
#         with open(output_path, 'a', newline='', encoding='utf-8') as outfile:
#             writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
#             if not file_exists:
#                 writer.writeheader()
#             for row in reader:
#                 listing_url = row.get("degree_program_link", "").strip()
#                 uni_name = row.get("university_name", "Unknown University")
#                 if not listing_url:
#                     print("Skipping row — no degree_program_link")
#                     continue
#                 print(f"\n=== {uni_name} ===")
#                 print(f"URL: {listing_url}")
#                 try:
#                     categories = extract_categories_from_listing(listing_url)
#                     if not categories:
#                         print(" → No categories extracted.")
#                         # Still write original row with empty scraped fields
#                         output_row = row.copy()
#                         for field in scraped_fields:
#                             output_row[field] = ""
#                         writer.writerow(output_row)
#                     else:
#                         total_subs = 0
#                         for cat in categories:
#                             subs = extract_sub_programs_from_first_layer(cat["first_layer"])
#                             for sub in subs:
#                                 output_row = row.copy()  # Keep ALL original input data
#                                 output_row.update(cat)  # Add category info (category_name, campus_name, etc.)
#                                 output_row.update(sub)  # Add/override with sub info (program_name, programUrl, program_overview)
#                                 writer.writerow(output_row)
#                                 total_subs += 1
#                         if total_subs == 0:
#                             # If no subs at all, write originals
#                             output_row = row.copy()
#                             for field in scraped_fields:
#                                 output_row[field] = ""
#                             writer.writerow(output_row)
#                         print(f" → Successfully extracted {total_subs} sub-programs from {len(categories)} categories")
#                 except Exception as e:
#                     print(f" → Critical error: {e}")
#                     # Write original row on error
#                     output_row = row.copy()
#                     for field in scraped_fields:
#                         output_row[field] = ""
#                     writer.writerow(output_row)
#     driver.quit()
#     print(f"\nAll done! Saved to {CSV_OUTPUT}")

# if __name__ == "__main__":
#     main()









import csv
import time
import re
from pathlib import Path
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------------------- CONFIG -----------------------------
CSV_INPUT = "../crawling-scrapping/phase-1_input_files/utulsa_input_latest.csv"
CSV_OUTPUT = "../crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_programs_utulsa_latest_grad.csv"

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

def scroll_to_load_all():
    print(" Scrolling to ensure all content is loaded...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    time.sleep(2)  # Final wait

def extract_program_groups_from_listing(page_url):
    print(f" Loading listing page: {page_url}")
    driver.get(page_url)
    
    # Wait for program-list uls to appear
    try:
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "program-list")))
        print(" Found program-list uls")
    except:
        print(" ERROR: Could not find program-list uls — page structure changed or blocked?")
        return []
    
    scroll_to_load_all()
    
    # Find all ul.program-list, but only take first 3
    uls = driver.find_elements(By.CLASS_NAME, "program-list")[:4]
    print(f" Found {len(uls)} program groups (limited to first 3)")
    
    program_groups = []
    for ul in uls:
        try:
            # Find preceding <p> for program_type
            p_elem = ul.find_element(By.XPATH, "./preceding-sibling::p[1]")
            program_type = clean_text(p_elem.text)
        except:
            print(" Warning: No preceding <p> found for program_type")
            program_type = ""
        
        # Extract programs from this ul
        programs = []
        a_elems = ul.find_elements(By.TAG_NAME, "a")
        print(f" Found {len(a_elems)} program links in this group")
        for a in a_elems:
            try:
                full_text = clean_text(a.text)
                parts = [p.strip() for p in full_text.split(',') if p.strip()]
                
                # Find degree part from the end
                degree_index = -1
                for i in range(len(parts) - 1, -1, -1):
                    p = parts[i]
                    if ' ' not in p and '.' in p and all(c.isalpha() or c == '.' for c in p) and len(p) > 3 and len(p) < 15:
                        degree_index = i
                        break
                
                if degree_index != -1:
                    program_name = ', '.join(parts[:degree_index] + parts[degree_index + 1:])
                    degree_code = parts[degree_index]
                else:
                    program_name = ', '.join(parts)
                    degree_code = ""
                
                href = a.get_attribute("href")
                program_url = urljoin(page_url, href)
                
                if program_name and program_url:
                    programs.append({
                        "program_name": program_name,
                        "degree_code": degree_code,
                        "programUrl": program_url
                    })
            except Exception as e:
                print(f" Warning: Failed to parse one program link → {e}")
                continue
        
        if programs:
            program_groups.append({
                "program_type": program_type,
                "programs": programs
            })
    
    return program_groups

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
        input_fieldnames = reader.fieldnames  # All original columns
        scraped_fields = ["program_type", "program_name", "degree_code", "programUrl"]
        # Preserve order: original first, then append new fields
        output_fieldnames = input_fieldnames + [f for f in scraped_fields if f not in input_fieldnames]
    
    # Now process
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        with open(output_path, 'a', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            if not file_exists:
                writer.writeheader()
            for row in reader:
                listing_url = row.get("degree_program_link", "").strip()
                uni_name = row.get("university_name", "Unknown University")
                if not listing_url:
                    print("Skipping row — no degree_program_link")
                    continue
                print(f"\n=== {uni_name} ===")
                print(f"URL: {listing_url}")
                try:
                    groups = extract_program_groups_from_listing(listing_url)
                    if not groups:
                        print(" → No program groups extracted.")
                        # Still write original row with empty scraped fields
                        output_row = row.copy()
                        for field in scraped_fields:
                            output_row[field] = ""
                        writer.writerow(output_row)
                    else:
                        total_programs = 0
                        for group in groups:
                            for program in group["programs"]:
                                output_row = row.copy()  # Keep ALL original input data
                                output_row["program_type"] = group["program_type"]
                                output_row.update(program)  # Add program info
                                writer.writerow(output_row)
                                total_programs += 1
                        if total_programs == 0:
                            # If no programs at all, write originals
                            output_row = row.copy()
                            for field in scraped_fields:
                                output_row[field] = ""
                            writer.writerow(output_row)
                        print(f" → Successfully extracted {total_programs} programs from {len(groups)} groups")
                except Exception as e:
                    print(f" → Critical error: {e}")
                    # Write original row on error
                    output_row = row.copy()
                    for field in scraped_fields:
                        output_row[field] = ""
                    writer.writerow(output_row)
    driver.quit()
    print(f"\nAll done! Saved to {CSV_OUTPUT}")

if __name__ == "__main__":
    main()