# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict, Set
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright
import time

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_umbc_programs_headless(
    url: str,
    *,
    timeout_ms: int = 90000,
    scroll_rounds: int = 10,
) -> pd.DataFrame:
    """
    Headless scraper for UMBC programs.
    Extracts:
      program_name
      programUrl (absolute)
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
        
        # Wait for the programs to load - the page uses dynamic loading
        # Look for any program links to appear
        page.wait_for_timeout(3000)
        
        # Wait for program content to load
        try:
            page.wait_for_selector("a[href*='/programs/']", timeout=30000)
            print("Program links loaded")
        except Exception as e:
            print(f"Warning: Timeout waiting for program links: {e}")
        
        # Scroll to load all programs
        print("Scrolling to load all programs...")
        for i in range(scroll_rounds):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)
            if i % 3 == 0:
                print(f"Scroll round {i+1}/{scroll_rounds}")
        
        # Additional wait for final content
        page.wait_for_timeout(2000)
        
        def collect_rows() -> List[Dict[str, str]]:
            rows = []
            
            # Find all program links
            # Based on the HTML structure, programs are organized in sections
            # Each program has a link like: href="https://umbc.edu/programs/..."
            
            program_links = page.query_selector_all("a[href*='/programs/']")
            print(f"Found {len(program_links)} program link elements")
            
            seen_urls = set()
            
            for link in program_links:
                try:
                    href = link.get_attribute("href") or ""
                    
                    # Skip navigation links and category pages
                    if not href or "programs/" not in href:
                        continue
                    
                    # Only get actual program pages (not category/overview pages)
                    # Program pages typically end with specific program names
                    if (href.endswith("/programs/") or 
                        "/undergraduate/" in href and href.endswith("programs/") or
                        "/graduate/" in href and href.endswith("programs/")):
                        continue
                    
                    program_url = urljoin(url, href)
                    
                    # Skip duplicates
                    if program_url in seen_urls:
                        continue
                    seen_urls.add(program_url)
                    
                    # Get program name from link text
                    program_name = _clean(link.inner_text())
                    
                    if not program_name or len(program_name) < 2:
                        continue
                    
                    # Skip generic navigation text
                    skip_terms = ["major", "minor", "certificate", "master's", "ph.d", 
                                 "undergraduate", "graduate", "concentration", "focus"]
                    if program_name.lower() in skip_terms:
                        continue
                    
                    rows.append({
                        "program_name": program_name,
                        "programUrl": program_url,
                        "degree_program_parsing_link": url,
                        "university_name": "University of Maryland, Baltimore County",
                        "rank_type_1": "CS",
                        "position_1": "88",
                        "url": "https://umbc.edu/",
                        "email": "",
                        "phone": "410-455-5555",
                        "country": "USA",
                        "city": "Baltimore",
                        "zipcode": "21250",
                        "address": "1000 Hilltop Circle, Baltimore, MD 21250",
                        "campus_name":"Baltimore"
                    })
                except Exception as e:
                    continue
            
            return rows
        
        # Collect all programs
        all_rows = collect_rows()
        
        print(f"Total programs found: {len(all_rows)}")
        
        browser.close()
    
    return pd.DataFrame(all_rows).drop_duplicates(subset=["programUrl"])

if __name__ == "__main__":
    url = "https://umbc.edu/programs/"
    df = scrape_umbc_programs_headless(url)
    
    print("\n" + "="*80)
    print("Sample of scraped programs:")
    print("="*80)
    print(df[["program_name", "programUrl"]].head(30).to_string(index=False))
    print("="*80)
    print(f"\nTotal unique programs scraped: {len(df)}")
    
    # Save to CSV
    df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_umbc_programs.csv", index=False)
    print("\nSaved to umbc_programs.csv")