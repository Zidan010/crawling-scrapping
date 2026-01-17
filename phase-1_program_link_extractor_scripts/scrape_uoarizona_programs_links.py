# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict, Set
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_arizona_programs_headless(
    url: str,
    *,
    timeout_ms: int = 60000,
    max_scroll_rounds: int = 20,
) -> pd.DataFrame:
    """
    Headless scraper for University of Arizona programs.
    Extracts:
      program_name
      delivery_type (location)
      programUrl (absolute)
      degree_type
      department
    """
    MAJOR_CONTAINER_SELECTOR = "div.major-initial-details"
    
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
        
        # Wait for major containers to load
        page.wait_for_selector(MAJOR_CONTAINER_SELECTOR, timeout=timeout_ms)
        
        def collect_rows() -> List[Dict[str, str]]:
            rows = []
            majors = page.query_selector_all(MAJOR_CONTAINER_SELECTOR)
            
            for major in majors:
                try:
                    # Extract program name and URL
                    link = major.query_selector("a.major-link")
                    if not link:
                        continue
                    
                    program_name = _clean(link.inner_text())
                    relative_url = link.get_attribute("href") or ""
                    program_url = urljoin(url, relative_url)
                    
                    # Extract degree type and department
                    degree_dept_div = major.query_selector("div.major-degree-type-and-college")
                    degree_type = ""
                    department = ""
                    
                    if degree_dept_div:
                        paragraphs = degree_dept_div.query_selector_all("p")
                        if len(paragraphs) >= 1:
                            degree_type = _clean(paragraphs[0].inner_text())
                        if len(paragraphs) >= 2:
                            department = _clean(paragraphs[1].inner_text())
                    
                    # Extract delivery type (location) from expanded details
                    delivery_type = ""
                    expanded = major.query_selector("xpath=following-sibling::div[@class='expanded-details']")
                    if not expanded:
                        # Try finding expanded details as next sibling
                        parent = major.query_selector("xpath=..")
                        if parent:
                            expanded = parent.query_selector("div.expanded-details")
                    
                    if expanded:
                        location_p = expanded.query_selector("p.locations span.major-courses")
                        if location_p:
                            delivery_type = _clean(location_p.inner_text())
                    
                    rows.append({
                        "program_name": program_name,
                        "delivery_type": delivery_type,
                        "programUrl": program_url,
                        "degree_type": degree_type,
                        "department": department,
                        "degree_program_parsing_link": url,
                        "university_name": "University of Arizona",
                        "rank_type_1": "CS",
                        "position_1": "80",
                        "url": "https://www.arizona.edu/",
                        "email": "",
                        "phone": "",
                        "country": "USA",
                        "city": "Tucson",
                        "zipcode": "85721",
                        "address": "Tucson, AZ 85721"
                    })
                except Exception as e:
                    print(f"Error processing major: {e}")
                    continue
            
            return rows
        
        # Expand all major details to get location info
        try:
            # Click all majors to expand them
            major_links = page.query_selector_all("a.major-link")
            for i, link in enumerate(major_links):
                try:
                    if i % 10 == 0:  # Scroll periodically
                        link.scroll_into_view_if_needed(timeout=2000)
                        page.wait_for_timeout(100)
                    link.click(timeout=1500)
                    page.wait_for_timeout(50)  # Small delay between clicks
                except Exception:
                    pass
            
            page.wait_for_timeout(1000)  # Wait for expansions to complete
        except Exception as e:
            print(f"Error expanding majors: {e}")
        
        # Lazy-load scroll loop
        seen: Set[str] = set()
        all_rows: List[Dict[str, str]] = []
        
        for _ in range(max_scroll_rounds):
            batch = collect_rows()
            new = [r for r in batch if r["programUrl"] not in seen]
            
            if new:
                for r in new:
                    seen.add(r["programUrl"])
                all_rows.extend(new)
            
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1200)
            
            if not new:
                break
        
        browser.close()
    
    return pd.DataFrame(all_rows).drop_duplicates()

if __name__ == "__main__":
    url = "https://www.arizona.edu/degree-search/majors"  # Replace with actual URL
    df = scrape_arizona_programs_headless(url)
    print(df.head(20))
    print("rows:", len(df))
    df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_programs_arizona.csv", index=False)