# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_gwu_programs_headless(
    url: str,
    *,
    timeout_ms: int = 60000,
) -> pd.DataFrame:
    """
    Headless scraper for George Washington University programs.
    Extracts:
      program_name
      programUrl
      campus (location)
      school (department)
      delivery_mode
      academic_level
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
        
        # Wait for isotope container to load
        print("Waiting for programs to load...")
        try:
            page.wait_for_selector("div.filter-items--grid ul.isotope", timeout=timeout_ms)
        except Exception as e:
            print(f"Warning: Could not find isotope container: {e}")
        
        # Scroll to ensure all content is loaded
        print("Scrolling to load all programs...")
        for i in range(10):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)
        
        page.wait_for_timeout(2000)
        print("Page loaded, extracting data...")
        
        def collect_rows() -> List[Dict[str, str]]:
            rows = []
            
            # Find all program items in the isotope list
            program_items = page.query_selector_all("div.filter-items--grid ul.isotope li.item")
            
            print(f"Found {len(program_items)} program items")
            
            for item in program_items:
                try:
                    # Get the link
                    link = item.query_selector("a[href]")
                    if not link:
                        continue
                    
                    # Get program URL
                    program_url = link.get_attribute("href") or ""
                    if not program_url.startswith("http"):
                        program_url = urljoin(url, program_url)
                    
                    # Get program name from span.title
                    title_elem = item.query_selector("span.title")
                    program_name = _clean(title_elem.inner_text()) if title_elem else ""
                    
                    if not program_name:
                        continue
                    
                    # Get all keywords (campus, school, delivery mode, level, degree type, subject area)
                    keywords = item.query_selector_all("span.keyword")
                    
                    # Parse keywords - order typically is:
                    # 0: Campus location
                    # 1: School/Department
                    # 2: Delivery mode
                    # 3: Academic level
                    # 4: Degree type
                    # 5: Subject area (optional)
                    
                    campus = ""
                    school = ""
                    delivery_mode = ""
                    academic_level = ""
                    degree_type = ""
                    subject_area = ""
                    
                    if len(keywords) > 0:
                        campus = _clean(keywords[0].inner_text())
                    if len(keywords) > 1:
                        school = _clean(keywords[1].inner_text())
                    if len(keywords) > 2:
                        delivery_mode = _clean(keywords[2].inner_text())
                    if len(keywords) > 3:
                        academic_level = _clean(keywords[3].inner_text())
                    if len(keywords) > 4:
                        degree_type = _clean(keywords[4].inner_text())
                    if len(keywords) > 5:
                        subject_area = _clean(keywords[5].inner_text())
                    
                    rows.append({
                        "program_name": program_name,
                        "programUrl": program_url,
                        "campus_name": campus,
                        "school": school,
                        "delivery_mode": delivery_mode,
                        "academic_level": academic_level,
                        "degree_type": degree_type,
                        "subject_area": subject_area,
                        "degree_program_parsing_link": url,
                        "university_name": "George Washington University",
                        "rank_type_1": "CS",
                        "position_1": "93",
                        "url": "https://www.gwu.edu/",
                        "email": "",
                        "phone": "",
                        "country": "USA",
                        "city": "Washington",
                        "zipcode": "20052",
                        "address": "2121 I Street NW, Washington, DC 20052"
                    })
                except Exception as e:
                    print(f"Error processing program item: {e}")
                    continue
            
            print(f"Collected {len(rows)} programs")
            return rows
        
        # Collect all programs
        all_rows = collect_rows()
        
        browser.close()
    
    return pd.DataFrame(all_rows).drop_duplicates(subset=["programUrl"])

if __name__ == "__main__":
    url = "https://bulletin.gwu.edu/find-your-program/"
    df = scrape_gwu_programs_headless(url)
    
    if len(df) == 0:
        print("No data collected. Please check the page structure.")
    else:
        print("\n" + "="*80)
        print("Sample of scraped programs:")
        print("="*80)
        print(df[["program_name", "degree_type", "school", "delivery_mode"]].head(30).to_string(index=False))
        print("="*80)
        print(f"\nTotal unique programs scraped: {len(df)}")
        
        # Show campus distribution
        print("\nCampus distribution:")
        print(df["campus_name"].value_counts())
        
        # Show delivery mode distribution
        print("\nDelivery mode distribution:")
        print(df["delivery_mode"].value_counts())
        
        # Show degree type distribution
        print("\nDegree type distribution:")
        print(df["degree_type"].value_counts())
        
        # Save to CSV
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_gwu_programs.csv", index=False)
        print("\nSaved to gwu_programs.csv")