# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    """Clean text: remove extra spaces, line breaks, nbsp"""
    return " ".join((s or "").replace("\xa0", " ").replace("\n", " ").split()).strip()

def _split_program_title(title: str) -> tuple[str, str]:
    """Split 'Accounting, MActg' → ('Accounting', 'MActg')"""
    title = _clean(title)
    if ',' not in title:
        return title, ""
    *parts, code = title.rsplit(',', 1)
    name = ",".join(parts).strip()  # handle cases with commas in name
    return _clean(name), _clean(code)

def scrape_uoregon_programs(
    url: str = "https://insight.uoregon.edu/portal/academic_programs",
    timeout_ms: int = 60000,
) -> pd.DataFrame:
    """
    Scraper for University of Oregon graduate programs table.
    Extracts only the requested fields:
      - program_name
      - degree_code
      - programUrl
      - department (College)
      - campus_name (Location)
      - degree_type (Degree)
    """
    
    base_url = "https://insight.uoregon.edu/portal/academic_programs"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        page = browser.new_page()
        
        print("Loading University of Oregon programs page...")
        page.goto(url, wait_until="networkidle", timeout=timeout_ms)
        
        # Wait for the table to appear (important - table may load dynamically)
        try:
            page.wait_for_selector('table.table.searchable.sortable', timeout=30000)
            print("Table found!")
            page.wait_for_timeout(3000)  # give extra time for full render
        except Exception as e:
            print(f"Warning: Could not find table quickly: {e}")
            print("Trying to proceed anyway...")
        
        # Optional: screenshot for debugging
        # page.screenshot(path="uoregon_programs_table.png", full_page=True)
        
        rows: List[Dict[str, str]] = []
        
        # Get all data rows (skip header)
        table_rows = page.query_selector_all('table.table.searchable.sortable tbody tr')
        print(f"Found {len(table_rows)} table rows")
        
        for row in table_rows:
            try:
                cells = row.query_selector_all('td')
                if len(cells) < 7:
                    continue
                
                # 1. Program column (link + name)
                program_cell = cells[0]
                link = program_cell.query_selector('a[href*="programid="]')
                if not link:
                    continue
                
                full_title = _clean(link.inner_text())
                program_name, degree_code = _split_program_title(full_title)
                
                relative_href = link.get_attribute("href") or ""
                program_url = urljoin(base_url, relative_href)
                
                # 2-6. Other columns
                department = _clean(cells[1].inner_text())      # College
                campus_name = _clean(cells[2].inner_text())     # Location
                degree_type = _clean(cells[3].inner_text())     # Degree
                
                rows.append({
                    "program_name": program_name,
                    "degree_code": degree_code,
                    "programUrl": program_url,
                    "department": department,
                    "campus_name": campus_name,
                    "degree_type": degree_type,
                    "university_name": "University of Oregon",
                    "degree_program_parsing_link": url,
                    "url": "https://www.uoregon.edu/",
                    "country": "USA",
                    "city": "Eugene",
                    "zipcode": "",
                    "address": "Eugene, OR 97403-1219",
                    "rank_type_1": "CS",
                    "position_1": "93",
                })
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
        
        browser.close()
    
    if not rows:
        print("No programs extracted. Possible reasons:")
        print("• Table loads via heavy JavaScript → try increasing wait time")
        print("• Different structure → inspect the page manually")
        print("• Bot protection → try headless=False")
    
    df = pd.DataFrame(rows).drop_duplicates(subset=["programUrl"])
    
    return df

if __name__ == "__main__":
    df = scrape_uoregon_programs()
    
    if len(df) == 0:
        print("No data collected.")
    else:
        print("\n" + "="*100)
        print("University of Oregon Graduate Programs (sample):")
        print("="*100)
        print(df[["program_name", "degree_code", "degree_type", "department", "campus_name", "programUrl"]].head(25).to_string(index=False))
        print("="*100)
        print(f"\nTotal unique programs scraped: {len(df)}")
        
        # Basic stats
        print("\nDegree type distribution:")
        print(df["degree_type"].value_counts())
        
        print("\nCampus distribution:")
        print(df["campus_name"].value_counts())
        
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_uoregon_programs.csv", index=False)
        print("\nSaved to: uoregon_programs.csv")