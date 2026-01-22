from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_colostate_catalog_headless(
    url: str,
    *,
    timeout_ms: int = 60000,
) -> pd.DataFrame:
    """
    Headless scraper for Colorado State University catalog programs.
    Extracts:
      program_name
      programUrl
      degree_type
      department
      delivery_type (Main Campus / Online)
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
        page.wait_for_timeout(3000)
        
        # Wait for table to load
        print("Waiting for table...")
        page.wait_for_selector("table", timeout=timeout_ms)
        page.wait_for_timeout(2000)
        
        print("Page loaded, extracting data...")
        
        def collect_rows() -> List[Dict[str, str]]:
            rows = []
            
            # Find all table rows (skip header)
            table_rows = page.query_selector_all("table tbody tr, table tr")
            
            print(f"Found {len(table_rows)} table rows")
            
            for row in table_rows:
                try:
                    # Get all cells in the row
                    cells = row.query_selector_all("td")
                    
                    # Skip if not enough cells or if it's a header row
                    if len(cells) < 6:
                        continue
                    
                    # Extract data from cells based on column order:
                    # 0: Academic Program
                    # 1: Department
                    # 2: College
                    # 3: Academic Level
                    # 4: Offered As (Main Campus / Online)
                    # 5: Degree Type (link)
                    
                    program_name = _clean(cells[0].inner_text())
                    department = _clean(cells[1].inner_text())
                    college = _clean(cells[2].inner_text())
                    academic_level = _clean(cells[3].inner_text())
                    offered_as = _clean(cells[4].inner_text())
                    
                    # Get degree type and URL from last cell
                    link = cells[5].query_selector("a[href]")
                    if not link:
                        continue
                    
                    degree_type = _clean(link.inner_text())
                    program_url = link.get_attribute("href") or ""
                    
                    # Make URL absolute
                    if not program_url.startswith("http"):
                        program_url = urljoin(url, program_url)
                    
                    # Determine delivery type
                    delivery_type = ""  # Default 
                    if "Main Campus, Online" in offered_as:
                        delivery_type = "Hybrid"                    
                    elif "Online" in offered_as:
                        delivery_type = "Online"
                    elif "Main Campus" in offered_as:
                        delivery_type = "Offline"
                    
                    # Skip empty program names
                    if not program_name:
                        continue
                    
                    rows.append({
                        "program_name": program_name,
                        "programUrl": program_url,
                        "degree_type": degree_type,
                        "department": department,
                        "college": college,
                        "academic_level": academic_level,
                        "delivery_type": delivery_type,
                        "degree_program_parsing_link": url,
                        "university_name": "Colorado State University",
                        "rank_type_1": "",
                        "position_1": "",
                        "url": "https://www.colostate.edu/",
                        "email": "",
                        "phone": "(970) 491-6909",
                        "country": "USA",
                        "city": "Fort Collins",
                        "zipcode": "80521",
                        "address": "711 Oval Drive, Fort Collins CO 80521",
                        "campus_name":"Fort Collins"
                    })
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue
            
            print(f"Collected {len(rows)} programs")
            return rows
        
        # Collect all programs
        all_rows = collect_rows()
        
        browser.close()
    
    return pd.DataFrame(all_rows).drop_duplicates(subset=["programUrl"])

if __name__ == "__main__":
    url = "https://catalog.colostate.edu/general-catalog/programsaz/"
    df = scrape_colostate_catalog_headless(url)
    
    if len(df) == 0:
        print("No data collected. Please check the page structure.")
    else:
        print("\n" + "="*80)
        print("Sample of scraped programs:")
        print("="*80)
        print(df[["program_name", "degree_type", "department", "delivery_type"]].head(30).to_string(index=False))
        print("="*80)
        print(f"\nTotal unique programs scraped: {len(df)}")
        
        # Show delivery type distribution
        print("\nDelivery type distribution:")
        print(df["delivery_type"].value_counts())
        
        # Show degree type distribution
        print("\nDegree type distribution:")
        print(df["degree_type"].value_counts().head(20))
        
        # Save to CSV
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_colostate_programs_3.csv", index=False)
        print("\nSaved to colostate_programs.csv")