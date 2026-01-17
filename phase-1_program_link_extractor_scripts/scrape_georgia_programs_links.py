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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ----------------------------- CONFIG -----------------------------
CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_input_files/ugeorgia_input_latest.csv"
CSV_OUTPUT = "../crawling-scrapping/phase-1_output_files_phase-2_input/extracted_programs_ugeorgia_latest.csv"

# Headless Chrome setup
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 60)

# ----------------------------- HELPERS -----------------------------
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip() if text else ""

def scroll_to_load_all():
    """Scroll to ensure all content is loaded"""
    print("    Scrolling to load content...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    time.sleep(1)

def debug_page_structure():
    """Debug function to understand page structure"""
    print("\n  🔍 DEBUGGING PAGE STRUCTURE:")
    try:
        # Check for common elements
        body_html = driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")
        print(f"  - Body HTML length: {len(body_html)} characters")
        
        # Check for specific elements
        elements_to_check = [
            ("ID: paginationContent", By.ID, "paginationContent"),
            ("CLASS: entry-card", By.CLASS_NAME, "entry-card"),
            ("CLASS: program-card", By.CLASS_NAME, "program-card"),
            ("LINK: View all Programs", By.PARTIAL_LINK_TEXT, "View all"),
            ("TAG: article", By.TAG_NAME, "article"),
            ("CLASS: flex-70", By.CLASS_NAME, "flex-70"),
        ]
        
        for desc, by, value in elements_to_check:
            try:
                elems = driver.find_elements(by, value)
                print(f"  - {desc}: Found {len(elems)} element(s)")
                if len(elems) > 0 and len(elems) < 5:
                    for i, elem in enumerate(elems[:3]):
                        text = elem.text[:100] if elem.text else "(no text)"
                        print(f"    [{i}]: {text}")
            except:
                print(f"  - {desc}: Not found")
        
        # Print first 1000 chars of body text
        body_text = driver.find_element(By.TAG_NAME, "body").text[:1000]
        print(f"\n  📄 Page text preview:\n  {body_text}\n")
        
    except Exception as e:
        print(f"  ✗ Debug error: {e}")

def extract_programs_from_listing(page_url):
    """Extract all programs from paginated listing"""
    print(f"  Loading listing page: {page_url}")
    driver.get(page_url)
    time.sleep(5)  # Initial load wait
    
    # Debug the page structure first
    debug_page_structure()
    
    # Try multiple strategies to trigger program listing
    print("\n  📋 Attempting to load program listing...")
    
    # Strategy 1: Click "View all Programs" button
    try:
        print("  Strategy 1: Looking for 'View all Programs' button...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        links = driver.find_elements(By.TAG_NAME, "a")
        
        for elem in buttons + links:
            text = clean_text(elem.text).lower()
            if "view all" in text or "view all programs" in text:
                print(f"  ✓ Found button/link with text: '{elem.text}'")
                driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", elem)
                print("  ✓ Clicked! Waiting for content to load...")
                time.sleep(5)
                break
        else:
            print("  ⚠ No 'View all Programs' button found")
    except Exception as e:
        print(f"  ⚠ Strategy 1 failed: {e}")
    
    # Strategy 2: Check if we need to submit a form or apply filters
    try:
        print("  Strategy 2: Checking for forms or filter buttons...")
        submit_buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        if submit_buttons:
            print(f"  Found {len(submit_buttons)} submit button(s)")
            for btn in submit_buttons:
                print(f"    Button text: '{btn.text}'")
    except Exception as e:
        print(f"  ⚠ Strategy 2 check failed: {e}")
    
    # Strategy 3: Try to execute any JavaScript that might load programs
    try:
        print("  Strategy 3: Checking for JavaScript functions...")
        js_functions = ["loadAllPrograms()", "showAllPrograms()", "applyFilters()"]
        for func in js_functions:
            try:
                driver.execute_script(func)
                print(f"  ✓ Executed {func}")
                time.sleep(3)
            except:
                pass
    except:
        pass
    
    # Now try to find programs
    print("\n  🔍 Searching for program elements...")
    scroll_to_load_all()
    
    # Wait and check for pagination content
    try:
        wait.until(EC.presence_of_element_located((By.ID, "paginationContent")))
        print("  ✓ Found paginationContent container")
    except:
        print("  ⚠ No paginationContent container found")
    
    programs = []
    page_num = 1
    max_pages = 100
    
    while page_num <= max_pages:
        print(f"\n  === Page {page_num} ===")
        scroll_to_load_all()
        time.sleep(2)
        
        # Try multiple selectors to find program cards
        cards = []
        selectors = [
            "#paginationContent .entry-card",
            ".entry-card",
            ".program-card",
            "article.entry-card",
            "div[class*='entry-card']",
            "div[class*='program-card']",
        ]
        
        for selector in selectors:
            try:
                cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if cards:
                    print(f"  ✓ Found {len(cards)} cards using selector: {selector}")
                    break
            except:
                continue
        
        if not cards:
            print("  ✗ No program cards found with any selector")
            print("\n  🔍 Final page structure check:")
            debug_page_structure()
            break
        
        # Extract data from cards
        for idx, card in enumerate(cards, 1):
            try:
                # Get program name - try multiple approaches
                program_name = ""
                name_selectors = [
                    "p.large-mw",
                    ".entry-card--text p",
                    "h3",
                    "h4",
                    "p[class*='large']",
                    "p",
                ]
                
                for sel in name_selectors:
                    try:
                        name_elem = card.find_element(By.CSS_SELECTOR, sel)
                        program_name = clean_text(name_elem.text)
                        if program_name:
                            break
                    except:
                        continue
                
                if not program_name:
                    print(f"    Card {idx}: No program name found, skipping")
                    continue
                
                # Find degree links
                degree_links = []
                link_selectors = [
                    "a.btn.btn--outline",
                    ".entry-card--text a",
                    "a[href*='/Program/']",
                    "a.btn",
                    "a",
                ]
                
                for sel in link_selectors:
                    try:
                        degree_links = card.find_elements(By.CSS_SELECTOR, sel)
                        if degree_links:
                            break
                    except:
                        continue
                
                if not degree_links:
                    print(f"    Card {idx} ({program_name}): No degree links found")
                    continue
                
                print(f"    Card {idx}: {program_name} - {len(degree_links)} degree(s)")
                
                # Extract each degree
                for deg_idx, link in enumerate(degree_links, 1):
                    try:
                        degree_text = clean_text(link.text)
                        if not degree_text or len(degree_text) > 200:  # Skip if too long
                            continue
                        
                        degree_href = link.get_attribute("href")
                        if not degree_href or "javascript:" in degree_href:
                            continue
                        
                        program_url = urljoin(page_url, degree_href)
                        
                        # Extract degree class from span if exists
                        degree_type = degree_text
                        try:
                            span = link.find_element(By.TAG_NAME, "span")
                            class_attr = span.get_attribute("class") or ""
                            degree_class = re.sub(r'program-', '', class_attr).strip()
                            if degree_class and degree_class not in degree_text.lower():
                                degree_type = f"{degree_text} ({degree_class})"
                        except:
                            pass
                        
                        programs.append({
                            "program_name": program_name,
                            "degree_type": degree_type,
                            "programUrl": program_url
                        })
                        print(f"      ✓ {degree_type}")
                        
                    except Exception as e:
                        print(f"      ✗ Error extracting degree {deg_idx}: {e}")
                        continue
                        
            except Exception as e:
                print(f"    ✗ Error parsing card {idx}: {e}")
                continue
        
        # Check for next page
        try:
            next_btn = driver.find_element(By.ID, "nextPageBtn")
            is_disabled = next_btn.get_attribute("disabled")
            btn_classes = next_btn.get_attribute("class") or ""
            
            if is_disabled or "disabled" in btn_classes.lower():
                print(f"\n  ✓ Reached last page")
                break
            
            old_content = driver.find_element(By.ID, "paginationContent").get_attribute("innerHTML")
            print(f"  → Clicking Next...")
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(4)
            
            try:
                wait.until(lambda d: d.find_element(By.ID, "paginationContent").get_attribute("innerHTML") != old_content)
                print(f"  ✓ Page {page_num + 1} loaded")
            except TimeoutException:
                print(f"  ⚠ Timeout - assuming end")
                break
            
            page_num += 1
            
        except NoSuchElementException:
            print(f"\n  ✓ No Next button - end of pagination")
            break
        except Exception as e:
            print(f"\n  ⚠ Pagination error: {e}")
            break
    
    print(f"\n  📊 Total: {len(programs)} program entries from {page_num} page(s)")
    return programs

# ----------------------------- MAIN -----------------------------
def main():
    input_path = Path(CSV_INPUT)
    output_path = Path(CSV_OUTPUT)
    
    if not input_path.exists():
        print(f"❌ Input CSV not found: {CSV_INPUT}")
        return
    
    file_exists = output_path.exists()
    
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        input_fieldnames = reader.fieldnames
        scraped_fields = ["program_name", "degree_type", "programUrl"]
        output_fieldnames = list(input_fieldnames) + [f for f in scraped_fields if f not in input_fieldnames]
    
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        with open(output_path, 'a', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            for row_num, row in enumerate(reader, 1):
                listing_url = row.get("degree_program_link", "").strip()
                uni_name = row.get("university_name", "Unknown University")
                
                if not listing_url:
                    print(f"\n⚠ Row {row_num}: Skipping - no degree_program_link")
                    continue
                
                print(f"\n{'='*60}")
                print(f"🎓 {uni_name}")
                print(f"🔗 {listing_url}")
                print(f"{'='*60}")
                
                try:
                    programs = extract_programs_from_listing(listing_url)
                    
                    if not programs:
                        print(f"\n  ⚠ No programs extracted - writing empty row")
                        output_row = row.copy()
                        for field in scraped_fields:
                            output_row[field] = ""
                        writer.writerow(output_row)
                    else:
                        for program in programs:
                            output_row = row.copy()
                            output_row.update(program)
                            writer.writerow(output_row)
                        print(f"\n  ✅ Successfully wrote {len(programs)} program entries")
                    
                    outfile.flush()
                    
                except Exception as e:
                    print(f"\n  ❌ Critical error: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    output_row = row.copy()
                    for field in scraped_fields:
                        output_row[field] = ""
                    writer.writerow(output_row)
                
                time.sleep(2)
    
    driver.quit()
    print(f"\n{'='*60}")
    print(f"✅ All done! Output saved to: {CSV_OUTPUT}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()