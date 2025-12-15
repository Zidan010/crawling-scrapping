import json
import asyncio
import logging
import csv
import random
import re
from pathlib import Path
from types import SimpleNamespace
import requests
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from urllib.parse import urlparse, urljoin

# ----------------------------------------------------------
# Logging setup
# ----------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------
# Constant field definitions
# ----------------------------------------------------------
PREDEFINED_FIELDS = [
    "university_name", "university_email", "university_rank", "university_url",
    "university_phone", "university_address", "university_campus",
    "department_url", "department_name", "program_url", "program_type",
    "degree_program", "program_name", "delivery_type", "session", "duration",
    "scholarship", "useful_links"
]

# ----------------------------------------------------------
# Browser and crawler configuration
# ----------------------------------------------------------
browser_config = BrowserConfig(
    headless=True,
    verbose=True,
    java_script_enabled=True,
    text_mode=True
)

crawl_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    scan_full_page=True,
    scroll_delay=2.0,
    page_timeout=120000,
    wait_for_timeout=30,
    excluded_tags=["form", "header", "footer", "nav", "img"],
    exclude_social_media_links=True,
    exclude_external_images=True,
    exclude_external_links=False,  # Need to capture all links
)

# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------
def clean_filename(text: str) -> str:
    if not text:
        return "unknown"
    text = text.strip()
    text = re.sub(r'[\\/*?:"<>|\r\n]+', "", text)
    text = re.sub(r"\s+", "_", text)
    return text[:150]

def is_same_domain(base_url: str, check_url: str) -> bool:
    base_netloc = urlparse(base_url).netloc
    check_netloc = urlparse(check_url).netloc
    return base_netloc == check_netloc

def normalize_url(url: str, base_url: str) -> str:
    return urljoin(base_url, url.strip())

def load_csv_data(csv_file: str):
    programs = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get("program_url", "").strip():
                    programs.append(row)
        logger.info(f"Loaded {len(programs)} programs with valid program_url from {csv_file}")
        return programs
    except FileNotFoundError:
        logger.error(f"CSV file {csv_file} not found")
        return []
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_file}: {str(e)}")
        return []

async def extract_internal_links(result, base_url: str, visited: set) -> list:
    """Extract unique internal links not yet visited."""
    if not result:
        return []
    internal_links_list = result.links.get("internal", [])
    raw_links = {
        normalize_url(link.get("href", ""), base_url)
        for link in internal_links_list
        if link.get("href")
    }
    filtered = [
        link for link in raw_links
        if link.startswith(('http://', 'https://'))
        and is_same_domain(base_url, link)
        and link != base_url
        and link not in visited
    ]
    return filtered

# ----------------------------------------------------------
# Fetch logic (only for pages we need content + links from)
# ----------------------------------------------------------
async def fetch_url(crawler, url: str, config, retries=3, base_delay=5):
    blocked_domains = ["utulsa.edu"]
    if any(domain in url for domain in blocked_domains):
        logger.warning(f"⚠️ Skipping blocked domain: {url}")
        return None

    for attempt in range(retries):
        try:
            logger.info(f"Fetching {url} (attempt {attempt + 1})")
            result = await crawler.arun(url=url, config=config)
            if result and result.markdown:
                logger.info(f"✅ Successfully fetched {url}")
                return result
        except Exception as e:
            logger.error(f"Error on {url}: {str(e)}")
            if attempt < retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt))
    logger.warning(f"⚠️ Failed to fetch {url} after retries")
    return None

# ----------------------------------------------------------
# Main async function
# ----------------------------------------------------------
async def main():
    csv_file = r"../crawling-scrapping/input_test.csv"
    output_dir = Path(r"../crawling-scrapping/link_crawled")
    output_dir.mkdir(parents=True, exist_ok=True)

    programs = load_csv_data(csv_file)
    if not programs:
        logger.error("No programs to process.")
        return

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for idx, program in enumerate(programs, 1):
            logger.info(f"\n=== Processing program {idx}/{len(programs)} ===")

            predefined_data = {field: program.get(field, "") for field in PREDEFINED_FIELDS}
            program_url = predefined_data.get("program_url", "").strip()
            if not program_url:
                logger.warning("Skipping empty program_url")
                continue

            program_name = clean_filename(predefined_data.get("program_name", "unknown_program"))
            uni_name = clean_filename(predefined_data.get("university_name", "unknown_university"))

            # Structures to store results
            associated_links = {}      # {"url_1": "https://...", ...}
            link_hierarchy = {"main": []}  # parent → [child_keys]
            visited = {program_url}    # Track all seen URLs for uniqueness

            # 1. Fetch main program page (content + layer 1 links)
            main_result = await fetch_url(crawler, program_url, crawl_config)
            main_content = main_result.markdown if main_result and main_result.markdown else ""
            logger.info(f"Main page content length: {len(main_content)} characters")

            # 2. Extract Layer 1 links
            layer1_links = await extract_internal_links(main_result, program_url, visited)
            logger.info(f"Found {len(layer1_links)} unique Layer 1 links")

            url_counter = 1

            # Process each Layer 1 page (we need their links for Layer 2)
            for l1_url in layer1_links:
                key = f"url_{url_counter}"
                associated_links[key] = l1_url
                link_hierarchy["main"].append(key)
                link_hierarchy[key] = []  # prepare for possible Layer 2 children
                visited.add(l1_url)

                await asyncio.sleep(random.uniform(3, 8))

                l1_result = await fetch_url(crawler, l1_url, crawl_config)
                if l1_result:
                    # Extract Layer 2 links from this page
                    layer2_links = await extract_internal_links(l1_result, l1_url, visited)
                    logger.info(f"From {key}: found {len(layer2_links)} unique Layer 2 links")

                    for l2_url in layer2_links:
                        l2_key = f"url_{url_counter + 1}"
                        associated_links[l2_key] = l2_url
                        link_hierarchy[key].append(l2_key)
                        visited.add(l2_url)
                        url_counter += 1

                url_counter += 1  # for next Layer 1

            # Final output: only main content + all links + hierarchy
            output_data = {
                **predefined_data,
                "main_content": main_content,
                "associated_links": associated_links,        # all unique links with keys
                "link_hierarchy": link_hierarchy            # clear parent-child mapping
            }

            js_file = output_dir / f"{uni_name}_{program_name}_links_only.json"
            with open(js_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=4, ensure_ascii=False)

            logger.info(f"💾 Saved links-only data → {js_file}")
            logger.info(f"Total unique links collected: {len(associated_links)}\n")

            if idx < len(programs):
                await asyncio.sleep(random.uniform(6, 12))

# ----------------------------------------------------------
# Entry point
# ----------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())