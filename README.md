# Crawling-Scrapping Workflow

This project provides multiple methods for web content extraction and link crawling, supporting various levels of depth and content retrieval strategies.

## Workflow Overview

### 1. `prev_scrape.py`
- **Purpose:** Link-wise content extraction. For each provided link, the script extracts the content directly associated with that link.
- **Usage:** Use this script when you want to extract content from a list of links, processing each link individually.

### 2. `initial_crawler.py`
- **Purpose:** Single-link extraction with Layer 1 crawling. Starts from one link, extracts its content, and then extracts content from all directly linked (Layer 1) pages.
- **Usage:** Use this script to extract content from a starting link and all its immediate (Layer 1) linked pages.

### 3. `initial_crawler_l2.py`
- **Purpose:** Single-link extraction with Layer 1 and Layer 2 crawling. Starts from one link, extracts its content, then extracts content from all Layer 1 and Layer 2 linked pages.
- **Usage:** Use this script to extract content from a starting link, its Layer 1 links, and all Layer 2 links found from Layer 1 pages.

### 4. `crawl_links.py`
- **Purpose:** Single-link link-only crawling up to Layer 2. Starts from one link, extracts its content, and collects all Layer 1 and Layer 2 links (without extracting their content).
- **Usage:** Use this script to gather all links up to Layer 2 from a starting link, extracting content only from the initial link.

## Output Folders

- `latest_crawled/`
- `latest_crawled_l2/`
- `link_crawled/`
- `prev_crawled/`

## Requirements

Install dependencies using:
```bash
pip install -r requirements.txt