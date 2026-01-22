from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_augusta_programs_headless(
    url: str,
    *,
    timeout_ms: int = 60000,
) -> pd.DataFrame:
    """
    Headless scraper for Augusta University programs.
    Extracts:
      program_name
      programUrl (absolute)
      degree_type
      department (college/school)
    """
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        page = browser.new_page()
        
        # Load page & wait for content
        print("Loading page...")
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        page.wait_for_timeout(4000)
        
        # Scroll to load all programs
        print("Scrolling to load all programs...")
        for i in range(8):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)
        
        page.wait_for_timeout(2000)
        print("Page loaded, extracting data...")
        
        def collect_rows() -> List[Dict[str, str]]:
            rows = []
            
            # Find all program cards with class "program"
            program_divs = page.query_selector_all("div.program")
            
            print(f"Found {len(program_divs)} program cards")
            
            for div in program_divs:
                try:
                    # Extract department from p.college
                    department = ""
                    college_elem = div.query_selector("p.college")
                    if college_elem:
                        department = _clean(college_elem.inner_text())
                    
                    # Extract program name from p.concentration
                    program_name = ""
                    concentration_elem = div.query_selector("p.concentration")
                    if concentration_elem:
                        program_name = _clean(concentration_elem.inner_text())
                    
                    # Extract degree type from div.degree
                    degree_type = ""
                    degree_elem = div.query_selector("div.degree")
                    if degree_elem:
                        degree_type = _clean(degree_elem.inner_text())
                    
                    # Extract program URL from a.link-tag
                    program_url = ""
                    link_elem = div.query_selector("a.link-tag")
                    if link_elem:
                        href = link_elem.get_attribute("href") or ""
                        program_url = urljoin(url, href)
                    
                    # Skip if missing essential data
                    if not program_name or not program_url:
                        continue
                    
                    rows.append({
                        "program_name": program_name,
                        "programUrl": program_url,
                        "degree_type": degree_type,
                        "department": department,
                        "degree_program_parsing_link": url,
                        "university_name": "Augusta University",
                        "rank_type_1": "CS",
                        "position_1": "93",
                        "url": "https://www.augusta.edu/",
                        "email": "",
                        "phone": "",
                        "country": "USA",
                        "city": "Augusta",
                        "zipcode": "30912",
                        "address": "1120 15th Street, Augusta, GA 30912",
                        "campus_name":"Augusta"
                    })
                except Exception as e:
                    print(f"Error processing program: {e}")
                    continue
            
            print(f"Collected {len(rows)} programs")
            return rows
        
        # Collect all programs
        all_rows = collect_rows()
        
        browser.close()
    
    return pd.DataFrame(all_rows).drop_duplicates(subset=["programUrl"])

if __name__ == "__main__":
    url = "https://www.augusta.edu/programs/"
    df = scrape_augusta_programs_headless(url)
    
    print("\n" + "="*80)
    print("Sample of scraped programs:")
    print("="*80)
    print(df[["program_name", "degree_type", "department"]].head(30).to_string(index=False))
    print("="*80)
    print(f"\nTotal unique programs scraped: {len(df)}")
    
    # Show department distribution
    print("\nDepartment distribution:")
    print(df["department"].value_counts().head(10))
    
    # Show degree type distribution
    print("\nDegree type distribution:")
    print(df["degree_type"].value_counts())
    
    # Save to CSV
    df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated_extracted_augusta_programs_2.csv", index=False)
    print("\nSaved to augusta_programs.csv")