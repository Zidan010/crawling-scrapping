import csv
import json
import re
import requests
from pathlib import Path
from urllib.parse import urlparse, urljoin
from xml.etree import ElementTree as ET
from collections import defaultdict

# ----------------------------- CONFIG -----------------------------
CSV_FILE_PATH = "../crawling-scrapping/input_test.csv"  # Change to your CSV path
OUTPUT_DIR = Path("sitemaps_from_xml")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Extensions to exclude
EXCLUDE_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp',
    '.mp3', '.mp4', '.avi', '.zip', '.tar', '.gz',
    '.xml', '.txt', '.csv'
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SitemapScraper/1.0)"
}
# ------------------------------------------------------------------

def clean_university_name(name: str) -> str:
    """Clean name for safe filename"""
    return re.sub(r'[\\/*?:"<>|]', "_", name.strip())

def get_section_from_url(url: str) -> str:
    """Extract first path segment as section name"""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return "extra"
    first_segment = path.split("/")[0]
    return first_segment if first_segment else "extra"

def process_university(university_name: str, base_url: str):
    base_url = base_url.rstrip("/")
    sitemap_url = f"{base_url}/sitemap.xml"

    print(f"Fetching sitemap: {sitemap_url}")

    try:
        response = requests.get(sitemap_url, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            print(f"  → No sitemap.xml (status {response.status_code})")
            return {
                "university_name": university_name,
                "base_url": base_url,
                "sitemap_url": sitemap_url,
                "status": "no_sitemap",
                "total_urls": 0,
                "sections": {}
            }

        # Parse XML
        root = ET.fromstring(response.content)
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        urls = []
        # Handle both <url><loc> and nested sitemaps <sitemap><loc>
        for loc_elem in root.findall('.//sm:loc', ns):
            url = loc_elem.text.strip() if loc_elem.text else None
            if url:
                # Basic validation
                if any(url.lower().endswith(ext) for ext in EXCLUDE_EXTENSIONS):
                    continue
                if url.lower().startswith(('http://', 'https://')):
                    urls.append(url)

        # Deduplicate while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        # Group by section
        sections = defaultdict(list)
        for url in unique_urls:
            section = get_section_from_url(url)
            sections[section].append(url)

        # Sort sections and URLs for consistent output
        sorted_sections = {k: sorted(v) for k, v in sorted(sections.items())}

        result = {
            "university_name": university_name,
            "base_url": base_url,
            "sitemap_url": sitemap_url,
            "status": "success",
            "total_urls": len(unique_urls),
            "sections": sorted_sections
        }

        print(f"  → Found {len(unique_urls)} valid URLs in {len(sorted_sections)} sections")
        return result

    except ET.ParseError:
        print("  → Invalid XML in sitemap")
        return {
            "university_name": university_name,
            "base_url": base_url,
            "sitemap_url": sitemap_url,
            "status": "invalid_xml",
            "total_urls": 0,
            "sections": {}
        }
    except Exception as e:
        print(f"  → Error: {str(e)}")
        return {
            "university_name": university_name,
            "base_url": base_url,
            "sitemap_url": sitemap_url,
            "status": "error",
            "error": str(e),
            "total_urls": 0,
            "sections": {}
        }

# ----------------------------- MAIN -----------------------------
def main():
    if not Path(CSV_FILE_PATH).exists():
        print(f"CSV file not found: {CSV_FILE_PATH}")
        return

    universities = []
    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            uni_name = row.get("university_name", "").strip()
            base_url = row.get("university_url", "").strip()
            if base_url:
                universities.append((uni_name or "Unknown", base_url))

    print(f"Loaded {len(universities)} universities from CSV\n")

    for uni_name, base_url in universities:
        data = process_university(uni_name, base_url)

        filename_safe = clean_university_name(uni_name or "unknown_university")
        output_file = OUTPUT_DIR / f"{filename_safe}_sitemap.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Saved → {output_file}\n")

if __name__ == "__main__":
    main()