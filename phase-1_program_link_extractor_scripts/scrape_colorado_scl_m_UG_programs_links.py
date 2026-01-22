# pip install playwright pandas
# playwright install chromium

from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def infer_degree_type(title: str) -> str:
    title_lower = title.lower()
    if "minor" in title_lower:
        return "Undergrad Minor"
    elif "certificate" in title_lower:
        return "Undergrad Certificate"
    elif any(x in title_lower for x in ["major", "bs ", "ba ", "b.s.", "b.a."]):
        return "Bachelor's"
    return "Undergraduate"

def scrape_mines_undergrad_programs(
    url: str = "https://www.mines.edu/academics/undergraduate-programs/",
    timeout_ms: int = 90000,
) -> pd.DataFrame:
    rows: List[Dict[str, str]] = []
    base_url = "https://www.mines.edu/"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ])
        page = browser.new_page()
        
        print("Loading Colorado School of Mines Undergraduate Programs...")
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        
        # Wait for masonry grid
        try:
            page.wait_for_selector('div.tg-grid-holder', timeout=30000)
            page.wait_for_timeout(4000)
        except:
            print("Warning: Grid not found quickly.")
        
        print("Scrolling + loading more items...")
        prev_count = 0
        for attempt in range(20):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2500)
            
            # Try clicking "Load More" if present
            try:
                load_more = page.query_selector('button:has-text("Load More"), button:has-text("More"), [class*="load-more"]')
                if load_more and load_more.is_visible():
                    load_more.click()
                    page.wait_for_timeout(4000)
            except:
                pass
            
            current_count = len(page.query_selector_all('article.tg-item'))
            print(f"  Attempt {attempt+1}: {current_count} programs visible")
            
            if current_count == prev_count and current_count > 0:
                print("  No more items loading → done.")
                break
            prev_count = current_count
        
        # Collect all articles
        articles = page.query_selector_all('article.tg-item')
        print(f"\nFinal total programs found: {len(articles)}")
        
        for article in articles:
            try:
                title_link = article.query_selector('h2.tg-item-title a')
                if not title_link:
                    continue
                
                full_title = _clean(title_link.inner_text())
                if not full_title:
                    continue
                
                program_url = urljoin(base_url, title_link.get_attribute("href") or "")
                
                degree_type = infer_degree_type(full_title)
                
                rows.append({
                    "program_name": full_title,
                    "degree_type": degree_type,
                    "delivery_type": "",  # All undergrad programs are campus-based
                    "programUrl": program_url,
                    "university_name": "Colorado School of Mines",
                    "degree_program_parsing_link": url,
                    "url": "https://www.mines.edu/",
                    "country": "USA",
                    "city": "Golden",
                    "zipcode": "80401",
                    "address": "1500 Illinois St, Golden, CO 80401",
                    "campus_name":"Golden",
                    "rank_type_1": "CS",
                    "position_1": "106"
                })
            except Exception as e:
                print(f"Error processing program: {e}")
                continue
        
        browser.close()
    
    df = pd.DataFrame(rows).drop_duplicates(subset=["programUrl"])
    
    return df

if __name__ == "__main__":
    df = scrape_mines_undergrad_programs()
    
    print(f"\nCollected {len(df)} unique undergraduate programs")
    print(df[["program_name", "degree_type", "delivery_type", "programUrl"]].head(30).to_string(index=False))
    
    df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_colorado_sm_UG.csv", index=False)
    print("\nSaved to mines_undergrad_programs.csv")