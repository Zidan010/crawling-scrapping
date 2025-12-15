# import json
# import asyncio
# import logging
# import csv
# import random
# import re
# from pathlib import Path
# from collections import deque, defaultdict
# from types import SimpleNamespace
# import requests
# from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
# from urllib.parse import urlparse, urljoin

# # ----------------------------------------------------------
# # Logging setup
# # ----------------------------------------------------------
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # # ----------------------------------------------------------
# # # Browser and crawler configuration
# # # ----------------------------------------------------------
# # browser_config = BrowserConfig(
# #     headless=True,
# #     verbose=False,
# #     java_script_enabled=True,
# #     text_mode=True
# # )

# # crawl_config = CrawlerRunConfig(
# #     cache_mode=CacheMode.BYPASS,
# #     scan_full_page=True,
# #     scroll_delay=2.0,
# #     page_timeout=120000,
# #     wait_for_timeout=30,
# #     excluded_tags=["form", "header", "footer", "nav", "img"],
# #     exclude_social_media_links=True,
# #     exclude_external_images=True,
# #     exclude_external_links=False,
# # )

# PREDEFINED_FIELDS = [
#     "university_name", "university_email", "university_rank", "university_url",
#     "university_phone", "university_address", "university_campus",
#     "department_url", "department_name", "program_url", "program_type",
#     "degree_program", "program_name", "delivery_type", "session", "duration",
#     "scholarship", "useful_links"
# ]

# browser_config = BrowserConfig(
#     headless=True,
#     verbose=True,  # Debug: See browser actions
#     java_script_enabled=True,
#     text_mode=False,  # Keep full for better link detection
#     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# )

# # Custom JS: Expand all accordions + scroll slowly + optional pagination
# expand_and_scroll_js = """
# async () => {
#     // Expand all Bootstrap accordions/collapses
#     document.querySelectorAll('[data-bs-toggle="collapse"], [data-toggle="collapse"]').forEach(btn => {
#         if (btn.getAttribute('aria-expanded') === 'false' || !btn.classList.contains('collapsed')) {
#             btn.click();
#         }
#     });
    
#     // Alternative for older Bootstrap
#     document.querySelectorAll('.accordion-button.collapsed').forEach(btn => btn.click());
    
#     // Slow scroll to bottom to trigger lazy loading
#     let scrollHeight = document.body.scrollHeight;
#     let current = 0;
#     const step = 500;
#     while (current < scrollHeight) {
#         window.scrollBy(0, step);
#         current += step;
#         await new Promise(r => setTimeout(r, 500));
#         scrollHeight = Math.max(scrollHeight, document.body.scrollHeight);
#     }
    
#     // Wait extra for any final loads
#     await new Promise(r => setTimeout(r, 8000));
    
#     // Optional: Click pagination "Next" up to 20 times if exists
#     for (let i = 0; i < 20; i++) {
#         const nextBtn = document.querySelector('a[rel="next"], .pagination .next a, button:contains("Next"), a:contains("Next")');
#         if (nextBtn && !nextBtn.disabled) {
#             nextBtn.click();
#             await new Promise(r => setTimeout(r, 5000));  // Wait for new page load
#         } else {
#             break;
#         }
#     }
# }
# """

# crawl_config = CrawlerRunConfig(
#     cache_mode=CacheMode.BYPASS,
#     scan_full_page=True,
#     scroll_delay=4.0,
#     page_timeout=240000,  # 4 min
#     wait_for_timeout=90,
#     excluded_tags=["form", "script", "style", "img"],  # Minimal exclusions
#     exclude_social_media_links=True,
#     exclude_external_images=True,
#     exclude_external_links=False,
#     js_code=expand_and_scroll_js  # Critical for nested accordions/pagination
# )

# # ----------------------------------------------------------
# # Helpers (unchanged)
# # ----------------------------------------------------------
# def clean_filename(text: str) -> str:
#     if not text:
#         return "unknown"
#     text = text.strip()
#     text = re.sub(r'[\\/*?:"<>|\r\n]+', "", text)
#     text = re.sub(r"\s+", "_", text)
#     return text[:150]

# def get_domain(url: str) -> str:
#     return urlparse(url).netloc

# def is_same_domain(base_url: str, check_url: str) -> bool:
#     return get_domain(base_url) == get_domain(check_url)

# def normalize_url(url: str, base_url: str) -> str:
#     normalized = urljoin(base_url, url.strip())
#     return normalized.split('#')[0]

# def get_section_from_url(url: str) -> str:
#     path = urlparse(url).path.strip('/').split('/')[0] if urlparse(url).path.strip('/') else 'root'
#     return path if path else 'other'

# def load_csv_data(csv_file: str):
#     programs = []
#     try:
#         with open(csv_file, 'r', encoding='utf-8') as file:
#             reader = csv.DictReader(file)
#             for row in reader:
#                 base_url = row.get("university_url", "").strip()
#                 if base_url:
#                     programs.append({**row, "base_url": base_url})
#         logger.info(f"Loaded {len(programs)} entries with base_url")
#         return programs
#     except Exception as e:
#         logger.error(f"Error reading CSV: {str(e)}")
#         return []

# async def extract_internal_links(result, current_url: str, visited: set, key_map: dict) -> list:
#     if not result or not hasattr(result, "links"):
#         return []
#     internal_links = result.links.get("internal", [])
#     logger.info(f"Raw internal links on {current_url}: {len(internal_links)}")
#     raw_links = {normalize_url(link.get("href", ""), current_url) for link in internal_links if link.get("href")}
#     filtered = [
#         link for link in raw_links
#         if link.startswith(('http://', 'https://'))
#         and is_same_domain(current_url, link)
#         and link not in visited
#     ]
#     return filtered

# # ----------------------------------------------------------
# # Fetch (force browser, more retries)
# # ----------------------------------------------------------
# async def fetch_url(crawler, url: str, config, retries=5, base_delay=10):
#     blocked_domains = ["utulsa.edu"]
#     if any(domain in url for domain in blocked_domains):
#         return None

#     for attempt in range(retries):
#         try:
#             logger.info(f"Browser fetch attempt {attempt+1} for {url}")
#             result = await crawler.arun(url=url, config=config)
#             if result and result.markdown:
#                 logger.info(f"Success: {url} → {len(result.links.get('internal', []))} raw internal links")
#                 return result
#         except Exception as e:
#             logger.error(f"Error on {url} (attempt {attempt+1}): {str(e)}")
#             if attempt < retries - 1:
#                 await asyncio.sleep(base_delay * (2 ** attempt))
#     logger.warning(f"Failed {url} after {retries} attempts")
#     return None

# # ----------------------------------------------------------
# # Full sitemap generation with graph connectivity and sections
# # ----------------------------------------------------------
# async def generate_full_sitemap(crawler, base_url: str, max_pages: int = 1500):
#     domain = get_domain(base_url)
#     logger.info(f"Starting FULL sitemap crawl for {base_url} (domain: {domain})")

#     visited = set()
#     url_map = {}  # key: url
#     key_map = {}  # url: key (for quick lookup)
#     connectivity_graph = defaultdict(list)  # parent_key: [child_keys]
#     queue = deque()

#     # Initialize root
#     root_key = "root"
#     url_map[root_key] = base_url
#     key_map[base_url] = root_key
#     visited.add(base_url)
#     queue.append(base_url)

#     pages_crawled = 0
#     new_links_found = True

#     while queue and pages_crawled < max_pages and new_links_found:
#         current_url = queue.popleft()
#         current_key = key_map[current_url]
#         pages_crawled += 1

#         await asyncio.sleep(random.uniform(2, 6))

#         result = await fetch_url(crawler, current_url, crawl_config)
#         if not result:
#             continue

#         child_links = await extract_internal_links(result, current_url, visited, key_map)
#         new_links_found = False

#         logger.info(f"[{pages_crawled}/{len(url_map)}] {current_url} → {len(child_links)} internal links found (including possibles duplicates)")

#         for link in child_links:
#             if len(url_map) >= max_pages:
#                 logger.warning("Reached max_pages limit")
#                 break

#             if link not in visited:
#                 new_links_found = True
#                 child_key = f"url_{len(url_map)}"
#                 url_map[child_key] = link
#                 key_map[link] = child_key
#                 visited.add(link)
#                 queue.append(link)

#             # Add connection even if already visited (full graph)
#             child_key = key_map[link]
#             if child_key not in connectivity_graph[current_key]:
#                 connectivity_graph[current_key].append(child_key)
#                 logger.debug(f"Added connection: {current_key} -> {child_key}")

#     # Post-process sections
#     sections = defaultdict(list)
#     for key, url in url_map.items():
#         section = get_section_from_url(url)
#         sections[section].append(key)

#     total_discovered = len(url_map)
#     logger.info(f"Sitemap complete: {total_discovered} unique pages for {domain}")

#     return {
#         "base_url": base_url,
#         "domain": domain,
#         "total_pages_discovered": total_discovered,
#         "pages_crawled": pages_crawled,
#         "url_map": url_map,
#         "connectivity_graph": dict(connectivity_graph),  # parent -> children
#         "sections": dict(sections)  # section -> [keys]
#     }

# # ----------------------------------------------------------
# # Main
# # ----------------------------------------------------------
# async def main():
#     csv_file = r"../crawling-scrapping/input_test.csv"
#     output_dir = Path(r"../crawling-scrapping/sitemaps_full")
#     output_dir.mkdir(parents=True, exist_ok=True)

#     entries = load_csv_data(csv_file)
#     if not entries:
#         logger.error("No entries to process")
#         return

#     async with AsyncWebCrawler(config=browser_config) as crawler:
#         for idx, entry in enumerate(entries, 1):
#             logger.info(f"\n=== [{idx}/{len(entries)}] Processing {entry.get('university_name', 'Unknown University')} ===")

#             base_url = entry.get("university_url", "").strip()
#             if not base_url:
#                 logger.warning("No university_url — skipping")
#                 continue

#             uni_name = clean_filename(entry.get("university_name", "unknown_university"))

#             sitemap_data = await generate_full_sitemap(
#                 crawler,
#                 base_url,
#                 max_pages=1500
#             )

#             output_data = {
#                 **{k: entry.get(k, "") for k in PREDEFINED_FIELDS},
#                 "sitemap": sitemap_data
#             }

#             json_file = output_dir / f"{uni_name}_full_sitemap.json"
#             with open(json_file, 'w', encoding='utf-8') as f:
#                 json.dump(output_data, f, indent=4, ensure_ascii=False)

#             logger.info(f"💾 Full sitemap saved → {json_file}")
#             logger.info(f"   → {sitemap_data['total_pages_discovered']} unique URLs, {len(sitemap_data['sections'])} sections\n")

#             if idx < len(entries):
#                 await asyncio.sleep(random.uniform(15, 30))

# # ----------------------------------------------------------
# # Entry point
# # ----------------------------------------------------------
# if __name__ == "__main__":
#     asyncio.run(main())






import json
import asyncio
import logging
import csv
import random
import re
from pathlib import Path
from collections import deque, defaultdict
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from urllib.parse import urlparse, urljoin

# ----------------------------------------------------------
# Logging setup
# ----------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------
# Browser and crawler configuration
# ----------------------------------------------------------
browser_config = BrowserConfig(
    headless=True,
    verbose=True,  # Keep True while testing
    java_script_enabled=True,
    text_mode=False,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# General-purpose JS: expand accordions, click pagination, scroll
custom_js = """
async () => {
    // Expand all common accordion/collapse elements
    document.querySelectorAll('.accordion-button.collapsed, [data-bs-toggle="collapse"], [data-toggle="collapse"], details:not([open]) > summary').forEach(el => {
        el.click();
    });
    await new Promise(r => setTimeout(r, 5000));

    // Try to handle pagination (common patterns)
    const nextSelectors = [
        'a[rel="next"]',
        '.pagination .next a',
        '.pager-next a',
        'a:contains("Next")',
        'button:contains("Next")',
        '.next-page a'
    ];
    for (const selector of nextSelectors) {
        const btn = document.querySelector(selector);
        if (btn && btn.offsetParent !== null && !btn.disabled) {
            btn.scrollIntoView({behavior: "smooth", block: "center"});
            btn.click();
            await new Promise(r => setTimeout(r, 8000));
            // Re-expand after new content loads
            document.querySelectorAll('.accordion-button.collapsed, [data-bs-toggle="collapse"]').forEach(el => el.click());
            await new Promise(r => setTimeout(r, 3000));
        }
    }

    // Slow scroll to trigger lazy loading
    let height = document.body.scrollHeight;
    let pos = 0;
    const step = 500;
    while (pos < height) {
        window.scrollBy(0, step);
        pos += step;
        await new Promise(r => setTimeout(r, 800));
        height = Math.max(height, document.body.scrollHeight);
    }

    // Final wait for any remaining loads
    await new Promise(r => setTimeout(r, 10000));
}
"""

crawl_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    scan_full_page=True,
    scroll_delay=4.0,
    page_timeout=300000,   # 5 minutes
    wait_for_timeout=120,
    excluded_tags=["script", "style"],
    exclude_social_media_links=True,
    exclude_external_images=True,
    exclude_external_links=False,
    js_code=custom_js
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

def get_domain(url: str) -> str:
    return urlparse(url).netloc

def is_same_domain(base_url: str, check_url: str) -> bool:
    return get_domain(base_url) == get_domain(check_url)

def normalize_url(url: str, base_url: str) -> str:
    normalized = urljoin(base_url, url.strip())
    return normalized.split('#')[0].rstrip('/')

def get_section_from_url(url: str) -> str:
    path = urlparse(url).path.strip('/').split('/', 1)[0] if urlparse(url).path.strip('/') else 'root'
    return path if path else 'other'

def load_csv_data(csv_file: str):
    entries = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                base_url = row.get("university_url", "").strip()  # ← Correct column name
                uni_name = row.get("university_name", "unknown").strip()
                if base_url:
                    entries.append({"base_url": base_url, "uni_name": uni_name})
        logger.info(f"Loaded {len(entries)} entries from CSV")
        return entries
    except Exception as e:
        logger.error(f"Error reading CSV: {str(e)}")
        return []

async def extract_internal_links(result, current_url: str, visited: set) -> list:
    if not result or not hasattr(result, "links"):
        return []
    internal_links = result.links.get("internal", [])
    logger.info(f"Raw internal links on {current_url}: {len(internal_links)}")
    raw_links = {normalize_url(link.get("href", ""), current_url) for link in internal_links if link.get("href")}
    filtered = [
        link for link in raw_links
        if link.startswith(('http://', 'https://'))
        and is_same_domain(current_url, link)
    ]
    logger.info(f"Filtered internal links (potential new): {len(filtered)}")
    return filtered

# ----------------------------------------------------------
# Fetch logic
# ----------------------------------------------------------
async def fetch_url(crawler, url: str, config, retries=5, base_delay=10):
    blocked_domains = ["utulsa.edu"]
    if any(domain in url for domain in blocked_domains):
        logger.warning(f"Skipping blocked domain: {url}")
        return None

    for attempt in range(retries):
        try:
            logger.info(f"Browser fetch attempt {attempt+1} → {url}")
            result = await crawler.arun(url=url, config=config)
            if result and result.markdown:
                logger.info(f"SUCCESS → {url} | {len(result.links.get('internal', []))} raw internal links")
                return result
        except Exception as e:
            logger.error(f"Error fetching {url} (attempt {attempt+1}): {str(e)}")
            if attempt < retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt))
    logger.warning(f"FAILED to fetch {url} after {retries} attempts")
    return None

# ----------------------------------------------------------
# Sitemap generation
# ----------------------------------------------------------
async def generate_full_sitemap(crawler, base_url: str, max_pages: int = 3000):
    domain = get_domain(base_url)
    logger.info(f"Starting full sitemap crawl for {base_url} (domain: {domain})")

    visited = set()
    url_map = {}
    key_map = {}
    connectivity_graph = defaultdict(list)
    queue = deque()

    # Root
    root_key = "root"
    url_map[root_key] = base_url
    key_map[base_url] = root_key
    visited.add(base_url)
    queue.append(base_url)

    pages_crawled = 0

    while queue and len(url_map) < max_pages:
        current_url = queue.popleft()
        current_key = key_map[current_url]
        pages_crawled += 1

        await asyncio.sleep(random.uniform(2, 6))

        result = await fetch_url(crawler, current_url, crawl_config)
        if not result:
            continue

        child_links = await extract_internal_links(result, current_url, visited)

        logger.info(f"[{pages_crawled}/{len(url_map)}] {current_url} → {len(child_links)} potential new links")

        for link in child_links:
            if len(url_map) >= max_pages:
                logger.warning("Max pages limit reached")
                break

            if link not in visited:
                child_key = f"url_{len(url_map)}"
                url_map[child_key] = link
                key_map[link] = child_key
                visited.add(link)
                queue.append(link)

            # Record connection (full graph)
            child_key = key_map[link]
            if child_key not in connectivity_graph[current_key]:
                connectivity_graph[current_key].append(child_key)

    # Sections
    sections = defaultdict(list)
    for key, url in url_map.items():
        sections[get_section_from_url(url)].append(key)

    total = len(url_map)
    logger.info(f"Sitemap complete: {total} unique pages discovered")

    return {
        "base_url": base_url,
        "domain": domain,
        "total_pages_discovered": total,
        "pages_crawled": pages_crawled,
        "url_map": url_map,
        "connectivity_graph": dict(connectivity_graph),
        "sections": dict(sections)
    }

# ----------------------------------------------------------
# Main
# ----------------------------------------------------------
async def main():
    csv_file = r"/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/input_test.csv"
    output_dir = Path(r"/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/sitemaps_full")
    output_dir.mkdir(parents=True, exist_ok=True)

    entries = load_csv_data(csv_file)
    if not entries:
        logger.error("No valid entries found in CSV")
        return

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for idx, entry in enumerate(entries, 1):
            logger.info(f"\n=== [{idx}/{len(entries)}] Processing {entry['uni_name']} ===")
            base_url = entry["base_url"]
            uni_name = clean_filename(entry["uni_name"])

            sitemap_data = await generate_full_sitemap(crawler, base_url, max_pages=3000)

            json_path = output_dir / f"{uni_name}_full_sitemap.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(sitemap_data, f, indent=4, ensure_ascii=False)

            logger.info(f"Saved sitemap → {json_path}")
            logger.info(f"Discovered {sitemap_data['total_pages_discovered']} unique URLs\n")

            if idx < len(entries):
                await asyncio.sleep(random.uniform(15, 30))

if __name__ == "__main__":
    asyncio.run(main())