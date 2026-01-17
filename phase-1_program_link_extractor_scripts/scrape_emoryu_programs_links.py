# pip install playwright
# playwright install chromium
from __future__ import annotations
from typing import List, Dict, Set
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_emory_programs_headless(
    url: str,
    *,
    timeout_ms: int = 60000,
    max_scroll_rounds: int = 20,
) -> pd.DataFrame:
    """
    Headless scraper for Emory University programs.
    Extracts:
      program_name
      degree_type
      delivery_mode
      study_mode
      department
      description
      programUrl (absolute)
    """
    PROGRAM_CARD_SELECTOR = "div.card.card-link a.program-card"
    
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
        
        # Wait for program cards to load
        page.wait_for_selector(PROGRAM_CARD_SELECTOR, timeout=timeout_ms)
        
        def collect_rows() -> List[Dict[str, str]]:
            rows = []
            cards = page.query_selector_all(PROGRAM_CARD_SELECTOR)
            
            for card in cards:
                try:
                    # Extract program URL
                    program_url = card.get_attribute("href") or ""
                    if not program_url.startswith("http"):
                        program_url = urljoin(url, program_url)
                    
                    # Extract program name
                    title = card.query_selector("h2.card-title")
                    program_name = _clean(title.inner_text()) if title else ""
                    
                    # Extract degree type, delivery mode, and study mode from tags
                    degree_type = ""
                    delivery_mode = ""
                    study_mode = ""
                    
                    tags = card.query_selector_all("ul.list-tags li")
                    for tag in tags:
                        tag_text = _clean(tag.inner_text())
                        
                        # Identify tag type by icon class
                        icon = tag.query_selector("span.list-tags__icon")
                        if icon:
                            icon_class = icon.get_attribute("class") or ""
                            
                            if "fa-star" in icon_class:
                                degree_type = tag_text
                            elif "fa-landmark" in icon_class or "fa-building" in icon_class:
                                delivery_mode = tag_text
                            elif "fa-clock" in icon_class:
                                study_mode = tag_text
                    
                    # Extract department and description
                    department = ""
                    description = ""
                    
                    school_div = card.query_selector("div.program-card__school")
                    if school_div:
                        dept_div = school_div.query_selector("div.font-weight-bold")
                        if dept_div:
                            department = _clean(dept_div.inner_text())
                        
                        desc_p = school_div.query_selector("p")
                        if desc_p:
                            description = _clean(desc_p.inner_text())
                    
                    rows.append({
                        "program_name": program_name,
                        "degree_type": degree_type,
                        "delivery_type": delivery_mode,
                        "study_mode": study_mode,
                        "department": department,
                        "description": description,
                        "programUrl": program_url,
                        "degree_program_parsing_link": url,
                        "university_name": "Emory University",
                        "rank_type_1": "CS",
                        "position_1": "83",
                        "url": "https://www.emory.edu/",
                        "email": "",
                        "phone": "",
                        "country": "USA",
                        "city": "Atlanta",
                        "zipcode": "30322",
                        "address": "Atlanta, GA 30322",
                        "campus_name": "Atlanta"
                    })
                except Exception as e:
                    print(f"Error processing program card: {e}")
                    continue
            
            return rows
        
        # Lazy-load scroll loop to capture all programs
        seen: Set[str] = set()
        all_rows: List[Dict[str, str]] = []
        
        for round_num in range(max_scroll_rounds):
            # Collect visible programs
            batch = collect_rows()
            new = [r for r in batch if r["programUrl"] not in seen]
            
            if new:
                for r in new:
                    seen.add(r["programUrl"])
                all_rows.extend(new)
                print(f"Round {round_num + 1}: Found {len(new)} new programs (total: {len(all_rows)})")
            
            # Scroll to load more
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)
            
            # Check if we've stopped finding new programs
            if not new:
                # Try one more scroll just to be sure
                if round_num > 2:
                    break
        
        browser.close()
    
    return pd.DataFrame(all_rows).drop_duplicates(subset=["programUrl"])

if __name__ == "__main__":
    url = "https://www.emory.edu/home/academics/degrees-programs.html"
    df = scrape_emory_programs_headless(url)
    print("\n" + "="*50)
    print(df.head(20))
    print("="*50)
    print(f"\nTotal rows: {len(df)}")
    df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_programs_emory.csv", index=False)
    print("Saved to emory_programs.csv")