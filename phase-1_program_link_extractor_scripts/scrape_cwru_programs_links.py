# pip install playwright pandas
# playwright install chromium
from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright
import re

def _clean(s: str) -> str:
    """Clean and normalize text strings."""
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def scrape_case_programs_headless(
    url: str,
    *,
    timeout_ms: int = 90000,  # Increased default timeout
) -> pd.DataFrame:
    """
    Headless scraper for Case Western Reserve University programs.
    Extracts:
      - program_name
      - degree_code (BS, MAcc, PhD, Minor, etc.)
      - programUrl (URL for specific degree)
      - program_format (Full-Time, Part-Time, etc.)
    
    Each degree type creates a separate row.
    """
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        # Set longer default timeout
        page.set_default_timeout(90000)
        
        print(f"Loading page: {url}")
        
        # Try different wait strategies
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            print("Page loaded (domcontentloaded)")
        except Exception as e:
            print(f"Error with domcontentloaded: {e}")
            try:
                page.goto(url, wait_until="load", timeout=timeout_ms)
                print("Page loaded (load)")
            except Exception as e2:
                print(f"Error with load: {e2}")
                print("Trying one more time with commit...")
                page.goto(url, wait_until="commit", timeout=timeout_ms)
                print("Page loaded (commit)")
        
        # Wait for the view-content container - this is the key element
        try:
            page.wait_for_selector('div.view-content', timeout=30000)
            print("Found view-content container")
            page.wait_for_timeout(3000)  # Extra wait for content to fully render
        except Exception as e:
            print(f"Warning: view-content container not found: {e}")
            # Try to continue anyway
            page.wait_for_timeout(5000)
        
        # Scroll to load any lazy-loaded content
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        
        # Collect all programs
        all_rows = collect_programs(page, url)
        
        print(f"\nTotal program entries collected: {len(all_rows)}")
        
        browser.close()
    
    return pd.DataFrame(all_rows)

def collect_programs(page, source_url: str) -> List[Dict[str, str]]:
    """
    Collect all program data from the page.
    Each degree type within a program creates a separate row.
    """
    rows = []
    
    # Find the view-content container
    view_content = page.query_selector('div.view-content')
    if not view_content:
        print("Error: Could not find view-content container")
        return rows
    
    # Find all program blocks (views-row)
    program_blocks = view_content.query_selector_all('div.views-row')
    print(f"Found {len(program_blocks)} program blocks")
    
    for idx, block in enumerate(program_blocks):
        try:
            # Extract program name from h2
            program_name_elem = block.query_selector('h2.header--main--dark')
            if not program_name_elem:
                print(f"  Block {idx}: No program name found, skipping")
                continue
            
            program_name = _clean(program_name_elem.inner_text())
            if not program_name:
                continue
            
            # Extract program description (optional)
            description_elem = block.query_selector('p')
            description = _clean(description_elem.inner_text()) if description_elem else ""
            
            # Find all degree options within this program
            degree_items = block.query_selector_all('mark.academics__block-degree ul li')
            
            if not degree_items:
                print(f"  Block {idx} ({program_name}): No degree items found")
                continue
            
            print(f"\n  Block {idx}: {program_name} - Found {len(degree_items)} degree option(s)")
            
            # Process each degree type as a separate row
            for degree_idx, degree_item in enumerate(degree_items):
                try:
                    # Extract degree URL and code
                    link_elem = degree_item.query_selector('a[href]')
                    if not link_elem:
                        continue
                    
                    degree_code = _clean(link_elem.inner_text())
                    program_url = link_elem.get_attribute('href') or ""
                    
                    # Make URL absolute if needed
                    if program_url and not program_url.startswith('http'):
                        program_url = urljoin('https://case.edu', program_url)
                    
                    # Extract program format (Full-Time, Part-Time, etc.)
                    format_elem = degree_item.query_selector('div.field--name-field-program-format-ref div.field--item')
                    program_format = _clean(format_elem.inner_text()) if format_elem else ""
                    
                    print(f"    Degree {degree_idx + 1}: {degree_code} - {program_url}")
                    
                    rows.append({
                        "program_name": program_name,
                        "degree_code": degree_code,
                        "programUrl": program_url,
                        "program_format": program_format,
                        "program_description": description,
                        "degree_program_parsing_link": source_url,
                        "university_name": "Case Western Reserve University",
                        "rank_type_1": "",
                        "position_1": "",
                        "url": "https://case.edu/",
                        "email": "",
                        "phone": "",
                        "country": "USA",
                        "city": "Cleveland",
                        "zipcode": "44106",
                        "address": "10900 Euclid Ave, Cleveland, OH 44106",
                        "campus_name": "Cleveland"
                    })
                    
                except Exception as e:
                    print(f"    Error processing degree item {degree_idx}: {e}")
                    continue
            
        except Exception as e:
            print(f"  Error processing block {idx}: {e}")
            continue
    
    return rows


if __name__ == "__main__":
    url = "https://case.edu/programs/"
    
    df = scrape_case_programs_headless(url)
    
    print("\n" + "="*80)
    print("Sample of scraped programs:")
    print("="*80)
    print(df[["program_name", "degree_code", "program_format"]].head(20).to_string(index=False))
    print("="*80)
    print(f"\nTotal program entries scraped: {len(df)}")
    
    # Save to CSV
    output_file = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_case_western_programs.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}")
    
    
    print("\n" + "="*80)
    print("Degree codes found:")
    print("="*80)
    print(df['degree_code'].value_counts().head(20).to_string())
    
    print("\n" + "="*80)
    print("Program format distribution:")
    print("="*80)
    print(df['program_format'].value_counts().to_string())
    
    # Show examples of programs with multiple degrees
    print("\n" + "="*80)
    print("Programs with multiple degree options:")
    print("="*80)
    program_counts = df.groupby('program_name').size().sort_values(ascending=False)
    for prog_name in program_counts.head(10).index:
        count = program_counts[prog_name]
        degrees = df[df['program_name'] == prog_name]['degree_code'].tolist()
        print(f"{prog_name} ({count} degrees): {', '.join(degrees)}")