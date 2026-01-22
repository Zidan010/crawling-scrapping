from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import time
import random
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_unt_programs(
    start_url: str = "https://search.unt.edu/s/search.html?profile=_default&collection=unt%7Esp-program-finder&sort=title",
    timeout_sec: int = 60,
) -> pd.DataFrame:
    """
    Scraper for UNT programs using the exact HTML structure you provided.
    Waits specifically for search-results__item elements.
    """
    
    all_rows: List[Dict[str, str]] = []
    current_url = start_url
    page_num = 1
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        context = browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        while True:
            print(f"\nScraping page {page_num}: {current_url}")
            
            page.goto(current_url, wait_until="networkidle", timeout=timeout_sec * 1000)
            
            # Critical wait: wait until at least one program item appears
            try:
                page.wait_for_selector("article.search-results__item", timeout=45000)
                print("  → Results loaded successfully!")
                page.wait_for_timeout(4000 + random.randint(1000, 4000))  # extra time for stability
            except PlaywrightTimeoutError:
                print("  → Timeout waiting for 'article.search-results__item' (results not loading)")
                page.screenshot(path=f"unt_failure_page_{page_num}.png", full_page=True)
                print("  Screenshot saved: unt_failure_page_{page_num}.png")
                break
            
            # Screenshot for verification
            page.screenshot(path=f"unt_page_{page_num}.png", full_page=True)
            print(f"  Screenshot saved: unt_page_{page_num}.png")
            
            # Extract all program items
            items = page.query_selector_all("article.search-results__item")
            print(f"  Found {len(items)} program items on this page")
            
            for item in items:
                try:
                    # Title link
                    link = item.query_selector("h3.search-results__title a.search-results__link")
                    if not link:
                        continue
                    
                    program_name = _clean(link.inner_text())
                    href = link.get_attribute("href") or ""
                    if not program_name or not href:
                        continue
                    
                    program_url = urljoin("https://www.unt.edu/", href)
                    
                    # Info spans for type & location
                    infos = item.query_selector_all("span.search-results__info")
                    degree_type = ""
                    campus_name = ""
                    
                    for span in infos:
                        text = _clean(span.inner_text())
                        if text.startswith("Program Type:"):
                            degree_type = text.replace("Program Type:", "").strip()
                        elif text.startswith("Location(s):"):
                            campus_name = text.replace("Location(s):", "").strip()
                    
                    all_rows.append({
                            "program_name": program_name,
                            "programUrl": program_url,
                            "degree_type": degree_type,
                            "campus_name": campus_name,
                            "university_name": "University of North Texas",
                            "degree_program_parsing_link": current_url,
                            "url": "https://www.unt.edu/",
                            "country": "USA",
                            "city": "Denton",
                            "zipcode": "",
                            "address": "1155 Union Circle Denton, Texas 76203-5017",
                            "rank_type_1": "CS",
                            "position_1": "93",
                        })
                except Exception as e:
                    print(f"  Error on one item: {e}")
                    continue
            
            # Pagination: look for Next link
            next_link = page.query_selector(
                'a:has-text("Next"), a:text("Next"), '
                'a[href*="start_rank="]:has-text("Next"), '
                'a[rel="next"], .pagination a.next'
            )
            
            if not next_link or not next_link.is_visible():
                print("  → No 'Next' link found → last page")
                break
            
            next_href = next_link.get_attribute("href")
            if not next_href:
                break
            
            current_url = urljoin(current_url, next_href)
            page_num += 1
            
            time.sleep(random.uniform(4, 8))  # polite delay
        
        context.close()
        browser.close()
    
    df = pd.DataFrame(all_rows).drop_duplicates(subset=["programUrl"])
    return df

if __name__ == "__main__":
    df = scrape_unt_programs()  
    if len(df) == 0:
        print("No data collected. Try opening the page and inspect the pagination & result structure.")
    else:
        print("\n" + "="*100)
        print("Sample of scraped UNT programs:")
        print("="*100)
        cols = ["program_name", "degree_type", "campus_name", "programUrl"]
        print(df[cols].head(35).to_string(index=False))
        print("="*100)
        print(f"\nTotal unique programs collected: {len(df)}")
        
        print("\nCampus distribution:")
        print(df["campus_name"].value_counts())
        
        print("\nDegree type distribution:")
        print(df["degree_type"].value_counts())
        
        # Save result
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_unorthtexus_programs.csv", index=False)
        print("\nSaved to: unt_programs.csv")