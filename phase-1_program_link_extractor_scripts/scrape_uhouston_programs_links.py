# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    """Clean text: remove extra spaces, non-breaking spaces, etc."""
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_uh_programs_simple(
    url: str,
    *,
    timeout_ms: int = 90000,
) -> pd.DataFrame:
    """
    Simple headless scraper for University of Houston programs.
    Collects only:
      - program_name
      - programUrl
      
    Targets all <a> links containing "preview_program.php" in href.
    Works well for Acalog-style catalogs where programs are listed as direct links.
    """
    
    base_url = "https://publications.uh.edu/"
    
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
        
        print("Loading page...")
        page.goto(url, wait_until="networkidle", timeout=timeout_ms)  # networkidle is usually better for catalogs
        page.wait_for_timeout(5000)
        
        # Scroll several times to make sure any lazy-loaded or bottom content appears
        print("Scrolling to load full content...")
        for _ in range(12):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1200)
        
        page.wait_for_timeout(3000)
        print("Page fully loaded, extracting program links...")
        
        def collect_programs() -> List[Dict[str, str]]:
            rows = []
            
            # Most reliable selector: ALL links pointing to individual program previews
            program_links = page.query_selector_all('a[href*="preview_program.php"]')
            
            print(f"Found {len(program_links)} potential program links")
            
            for link in program_links:
                try:
                    # Get clean program name
                    name = _clean(link.inner_text())
                    if not name or len(name) < 5 or "returnto" in name.lower():
                        continue
                    
                    # Get href and build full URL
                    href = link.get_attribute("href") or ""
                    if not href:
                        continue
                    
                    full_url = urljoin(base_url, href)
                    
                    # Skip if it's not a proper program link (safety check)
                    if "preview_program.php" not in full_url:
                        continue
                    
                    rows.append({
                        "program_name": name,
                        "programUrl": full_url,
                        "degree_program_parsing_link": url,
                        "university_name": "University of Houston",
                        "url": "https://www.uh.edu/",
                        "rank_type_1": "CS",
                        "position_1": "93",
                        "country": "USA",
                        "city": "Houston",
                        "zipcode": "77204",
                        "address": "212 Ezekiel W. Cullen Building, Houston, TX 77204",
                        "campus_name":"Houston"
                    })
                except Exception as e:
                    print(f"Error processing link: {e}")
                    continue
            
            print(f"Collected {len(rows)} valid programs after filtering")
            return rows
        
        all_rows = collect_programs()
        
        browser.close()
    
    df = pd.DataFrame(all_rows).drop_duplicates(subset=["programUrl"])
    
    return df

if __name__ == "__main__":
    url = "https://publications.uh.edu/content.php?catoid=56&navoid=21093"
    df = scrape_uh_programs_simple(url)
    
    if len(df) == 0:
        print("No programs collected.")
        print("Possible reasons:")
        print("1. Page returned error (check manually)")
        print("2. Programs are loaded via JavaScript after clicking filters/tabs")
        print("3. Different link pattern — inspect element to see actual hrefs")
        print("Try opening the page in browser and search for 'preview_program.php'")
    else:
        print("\n" + "="*80)
        print("Sample of scraped programs:")
        print("="*80)
        print(df[["program_name", "programUrl"]].head(40).to_string(index=False))
        print("="*80)
        print(f"\nTotal unique programs scraped: {len(df)}")
        
        # Save to CSV
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_uhouston_programs.csv", index=False)
        print("\nSaved to uh_programs_simple.csv")