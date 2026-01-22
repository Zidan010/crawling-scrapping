# pip install playwright pandas
# playwright install chromium

from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    """Clean text: normalize spaces, remove extras."""
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def _map_delivery(text: str) -> str:
    """Map 'On Campus' → 'Offline', 'Online' → 'Online', etc."""
    text = _clean(text).lower()
    if "on campus" in text:
        return "Offline"
    if "online" in text:
        return "Online"
    return text.title()  # fallback

def scrape_iit_programs(
    url: str = "https://www.iit.edu/academics/programs",
    timeout_ms: int = 90000,
) -> pd.DataFrame:
    """
    Scraper for Illinois Institute of Technology (IIT) programs.
    Extracts from <article class="program-large-list listing-item">
      - program_name
      - programUrl
      - degree_type (from Program Type)
      - degree_code (from Degree tooltip)
      - department_name (College/School)
      - department_url
      - delivery_type (comma-separated, mapped)
    """
    
    base_url = "https://www.iit.edu/"
    
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
        
        print("Loading IIT programs page...")
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        
        # Wait for program articles
        try:
            page.wait_for_selector('article.program-large-list', timeout=30000)
            print("Found program articles.")
        except:
            print("Warning: No articles found quickly.")
        
        # Scroll to load all (if lazy-loaded)
        print("Scrolling to load all programs...")
        for _ in range(20):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
        
        rows: List[Dict[str, str]] = []
        
        articles = page.query_selector_all('article.program-large-list')
        print(f"Found {len(articles)} program articles")
        
        for article in articles:
            try:
                # Program name & URL
                title_link = article.query_selector('h2.listing-item__title a')
                if not title_link:
                    continue
                
                program_name = _clean(title_link.inner_text())
                program_url = urljoin(base_url, title_link.get_attribute("href") or "")
                
                # Degree type (Program Type)
                degree_type_elem = article.query_selector('div.cell:has(h3:has-text("Program Type")) span.h4')
                degree_type = _clean(degree_type_elem.inner_text()) if degree_type_elem else ""
                
                # Degree code (from Degree tooltip)
                degree_code_elem = article.query_selector('div.cell:has(h3:has-text("Degree")) span.popper')
                degree_code = _clean(degree_code_elem.inner_text()) if degree_code_elem else ""
                
                # Department / College
                dept_link = article.query_selector('div.cell:has(h3:has-text("College/School")) a')
                department_name = _clean(dept_link.inner_text()) if dept_link else ""
                department_url = urljoin(base_url, dept_link.get_attribute("href") or "") if dept_link else ""
                
                # Delivery type (Program Location)
                delivery_items = article.query_selector_all('ul.program-modality-list li span')
                delivery_list = [_map_delivery(item.inner_text()) for item in delivery_items if item.inner_text()]
                delivery_type = ", ".join(delivery_list) if delivery_list else ""
                
                rows.append({
                    "program_name": program_name,
                    "programUrl": program_url,
                    "degree_type": degree_type,
                    "degree_code": degree_code,
                    "department_name": department_name,
                    "department_url": department_url,
                    "delivery_type": delivery_type,
                    "university_name": "Illinois Institute of Technology",
                    "degree_program_parsing_link": url,
                    "url": "https://www.iit.edu/",
                    "country": "USA",
                    "city": "Chicago",
                    "zipcode": "60616",
                    "address": "10 West 35th Street, Chicago, IL 60616",
                    "campus_name":"Chicago",
                    "rank_type_1": "CS",
                    "position_1": "106"
                })
            except Exception as e:
                print(f"Error processing program: {e}")
                continue
        
        browser.close()
    
    if not rows:
        print("No programs collected. Possible issues:")
        print("• Programs load after filter or search interaction")
        print("• Heavy JS → try headless=False")
        print("• Page structure changed")
    
    df = pd.DataFrame(rows).drop_duplicates(subset=["programUrl"])
    
    return df

if __name__ == "__main__":
    df = scrape_iit_programs()
    
    if len(df) == 0:
        print("No data collected.")
    else:
        print("\n" + "="*120)
        print("Illinois Institute of Technology Programs (sample):")
        print("="*120)
        print(df[["program_name", "degree_type", "degree_code", "department_name", "delivery_type", "programUrl"]].head(30).to_string(index=False))
        print("="*120)
        print(f"\nTotal unique programs scraped: {len(df)}")
        
        print("\nDelivery type distribution:")
        print(df["delivery_type"].value_counts())
        
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_illinois_it_programs.csv", index=False)
        print("\nSaved to iit_programs.csv")