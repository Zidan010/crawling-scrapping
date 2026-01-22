# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_rpi_programs_headless(
    url: str,
    *,
    timeout_ms: int = 60000,
) -> pd.DataFrame:
    """
    Headless scraper for Rensselaer Polytechnic Institute programs.
    Extracts:
      program_name
      programUrl
      degree_type
    """
    
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
        print("Loading page...")
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        page.wait_for_timeout(4000)
        
        print("Page loaded, extracting data...")
        
        def collect_rows() -> List[Dict[str, str]]:
            rows = []
            
            # Find all degree type headings
            degree_headings = page.query_selector_all('p[style="padding-left: 30px"] strong')
            
            print(f"Found {len(degree_headings)} degree type headings")
            
            for heading in degree_headings:
                try:
                    degree_type = _clean(heading.inner_text())
                    if not degree_type:
                        continue
                    
                    # Get the parent p and find the next ul.program-list
                    p_element = heading.evaluate_handle('el => el.parentElement')
                    ul_handle = p_element.evaluate_handle("""
                        el => {
                            let next = el.nextElementSibling;
                            while (next && (next.tagName !== 'UL' || !next.classList.contains('program-list'))) {
                                next = next.nextElementSibling;
                            }
                            return next;
                        }
                    """)
                    
                    if not ul_handle:
                        print(f"No program list found for degree type: {degree_type}")
                        continue
                    
                    # Get all links in the ul
                    links = ul_handle.query_selector_all('li a')
                    
                    for link in links:
                        try:
                            program_name = _clean(link.inner_text())
                            if not program_name:
                                continue
                            
                            program_url = link.get_attribute("href") or ""
                            if not program_url.startswith("http"):
                                program_url = urljoin(url, program_url)
                            
                            rows.append({
                                "program_name": program_name,
                                "programUrl": program_url,
                                "degree_type": degree_type,
                                "degree_program_parsing_link": url,
                                "university_name": "Rensselaer Polytechnic Institute",
                                "rank_type_1": "CS",  # Fill if known
                                "position_1": "93",   # Fill if known
                                "url": "https://www.rpi.edu/",
                                "email": "",
                                "phone": "",
                                "country": "USA",
                                "city": "Troy",
                                "zipcode": "12180",
                                "address": "110 8th St, Troy, NY 12180",
                                "campus_name":"Troy"
                            })
                        except Exception as e:
                            print(f"Error processing program link: {e}")
                            continue
                    
                except Exception as e:
                    print(f"Error processing degree heading: {e}")
                    continue
            
            print(f"Collected {len(rows)} programs")
            return rows
        
        # Collect all programs
        all_rows = collect_rows()
        
        browser.close()
    
    return pd.DataFrame(all_rows).drop_duplicates(subset=["programUrl"])

if __name__ == "__main__":
    url = "https://catalog.rpi.edu/content.php?catoid=33&navoid=873"
    df = scrape_rpi_programs_headless(url)
    
    if len(df) == 0:
        print("No data collected. Please check the page structure.")
    else:
        print("\n" + "="*80)
        print("Sample of scraped programs:")
        print("="*80)
        print(df[["program_name", "degree_type", "programUrl"]].head(30).to_string(index=False))
        print("="*80)
        print(f"\nTotal unique programs scraped: {len(df)}")
        
        # Show degree type distribution
        print("\nDegree type distribution:")
        print(df["degree_type"].value_counts())
         
        # Save to CSV
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_rensselaerpi_programs.csv", index=False)
        print("\nSaved to rpi_programs.csv")