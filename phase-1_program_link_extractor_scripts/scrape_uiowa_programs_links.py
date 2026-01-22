# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    """Clean text: remove extra spaces, nbsp, etc."""
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def _split_program_title(title: str) -> tuple[str, str]:
    """Split 'Accounting, BBA' → ('Accounting', 'BBA')"""
    title = _clean(title)
    if ',' not in title:
        return title, ""
    name, code = title.rsplit(',', 1)
    return _clean(name), _clean(code)

def scrape_uiowa_programs(
    url: str = "https://catalog.registrar.uiowa.edu/your-program/",
    timeout_ms: int = 90000,
) -> pd.DataFrame:
    """
    Headless scraper for University of Iowa programs page.
    Extracts:
      - program_name        (major/subject name before comma)
      - degree_code         (after comma, e.g. BBA, BS, BA)
      - programUrl
      - degree_level        (e.g. Undergraduate)
      - degree_type         (e.g. Bachelor of Business Administration)
    """
    
    base_url = "https://catalog.registrar.uiowa.edu/"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ])
        page = browser.new_page()
        
        print("Loading UIowa programs page...")
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        page.wait_for_timeout(5000)
        
        # Scroll multiple times - Isotope grids often load more on scroll
        print("Scrolling to load all program items...")
        last_height = page.evaluate("document.body.scrollHeight")
        for _ in range(25):  # generous number for large lists
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1400)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        page.wait_for_timeout(3000)
        print("Extracting program items...")
        
        rows: List[Dict[str, str]] = []
        
        # Main selector for program cards/items
        items = page.query_selector_all('li.isotope-item, li.item, li[id^="isotope-item"]')
        
        print(f"Found {len(items)} potential program items")
        
        for item in items:
            try:
                # Get the main link (usually the one with background-image)
                link = item.query_selector('a.filterimage[href], a[href]:not([href="#"])')
                if not link:
                    continue
                
                href = link.get_attribute("href") or ""
                if not href:
                    continue
                program_url = urljoin(base_url, href)
                
                # Program title - most reliable from div.filtertitle or sr-only span
                title_elem = (
                    item.query_selector('div.filtertitle') or
                    item.query_selector('a.filterimage span.sr-only') or
                    item.query_selector('div.card-title, .title')
                )
                
                full_title = _clean(title_elem.inner_text()) if title_elem else ""
                if not full_title:
                    continue
                
                program_name, degree_code = _split_program_title(full_title)
                
                # Keywords (degree level & type)
                keywords = item.query_selector_all('span.keyword')
                degree_level = _clean(keywords[0].inner_text()) if len(keywords) > 0 else ""
                degree_type = _clean(keywords[1].inner_text()) if len(keywords) > 1 else ""
                
                rows.append({
                    "program_name": program_name,
                    "degree_code": degree_code,
                    "full_title": full_title,               # for reference
                    "programUrl": program_url,
                    "degree_level": degree_level,
                    "degree_type": degree_type,
                    "rank_type_1": "CS",
                    "position_1": "93",                    
                    "university_name": "University of Iowa",
                    "degree_program_parsing_link": url,
                    "url": "https://uiowa.edu/",
                    "country": "USA",
                    "city": "Iowa City",
                    "zipcode": "52242",
                    "address": "Iowa City, IA 52242",
                    "campus_name":"Iowa City"
                })
                
            except Exception as e:
                print(f"Error processing item: {e}")
                continue
        
        browser.close()
    
    if not rows:
        print("Warning: No programs found. Page structure may have changed.")
        print("Try inspecting elements → look for classes: isotope-item, filterimage, filtertitle, keyword")
    
    df = pd.DataFrame(rows).drop_duplicates(subset=["programUrl"])
    
    return df

if __name__ == "__main__":
    df = scrape_uiowa_programs()
    
    if len(df) == 0:
        print("No data collected. Possible reasons:")
        print("- Heavy JS filtering (need to click 'All' or remove filters)")
        print("- Different class names → inspect page manually")
    else:
        print("\n" + "="*90)
        print("Sample of scraped University of Iowa programs:")
        print("="*90)
        cols = ["program_name", "degree_code", "degree_level", "degree_type", "programUrl"]
        print(df[cols].head(35).to_string(index=False))
        print("="*90)
        print(f"\nTotal unique programs collected: {len(df)}")
        
        print("\nDegree level distribution:")
        print(df["degree_level"].value_counts())
        
        # Save result
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_uiowa_programs.csv", index=False)
        print("\nSaved to: uiowa_programs.csv")