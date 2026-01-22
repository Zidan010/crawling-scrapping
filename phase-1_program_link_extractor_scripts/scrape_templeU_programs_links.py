# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_temple_programs_headless(
    url: str,
    *,
    timeout_ms: int = 60000,
) -> pd.DataFrame:
    """
    Headless scraper for Temple University programs.
    Extracts:
      program_name
      programUrl
      degree_type (parsed from URL)
      school (parsed from URL)
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
        
        # Scroll to ensure all content is loaded
        print("Scrolling to load all programs...")
        for i in range(10):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)
        
        page.wait_for_timeout(2000)
        print("Page loaded, extracting data...")
        
        def collect_rows() -> List[Dict[str, str]]:
            rows = []
            
            # Find all program items
            program_items = page.query_selector_all("li.program")
            
            print(f"Found {len(program_items)} program items")
            
            for item in program_items:
                try:
                    # Get the link
                    link = item.query_selector("a[href]")
                    if not link:
                        continue
                    
                    # Get program URL
                    relative_url = link.get_attribute("href") or ""
                    program_url = urljoin("https://www.temple.edu/", relative_url)
                    
                    # Get program name
                    program_name = _clean(link.inner_text())
                    if not program_name:
                        continue
                    
                    # Parse degree_type and school from URL slug
                    slug = relative_url.split("/")[-1] if "/" in relative_url else relative_url
                    parts = slug.split("-")
                    degree_type = ""
                    school = ""
                    if len(parts) >= 3:
                        degree_type = parts[-1].upper()
                        school = parts[-3].upper()
                    
                    rows.append({
                        "program_name": program_name,
                        "programUrl": program_url,
                        "degree_type": degree_type,
                        "school": school,
                        "degree_program_parsing_link": url,
                        "university_name": "Temple University",
                        "rank_type_1": "CS",  # Fill if known
                        "position_1": "93",   # Fill if known
                        "url": "https://www.temple.edu/",
                        "email": "",
                        "phone": "",
                        "country": "USA",
                        "city": "Philadelphia",
                        "zipcode": "19122",
                        "address": "1801 N. Broad St., Philadelphia, PA 19122",
                        "campus_name":"Philadelphia"
                    })
                except Exception as e:
                    print(f"Error processing program item: {e}")
                    continue
            
            print(f"Collected {len(rows)} programs")
            return rows
        
        # Collect all programs
        all_rows = collect_rows()
        
        browser.close()
    
    return pd.DataFrame(all_rows).drop_duplicates(subset=["programUrl"])

if __name__ == "__main__":
    url = "https://www.temple.edu/academics/degree-programs"
    df = scrape_temple_programs_headless(url)
    
    if len(df) == 0:
        print("No data collected. Please check the page structure.")
    else:
        print("\n" + "="*80)
        print("Sample of scraped programs:")
        print("="*80)
        print(df[["program_name", "degree_type", "school", "programUrl"]].head(30).to_string(index=False))
        print("="*80)
        print(f"\nTotal unique programs scraped: {len(df)}")
        
        # Show degree type distribution
        print("\nDegree type distribution:")
        print(df["degree_type"].value_counts())
        
        # Save to CSV
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_templeU_programs.csv", index=False)
        print("\nSaved to temple_programs.csv")