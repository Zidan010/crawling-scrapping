# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict, Set
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_fiu_programs_headless(
    url: str,
    *,
    timeout_ms: int = 60000,
) -> pd.DataFrame:
    """
    Headless scraper for Florida International University programs.
    Extracts:
      program_name
      degree_type
      department (college)
      delivery_mode (Online/On-campus)
      programUrl (absolute)
    """
    PROGRAM_LIST_SELECTOR = "ul.list"
    PROGRAM_ITEM_SELECTOR = "ul.list > li"
    
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
        
        # Wait for program list to load
        page.wait_for_selector(PROGRAM_LIST_SELECTOR, timeout=timeout_ms)
        
        def collect_rows() -> List[Dict[str, str]]:
            rows = []
            
            # Find all program list items
            programs = page.query_selector_all(PROGRAM_ITEM_SELECTOR)
            
            for li in programs:
                try:
                    # Extract program name and URL from the main link
                    main_link = li.query_selector("a.link[href]")
                    if not main_link:
                        continue
                    
                    program_url = main_link.get_attribute("href") or ""
                    if not program_url.startswith("http"):
                        program_url = urljoin(url, program_url)
                    
                    # Get program name from p.program
                    program_p = main_link.query_selector("p.program")
                    program_name = _clean(program_p.inner_text()) if program_p else ""
                    
                    if not program_name:
                        continue
                    
                    # Extract degree type
                    degree_type = ""
                    degree_span = li.query_selector("span.degree-type")
                    if degree_span:
                        degree_type = _clean(degree_span.inner_text())
                    
                    # Extract department (college)
                    department = ""
                    college_span = li.query_selector("span.college")
                    if college_span:
                        department = _clean(college_span.inner_text())
                    
                    # Check for online delivery
                    delivery_mode = ""  # Default
                    online_link = li.query_selector("a.online")
                    if online_link:
                        delivery_mode = "Online"
                    
                    rows.append({
                        "program_name": program_name,
                        "degree_type": degree_type,
                        "department": department,
                        "delivery_type": delivery_mode,
                        "programUrl": program_url,
                        "degree_program_parsing_link": url,
                        "university_name": "Florida International University",
                        "rank_type_1": "CS",
                        "position_1": "88",
                        "url": "https://www.fiu.edu/",
                        "email": "",
                        "phone": "",
                        "country": "USA",
                        "city": "Miami",
                        "zipcode": "33199",
                        "address": "11200 SW 8th Street, Miami, FL 33199",
                        "campus_name":"Miami"
                    })
                except Exception as e:
                    print(f"Error processing program item: {e}")
                    continue
            
            return rows
        
        # Collect all programs
        all_rows = collect_rows()
        
        print(f"Found {len(all_rows)} programs")
        
        browser.close()
    
    return pd.DataFrame(all_rows).drop_duplicates(subset=["programUrl"])

if __name__ == "__main__":
    url = "https://www.fiu.edu/academics/degrees-and-programs/index.html"
    df = scrape_fiu_programs_headless(url)
    
    print("\n" + "="*80)
    print("Sample of scraped programs:")
    print("="*80)
    print(df[["program_name", "degree_type", "department", "delivery_type"]].head(20).to_string(index=False))
    print("="*80)
    print(f"\nTotal programs scraped: {len(df)}")
    
    # Show online vs on-campus distribution
    print("\nDelivery mode distribution:")
    print(df["delivery_type"].value_counts())
    
    # Show degree type distribution
    print("\nDegree type distribution:")
    print(df["degree_type"].value_counts())
    
    # Save to CSV
    df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_florida_iu_programs.csv", index=False)
    print("\nSaved to fiu_programs.csv")


# ```

# **Key features of this scraper:**

# 1. **Program name**: Extracted from `p.program` within the main `a.link`
# 2. **Degree type**: Extracted from `span.degree-type` (e.g., "Undergraduate", "Graduate")
# 3. **Department**: Extracted from `span.college` (e.g., "Business", "Arts, Sciences & Education")
# 4. **Delivery mode**: Determined by checking for presence of `a.online` link
#    - If `a.online` exists → "Online"
#    - Otherwise → "On-campus"
# 5. **Program URL**: Direct link from the `a.link` href attribute

# **Structure mapping:**
# ```
# <li>
#   <a class="link" href="...">
#     <p class="program">Program Name</p>
#   </a>
#   <p>
#     <span class="degree-type">Undergraduate/Graduate</span>
#     <a class="online">Available Online</a>  <!-- Optional -->
#     <a class="college-link">
#       <span class="college">Department Name</span>
#     </a>
#   </p>
# </li>