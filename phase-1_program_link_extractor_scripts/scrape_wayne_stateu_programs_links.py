# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    """Clean text: normalize spaces, remove extras."""
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_wayne_programs(
    url: str = "https://wayne.edu/programs",
    timeout_ms: int = 60000,
) -> pd.DataFrame:
    """
    Scraper for Wayne State University programs page.
    Extracts from <ul class="space-y-4 lg:space-y-3"> and each <li class="program-item">.
    For each program, creates separate rows for each degree option with:
      - program_name
      - degree_code (e.g. BA, BS, MS)
      - programUrl
    """
    
    base_url = "https://wayne.edu/"
    
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
        
        print("Loading Wayne State programs page...")
        page.goto(url, wait_until="networkidle", timeout=timeout_ms)
        
        # Wait for the main list container
        try:
            page.wait_for_selector('ul[class*="space-y-4"]', timeout=30000)
            print("Found programs list container.")
            page.wait_for_timeout(4000)  # extra time for dynamic elements if any
        except Exception as e:
            print(f"Warning: Could not find list container: {e}")
            print("Trying to proceed...")
        
        rows: List[Dict[str, str]] = []
        
        # Find the main <ul> (using partial class match)
        program_ul = page.query_selector('ul[class*="space-y-4"]')
        if not program_ul:
            print("No main <ul> found. Falling back to all program-item <li>.")
            program_items = page.query_selector_all('li.program-item')
        else:
            program_items = program_ul.query_selector_all('li.program-item')
        
        print(f"Found {len(program_items)} program items")
        
        for item in program_items:
            try:
                # Program name from first span
                name_span = item.query_selector('span.text-lg, span[class*="text-lg"]')
                program_name = _clean(name_span.inner_text()) if name_span else ""
                if not program_name:
                    continue
                
                # Each degree span
                degree_spans = item.query_selector_all('span[data-level]')
                
                for deg_span in degree_spans:
                    link = deg_span.query_selector('a[href]')
                    if not link:
                        continue
                    
                    degree_type = _clean(link.inner_text())
                    if not degree_type:
                        continue
                    
                    href = link.get_attribute("href") or ""
                    program_url = urljoin(base_url, href)
                    
                    rows.append({
                        "program_name": program_name,
                        "degree_code": degree_type,
                        "programUrl": program_url,
                        "university_name": "Wayne State University",
                        "degree_program_parsing_link": url,
                        "url": "https://wayne.edu/",
                        "country": "USA",
                        "city": "Detroit",
                        "zipcode": "48202",
                        "address": "42 W. Warren Ave., Detroit, MI 48202",
                        "campus_name":"Detroit",
                        "rank_type_1": "CS",
                        "position_1": "93",
                    })
            except Exception as e:
                print(f"Error processing program item: {e}")
                continue
        
        browser.close()
    
    if not rows:
        print("No programs collected. Possible issues:")
        print("• List loads after filter/interaction (e.g. click 'All Programs')")
        print("• Class names changed → inspect current page")
        print("• Bot detection → try headless=False")
    
    df = pd.DataFrame(rows)#.drop_duplicates(subset=["programUrl"])
    
    return df

if __name__ == "__main__":
    df = scrape_wayne_programs()
    
    if len(df) == 0:
        print("No data collected.")
    else:
        print("\n" + "="*100)
        print("Sample of scraped Wayne State programs:")
        print("="*100)
        print(df[["program_name", "degree_code", "programUrl"]].head(40).to_string(index=False))
        print("="*100)
        print(f"\nTotal unique program entries scraped: {len(df)}")
        
        # Show degree type distribution
        print("\nDegree type distribution:")
        print(df["degree_code"].value_counts())
        
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_wayne_stateu_programs.csv", index=False)
        print("\nSaved to wayne_programs.csv")