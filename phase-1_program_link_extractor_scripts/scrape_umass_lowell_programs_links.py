# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    """Clean text: normalize spaces, remove nbsp etc."""
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_umass_lowell_programs(
    url: str = "https://www.uml.edu/academics/programs/?search=",
    timeout_ms: int = 90000,
) -> pd.DataFrame:
    """
    Headless scraper for UMass Lowell programs listing.
    Extracts:
      - program_name
      - programUrl          (absolute URL)
      - degree_type         (e.g. Undergraduate Certificate, Bachelor's Degree, ...)
      - delivery_mode       (e.g. Online, On Campus, Hybrid, Flexibility: Part Time, ...)
    """
    
    base_url = "https://www.uml.edu/"
    
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
        
        print("Loading UMass Lowell programs page...")
        page.goto(url, wait_until="networkidle", timeout=timeout_ms)
        page.wait_for_timeout(5000)
        
        # Many university search pages load more items on scroll
        print("Scrolling to load all programs (if lazy-loaded)...")
        for _ in range(20):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1200)
        
        page.wait_for_timeout(3000)
        print("Extracting program items...")
        
        rows: List[Dict[str, str]] = []
        
        # Find all program list items
        program_items = page.query_selector_all(
            'div.app-program-search__programs li.app-program-search__program-list-item, '
            'li:has(div.app-program-search__program-list-item)'
        )
        
        print(f"Found {len(program_items)} program items")
        
        for item in program_items:
            try:
                # Program name & link
                name_link = item.query_selector('div.app-program-search__program-list-item__name a')
                if not name_link:
                    continue
                
                program_name = _clean(name_link.inner_text())
                if not program_name:
                    continue
                
                href = name_link.get_attribute("href") or ""
                program_url = urljoin(base_url, href)
                
                # Degree type/level
                degree_elem = item.query_selector('div.app-program-search__program-list-item__degree div')
                degree_type = _clean(degree_elem.inner_text()) if degree_elem else ""
                
                # Delivery mode / location / flexibility
                delivery_parts = []
                
                # Icons with labels (Online / On Campus / Hybrid / Part Time etc.)
                icons = item.query_selector_all('div.app-program-search__program-icon__label')
                for icon_label in icons:
                    label_text = _clean(icon_label.inner_text())
                    if label_text:
                        delivery_parts.append(label_text)
                
                delivery_mode = " | ".join(delivery_parts) if delivery_parts else ""
                
                rows.append({
                    "program_name": program_name,
                    "programUrl": program_url,
                    "degree_type": degree_type,
                    "delivery_mode": delivery_mode,
                    "university_name": "University of Massachusetts Lowell",
                    "degree_program_parsing_link": url,
                    "url": "https://www.uml.edu/",
                    "country": "USA",
                    "city": "Lowell",
                    "zipcode": "01854",
                    "address": "220 Pawtucket St, Lowell, MA 01854",
                    "campus_name":"Lowell",
                    "rank_type_1": "CS",
                    "position_1": "93",

                })
                
            except Exception as e:
                print(f"Error processing program item: {e}")
                continue
        
        browser.close()
    
    if not rows:
        print("Warning: No programs were found.")
        print("Possible reasons:")
        print("• Programs are loaded only after selecting filters/colleges")
        print("• List uses different class names now")
        print("• Heavy client-side rendering → need to wait for specific selector")
        print("Try inspecting → search for 'app-program-search__program-list-item'")
    
    df = pd.DataFrame(rows).drop_duplicates(subset=["programUrl"])
    
    return df

if __name__ == "__main__":
    df = scrape_umass_lowell_programs()
    
    if len(df) == 0:
        print("No data collected.")
    else:
        print("\n" + "="*100)
        print("Sample of scraped UMass Lowell programs:")
        print("="*100)
        cols = ["program_name", "degree_type", "delivery_mode", "programUrl"]
        print(df[cols].head(40).to_string(index=False))
        print("="*100)
        print(f"\nTotal unique programs collected: {len(df)}")
        
        print("\nDelivery mode distribution:")
        print(df["delivery_mode"].value_counts())
        
        print("\nDegree type distribution:")
        print(df["degree_type"].value_counts())
        
        # Save to file
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_umass_lowell_programs.csv", index=False)
        print("\nSaved to: umass_lowell_programs.csv")