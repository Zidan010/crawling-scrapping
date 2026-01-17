# import sys
# import csv
# import asyncio
# import logging
# import random
# import re
# from pathlib import Path
# import requests
# from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
# from bs4 import BeautifulSoup, Comment
# import uuid

# csv.field_size_limit(sys.maxsize)

# # ==============================================================================
# # CONFIGURATION
# # ==============================================================================
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# INPUT_CSV = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/Program-Scrapper-AI-/Codes/University of Toronto/uot_UGprograms.csv"
# OUTPUT_CSV = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/latest_output_of_phase-2_scrape/updated-extracted_programs_content_uot_UGprograms_2.csv"

# browser_config = BrowserConfig(
#     headless=True,
#     verbose=True,
#     java_script_enabled=True,
#     text_mode=False,
#     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# )

# # CRITICAL FIX: Increased wait times and added JS execution wait
# crawl_config = CrawlerRunConfig(
#     cache_mode=CacheMode.BYPASS,
#     scan_full_page=True,
#     scroll_delay=3.0,  # Increased
#     page_timeout=120000,
#     wait_for_timeout=90,  # Increased to 90 seconds
#     js_code=["window.scrollTo(0, document.body.scrollHeight);"],  # Trigger lazy loading
#     wait_for="css:.program-details, #program-content, .content-area",  # Wait for content
#     exclude_social_media_links=True,
#     exclude_external_images=True,
#     exclude_external_links=False,
# )

# # ==============================================================================
# # HELPER FUNCTIONS - HTML PROCESSING
# # ==============================================================================

# def extract_uga_bulletin_content(html_content: str) -> str:
#     """
#     SPECIFIC extractor for UGA bulletin pages.
#     Targets the actual program details container.
#     """
#     if not html_content:
#         return ""
    
#     try:
#         soup = BeautifulSoup(html_content, 'html.parser')
        
#         # FIX 1: Target UGA-specific content containers
#         # These are common class/id patterns in bulletin systems
#         target_selectors = [
#             # Direct program details
#             {'class': re.compile(r'program-details|program-content|programdetails', re.I)},
#             {'id': re.compile(r'program-details|program-content|programdetails', re.I)},
            
#             # Content area
#             {'class': re.compile(r'content-area|main-content|page-content', re.I)},
#             {'id': re.compile(r'content-area|main-content|page-content', re.I)},
            
#             # Academic bulletin specific
#             {'class': re.compile(r'bulletin-content|academic-program', re.I)},
#             {'id': re.compile(r'bulletin-content|academic-program', re.I)},
#         ]
        
#         main_content = None
#         for selector in target_selectors:
#             main_content = soup.find(['div', 'section', 'article'], selector)
#             if main_content:
#                 logger.debug(f"Found content with selector: {selector}")
#                 break
        
#         # FIX 2: Remove navigation BEFORE processing
#         if main_content:
#             # Remove common navigation elements
#             for nav_element in main_content.find_all(['nav', 'aside']):
#                 nav_element.decompose()
            
#             # Remove elements with navigation-related classes
#             nav_patterns = [
#                 re.compile(r'nav|menu|breadcrumb|sidebar|footer|header', re.I)
#             ]
#             for pattern in nav_patterns:
#                 for elem in main_content.find_all(class_=pattern):
#                     elem.decompose()
#                 for elem in main_content.find_all(id=pattern):
#                     elem.decompose()
        
#         # FIX 3: If still not found, try semantic tags but aggressively remove nav
#         if not main_content:
#             for tag in ['main', 'article']:
#                 main_content = soup.find(tag)
#                 if main_content:
#                     # Remove ALL navigation
#                     for unwanted in main_content.find_all(['header', 'footer', 'aside', 'nav']):
#                         unwanted.decompose()
#                     logger.debug(f"Found content in <{tag}> tag after nav removal")
#                     break
        
#         if not main_content:
#             logger.warning("Could not find main content container")
#             return ""
        
#         return html_to_markdown(main_content)
    
#     except Exception as e:
#         logger.error(f"Error extracting UGA bulletin content: {e}")
#         return ""


# def html_to_markdown(element) -> str:
#     """Convert HTML element to markdown with ALL content preserved."""
#     if not element:
#         return ""
    
#     result = []
    
#     def process_element(elem, in_list=False):
#         # Skip garbage
#         if elem.name in ['script', 'style', 'noscript', 'iframe', 'svg', 'nav', 'aside']:
#             return
        
#         if isinstance(elem, Comment):
#             return
        
#         # Text nodes
#         if isinstance(elem, str):
#             text = elem.strip()
#             if text:
#                 result.append(text + ' ')
#             return
        
#         # Headings
#         if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
#             level = int(elem.name[1])
#             text = elem.get_text(strip=True)
#             if text:
#                 result.append('\n\n' + '#' * level + ' ' + text + '\n\n')
#             return
        
#         # Unordered lists
#         if elem.name == 'ul':
#             result.append('\n')
#             for li in elem.find_all('li', recursive=False):
#                 result.append('- ')
#                 for child in li.children:
#                     process_element(child, in_list=True)
#                 result.append('\n')
#             result.append('\n')
#             return
        
#         # Ordered lists
#         if elem.name == 'ol':
#             result.append('\n')
#             for idx, li in enumerate(elem.find_all('li', recursive=False), 1):
#                 result.append(f'{idx}. ')
#                 for child in li.children:
#                     process_element(child, in_list=True)
#                 result.append('\n')
#             result.append('\n')
#             return
        
#         # Links
#         if elem.name == 'a':
#             text = elem.get_text(strip=True)
#             href = elem.get('href', '')
#             if text and href and not href.startswith('#'):  # Skip anchor links
#                 result.append(f'**{text}** [{href}]')
#             elif text:
#                 result.append(text)
#             if not in_list:
#                 result.append(' ')
#             return
        
#         # Paragraphs
#         if elem.name == 'p':
#             for child in elem.children:
#                 process_element(child, in_list)
#             result.append('\n\n')
#             return
        
#         # Tables
#         if elem.name == 'table':
#             result.append('\n\n')
#             for row in elem.find_all('tr'):
#                 cells = row.find_all(['td', 'th'])
#                 if cells:
#                     row_text = ' | '.join(cell.get_text(strip=True) for cell in cells if cell.get_text(strip=True))
#                     if row_text:
#                         result.append(row_text + '\n')
#             result.append('\n')
#             return
        
#         # Line breaks
#         if elem.name == 'br':
#             result.append('\n')
#             return
        
#         # Bold
#         if elem.name in ['strong', 'b']:
#             text = elem.get_text(strip=True)
#             if text:
#                 result.append(f'**{text}** ')
#             return
        
#         # Italic
#         if elem.name in ['em', 'i']:
#             text = elem.get_text(strip=True)
#             if text:
#                 result.append(f'*{text}* ')
#             return
        
#         # Containers - process children
#         if elem.name in ['div', 'section', 'article', 'main', 'header', 'footer']:
#             for child in elem.children:
#                 process_element(child, in_list)
#             return
        
#         # Inline elements
#         if elem.name in ['span', 'label', 'small']:
#             for child in elem.children:
#                 process_element(child, in_list)
#             return
        
#         # Process any other elements with children
#         if hasattr(elem, 'children'):
#             for child in elem.children:
#                 process_element(child, in_list)
    
#     process_element(element)
    
#     # Clean up
#     text = ''.join(result)
#     text = re.sub(r' +', ' ', text)
#     text = re.sub(r'\n +', '\n', text)
#     text = re.sub(r' +\n', '\n', text)
#     text = re.sub(r'\n{3,}', '\n\n', text)
    
#     return text.strip()


# def remove_navigation_noise(content: str) -> str:
#     """Remove obvious navigation patterns."""
#     if not content:
#         return ""
    
#     lines = content.split('\n')
#     cleaned_lines = []
    
#     # Navigation patterns to remove
#     noise_patterns = [
#         r'^\s*skip to (main |primary )?content\s*$',
#         r'^\s*toggle (navigation|menu)\s*$',
#         r'^\s*open menu\s*$',
#         r'^\s*close\s*$',
#         r'^[\s\|>›/-]{3,}$',
#         r'^\s*(search|menu)\s*$',
#         r'^\s*-\s*\*\*Programs\*\*\s*\[',  # Remove the specific menu items
#         r'^\s*-\s*\*\*Courses\*\*\s*\[',
#         r'^\s*-\s*\*\*University Info\*\*\s*\[',
#         r'^\s*-\s*\*\*searchSearch\*\*\s*\[',
#         r'^\s*menuMenu\s*$',
#     ]
    
#     for line in lines:
#         stripped = line.strip()
        
#         if not stripped:
#             cleaned_lines.append(line)
#             continue
        
#         # Check if it matches noise patterns
#         is_noise = any(re.match(pattern, stripped, re.IGNORECASE) for pattern in noise_patterns)
        
#         if not is_noise:
#             cleaned_lines.append(line)
    
#     return '\n'.join(cleaned_lines)


# def clean_program_content(raw_markdown: str, raw_html: str = "") -> str:
#     """Clean program content with UGA-specific extraction."""
#     content = ""
    
#     # Use UGA-specific HTML extraction
#     if raw_html:
#         content = extract_uga_bulletin_content(raw_html)
#         logger.debug(f"Extracted from HTML: {len(content)} chars")
    
#     # Fallback to markdown
#     if not content or len(content) < 200:
#         content = raw_markdown
#         logger.debug(f"Using markdown: {len(content)} chars")
    
#     if not content:
#         return ""
    
#     # Remove navigation noise
#     content = remove_navigation_noise(content)
    
#     # Normalize Unicode
#     replacements = {
#         '"': '"', '"': '"', "'": "'", "'": "'",
#         '–': '-', '—': '-', '…': '...',
#         '\u00a0': ' ', '\u200b': '', '\u2022': '-',
#         '\u2013': '-', '\u2014': '-',
#         '\u2018': "'", '\u2019': "'",
#         '\u201c': '"', '\u201d': '"',
#     }
    
#     for old, new in replacements.items():
#         content = content.replace(old, new)
    
#     # Remove control characters
#     content = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', content)
#     content = re.sub(r'\n{3,}', '\n\n', content)
    
#     return content.strip()


# def sanitize_for_csv(text: str) -> str:
#     """Ensure CSV compatibility."""
#     if not text:
#         return ""
#     text = text.replace('\x00', '')
#     text = text.replace('\r\n', '\n')
#     return text


# # ==============================================================================
# # WEB FETCHING
# # ==============================================================================

# async def fetch_url(crawler, url: str, retries=3, base_delay=5):
#     """Fetch URL with retry logic."""
#     for attempt in range(retries):
#         try:
#             logger.info(f"Fetching {url} (attempt {attempt + 1})")
#             result = await crawler.arun(url=url, config=crawl_config)
            
#             if result:
#                 markdown = result.markdown.strip() if result.markdown else ""
#                 html = result.html if hasattr(result, 'html') and result.html else ""
                
#                 if markdown or html:
#                     logger.info(f"Success → {url}")
#                     logger.debug(f"HTML length: {len(html)}, Markdown length: {len(markdown)}")
#                     return (markdown, html)
#                 else:
#                     raise ValueError("No content retrieved")
#             else:
#                 raise ValueError("No result object")
                
#         except Exception as e:
#             logger.error(f"Error on {url} (attempt {attempt + 1}): {str(e)}")
#             if attempt < retries - 1:
#                 await asyncio.sleep(base_delay * (2 ** attempt))
#             else:
#                 # Fallback to requests
#                 try:
#                     resp = requests.get(url, timeout=20, 
#                                       headers={"User-Agent": "Mozilla/5.0"})
#                     if resp.ok and "text/html" in resp.headers.get("Content-Type", ""):
#                         logger.info(f"Fallback success → {url}")
#                         return ("", resp.text)
#                 except Exception as ex:
#                     logger.error(f"Fallback failed: {ex}")
#                 return ("", "")


# def generate_custom_id(prefix):
#     """Generate custom ID with prefix."""
#     separator = "_"
#     prefix_len = len(prefix) + len(separator)
#     new_uuid = str(uuid.uuid4())[:36 - prefix_len]
#     return f"{prefix}{separator}{new_uuid}"


# # ==============================================================================
# # MAIN
# # ==============================================================================

# async def main():
#     """Main scraping function."""
#     input_path = Path(INPUT_CSV)
#     output_path = Path(OUTPUT_CSV)
    
#     if not input_path.exists():
#         logger.error(f"Input CSV not found: {INPUT_CSV}")
#         return
    
#     # Read input
#     rows = []
#     with open(input_path, newline='', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             rows.append(row)
    
#     logger.info(f"Loaded {len(rows)} programs from {INPUT_CSV}")
    
#     file_exists = output_path.exists()
    
#     async with AsyncWebCrawler(config=browser_config) as crawler:
#         with open(output_path, 'a' if file_exists else 'w',
#                   newline='', encoding='utf-8-sig') as outfile:
            
#             fieldnames = list(rows[0].keys()) if rows else []
#             if "program_content" not in fieldnames:
#                 fieldnames.append("program_content")
#             if "id" not in fieldnames:
#                 fieldnames.append("id")
            
#             writer = csv.DictWriter(outfile, fieldnames=fieldnames,
#                                     quoting=csv.QUOTE_ALL)
            
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
                
#                 # Fetch content
#                 raw_markdown, raw_html = await fetch_url(crawler, program_link)
                
#                 # Clean content
#                 cleaned_content = clean_program_content(raw_markdown, raw_html)
#                 cleaned_content = sanitize_for_csv(cleaned_content)
                
#                 if cleaned_content:
#                     logger.info(f" → Content length: {len(cleaned_content)} chars")
#                     sample = cleaned_content[:200].replace('\n', ' ')
#                     logger.info(f" → Sample: {sample}...")
#                 else:
#                     logger.warning(f" → No content: {program_link}")
                
#                 # Sanitize row
#                 sanitized_row = {k: sanitize_for_csv(v) if isinstance(v, str) else v 
#                                for k, v in row.items()}
                
#                 sanitized_row["program_content"] = cleaned_content
#                 sanitized_row["id"] = generate_custom_id("uotug")
                
#                 writer.writerow(sanitized_row)
#                 batch_count += 1
                
#                 if batch_count >= 10:
#                     outfile.flush()
#                     logger.info(" → Saved progress (10 programs)")
#                     batch_count = 0
                
#                 await asyncio.sleep(random.uniform(3, 6))
    
#     logger.info(f"\nAll done! {len(rows)} programs processed.")
#     logger.info(f"Final output saved to: {OUTPUT_CSV}")


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
from bs4 import BeautifulSoup, Comment
import uuid

csv.field_size_limit(sys.maxsize)

# ==============================================================================
# CONFIGURATION
# ==============================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INPUT_CSV = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-1_output_files_phase-2_input/updated-extracted_programs_arizona.csv"
OUTPUT_CSV = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/latest_output_of_phase-2_scrape/updated-extracted_programs_content_arizona.csv"

browser_config = BrowserConfig(
    headless=True,
    verbose=True,
    java_script_enabled=True,
    text_mode=False,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

crawl_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    scan_full_page=True,
    scroll_delay=3.0,
    page_timeout=120000,
    wait_for_timeout=90,
    js_code=["window.scrollTo(0, document.body.scrollHeight);"],
    exclude_social_media_links=True,
    exclude_external_images=True,
    exclude_external_links=False,
)

# ==============================================================================
# UNIVERSAL HTML EXTRACTION
# ==============================================================================

def remove_unwanted_elements(soup):
    """Remove navigation, ads, scripts, and other non-content elements."""
    
    # Remove by tag
    unwanted_tags = [
        'script', 'style', 'noscript', 'iframe', 'svg',
        'nav', 'header', 'footer', 'aside'
    ]
    for tag in unwanted_tags:
        for element in soup.find_all(tag):
            element.decompose()
    
    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # Remove by common class/id patterns
    noise_patterns = [
        r'nav', r'menu', r'breadcrumb', r'sidebar', r'advertisement',
        r'ad-', r'social', r'share', r'cookie', r'popup', r'modal',
        r'banner', r'promo', r'related', r'comments', r'footer', r'header'
    ]
    
    for pattern in noise_patterns:
        regex = re.compile(pattern, re.I)
        
        # Remove by class
        for element in soup.find_all(class_=regex):
            element.decompose()
        
        # Remove by id
        for element in soup.find_all(id=regex):
            element.decompose()
    
    # Remove hidden elements
    for element in soup.find_all(style=re.compile(r'display\s*:\s*none', re.I)):
        element.decompose()
    
    return soup


def find_main_content(soup):
    """
    Universal main content finder - tries multiple strategies to locate
    the actual program content regardless of university website structure.
    """
    
    # Strategy 1: Semantic HTML5 tags (most reliable)
    for tag in ['main', 'article']:
        content = soup.find(tag)
        if content:
            logger.debug(f"Found content in <{tag}> tag")
            return content
    
    # Strategy 2: Common content container patterns
    content_selectors = [
        # Generic content containers
        {'class': re.compile(r'content|main|primary|page-content', re.I)},
        {'id': re.compile(r'content|main|primary|page-content', re.I)},
        
        # Program-specific containers
        {'class': re.compile(r'program|course|academic|bulletin', re.I)},
        {'id': re.compile(r'program|course|academic|bulletin', re.I)},
        
        # CMS-specific patterns
        {'class': re.compile(r'entry-content|post-content|article-content', re.I)},
        {'id': re.compile(r'entry-content|post-content|article-content', re.I)},
    ]
    
    for selector in content_selectors:
        content = soup.find(['div', 'section', 'article'], selector)
        if content:
            logger.debug(f"Found content with selector: {selector}")
            return content
    
    # Strategy 3: Largest text block heuristic
    # Find the div/section with the most text content
    candidates = soup.find_all(['div', 'section', 'article'])
    if candidates:
        # Score each candidate by text length
        scored = [(elem, len(elem.get_text(strip=True))) for elem in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        if scored and scored[0][1] > 500:  # At least 500 chars
            logger.debug(f"Using largest content block ({scored[0][1]} chars)")
            return scored[0][0]
    
    # Strategy 4: Fall back to body
    logger.warning("Could not find specific content container, using body")
    return soup.find('body') or soup


def extract_universal_content(html_content: str) -> str:
    """
    Universal content extractor that works with any university website.
    Extracts ALL meaningful content from the page.
    """
    if not html_content:
        return ""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Step 1: Remove all unwanted elements
        soup = remove_unwanted_elements(soup)
        
        # Step 2: Find the main content area
        main_content = find_main_content(soup)
        
        if not main_content:
            logger.warning("No content found")
            return ""
        
        # Step 3: Convert to markdown
        markdown = html_to_markdown(main_content)
        
        return markdown
    
    except Exception as e:
        logger.error(f"Error extracting content: {e}")
        return ""


def html_to_markdown(element) -> str:
    """
    Convert HTML element to markdown, preserving ALL content structure.
    """
    if not element:
        return ""
    
    result = []
    
    def process_element(elem, depth=0, in_list=False):
        # Skip if None
        if elem is None:
            return
        
        # Skip comments
        if isinstance(elem, Comment):
            return
        
        # Handle text nodes
        if isinstance(elem, str):
            text = elem.strip()
            if text:
                result.append(text + ' ')
            return
        
        # Get tag name
        tag = elem.name if hasattr(elem, 'name') else None
        
        # Headings (h1-h6)
        if tag and re.match(r'h[1-6]', tag):
            level = int(tag[1])
            text = elem.get_text(strip=True)
            if text:
                result.append('\n\n' + '#' * level + ' ' + text + '\n\n')
            return
        
        # Unordered lists
        if tag == 'ul':
            result.append('\n')
            for li in elem.find_all('li', recursive=False):
                result.append('- ')
                for child in li.children:
                    process_element(child, depth + 1, in_list=True)
                result.append('\n')
            result.append('\n')
            return
        
        # Ordered lists
        if tag == 'ol':
            result.append('\n')
            for idx, li in enumerate(elem.find_all('li', recursive=False), 1):
                result.append(f'{idx}. ')
                for child in li.children:
                    process_element(child, depth + 1, in_list=True)
                result.append('\n')
            result.append('\n')
            return
        
        # Definition lists
        if tag == 'dl':
            result.append('\n')
            for child in elem.children:
                if hasattr(child, 'name'):
                    if child.name == 'dt':
                        result.append('**' + child.get_text(strip=True) + '**\n')
                    elif child.name == 'dd':
                        result.append('  ' + child.get_text(strip=True) + '\n')
            result.append('\n')
            return
        
        # Links
        if tag == 'a':
            text = elem.get_text(strip=True)
            href = elem.get('href', '')
            if text and href and not href.startswith('#'):
                result.append(f'[{text}]({href})')
            elif text:
                result.append(text)
            if not in_list:
                result.append(' ')
            return
        
        # Paragraphs
        if tag == 'p':
            for child in elem.children:
                process_element(child, depth, in_list)
            result.append('\n\n')
            return
        
        # Tables
        if tag == 'table':
            result.append('\n\n')
            headers = []
            rows_data = []
            
            # Extract headers
            thead = elem.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            # Extract rows
            tbody = elem.find('tbody') or elem
            for row in tbody.find_all('tr'):
                cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                if cells:
                    if not headers and row.find('th'):
                        headers = cells
                    else:
                        rows_data.append(cells)
            
            # Format as markdown table
            if headers:
                result.append('| ' + ' | '.join(headers) + ' |\n')
                result.append('| ' + ' | '.join(['---'] * len(headers)) + ' |\n')
            
            for row in rows_data:
                if row:
                    result.append('| ' + ' | '.join(row) + ' |\n')
            
            result.append('\n')
            return
        
        # Line breaks
        if tag == 'br':
            result.append('\n')
            return
        
        # Horizontal rules
        if tag == 'hr':
            result.append('\n---\n')
            return
        
        # Bold/Strong
        if tag in ['strong', 'b']:
            text = elem.get_text(strip=True)
            if text:
                result.append(f'**{text}**')
            if not in_list:
                result.append(' ')
            return
        
        # Italic/Emphasis
        if tag in ['em', 'i']:
            text = elem.get_text(strip=True)
            if text:
                result.append(f'*{text}*')
            if not in_list:
                result.append(' ')
            return
        
        # Code
        if tag == 'code':
            text = elem.get_text(strip=True)
            if text:
                result.append(f'`{text}`')
            return
        
        # Blockquote
        if tag == 'blockquote':
            result.append('\n> ')
            for child in elem.children:
                process_element(child, depth, in_list)
            result.append('\n\n')
            return
        
        # Preformatted text
        if tag == 'pre':
            text = elem.get_text()
            if text:
                result.append('\n```\n' + text + '\n```\n\n')
            return
        
        # Containers - process children
        if tag in ['div', 'section', 'article', 'main', 'span', 'label', 'small']:
            if hasattr(elem, 'children'):
                for child in elem.children:
                    process_element(child, depth, in_list)
            return
        
        # For any other element with children, process them
        if hasattr(elem, 'children'):
            for child in elem.children:
                process_element(child, depth, in_list)
    
    # Start processing
    process_element(element)
    
    # Clean up the result
    text = ''.join(result)
    
    # Normalize whitespace
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n +', '\n', text)
    text = re.sub(r' +\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def clean_program_content(raw_markdown: str, raw_html: str = "") -> str:
    """
    Clean and normalize program content.
    """
    content = ""
    
    # Prefer HTML extraction for better structure preservation
    if raw_html:
        content = extract_universal_content(raw_html)
        logger.debug(f"Extracted from HTML: {len(content)} chars")
    
    # Fallback to markdown if HTML extraction failed or produced little content
    if not content or len(content) < 200:
        content = raw_markdown
        logger.debug(f"Using raw markdown: {len(content)} chars")
    
    if not content:
        return ""
    
    # Normalize Unicode characters
    replacements = {
        '"': '"', '"': '"', "'": "'", "'": "'",
        '–': '-', '—': '-', '…': '...',
        '\u00a0': ' ', '\u200b': '', '\u2022': '-',
        '\u2013': '-', '\u2014': '-',
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # Remove control characters
    content = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', content)
    
    # Normalize line breaks
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()


def sanitize_for_csv(text: str) -> str:
    """Ensure CSV compatibility."""
    if not text:
        return ""
    text = text.replace('\x00', '')
    text = text.replace('\r\n', '\n')
    return text


# ==============================================================================
# WEB FETCHING
# ==============================================================================

async def fetch_url(crawler, url: str, retries=3, base_delay=5):
    """Fetch URL with retry logic."""
    for attempt in range(retries):
        try:
            logger.info(f"Fetching {url} (attempt {attempt + 1})")
            result = await crawler.arun(url=url, config=crawl_config)
            
            if result:
                markdown = result.markdown.strip() if result.markdown else ""
                html = result.html if hasattr(result, 'html') and result.html else ""
                
                if markdown or html:
                    logger.info(f"Success → {url}")
                    logger.debug(f"HTML length: {len(html)}, Markdown length: {len(markdown)}")
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
                    resp = requests.get(url, timeout=20, 
                                      headers={"User-Agent": "Mozilla/5.0"})
                    if resp.ok and "text/html" in resp.headers.get("Content-Type", ""):
                        logger.info(f"Fallback success → {url}")
                        return ("", resp.text)
                except Exception as ex:
                    logger.error(f"Fallback failed: {ex}")
                return ("", "")


def generate_custom_id(prefix):
    """Generate custom ID with prefix."""
    separator = "_"
    prefix_len = len(prefix) + len(separator)
    new_uuid = str(uuid.uuid4())[:36 - prefix_len]
    return f"{prefix}{separator}{new_uuid}"


# ==============================================================================
# MAIN
# ==============================================================================

async def main():
    """Main scraping function."""
    input_path = Path(INPUT_CSV)
    output_path = Path(OUTPUT_CSV)
    
    if not input_path.exists():
        logger.error(f"Input CSV not found: {INPUT_CSV}")
        return
    
    # Read input
    rows = []
    with open(input_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    logger.info(f"Loaded {len(rows)} programs from {INPUT_CSV}")
    
    file_exists = output_path.exists()
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        with open(output_path, 'a' if file_exists else 'w',
                  newline='', encoding='utf-8-sig') as outfile:
            
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
            
            for idx, row in enumerate(rows, 1):
                program_link = row.get("programUrl", "").strip()
                if not program_link:
                    logger.warning(f"Row {idx}: No programUrl, skipping")
                    continue
                
                program_name = row.get("program_name", "unknown")
                uni_name = row.get("university_name", "unknown")
                logger.info(f"[{idx}/{len(rows)}] Processing: {uni_name} — {program_name}")
                
                # Fetch content
                raw_markdown, raw_html = await fetch_url(crawler, program_link)
                
                # Clean content
                cleaned_content = clean_program_content(raw_markdown, raw_html)
                cleaned_content = sanitize_for_csv(cleaned_content)
                
                if cleaned_content:
                    logger.info(f" → Content length: {len(cleaned_content)} chars")
                    sample = cleaned_content[:200].replace('\n', ' ')
                    logger.info(f" → Sample: {sample}...")
                else:
                    logger.warning(f" → No content: {program_link}")
                
                # Sanitize row
                sanitized_row = {k: sanitize_for_csv(v) if isinstance(v, str) else v 
                               for k, v in row.items()}
                
                sanitized_row["program_content"] = cleaned_content
                sanitized_row["id"] = generate_custom_id("arizona")
                
                writer.writerow(sanitized_row)
                batch_count += 1
                
                if batch_count >= 10:
                    outfile.flush()
                    logger.info(" → Saved progress (10 programs)")
                    batch_count = 0
                
                await asyncio.sleep(random.uniform(3, 6))
    
    logger.info(f"\nAll done! {len(rows)} programs processed.")
    logger.info(f"Final output saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    asyncio.run(main())