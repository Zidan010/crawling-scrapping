# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict, Set
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_usf_programs_headless(
    url: str,
    *,
    timeout_ms: int = 60000,
) -> pd.DataFrame:
    """
    Headless scraper for University of South Florida programs.
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
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        page.wait_for_timeout(2000)
        
        # Wait for content to load (look for links in the page)
        page.wait_for_selector("a[href*='preview_program.php']", timeout=timeout_ms)
        
        def collect_rows() -> List[Dict[str, str]]:
            rows = []
            
            # Find all program links
            program_links = page.query_selector_all("a[href*='preview_program.php']")
            
            for link in program_links:
                try:
                    # Extract program URL
                    relative_url = link.get_attribute("href") or ""
                    program_url = urljoin(url, relative_url)
                    
                    # Extract program name
                    program_name = _clean(link.inner_text())
                    
                    # Skip if no program name
                    if not program_name:
                        continue
                    
                    rows.append({
                        "program_name": program_name,
                        "programUrl": program_url,
                        "degree_program_parsing_link": url,
                        "university_name": "University of South Florida",
                        "rank_type_1": "CS",
                        "position_1": "83",
                        "url": "https://www.usf.edu/",
                        "email": "",
                        "phone": "813-974-2011",
                        "country": "USA",
                        "city": "Tampa",
                        "zipcode": "33620",
                        "address": "Tampa, FL 33620",
                        "campus_name":"Tampa"
                    })
                except Exception as e:
                    print(f"Error processing program link: {e}")
                    continue
            
            return rows
        
        # Collect all programs
        all_rows = collect_rows()
        
        browser.close()
    
    # Remove duplicates based on programUrl
    df = pd.DataFrame(all_rows).drop_duplicates(subset=["programUrl"])
    
    return df

if __name__ == "__main__":
    url = "https://catalog.usf.edu/content.php?catoid=24&navoid=4077"
    df = scrape_usf_programs_headless(url)
    
    print("\n" + "="*50)
    print(df.head(20))
    print("="*50)
    print(f"\nTotal rows: {len(df)}")
    
    df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_programs_usf_G.csv", index=False)
    print("Saved to usf_programs.csv")