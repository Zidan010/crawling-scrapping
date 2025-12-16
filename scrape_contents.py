import csv
import asyncio
import logging
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
# Crawl4AI configuration (same as your working reference)
# ----------------------------------------------------------
browser_config = BrowserConfig(
    headless=True,
    verbose=False,                    # Set True for debugging
    java_script_enabled=True,
    text_mode=True
)

crawl_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    scan_full_page=True,
    scroll_delay=2.0,
    page_timeout=120000,
    wait_for_timeout=30,
    excluded_tags=["form", "header", "footer", "nav", "img", "script", "style"],
    exclude_social_media_links=True,
    exclude_external_images=True,
    exclude_external_links=True,
)

# ----------------------------------------------------------
# Input / Output paths
# ----------------------------------------------------------
INPUT_CSV = "extracted_programs_utulsa.csv"               # ← Output from your first script
OUTPUT_CSV = "extracted_programs_with_content_utulsa.csv"   # ← Final CSV with content

# ----------------------------------------------------------
# Fetch with retry + fallback (same as your reference)
# ----------------------------------------------------------
async def fetch_url(crawler, url: str, retries=3, base_delay=5):
    blocked_domains = ["utulsa.edu"]
    if any(domain in url for domain in blocked_domains):
        logger.warning(f"Skipping blocked domain: {url}")
        return ""

    for attempt in range(retries):
        try:
            logger.info(f"Fetching {url} (attempt {attempt + 1})")
            result = await crawler.arun(url=url, config=crawl_config)
            if result and result.markdown:
                logger.info(f"Success → {url}")
                return result.markdown.strip()
            else:
                raise ValueError("No markdown content")
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
                        return resp.text
                except Exception as ex:
                    logger.error(f"Fallback failed: {ex}")
                return ""

# ----------------------------------------------------------
# Main async function
# ----------------------------------------------------------
async def main():
    input_path = Path(INPUT_CSV)
    output_path = Path(OUTPUT_CSV)

    if not input_path.exists():
        logger.error(f"Input CSV not found: {INPUT_CSV}")
        logger.error("Run the first-phase script first to generate program links.")
        return

    # Read all rows first
    rows = []
    with open(input_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    logger.info(f"Loaded {len(rows)} programs from {INPUT_CSV}")

    file_exists = output_path.exists()

    async with AsyncWebCrawler(config=browser_config) as crawler:
        with open(output_path, 'a', newline='', encoding='utf-8') as outfile:
            fieldnames = rows[0].keys()
            if "program_content" not in fieldnames:
                fieldnames = list(fieldnames) + ["program_content"]

            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()

            batch_count = 0

            for idx, row in enumerate(rows, 1):
                program_link = row.get("program_link", "").strip()
                if not program_link:
                    logger.warning(f"Row {idx}: No program_link, skipping")
                    continue

                program_name = row.get("program_name", "unknown")
                uni_name = row.get("university_name", "unknown")

                logger.info(f"[{idx}/{len(rows)}] Processing: {uni_name} — {program_name}")

                # Fetch clean content using Crawl4AI
                content = await fetch_url(crawler, program_link)

                # Add content to row
                row["program_content"] = content

                # Write row
                writer.writerow(row)
                batch_count += 1

                # Save every 10 programs
                if batch_count >= 10:
                    outfile.flush()
                    logger.info("  → Saved progress (10 programs)")
                    batch_count = 0

                # Polite delay
                await asyncio.sleep(random.uniform(2, 5))

    logger.info(f"\nAll done! {len(rows)} programs processed.")
    logger.info(f"Final output saved to: {OUTPUT_CSV}")

# ----------------------------------------------------------
# Entry point
# ----------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())