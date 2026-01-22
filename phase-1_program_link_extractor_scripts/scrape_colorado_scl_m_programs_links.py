# pip install playwright pandas
# playwright install chromium

from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def _extract_degree_code(title: str) -> str:
    """Extract degree code from last bracket: 'Additive Manufacturing (Certificate)' → 'Certificate'"""
    title = _clean(title)
    if '(' not in title or not title.endswith(')'):
        return ""
    return title[title.rfind('(') + 1 : -1].strip()

def map_delivery_type(tag_text: str) -> str:
    tag = _clean(tag_text).lower()
    if "online or campus" in tag or "hybrid" in tag:
        return "Hybrid"
    elif "online" in tag:
        return "Online"
    elif "campus" in tag:
        return "Offline"
    return tag.title()  # fallback

def scrape_mines_grad_programs(
    url: str = "https://gradprograms.mines.edu/programs/",
    timeout_ms: int = 90000,
) -> pd.DataFrame:
    rows: List[Dict[str, str]] = []
    base_url = "https://gradprograms.mines.edu/"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ])
        page = browser.new_page()
        
        print("Loading Colorado School of Mines Graduate Programs...")
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        
        # Wait for the masonry grid
        try:
            page.wait_for_selector('div.tg-grid-holder', timeout=30000)
            page.wait_for_timeout(4000)
        except:
            print("Warning: Grid not detected quickly.")
        
        # Scroll + click "Load More" if present (common in masonry grids)
        print("Scrolling and loading more items...")
        for i in range(15):  # max attempts
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2500)
            
            # Try to click Load More button if exists
            try:
                load_more = page.query_selector(
                    'button:has-text("Load More"), button:has-text("More"), '
                    '.load-more, [class*="load-more"], [class*="show-more"]'
                )
                if load_more and load_more.is_visible():
                    print("  Clicking 'Load More'...")
                    load_more.click()
                    page.wait_for_timeout(4000)
            except:
                pass
            
            # Check if no more items are being added
            if i > 3:
                current_count = len(page.query_selector_all('article.tg-item'))
                prev_count = len(page.query_selector_all('article.tg-item'))  # simplistic check
                if current_count == prev_count:
                    break
        
        # Collect all program articles
        articles = page.query_selector_all('article.tg-item')
        print(f"Found {len(articles)} program cards")
        
        for article in articles:
            try:
                # Main link and title
                title_link = article.query_selector('h2.tg-item-title a')
                if not title_link:
                    continue
                
                full_title = _clean(title_link.inner_text())
                program_name = full_title.split('(')[0].strip() if '(' in full_title else full_title
                degree_code = _extract_degree_code(full_title)
                
                program_url = urljoin(base_url, title_link.get_attribute("href") or "")
                
                # Degree type from excerpt
                degree_elem = article.query_selector('p.tg-item-excerpt')
                degree_type = _clean(degree_elem.inner_text()) if degree_elem else ""
                
                # Delivery type from tag
                tag_elem = article.query_selector('span.tg-item-term')
                delivery_raw = tag_elem.inner_text() if tag_elem else ""
                delivery_type = map_delivery_type(delivery_raw)
                
                rows.append({
                    "program_name": program_name,
                    "degree_code": degree_code,
                    "degree_type": degree_type,
                    "delivery_type": delivery_type,
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
                print(f"Error processing article: {e}")
                continue
        
        browser.close()
    
    df = pd.DataFrame(rows).drop_duplicates(subset=["programUrl"])
    
    return df

if __name__ == "__main__":
    df = scrape_mines_grad_programs()
    
    print(f"\nCollected {len(df)} unique programs")
    print(df[["program_name", "degree_code", "degree_type", "delivery_type", "programUrl"]].head(30).to_string(index=False))
    
    df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_colorado_sm_grad.csv", index=False)
    print("\nSaved to mines_grad_programs.csv")