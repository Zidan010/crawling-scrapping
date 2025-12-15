
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
    exclude_external_links=False,  # To capture all links initially
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

# ----------------------------------------------------------
# Fetch logic with retry + fallback
# ----------------------------------------------------------
async def fetch_url(crawler, url: str, config, retries=3, base_delay=5):
    blocked_domains = ["utulsa.edu"]
    if any(domain in url for domain in blocked_domains):
        logger.warning(f"⚠️ Skipping likely blocked domain: {url}")
        return None

    for attempt in range(retries):
        try:
            logger.info(f"Attempt {attempt + 1} for URL: {url}")
            result = await crawler.arun(url=url, config=config)

            if result and result.markdown:
                logger.info(f"✅ Successfully fetched {url}")
                return result
            else:
                raise ValueError("No content retrieved from URL")

        except Exception as e:
            logger.error(f"Error fetching {url} on attempt {attempt + 1}: {str(e)}")
            if attempt < retries - 1:
                wait_time = base_delay * (2 ** attempt)
                logger.info(f"Retrying {url} after {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logger.warning(f"⛔ Fetch failed after {retries} attempts, trying fallback...")
                try:
                    resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
                    if resp.ok and "text/html" in resp.headers.get("Content-Type", ""):
                        logger.info(f"✅ Fallback fetch succeeded for {url}")
                        return SimpleNamespace(markdown=resp.text, links={"internal": [], "external": []})
                except Exception as ex:
                    logger.error(f"Fallback fetch failed for {url}: {str(ex)}")
                return None

async def extract_links(result, base_url: str, visited: set) -> list:
    if not result:
        return []
    internal_links_list = result.links.get("internal", [])
    links_raw = list(set(
        normalize_url(link.get("href", ""), base_url)
        for link in internal_links_list
        if link.get("href")
    ))
    links_filtered = [
        link for link in links_raw
        if link.startswith(('http://', 'https://'))
        and is_same_domain(base_url, link)
        and link != base_url
        and link not in visited
    ]
    return links_filtered

# ----------------------------------------------------------
# Main async function
# ----------------------------------------------------------
async def main():
    csv_file = r"../crawling-scrapping/input_test.csv"
    output_dir = Path(r"../crawling-scrapping/latest_crawled_l2")
    output_dir.mkdir(parents=True, exist_ok=True)

    programs = load_csv_data(csv_file)
    if not programs:
        logger.error("No programs to process. Exiting.")
        return

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for idx, program in enumerate(programs, 1):
            logger.info(f"Processing program {idx}/{len(programs)}")

            predefined_data = {field: program.get(field, "") for field in PREDEFINED_FIELDS}

            program_url = predefined_data.get("program_url", "").strip()
            if not program_url:
                logger.warning("Skipping row with empty program_url")
                continue

            program_name = clean_filename(predefined_data.get("program_name", "unknown_program"))
            uni_name = clean_filename(predefined_data.get("university_name", "unknown_university"))

            # Track all unique URLs and their keys
            associated_links = {}  # {"url_1": "https://...", ...}
            program_details = {}   # {"main": "...", "url_1": "...", ...}
            link_hierarchy = {"main": []}  # {"main": ["url_1", "url_2"], "url_1": ["url_3", ...], ...}
            visited = set([program_url])   # To avoid duplicates and cycles

            # Fetch main program page
            main_result = await fetch_url(crawler, program_url, crawl_config)
            if main_result and main_result.markdown:
                program_details["main"] = main_result.markdown
                level1_links = await extract_links(main_result, program_url, visited)
                logger.info(f"Found {len(level1_links)} level 1 links for {program_url}")
            else:
                program_details["main"] = ""
                level1_links = []
                logger.warning(f"⚠️ Failed to fetch main program page: {program_url}")

            # Process level 1
            url_counter = 1
            level2_queue = {}  # Temp: {"url_1": [sublinks], ...}
            for link in level1_links:
                key = f"url_{url_counter}"
                associated_links[key] = link
                link_hierarchy["main"].append(key)
                link_hierarchy[key] = []  # Init for potential children
                visited.add(link)

                await asyncio.sleep(random.uniform(3, 8))
                result = await fetch_url(crawler, link, crawl_config)
                content = result.markdown if result and result.markdown else ""
                program_details[key] = content
                status = "✅" if content else "⚠️"
                logger.info(f"{status} Stored level 1 content for {key} → {link}")

                # Extract level 2 links
                sub_links = await extract_links(result, link, visited)
                level2_queue[key] = sub_links
                logger.info(f"Found {len(sub_links)} level 2 links from {key}")

                url_counter += 1

            # Process level 2
            for parent_key, sub_links in level2_queue.items():
                for sub_link in sub_links:
                    key = f"url_{url_counter}"
                    associated_links[key] = sub_link
                    link_hierarchy[parent_key].append(key)
                    visited.add(sub_link)

                    await asyncio.sleep(random.uniform(3, 8))
                    result = await fetch_url(crawler, sub_link, crawl_config)
                    content = result.markdown if result and result.markdown else ""
                    program_details[key] = content
                    status = "✅" if content else "⚠️"
                    logger.info(f"{status} Stored level 2 content for {key} → {sub_link} (from {parent_key})")

                    url_counter += 1

            # Final output
            output_data = {
                **predefined_data,
                "associated_links": associated_links,      # All links: {"url_1": "https://...", ...}
                "link_hierarchy": link_hierarchy,          # Mapping: {"main": ["url_1", ...], "url_1": ["url_3", ...], ...}
                "program_details": program_details         # All contents: {"main": "...", "url_1": "...", ...}
            }

            js_file = output_dir / f"{uni_name}_{program_name}_scraped.json"
            with open(js_file, 'w', encoding='utf-8') as file:
                json.dump(output_data, file, indent=4, ensure_ascii=False)
            logger.info(f"💾 Saved scraped data → {js_file}")

            if idx < len(programs):
                await asyncio.sleep(random.uniform(5, 10))

# ----------------------------------------------------------
# Entry point
# ----------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())