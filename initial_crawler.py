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
    exclude_external_links=False,  # Needed to capture all links
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
    return text

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

# ----------------------------------------------------------
# Main async function
# ----------------------------------------------------------
async def main():
    csv_file = r"crawling-scrapping/input_test.csv"
    output_dir = Path(r"crawling-scrapping/latest_crawled")
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

            # Fetch main program page
            main_result = await fetch_url(crawler, program_url, crawl_config)
            if main_result and main_result.markdown:
                main_content = main_result.markdown

                # Extract unique internal associated links
                internal_links_list = main_result.links.get("internal", [])
                associated_links_raw = list(set(
                    normalize_url(link.get("href", ""), program_url)
                    for link in internal_links_list
                    if link.get("href")
                ))
                associated_links_raw = [
                    link for link in associated_links_raw
                    if link.startswith(('http://', 'https://'))
                    and is_same_domain(program_url, link)
                    and link != program_url
                ]
                associated_links = {f"url_{i}": link for i, link in enumerate(associated_links_raw, 1)}
                logger.info(f"Found {len(associated_links)} unique associated internal links for {program_url}")
            else:
                main_content = ""
                associated_links = {}
                logger.warning(f"⚠️ Failed to fetch main program page: {program_url}")

            # Initialize program_details as dict: "main" + "url_1", "url_2", ...
            program_details = {"main": main_content}

            # Crawl each associated link and store content under matching key
            for key, url in associated_links.items():
                await asyncio.sleep(random.uniform(3, 8))
                result = await fetch_url(crawler, url, crawl_config)
                content = result.markdown if result and result.markdown else ""
                program_details[key] = content
                status = "✅" if content else "⚠️"
                logger.info(f"{status} Stored content for {key} → {url}")

            # Final output
            output_data = {
                **predefined_data,
                "associated_links": associated_links,      # {"url_1": "https://...", ...}
                "program_details": program_details         # {"main": "...", "url_1": "...", "url_2": "..."}
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