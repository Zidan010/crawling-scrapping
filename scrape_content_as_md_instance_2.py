
# import sys
# import csv
# import asyncio
# import logging
# import random
# import re
# from pathlib import Path
# import requests
# from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
# import uuid
# csv.field_size_limit(sys.maxsize)



# # ----------------------------------------------------------
# # Logging setup
# # ----------------------------------------------------------
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# # ----------------------------------------------------------
# # Crawl4AI configuration
# # ----------------------------------------------------------
# browser_config = BrowserConfig(
#     headless=True,
#     verbose=False,
#     java_script_enabled=True,
#     text_mode=False # Changed to False to preserve more structured content for markdown
# )
# crawl_config = CrawlerRunConfig(
#     cache_mode=CacheMode.BYPASS,
#     scan_full_page=True,
#     scroll_delay=2.0,
#     page_timeout=120000,
#     wait_for_timeout=30,
#     excluded_tags=["form", "nav", "img", "script", "style", "footer", "header"],
#     exclude_social_media_links=True,
#     exclude_external_images=True,
#     exclude_external_links=True,
# )
# # ----------------------------------------------------------
# # Input / Output paths
# # ----------------------------------------------------------
# INPUT_CSV = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/latest_input_for_phase-2_scrape/extracted_programs_ucflorida_latest.csv" # ← Output from your first script
# OUTPUT_CSV = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/latest_output_of_phase-2_scrape/updated-extracted_programs_content_ucflorida_latest_final.csv" # ← Final CSV with content
# # ----------------------------------------------------------
# # Prefix for PID
# # ----------------------------------------------------------
# PREFIX = "ucflorida_"  # Change this prefix as needed each time you run the code
# # ----------------------------------------------------------
# # NEW: Content cleaning function (preserves markdown structure)
# # ----------------------------------------------------------
# def clean_program_content(raw_markdown: str) -> str:
#     """
#     Clean the scraped program content while preserving markdown structure:
#     - Remove any remaining HTML tags
#     - Normalize unicode characters
#     - Preserve indentation, headers, lists, and paragraph spacing
#     - Remove excessive blank lines (collapse to single blank for paragraphs)
#     - Remove common noise patterns without breaking structure
#     """
#     if not raw_markdown:
#         return ""
#     # 1. Remove any remaining HTML tags (safety net)
#     content = re.sub(r'<[^>]+>', '', raw_markdown)
#     # 2. Replace common Unicode/smart quotes and dashes with ASCII equivalents
#     content = content.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")
#     content = content.replace('–', '-').replace('—', '-').replace('…', '...')
#     # 3. Split into lines and clean each (preserve leading spaces for indentation, e.g., lists)
#     lines = content.split('\n')
#     lines = [line.rstrip() for line in lines] # Remove trailing whitespace per line
#     # 4. Collapse multiple consecutive blank lines to a single blank (preserves paragraphs)
#     cleaned_lines = []
#     prev_was_blank = False
#     for line in lines:
#         if not line.strip(): # Blank line
#             if not prev_was_blank:
#                 cleaned_lines.append('')
#                 prev_was_blank = True
#         else:
#             cleaned_lines.append(line)
#             prev_was_blank = False
#     # 5. Rejoin lines
#     content = '\n'.join(cleaned_lines)
#     # 6. Remove leading/trailing blank lines
#     content = content.strip()
#     # 7. Remove common footer/copyright noise (customize if needed)
#     noise_patterns = [
#         r'© \d{4}.*?All rights reserved\.?',
#         r'Privacy Policy.*?Terms of Use',
#         r'Follow us on.*?(Facebook|Twitter|Instagram|LinkedIn)',
#         r'University of.*?Home\s*$',
#     ]
#     for pattern in noise_patterns:
#         content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)
#     # 8. Final trim
#     return content.strip()
# # ----------------------------------------------------------
# # Fetch with retry + fallback
# # ----------------------------------------------------------
# async def fetch_url(crawler, url: str, retries=3, base_delay=5):
#     for attempt in range(retries):
#         try:
#             logger.info(f"Fetching {url} (attempt {attempt + 1})")
#             result = await crawler.arun(url=url, config=crawl_config)
#             if result and result.markdown:
#                 logger.info(f"Success → {url}")
#                 return result.markdown.strip()
#             else:
#                 raise ValueError("No markdown content")
#         except Exception as e:
#             logger.error(f"Error on {url} (attempt {attempt + 1}): {str(e)}")
#             if attempt < retries - 1:
#                 await asyncio.sleep(base_delay * (2 ** attempt))
#             else:
#                 # Fallback to requests (note: this returns HTML, which will be cleaned to text, losing some structure)
#                 try:
#                     resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
#                     if resp.ok and "text/html" in resp.headers.get("Content-Type", ""):
#                         logger.info(f"Fallback success → {url}")
#                         return resp.text # Will be processed as markdown-like text in cleaning
#                 except Exception as ex:
#                     logger.error(f"Fallback failed: {ex}")
#                 return ""
# # ----------------------------------------------------------
# # Main async function
# # ----------------------------------------------------------
# async def main():
#     input_path = Path(INPUT_CSV)
#     output_path = Path(OUTPUT_CSV)
#     if not input_path.exists():
#         logger.error(f"Input CSV not found: {INPUT_CSV}")
#         logger.error("Run the first-phase script first to generate program links.")
#         return
#     # Read all rows first
#     # rows = []
#     # with open(input_path, newline='', encoding='utf-8') as f:
#     #     reader = csv.DictReader(f)
#     #     for row in reader:
#     #         rows.append(row)
#     # logger.info(f"Loaded {len(rows)} programs from {INPUT_CSV}")

#     rows = []
#     seen_urls = set()
#     duplicate_count = 0

#     with open(input_path, newline='', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             url = (row.get("programUrl") or "").strip()
#             if not url:
#                 continue

#             if url in seen_urls:
#                 duplicate_count += 1
#                 continue

#             seen_urls.add(url)
#             rows.append(row)

#     logger.info(f"Loaded {len(rows)} unique programs from {INPUT_CSV}")
#     logger.info(f"Skipped {duplicate_count} duplicate programUrl rows")



#     file_exists = output_path.exists()
#     async with AsyncWebCrawler(config=browser_config) as crawler:
#         with open(output_path, 'a' if file_exists else 'w', newline='', encoding='utf-8') as outfile:
#             fieldnames = list(rows[0].keys()) if rows else []
#             if "program_content" not in fieldnames:
#                 fieldnames.append("program_content")
#             if "pid" not in fieldnames:
#                 fieldnames.append("pid")
#             writer = csv.DictWriter(outfile, fieldnames=fieldnames)
#             if not file_exists:
#                 writer.writeheader()
#             batch_count = 0
#             for idx, row in enumerate(rows, 1):
#                 program_link = row.get("programUrl", "").strip()
#                 if not program_link:
#                     logger.warning(f"Row {idx}: No programUrl, skipping")
#                     continue
#                 program_name = row.get("program_name", "unknown")
#                 uni_name = row.get("university_name", "unknown")
#                 logger.info(f"[{idx}/{len(rows)}] Processing: {uni_name} — {program_name}")
#                 # Fetch raw content (markdown from crawler)
#                 raw_content = await fetch_url(crawler, program_link)
#                 # CLEAN THE CONTENT (preserving markdown structure)
#                 cleaned_content = clean_program_content(raw_content)
#                 # Optional: log sample for debugging
#                 if cleaned_content:
#                     logger.info(f" → Cleaned content length: {len(cleaned_content)} chars")
#                     logger.debug(f" → Sample: {cleaned_content[:200]}...") # Debug sample
#                 else:
#                     logger.warning(f" → No content after cleaning: {program_link}")
#                 # Add cleaned content to row
#                 row["program_content"] = cleaned_content
#                 row["pid"] = PREFIX + str(uuid.uuid4())
#                 # Write row
#                 writer.writerow(row)
#                 batch_count += 1
#                 # Save every 10 programs
#                 if batch_count >= 10:
#                     outfile.flush()
#                     logger.info(" → Saved progress (10 programs)")
#                     batch_count = 0
#                 # Polite delay to avoid rate limiting
#                 await asyncio.sleep(random.uniform(2, 5))
#     logger.info(f"\nAll done! {len(rows)} programs processed.")
#     logger.info(f"Final output saved to: {OUTPUT_CSV}")
# # ----------------------------------------------------------
# # Entry point
# # ----------------------------------------------------------
# if __name__ == "__main__":
#     asyncio.run(main())









import sys
import csv
import asyncio
import logging
import random
import re
from pathlib import Path
import requests
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from bs4 import BeautifulSoup
import uuid

csv.field_size_limit(sys.maxsize)

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------
# Input / Output paths
# ----------------------------------------------------------
INPUT_CSV = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_input_files/michiganu_input_latest_undergrad_cert.csv"
OUTPUT_CSV = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/latest_output_of_phase-2_scrape/updated-extracted_programs_content_michiganu_undergrad_cert_latest_final.csv"

# ----------------------------------------------------------
# Prefix for PID
# ----------------------------------------------------------
# PREFIX = "riceu_"

# Crawl4AI configuration
browser_config = BrowserConfig(
    headless=True,
    verbose=False,
    java_script_enabled=True,
    text_mode=False
)

crawl_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    scan_full_page=True,
    scroll_delay=2.0,
    page_timeout=120000,
    wait_for_timeout=30,
    # excluded_tags=["script", "style", "noscript"],
    exclude_social_media_links=True,
    exclude_external_images=True,
    exclude_external_links=False,
)

# ==============================================================================
# HELPER FUNCTIONS - HTML PROCESSING
# ==============================================================================

def extract_main_content(html_content: str) -> str:
    """
    Extract main content from any university webpage.
    Uses semantic HTML and common patterns.
    """
    if not html_content:
        return ""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        main_content = None
        
        # 1. Try semantic HTML5 tags (most reliable)
        for tag in ['main', 'article']:
            main_content = soup.find(tag)
            if main_content:
                logger.debug(f"Found content in <{tag}> tag")
                break
        
        # 2. Try common main content IDs/classes
        if not main_content:
            common_patterns = [
                {'id': re.compile(r'main|content|primary|page-content|main-content', re.I)},
                {'class': re.compile(r'main|content|primary|page-content|main-content', re.I)},
                {'role': 'main'},
            ]
            for pattern in common_patterns:
                main_content = soup.find(['div', 'section'], pattern)
                if main_content:
                    logger.debug(f"Found content with pattern: {pattern}")
                    break
        
        # 3. If still not found, use the body but remove header/footer/aside
        if not main_content:
            main_content = soup.find('body')
            if main_content:
                for unwanted in main_content.find_all(['header', 'footer', 'aside']):
                    text = unwanted.get_text().lower()
                    if not any(kw in text for kw in ['apply', 'admission', 'requirement', 'program', 'degree', 'course']):
                        unwanted.decompose()
                logger.debug("Using body with header/footer removed")
        
        if not main_content:
            return ""
        
        return html_to_markdown(main_content)
    
    except Exception as e:
        logger.error(f"Error extracting main content: {e}")
        return ""


def html_to_markdown(element) -> str:
    """
    Convert HTML element to markdown-style text.
    Extracts ALL content with proper structure - headings, lists, links, etc.
    """
    if not element:
        return ""
    
    result = []
    
    def process_element(elem, in_list=False):
        """Recursively process ALL elements and their children"""
        
        # Skip garbage elements
        if elem.name in ['script', 'style', 'noscript', 'iframe', 'svg']:
            return
        
        # Handle text nodes
        if isinstance(elem, str):
            text = elem.strip()
            if text:
                result.append(text + ' ')
            return
        
        # Handle headings
        if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(elem.name[1])
            text = elem.get_text(strip=True)
            if text:
                result.append('\n\n' + '#' * level + ' ' + text + '\n\n')
            return
        
        # Handle unordered lists
        if elem.name == 'ul':
            result.append('\n')
            for li in elem.find_all('li', recursive=False):
                result.append('- ')
                for child in li.children:
                    process_element(child, in_list=True)
                result.append('\n')
            result.append('\n')
            return
        
        # Handle ordered lists
        if elem.name == 'ol':
            result.append('\n')
            for idx, li in enumerate(elem.find_all('li', recursive=False), 1):
                result.append(f'{idx}. ')
                for child in li.children:
                    process_element(child, in_list=True)
                result.append('\n')
            result.append('\n')
            return
        
        # Handle links - ALWAYS capture with URL
        if elem.name == 'a':
            text = elem.get_text(strip=True)
            href = elem.get('href', '')
            if text and href:
                result.append(f'**{text}** [{href}]')
            elif text:
                result.append(text)
            if not in_list:
                result.append(' ')
            return
        
        # Handle paragraphs
        if elem.name == 'p':
            for child in elem.children:
                process_element(child, in_list)
            result.append('\n\n')
            return
        
        # Handle tables
        if elem.name == 'table':
            result.append('\n\n')
            for row in elem.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_text = ' | '.join(cell.get_text(strip=True) for cell in cells if cell.get_text(strip=True))
                    if row_text:
                        result.append(row_text + '\n')
            result.append('\n')
            return
        
        # Handle line breaks
        if elem.name == 'br':
            result.append('\n')
            return
        
        # Handle strong/bold
        if elem.name in ['strong', 'b']:
            text = elem.get_text(strip=True)
            if text:
                result.append(f'**{text}** ')
            return
        
        # Handle emphasis/italic
        if elem.name in ['em', 'i']:
            text = elem.get_text(strip=True)
            if text:
                result.append(f'*{text}* ')
            return
        
        # For containers - process ALL children
        if elem.name in ['div', 'section', 'article', 'main', 'aside', 'nav', 'header', 'footer']:
            for child in elem.children:
                process_element(child, in_list)
            return
        
        # For inline elements - process children
        if elem.name in ['span', 'label', 'small']:
            for child in elem.children:
                process_element(child, in_list)
            return
        
        # For any other element with children - process them all
        if hasattr(elem, 'children'):
            for child in elem.children:
                process_element(child, in_list)
    
    # Start processing from root
    process_element(element)
    
    # Join and clean up
    text = ''.join(result)
    
    # Clean up excessive whitespace
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n +', '\n', text)
    text = re.sub(r' +\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

# ==============================================================================
# HELPER FUNCTIONS - CONTENT CLEANING
# ==============================================================================

def remove_navigation_noise(content: str) -> str:
    """
    Remove ONLY obvious navigation noise.
    Very conservative - when in doubt, keep the content.
    """
    if not content:
        return ""
    
    lines = content.split('\n')
    cleaned_lines = []
    
    # Only remove OBVIOUS navigation/UI elements
    obvious_noise_patterns = [
        r'^\s*skip to (main |primary )?content\s*$',
        r'^\s*toggle (navigation|menu)\s*$',
        r'^\s*open menu\s*$',
        r'^\s*close\s*$',
        r'^[\s\|>›/-]{3,}$',
        r'^\s*search\s*$',
    ]
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            cleaned_lines.append(line)
            continue
        
        # Check if it's obvious noise
        is_noise = False
        for pattern in obvious_noise_patterns:
            if re.match(pattern, stripped, re.IGNORECASE):
                is_noise = True
                break
        
        if not is_noise:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def clean_program_content(raw_markdown: str, raw_html: str = "") -> str:
    """
    Clean program content - works for ANY university website.
    Prioritizes HTML parsing for better structure preservation.
    """
    content = ""
    
    # Use HTML parsing if available (most reliable)
    if raw_html:
        content = extract_main_content(raw_html)
        logger.debug(f"Extracted from HTML: {len(content)} chars")
    
    # Fallback to markdown if HTML extraction failed
    if not content or len(content) < 200:
        content = raw_markdown
        logger.debug(f"Using markdown: {len(content)} chars")
    
    if not content:
        return ""
    
    # Remove navigation noise
    content = remove_navigation_noise(content)
    
    # Normalize Unicode characters for Excel compatibility
    replacements = {
        '"': '"', '"': '"', "'": "'", "'": "'",
        '–': '-', '—': '-', '…': '...', 
        '\u00a0': ' ',
        '\u200b': '',
        '\u2022': '-',
        '\u2013': '-',
        '\u2014': '-',
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # Remove problematic control characters
    content = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', content)
    
    # Collapse excessive blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()


def sanitize_for_csv(text: str) -> str:
    """Ensure CSV compatibility"""
    if not text:
        return ""
    text = text.replace('\x00', '')
    text = text.replace('\r\n', '\n')
    return text

# ==============================================================================
# HELPER FUNCTIONS - WEB FETCHING
# ==============================================================================

async def fetch_url(crawler, url: str, retries=3, base_delay=5):
    """
    Fetch URL and return both markdown and HTML.
    Returns tuple: (markdown, html)
    """
    for attempt in range(retries):
        try:
            logger.info(f"Fetching {url} (attempt {attempt + 1})")
            result = await crawler.arun(url=url, config=crawl_config)
            if result:
                markdown = result.markdown.strip() if result.markdown else ""
                html = result.html if hasattr(result, 'html') and result.html else ""
                
                if markdown or html:
                    logger.info(f"Success → {url}")
                    return (markdown, html)
                else:
                    raise ValueError("No content retrieved")
            else:
                raise ValueError("No result object")
        except Exception as e:
            logger.error(f"Error on {url} (attempt {attempt + 1}): {str(e)}")
            if attempt < retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt))
            else:
                # Fallback to requests
                try:
                    resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
                    if resp.ok and "text/html" in resp.headers.get("Content-Type", ""):
                        logger.info(f"Fallback success → {url}")
                        return ("", resp.text)
                except Exception as ex:
                    logger.error(f"Fallback failed: {ex}")
                return ("", "")

# ==============================================================================
# MAIN SCRAPING FUNCTION
# ==============================================================================

async def main():
    """
    Main scraping function:
    1. Reads input CSV with program URLs
    2. Fetches and extracts content from each URL
    3. Cleans and processes content to markdown
    4. Saves to output CSV with Excel compatibility
    """
    input_path = Path(INPUT_CSV)
    output_path = Path(OUTPUT_CSV)
    
    # Validate input file exists
    if not input_path.exists():
        logger.error(f"Input CSV not found: {INPUT_CSV}")
        return
    
    # Read all rows from input CSV
    rows = []
    with open(input_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    logger.info(f"Loaded {len(rows)} programs from {INPUT_CSV}")
    
    file_exists = output_path.exists()
    
    # Start crawling
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Open output CSV with UTF-8 BOM for Excel compatibility
        with open(output_path, 'a' if file_exists else 'w', 
                  newline='', encoding='utf-8-sig') as outfile:
            
            # Setup CSV writer
            fieldnames = list(rows[0].keys()) if rows else []
            if "program_content" not in fieldnames:
                fieldnames.append("program_content")
            if "id" not in fieldnames:
                fieldnames.append("id")
            
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, 
                                    quoting=csv.QUOTE_ALL)
            
            if not file_exists:
                writer.writeheader()
            
            batch_count = 0
            
            # Process each program
            for idx, row in enumerate(rows, 1):
                program_link = row.get("programUrl", "").strip()
                if not program_link:
                    logger.warning(f"Row {idx}: No programUrl, skipping")
                    continue
                
                program_name = row.get("program_name", "unknown")
                uni_name = row.get("university_name", "unknown")
                logger.info(f"[{idx}/{len(rows)}] Processing: {uni_name} — {program_name}")
                
                # Fetch content (both markdown and HTML)
                raw_markdown, raw_html = await fetch_url(crawler, program_link)
                
                # Clean content (works for any university)
                cleaned_content = clean_program_content(raw_markdown, raw_html)
                cleaned_content = sanitize_for_csv(cleaned_content)
                
                if cleaned_content:
                    logger.info(f" → Content length: {len(cleaned_content)} chars")
                    sample = cleaned_content[:200].replace('\n', ' ')
                    logger.info(f" → Sample: {sample}...")
                else:
                    logger.warning(f" → No content: {program_link}")
                
                # Sanitize all fields in the row
                sanitized_row = {}
                for key, value in row.items():
                    sanitized_row[key] = sanitize_for_csv(value) if isinstance(value, str) else value
                
                # Add cleaned content and generate PID
                sanitized_row["program_content"] = cleaned_content
                # sanitized_row["pid"] = PREFIX + str(uuid.uuid4())
                sanitized_row["id"] = str(uuid.uuid4())
                
                # Write row to CSV
                writer.writerow(sanitized_row)
                batch_count += 1
                
                # Save progress every 10 programs
                if batch_count >= 10:
                    outfile.flush()
                    logger.info(" → Saved progress (10 programs)")
                    batch_count = 0
                
                # Polite delay to avoid rate limiting
                await asyncio.sleep(random.uniform(2, 5))
    
    logger.info(f"\nAll done! {len(rows)} programs processed.")
    logger.info(f"Final output saved to: {OUTPUT_CSV}")

# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    asyncio.run(main())