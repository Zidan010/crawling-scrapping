# pip install playwright pandas
# playwright install chromium
from __future__ import annotations
from typing import List, Dict
from urllib.parse import urljoin
import pandas as pd
from playwright.sync_api import sync_playwright
import re
import time

def _clean(s: str) -> str:
    """Clean and normalize text strings."""
    return " ".join((s or "").replace("\xa0", " ").split()).strip()

def extract_degree_code(program_name: str) -> tuple[str, str]:
    """
    Extract degree code from program name.
    Example: "Accountancy - Professional (MAcc)" -> ("Accountancy - Professional", "MAcc")
    """
    match = re.search(r'\(([^)]+)\)\s*$', program_name)
    if match:
        degree_code = match.group(1).strip()
        # Remove the degree code from program name
        clean_name = program_name[:match.start()].strip()
        return clean_name, degree_code
    return program_name, ""

def scrape_byu_programs_headless(
    base_url: str,
    *,
    timeout_ms: int = 60000,
    max_pages: int = None,
) -> pd.DataFrame:
    """
    Headless scraper for BYU Graduate Programs.
    Extracts:
      - program_name (cleaned, without degree code)
      - degree_code (extracted from parentheses)
      - programUrl (absolute URL to program detail page)
    
    Args:
        base_url: Starting URL (e.g., page=1)
        timeout_ms: Timeout for page operations
        max_pages: Maximum number of pages to scrape (None = all pages)
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
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        all_rows = []
        seen_urls = set()  # Track URLs we've already collected
        current_page = 1
        consecutive_duplicate_pages = 0
        
        # Navigate to the first page
        # initial_url = "https://graduatecatalog24byu.catalog.prod.coursedog.com/programs" ##grad

        initial_url = "https://catalog.byu.edu/programs" ##undergrad

        print(f"Loading initial page: {initial_url}")
        page.goto(initial_url, wait_until="networkidle", timeout=timeout_ms)
        page.wait_for_timeout(3000)
        
        while True:
            # Check if we've reached max pages
            if max_pages and current_page > max_pages:
                print(f"Reached max pages limit: {max_pages}")
                break
            
            print(f"\nProcessing page {current_page}")
            
            try:
                # Wait for program cards to load
                try:
                    page.wait_for_selector('a.program-card[data-test="programCard"]', timeout=15000)
                    page.wait_for_timeout(2000)  # Additional wait for content to stabilize
                except:
                    print(f"No program cards found on page {current_page}. Stopping.")
                    break
                
                # Scroll to ensure all content is loaded
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
                
                # Collect programs from current page
                page_url = page.url
                page_rows, new_count = collect_programs_from_page(page, page_url, seen_urls)
                
                if not page_rows:
                    print(f"No programs found on page {current_page}. Stopping.")
                    break
                
                all_rows.extend(page_rows)
                print(f"Collected {len(page_rows)} programs from page {current_page} ({new_count} new, {len(page_rows) - new_count} duplicates)")
                
                # Track consecutive duplicate pages
                if new_count == 0:
                    consecutive_duplicate_pages += 1
                    print(f"Warning: No new programs on page {current_page} (consecutive duplicate pages: {consecutive_duplicate_pages})")
                    if consecutive_duplicate_pages >= 2:
                        print("Two consecutive pages with no new programs. Stopping.")
                        break
                else:
                    consecutive_duplicate_pages = 0
                
                # Try to navigate to next page
                next_button_found = False
                
                # Method 1: Look for pagination controls
                try:
                    # Look for various pagination button selectors
                    next_selectors = [
                        'button[aria-label*="next" i]',
                        'a[aria-label*="next" i]',
                        '.pagination button:last-child',
                        'button:has-text("Next")',
                        'a:has-text("Next")',
                    ]
                    
                    for selector in next_selectors:
                        next_button = page.query_selector(selector)
                        if next_button and not next_button.is_disabled():
                            print(f"Found next button with selector: {selector}")
                            next_button.click()
                            page.wait_for_load_state("networkidle", timeout=10000)
                            page.wait_for_timeout(2000)
                            next_button_found = True
                            break
                except Exception as e:
                    print(f"Error clicking next button: {e}")
                
                # Method 2: If no button found, try direct URL navigation
                if not next_button_found:
                    next_page = current_page + 1
                    next_url = f"https://graduatecatalog24byu.catalog.prod.coursedog.com/programs?page={next_page}&pq="
                    print(f"No next button found, navigating directly to: {next_url}")
                    
                    # Get current page HTML signature to detect if content changed
                    old_html = page.query_selector('a.program-card[data-test="programCard"]').get_attribute('href')
                    
                    page.goto(next_url, wait_until="networkidle", timeout=timeout_ms)
                    page.wait_for_timeout(3000)
                    
                    # Check if content actually changed
                    try:
                        new_html = page.query_selector('a.program-card[data-test="programCard"]').get_attribute('href')
                        if old_html == new_html:
                            print("Content didn't change after navigation. Checking if we're at the end.")
                    except:
                        pass
                
                current_page += 1
                time.sleep(1)  # Be nice to the server
                
            except Exception as e:
                print(f"Error on page {current_page}: {e}")
                import traceback
                traceback.print_exc()
                break
        
        browser.close()
    
    print(f"\nTotal programs collected (including duplicates): {len(all_rows)}")
    print(f"Unique programs: {len(seen_urls)}")
    
    # Create DataFrame and remove duplicates
    df = pd.DataFrame(all_rows)
    df_unique = df.drop_duplicates(subset=["programUrl"], keep='first')
    print(f"After deduplication: {len(df_unique)} programs")
    return df_unique

def collect_programs_from_page(page, page_url: str, seen_urls: set) -> tuple[List[Dict[str, str]], int]:
    """
    Collect all program data from the current page.
    Returns: (list of all programs, count of new programs)
    """
    rows = []
    new_count = 0
    
    # Find all program cards
    program_cards = page.query_selector_all('a.program-card[data-test="programCard"]')
    print(f"  Found {len(program_cards)} program cards on page")
    
    for idx, card in enumerate(program_cards):
        try:
            # Extract program name from the h3 title
            title_elem = card.query_selector('h3.media-title')
            if not title_elem:
                continue
            
            full_program_name = _clean(title_elem.inner_text())
            if not full_program_name:
                continue
            
            # Extract degree code from program name
            program_name, degree_code = extract_degree_code(full_program_name)
            
            # Extract program URL
            relative_url = card.get_attribute("href") or ""
            program_url = urljoin("https://graduatecatalog24byu.catalog.prod.coursedog.com", relative_url)
            
            # Check if this is a new URL
            is_new = program_url not in seen_urls
            if is_new:
                seen_urls.add(program_url)
                new_count += 1
                # Print first few new programs for debugging
                if new_count <= 3:
                    print(f"    New program {new_count}: {program_name} ({degree_code})")
            
            rows.append({
                "program_name": program_name,
                "degree_code": degree_code,
                "programUrl": program_url,
                "degree_program_parsing_link": page_url,
                "university_name": "Brigham Young University",
                "rank_type_1": "CS",
                "position_1": "106",
                "url": "https://www.byu.edu/",
                "email": "",
                "phone": "",
                "country": "USA",
                "city": "Provo",
                "zipcode": "84602",
                "address": "Provo, UT 84602",
                "campus_name": "Provo",
                "degree_type": "Graduate"
            })
            
        except Exception as e:
            print(f"  Error processing program card {idx}: {e}")
            continue
    
    return rows, new_count

if __name__ == "__main__":
    url = "https://catalog.byu.edu/programs?page=1&pq="
    
    # Scrape all pages (or set max_pages to limit for testing)
    df = scrape_byu_programs_headless(url, max_pages=None)
    
    print("\n" + "="*80)
    print("Sample of scraped programs:")
    print("="*80)
    print(df[["program_name", "degree_code", "programUrl"]].head(20).to_string(index=False))
    print("="*80)
    print(f"\nTotal unique programs scraped: {len(df)}")
    
    # Save to CSV
    output_file = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_brigham_youngU_UG_programs.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}")
    
    # Display degree code statistics
    print("\n" + "="*80)
    print("Degree codes found:")
    print("="*80)
    print(df['degree_code'].value_counts().to_string())
    
    # Show some examples of each degree code
    print("\n" + "="*80)
    print("Sample programs by degree code:")
    print("="*80)
    for code in df['degree_code'].value_counts().head(10).index:
        sample = df[df['degree_code'] == code]['program_name'].iloc[0]
        count = len(df[df['degree_code'] == code])
        print(f"{code:8s} ({count:2d} programs): {sample}")