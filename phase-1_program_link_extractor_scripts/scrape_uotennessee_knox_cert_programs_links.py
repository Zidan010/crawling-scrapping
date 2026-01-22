from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright

def _clean(s: str) -> str:
    """Clean text: remove extra spaces, nbsp, hidden spans, etc."""
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_utk_catalog_programs(
    url: str = "https://catalog.utk.edu/content.php?catoid=55&navoid=11835",
    timeout_ms: int = 60000,
) -> pd.DataFrame:
    """
    Scraper for University of Tennessee, Knoxville graduate catalog page.
    Extracts program names and URLs from <ul> lists under <td> (no 'program-list' class here).
    Works with the alphabetical <h2> + <ul> structure you provided.
    """
    
    base_url = "https://catalog.utk.edu/"
    
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
        
        print("Loading UTK catalog page...")
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        
        # Give page time to render (Acalog is mostly static)
        page.wait_for_timeout(5000)
        
        # Scroll to bottom just in case (rarely needed here)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        
        rows: List[Dict[str, str]] = []
        
        # Find all <ul> that contain program links (inside the main <td>)
        ul_elements = page.query_selector_all('td a[name] + h2 + ul, td ul')
        print(f"Found {len(ul_elements)} potential <ul> blocks with programs")
        
        for ul in ul_elements:
            # Get all <a> tags inside this <ul> that point to preview_program.php
            program_links = ul.query_selector_all('li a[href*="preview_program.php"], a[href*="preview_program.php"]')
            
            for link in program_links:
                try:
                    # Clean name (remove any hidden spans or weird characters)
                    raw_text = link.inner_text()
                    program_name = _clean(raw_text)
                    
                    suffix = "Graduate Certificate"

                    # Split once from the right
                    # name_part, certificate_part = program_name.rsplit(suffix, 1)
                    name_part, matched_suffix, _ = raw_text.partition(suffix)
                    
                    # "program_name": name_part.strip(),
                    # "credential": suffix
                    


                    if not program_name or len(program_name) < 5:
                        continue
                    
                    href = link.get_attribute("href") or ""
                    if "preview_program.php" not in href:
                        continue
                    
                    full_url = urljoin(base_url, href)
                    
                    rows.append({
                        "program_name": name_part.strip(),
                        "programUrl": full_url,
                        "degree_type":matched_suffix ,
                        "university_name": "University of Tennessee, Knoxville",
                        "degree_program_parsing_link": url,
                        "url": "https://utk.edu/",
                        "country": "USA",
                        "city": "Knoxville",
                        "zipcode": "37996",
                        "address": "Knoxville, TN 37996",
                        "campus_name":"Knoxville",
                        "rank_type_1": "CS",
                        "position_1": "93",
                        "phone":"865-974-1000"
                    })
                except Exception as e:
                    print(f"Error processing link: {e}")
                    continue
        
        # Fallback: collect ALL preview links if structured ul not found
        if len(rows) < 10:
            print("Low count detected → falling back to all preview links on page")
            all_links = page.query_selector_all('a[href*="preview_program.php"]')
            for link in all_links:
                try:
                    name = _clean(link.inner_text())
                    if not name or "No active" in name or len(name) < 8:
                        continue
                    href = link.get_attribute("href") or ""
                    full_url = urljoin(base_url, href)
                    
                    rows.append({
                        "program_name": full_name,
                        "programUrl": program_url,
                        "university_name": "University of Tennessee, Knoxville",
                        "degree_program_parsing_link": url,
                        "url": "https://utk.edu/",
                        "country": "USA",
                        "city": "Knoxville",
                        "zipcode": "37996",
                        "address": "Knoxville, TN 37996",
                        "campus_name":"Knoxville",
                        "rank_type_1": "CS",
                        "position_1": "93",
                        "phone":"865-974-1000"
                    })
                except Exception as e:
                    print(f"Error processing link: {e}")
                    continue
        
        browser.close()
    
    if not rows:
        print("No programs found. Possible reasons:")
        print("• Content loaded via JavaScript after delay")
        print("• Different class names in current catalog version")
        print("• Bot protection or region restriction")
        print("Try running with headless=False and inspect manually.")
    
    df = pd.DataFrame(rows).drop_duplicates(subset=["programUrl"])
    
    return df

if __name__ == "__main__":
    df = scrape_utk_catalog_programs()    
    if len(df) == 0:
        print("No data collected.")
    else:
        print("\n" + "="*100)
        print("University of Tennessee, Knoxville Programs (sample):")
        print("="*100)
        print(df[["program_name", "programUrl"]].head(40).to_string(index=False))
        print("="*100)
        print(f"\nTotal unique programs scraped: {len(df)}")
        
        # Save result
        df.to_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_uotennessee_knox_cert_programs_2.csv", index=False)
        print("\nSaved to: utk_programs.csv")