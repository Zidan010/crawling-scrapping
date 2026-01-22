# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict, Set
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_drexel_programs_headless(
    url: str,
    *,
    timeout_ms: int = 60000,
) -> pd.DataFrame:
    """
    Headless scraper for Drexel University programs.
    Extracts:
      program_name
      programUrl (absolute)
    """
    CONTENT_CONTAINER_SELECTOR = "div#textcontainer.page_content"
    
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
        
        # Wait for content container to load
        page.wait_for_selector(CONTENT_CONTAINER_SELECTOR, timeout=timeout_ms)
        
        def collect_rows() -> List[Dict[str, str]]:
            rows = []
            
            # Find the text container
            container = page.query_selector(CONTENT_CONTAINER_SELECTOR)
            if not container:
                print("Content container not found")
                return rows
            
            # Find all <p> tags that contain links
            paragraphs = container.query_selector_all("p")
            
            for p in paragraphs:
                try:
                    # Get the link inside the paragraph
                    link = p.query_selector("a[href]")
                    if not link:
                        continue
                    
                    # Extract program name (text content of the link)
                    program_name = _clean(link.inner_text())
                    
                    # Skip empty program names
                    if not program_name:
                        continue
                    
                    # Extract program URL
                    relative_url = link.get_attribute("href") or ""
                    program_url = urljoin(url, relative_url)
                    
                    # Skip ROTC and other non-academic programs if needed
                    # (uncomment the next 2 lines if you want to exclude these)
                    # if "ROTC" in program_name or "Undeclared" in program_name:
                    #     continue
                    
                    rows.append({
                        "program_name": program_name,
                        "programUrl": program_url,
                        "degree_program_parsing_link": url,
                        "university_name": "Drexel University",
                        "rank_type_1": "CS",
                        "position_1": "88",
                        "url": "https://drexel.edu/",
                        "email": "",
                        "phone": "",
                        "country": "USA",
                        "city": "Philadelphia",
                        "zipcode": "19104",
                        "address": "3141 Chestnut Street, Philadelphia, PA 19104",
                        "campus_name":"Philadelphia",
                        "degree_type":"Graduate"
                    })
                except Exception as e:
                    print(f"Error processing paragraph: {e}")
                    continue
            
            return rows
        
        # Collect all programs (no scrolling needed as all content is loaded)
        all_rows = collect_rows()
        
        print(f"Found {len(all_rows)} programs")
        
        browser.close()
    
    return pd.DataFrame(all_rows).drop_duplicates(subset=["programUrl"])

if __name__ == "__main__":
    # url = "https://catalog.drexel.edu/majors/"
    # url = "https://catalog.drexel.edu/minors/undergraduate/"
    # url = "https://catalog.drexel.edu/graduateminors/"
    url = "https://catalog.drexel.edu/graduateprograms/"


    df = scrape_drexel_programs_headless(url)
    
    print("\n" + "="*80)
    print("Sample of scraped programs:")
    print("="*80)
    print(df[["program_name", "programUrl"]].head(20).to_string(index=False))
    print("="*80)
    print(f"\nTotal programs scraped: {len(df)}")
    
    # Save to CSV
    df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_drexel_G_programs.csv", index=False)
    print("Saved to drexel_programs.csv")