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

def scrape_uoregon_undergrad_majors(
    url: str = "https://admissions.uoregon.edu/majors",
    timeout_ms: int = 60000,
) -> pd.DataFrame:
    """
    Headless scraper for University of Oregon undergraduate majors.
    Targets cards inside div.view-content.
    Extracts only:
      - program_name     (e.g. "Accounting")
      - programUrl       (full URL, e.g. https://admissions.uoregon.edu/majors/accounting)
      - department       (from h5, e.g. "Lundquist College of Business")
    """
    
    base_url = "https://admissions.uoregon.edu/"
    
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
        
        print("Loading UO undergraduate majors page...")
        # page.goto(url, wait_until="networkidle", timeout=timeout_ms)

        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        page.wait_for_selector('div.view-content', state="visible", timeout=30000)
        page.wait_for_timeout(5000)  # extra breathing room for any late JS

        # Wait for main content container
        try:
            page.wait_for_selector('div.view-content', timeout=30000)
            print("Found view-content container.")
            page.wait_for_timeout(4000)  # give time for cards to render
        except Exception as e:
            print(f"Warning: Could not reliably wait for view-content: {e}")
            print("Proceeding anyway...")
        
        rows: List[Dict[str, str]] = []
        
        # Find all card wrappers
        cards = page.query_selector_all('div.view-content div.grid__item div.card-v2')
        print(f"Found {len(cards)} program cards")
        
        for card in cards:
            try:
                # Program name & link from h4 > a
                header_link = card.query_selector('div.card-v2__header h4 a')
                if not header_link:
                    continue
                
                program_name = _clean(header_link.inner_text())
                if not program_name:
                    continue
                
                href = header_link.get_attribute("href") or ""
                program_url = urljoin(base_url, href)
                
                # Department from h5
                dept_elem = card.query_selector('div.card-v2__body h5')
                department = _clean(dept_elem.inner_text()) if dept_elem else ""
                
                rows.append({
                    "program_name": program_name,
                    "programUrl": program_url,
                    "department": department,
                    "university_name": "University of Oregon",
                    "degree_program_parsing_link": url,
                    "url": "https://www.uoregon.edu/",
                    "country": "USA",
                    "city": "Eugene",
                    "zipcode": "",
                    "address": "Eugene, OR 97403-1219",
                    "rank_type_1": "CS",
                    "position_1": "93",
                    "campus_name":"Eugene"
                })
            except Exception as e:
                print(f"Error processing one card: {e}")
                continue
        
        browser.close()
    
    if not rows:
        print("No programs extracted. Possible issues:")
        print("• Cards loaded dynamically after interaction → try headless=False")
        print("• Different container/classes → inspect page")
        print("• Page requires accepting cookies or filter selection first")
    
    df = pd.DataFrame(rows).drop_duplicates(subset=["programUrl"])
    
    return df

if __name__ == "__main__":
    df = scrape_uoregon_undergrad_majors()
    
    if len(df) == 0:
        print("No data collected.")
    else:
        print("\n" + "="*100)
        print("University of Oregon Undergraduate Majors (sample):")
        print("="*100)
        print(df[["program_name", "department", "programUrl"]].head(30).to_string(index=False))
        print("="*100)
        print(f"\nTotal unique majors scraped: {len(df)}")
        
        # Quick stats
        print("\nTop departments:")
        print(df["department"].value_counts().head(10))
        
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_uoregon_ug_programs.csv", index=False)
        print("\nSaved to: uoregon_undergrad_majors.csv")