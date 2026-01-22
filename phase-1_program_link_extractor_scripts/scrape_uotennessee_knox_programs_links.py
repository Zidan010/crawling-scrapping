# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    """Clean text: normalize spaces, remove •, nbsp, etc."""
    return " ".join((s or "").replace("\xa0", " ").replace("•", "").split()).strip()

def scrape_utk_programs(
    url: str = "https://catalog.utk.edu/content.php?catoid=54&navoid=11859",
    timeout_ms: int = 60000,
) -> pd.DataFrame:
    """
    Scraper for University of Tennessee, Knoxville catalog programs.
    Finds all <ul class="program-list"> inside <td class="block_content">
    Extracts program name and full preview URL from each <a>.
    """
    
    base_url = "https://catalog.utk.edu/"
    
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
        
        print("Loading UTK catalog programs page...")
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        
        # Give time for content to appear (Acalog pages are usually static)
        page.wait_for_timeout(4000)
        
        # Optional: scroll to bottom in case of lazy elements (rare here)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        
        rows: List[Dict[str, str]] = []
        
        # Find all program lists
        program_lists = page.query_selector_all('td.block_content ul.program-list')
        print(f"Found {len(program_lists)} program-list <ul> blocks")
        
        for ul in program_lists:
            # Get all links inside this list
            links = ul.query_selector_all('li a[href*="preview_program.php"]')
            
            for link in links:
                try:
                    full_name = _clean(link.inner_text())
                    if not full_name:
                        continue
                    
                    href = link.get_attribute("href") or ""
                    if not href or "preview_program.php" not in href:
                        continue
                    
                    program_url = urljoin(base_url, href)
                    
                    rows.append({
                        "program_name": full_name,
                        "programUrl": program_url,
                        "university_name": "University of Tennessee, Knoxville",
                        "degree_program_parsing_link": url,
                        "url": "https://utk.edu/",
                        "country": "USA",
                        "city": "Knoxville",
                        "zipcode": "37996",
                        "address": "Knoxville, TN 37996",
                        "campus_name":"Knoxville",
                        "rank_type_1": "CS",
                        "position_1": "93",
                        "phone":"865-974-1000"
                    })
                except Exception as e:
                    print(f"Error processing link: {e}")
                    continue
        
        browser.close()
    
    if not rows:
        print("No programs found. Possible reasons:")
        print("• Content loaded via JavaScript after delay")
        print("• Different class names in current catalog version")
        print("• Bot protection or region restriction")
        print("Try running with headless=False and inspect manually.")
    
    df = pd.DataFrame(rows).drop_duplicates(subset=["programUrl"])
    
    return df

if __name__ == "__main__":
    df = scrape_utk_programs()
    
    if len(df) == 0:
        print("No data collected.")
    else:
        print("\n" + "="*100)
        print("University of Tennessee, Knoxville Programs (sample):")
        print("="*100)
        print(df[["program_name", "programUrl"]].head(40).to_string(index=False))
        print("="*100)
        print(f"\nTotal unique programs scraped: {len(df)}")
        
        # Save result
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_uotennessee_knox_programs.csv", index=False)
        print("\nSaved to: utk_programs.csv")