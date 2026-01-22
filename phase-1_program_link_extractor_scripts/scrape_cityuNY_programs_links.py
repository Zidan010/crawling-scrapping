# # pip install playwright
# # playwright install chromium
# from __future__ import annotations
# from typing import List, Dict
# from urllib.parse import urljoin
# import pandas as pd
# from playwright.sync_api import sync_playwright
# import time

# def _clean(s: str) -> str:
#     return " ".join((s or "").replace("\xa0", " ").split()).strip()

# def scrape_cuny_programs_headless(
#     url: str,
#     *,
#     timeout_ms: int = 60000,
#     max_pages: int = 100,
# ) -> pd.DataFrame:
#     """
#     Headless scraper for CUNY University programs.
#     Extracts from paginated DataTable:
#       department (College)
#       program_name (Degree Program)
#       programUrl
#       degree_type
#     """
    
#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=True,  # Set to True after testing
#             args=[
#                 "--disable-blink-features=AutomationControlled",
#                 "--no-sandbox",
#                 "--disable-dev-shm-usage",
#             ],
#         )
#         page = browser.new_page()
        
#         # Load page & wait for content
#         print("Loading page...")
#         page.goto(url, wait_until="networkidle", timeout=timeout_ms)
#         page.wait_for_timeout(3000)
        
#         # Wait for the table to be visible
#         print("Waiting for table...")
#         page.wait_for_selector("table#undergrad-programs", timeout=timeout_ms, state="visible")
#         page.wait_for_timeout(2000)
        
#         # Wait for DataTable to initialize
#         page.wait_for_selector("table#undergrad-programs tbody tr", timeout=timeout_ms)
#         page.wait_for_timeout(1000)
        
#         all_rows: List[Dict[str, str]] = []
#         pages_scraped = 0
        
#         while pages_scraped < max_pages:
#             print(f"\nScraping page {pages_scraped + 1}...")
            
#             # Wait a bit for any animations
#             page.wait_for_timeout(1000)
            
#             # Get all rows from current page
#             rows = page.query_selector_all("table#undergrad-programs tbody tr")
#             print(f"Found {len(rows)} rows on this page")
            
#             page_row_count = 0
#             for row in rows:
#                 try:
#                     # Check if row has the "no data" message
#                     if "dataTables_empty" in (row.get_attribute("class") or ""):
#                         continue
                    
#                     cells = row.query_selector_all("td")
                    
#                     if len(cells) < 3:
#                         print(f"  Skipping row with {len(cells)} cells")
#                         continue
                    
#                     # Extract department (College) - first column
#                     department = _clean(cells[0].inner_text())
                    
#                     # Extract program name and URL - second column
#                     program_cell = cells[1]
#                     program_link = program_cell.query_selector("a")
                    
#                     if program_link:
#                         program_name = _clean(program_link.inner_text())
#                         program_url = program_link.get_attribute("href") or ""
#                     else:
#                         # Some rows might not have links
#                         program_name = _clean(program_cell.inner_text())
#                         program_url = ""
                    
#                     # Extract degree type - third column
#                     degree_type = _clean(cells[2].inner_text())
                    
#                     # Skip empty rows
#                     if not program_name or not department:
#                         continue
                    
#                     all_rows.append({
#                         "program_name": program_name,
#                         "department": department,
#                         "degree_type": degree_type,
#                         "programUrl": program_url,
#                         "degree_program_parsing_link": url,
#                         "university_name": "City University of New York",
#                         "rank_type_1": "CS",
#                         "position_1": "88",
#                         "url": "https://www.cuny.edu/",
#                         "email": "",
#                         "phone": "",
#                         "country": "USA",
#                         "city": "New York",
#                         "zipcode": "10004",
#                         "address": "New York, NY 10004",
#                         "campus_name":"New York"
#                     })
#                     page_row_count += 1
                    
#                 except Exception as e:
#                     print(f"  Error processing row: {e}")
#                     continue
            
#             print(f"Successfully collected {page_row_count} programs from page {pages_scraped + 1}")
#             pages_scraped += 1
            
#             # Look for next button - try multiple selectors
#             next_button = None
#             next_selectors = [
#                 "a#undergrad-programs_next",
#                 "a.paginate_button.next",
#                 "#undergrad-programs_next",
#                 "div.dataTables_paginate a.next",
#                 "div#undergrad-programs_paginate a.next"
#             ]
            
#             for selector in next_selectors:
#                 next_button = page.query_selector(selector)
#                 if next_button:
#                     print(f"Found next button with selector: {selector}")
#                     break
            
#             if not next_button:
#                 print("No next button found with any selector")
#                 # Let's see what pagination elements exist
#                 pagination = page.query_selector("div.dataTables_paginate")
#                 if pagination:
#                     print("Pagination HTML:", pagination.inner_html()[:200])
#                 break
            
#             # Check if next button is disabled
#             classes = next_button.get_attribute("class") or ""
#             aria_disabled = next_button.get_attribute("aria-disabled") or ""
            
#             print(f"Next button classes: {classes}")
#             print(f"Next button aria-disabled: {aria_disabled}")
            
#             if "disabled" in classes or aria_disabled == "true":
#                 print("Next button is disabled - reached last page")
#                 break
            
#             try:
#                 # Scroll to next button
#                 next_button.scroll_into_view_if_needed(timeout=2000)
#                 page.wait_for_timeout(500)
                
#                 # Click next button
#                 print("Clicking next button...")
#                 next_button.click(timeout=3000)
                
#                 # Wait for table to update
#                 page.wait_for_timeout(2000)
                
#                 # Wait for loading to complete (if there's a loading indicator)
#                 # Try to wait for the processing class to disappear
#                 try:
#                     page.wait_for_selector("div#undergrad-programs_processing[style*='display: none']", timeout=5000)
#                 except:
#                     pass
                
#                 page.wait_for_timeout(1000)
                
#             except Exception as e:
#                 print(f"Error navigating to next page: {e}")
#                 break
        
#         browser.close()
    
#     print(f"\n{'='*50}")
#     print(f"Total programs collected: {len(all_rows)}")
#     print(f"{'='*50}")
    
#     if not all_rows:
#         print("\nWARNING: No data collected. The page structure may have changed.")
#         return pd.DataFrame()
    
#     # Create DataFrame and remove duplicates
#     df = pd.DataFrame(all_rows)
#     initial_count = len(df)
#     df = df.drop_duplicates(subset=["programUrl", "program_name", "department"])
    
#     if initial_count > len(df):
#         print(f"Removed {initial_count - len(df)} duplicate entries")
    
#     return df

# if __name__ == "__main__":
#     url = "https://www.cuny.edu/admissions/undergraduate/programs/"
#     df = scrape_cuny_programs_headless(url)
    
#     print("\n" + "="*50)
#     print("Sample data:")
#     print(df.head(20))
#     print("="*50)
#     print(f"\nTotal unique rows: {len(df)}")
    
#     if len(df) > 0:
#         df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_programs_cuny_ug.csv", index=False)
#         print("Saved to cuny_programs.csv")
#     else:
#         print("No data to save")











##### graduate #######


# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_cuny_graduate_programs_headless(
    url: str,
    *,
    timeout_ms: int = 60000,
) -> pd.DataFrame:
    """
    Headless scraper for CUNY Graduate programs.
    Extracts from table:
      department (College)
      program_name (Degree Program)
      programUrl
      degree_type
    """
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,  # Set to True after testing
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        page = browser.new_page()
        
        # Load page & wait for content
        print("Loading page...")
        page.goto(url, wait_until="networkidle", timeout=timeout_ms)
        page.wait_for_timeout(3000)
        
        # Wait for the table to be visible - correct ID is ajaxprograms
        print("Waiting for table...")
        page.wait_for_selector("table#ajaxprograms", timeout=timeout_ms, state="visible")
        page.wait_for_timeout(2000)
        
        # Wait for table rows to load
        page.wait_for_selector("table#ajaxprograms tbody tr", timeout=timeout_ms)
        page.wait_for_timeout(2000)
        
        all_rows: List[Dict[str, str]] = []
        
        print("Scraping programs...")
        
        # Get all rows from the table
        rows = page.query_selector_all("table#ajaxprograms tbody tr")
        print(f"Found {len(rows)} rows in table")
        
        # If still 0, let's debug
        if len(rows) == 0:
            print("\nDEBUG: Looking for any tables on the page...")
            all_tables = page.query_selector_all("table")
            print(f"Total tables found: {len(all_tables)}")
            for i, table in enumerate(all_tables):
                table_id = table.get_attribute("id") or "no-id"
                table_class = table.get_attribute("class") or "no-class"
                print(f"  Table {i+1}: id='{table_id}', class='{table_class}'")
        
        for idx, row in enumerate(rows, 1):
            try:
                # Check if row has the "no data" message
                row_class = row.get_attribute("class") or ""
                if "dataTables_empty" in row_class:
                    continue
                
                cells = row.query_selector_all("td")
                
                if len(cells) < 3:
                    print(f"  Row {idx}: Skipping row with {len(cells)} cells")
                    continue
                
                # Extract department (College) - first column
                department = _clean(cells[0].inner_text())
                
                # Extract program name and URL - second column
                program_cell = cells[2]
                program_link = program_cell.query_selector("a")
                
                if program_link:
                    program_name = _clean(program_link.inner_text())
                    program_url = program_link.get_attribute("href") or ""
                else:
                    # Some rows might not have links
                    program_name = _clean(program_cell.inner_text())
                    program_url = ""
                
                # Extract degree type - third column
                degree_type = _clean(cells[3].inner_text())
                
                # Skip empty rows
                if not program_name or not department:
                    print(f"  Row {idx}: Skipping empty row (program='{program_name}', dept='{department}')")
                    continue
                
                all_rows.append({
                    "program_name": program_name,
                    "department": department,
                    "degree_type": degree_type,
                    "programUrl": program_url,
                    "degree_program_parsing_link": url,
                    "university_name": "City University of New York",
                    "program_level": "Graduate",
                    "rank_type_1": "",
                    "position_1": "",
                    "url": "https://www.cuny.edu/",
                    "email": "",
                    "phone": "",
                    "country": "USA",
                    "city": "New York", 
                    "zipcode": "10004",
                    "address": "New York, NY 10004",
                    "campus_name":"New York"
                })
                
                if idx % 50 == 0:
                    print(f"  Processed {idx} rows...")
                
            except Exception as e:
                print(f"  Row {idx}: Error processing - {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\nSuccessfully collected {len(all_rows)} programs")
        browser.close()
    
    print(f"\n{'='*50}")
    print(f"Total programs collected: {len(all_rows)}")
    print(f"{'='*50}")
    
    if not all_rows:
        print("\nWARNING: No data collected. The page structure may have changed.")
        return pd.DataFrame()
    
    # Create DataFrame and remove duplicates
    df = pd.DataFrame(all_rows)
    initial_count = len(df)
    df = df.drop_duplicates(subset=["programUrl", "program_name", "department"])
    
    if initial_count > len(df):
        print(f"Removed {initial_count - len(df)} duplicate entries")
    
    return df

if __name__ == "__main__":
    url = "https://www.cuny.edu/admissions/graduate-studies/explore/academic-programs/"
    df = scrape_cuny_graduate_programs_headless(url)
    
    print("\n" + "="*50)
    print("Sample data:")
    print(df.head(20))
    print("="*50)
    print(f"\nTotal unique rows: {len(df)}")
    
    if len(df) > 0:
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_programs_cuny_G.csv", index=False)
        print("Saved to updated-extracted_programs_cuny_ug.csv")
    else:
        print("No data to save")