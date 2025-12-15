

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
# ----------------------------------------------------------
# Logging setup
# ----------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------
# Constant field definitions
# ----------------------------------------------------------
PROGRAM_DETAILS_FIELDS = [
    "program_overview", "start_at", "end_at", "course_outline", "admission_timeline",
    "tuition_fee_per_year", "application_fee", "how_to_apply",
    "general_requirement", "standardized_requirement", "language_requirement",
    "degree_requirement", "scholarship_requirement", "scholarship_detail"
]

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
    page_timeout=120000,  # ⏱ Increase timeout to 120s
    wait_for_timeout=30,  # ⏱ Increase timeout to 120s
    excluded_tags=["form", "header", "footer", "nav", "img"],
    exclude_social_media_links=True,
    exclude_external_images=True,
    exclude_external_links=True,
)

# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------
def clean_filename(text: str) -> str:
    """Sanitize text for safe filename use."""
    text = text.strip()
    text = re.sub(r'[\\/*?:"<>|\r\n]+', "", text)
    text = re.sub(r"\s+", "_", text)
    return text[:150]  # limit length to avoid path overflow


def load_csv_data(csv_file):
    """Load program data from CSV file."""
    programs = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                programs.append(row)
        logger.info(f"Loaded {len(programs)} programs from {csv_file}")
        return programs
    except FileNotFoundError:
        logger.error(f"CSV file {csv_file} not found")
        return []
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_file}: {str(e)}")
        return []


def get_unique_urls_and_fields(program):
    """Extract unique URLs and map them to fields from program data."""
    url_fields = {}
    for field in PROGRAM_DETAILS_FIELDS:
        if field in program and program[field]:
            urls = [url.strip().strip('"\'') for url in program[field].split(",") if url.strip()]
            for url in urls:
                if url not in url_fields:
                    url_fields[url] = []
                if field not in url_fields[url]:
                    url_fields[url].append(field)
    return url_fields


# ----------------------------------------------------------
# Fetch logic with retry + fallback
# ----------------------------------------------------------
async def fetch_url(crawler, url, config, retries=3, base_delay=5):
    """Fetch a URL with retry, exponential backoff, and fallback."""
    # Skip known blocked domains
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
                wait_time = base_delay * (attempt + 1)
                logger.info(f"Retrying {url} after {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logger.warning(f"⛔ Fetch failed after {retries} attempts, trying fallback...")
                # Try fallback requests.get
                try:
                    resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
                    if resp.ok and "text/html" in resp.headers.get("Content-Type", ""):
                        logger.info(f"✅ Fallback fetch succeeded for {url}")
                        return SimpleNamespace(markdown=resp.text)
                    else:
                        logger.warning(f"❌ Fallback fetch returned non-HTML or bad status for {url}")
                except Exception as ex:
                    logger.error(f"Fallback fetch failed for {url}: {str(ex)}")
                return None


# ----------------------------------------------------------
# Main async function
# ----------------------------------------------------------
async def main():
    csv_file = r"../crawling-scrapping/input_test.csv"
    output_dir = Path(r"../crawling-scrapping/prev_crawled")
    output_dir.mkdir(parents=True, exist_ok=True)

    programs = load_csv_data(csv_file)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for program in programs:
            predefined_data = {field: program.get(field, "") for field in PREDEFINED_FIELDS}

            program_name = clean_filename(predefined_data.get("program_name", "unknown_program"))
            uni_name = clean_filename(predefined_data.get("university_name", "unknown_university"))

            url_fields = get_unique_urls_and_fields(program)
            logger.info(f"📘 Processing program: {program_name} with {len(url_fields)} URLs")

            program_details = []
            for url, fields in url_fields.items():
                await asyncio.sleep(random.uniform(3, 8))  # ⏳ Random delay between fetches

                result = await fetch_url(crawler, url, crawl_config)
                if result and result.markdown:
                    program_details.append({
                        "url": url,
                        "fields": fields,
                        "content": result.markdown
                    })
                    logger.info(f"Stored content for {url} → {fields}")
                else:
                    program_details.append({
                        "url": url,
                        "fields": fields,
                        "content": ""
                    })
                    logger.warning(f"⚠️ Empty or failed content for {url}")

            # Ensure all fields represented
            scraped_fields = {f for entry in program_details for f in entry["fields"]}
            for field in PROGRAM_DETAILS_FIELDS:
                if field not in scraped_fields:
                    program_details.append({
                        "url": "",
                        "fields": [field],
                        "content": ""
                    })

            output_data = {**predefined_data, "program_details": program_details}

            js_file = output_dir / f"{uni_name}_{program_name}_scraped.json"
            with open(js_file, 'w', encoding='utf-8') as file:
                json.dump(output_data, file, indent=4, ensure_ascii=False)
            logger.info(f"💾 Saved scraped data for {program_name} → {js_file}")


# ----------------------------------------------------------
# Entry point
# ----------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
