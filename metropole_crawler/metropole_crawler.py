"""
Metropole Webcrawler - A structured webcrawler for the Metropole Ballard website.

This module implements a webcrawler that extracts visible text content
from the Metropole Ballard website, applies text cleanup, and outputs structured data
in JSON format for downstream ingestion by LLM systems.
"""

import os
import json
import time
import random
import datetime
import html2text
from tqdm import tqdm
from bs4 import BeautifulSoup
from crawler_utils import (
    fetch_page, 
    extract_internal_links, 
    extract_page_data
)
from logging_utils import (
    setup_crawler_logger,
    log_crawler_start,
    log_url_visit,
    log_url_skip,
    log_fetch_error,
    log_extraction_results,
    log_links_found,
    log_crawl_statistics,
    log_output_info,
    log_validation_results,
    log_completion
)

# Constants
BASE_URL = "https://sites.google.com/view/metropoleballard/home"
DOMAIN = "sites.google.com/view/metropoleballard"
MAX_DEPTH = 2
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def run_crawler() -> None:
    """
    Crawls Metropole Ballard website (depth 2), extracts content,
    saves structured text output to JSON file in /data,
    and writes a crawl log file with validation results.
    """
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Generate timestamp for filenames
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_json_path = os.path.join(DATA_DIR, f"metropole_site_data_{timestamp}.json")
    log_file_path = os.path.join(DATA_DIR, f"crawl_log_{timestamp}.txt")
    
    # Initialize logging
    logger = setup_crawler_logger(log_file_path)
    log_crawler_start(logger, BASE_URL, MAX_DEPTH)
    
    # Initialize data structures
    visited_urls = set()
    pages_data = []
    url_visit_count = {}  # Dictionary to track how many times each URL is visited
    
    def crawl_page(url, depth, visited_urls, pages_data):
        """
        Recursively crawl pages starting from the given URL up to the specified depth.
        
        Args:
            url (str): URL to crawl
            depth (int): Current depth level
            visited_urls (set): Set of already visited URLs
            pages_data (list): List to store page data
            
        Returns:
            None
        """
        # Track URL visit attempts (for debugging)
        url_visit_count[url] = url_visit_count.get(url, 0) + 1
        
        # Check if URL has already been visited
        if url in visited_urls:
            log_url_skip(logger, url, "already visited URL", url_visit_count[url])
            return
        
        # Check if we've reached the maximum depth
        if depth > MAX_DEPTH:
            log_url_skip(logger, url, "URL due to depth limit")
            return
        
        # Add URL to visited set
        visited_urls.add(url)
        
        # Log the visit
        log_url_visit(logger, url, depth, url_visit_count[url])
        
        # Fetch the page
        success, content = fetch_page(url)
        if not success:
            log_fetch_error(logger, content)
            return
        
        # Extract internal links
        internal_links = extract_internal_links(url, content, DOMAIN)
        log_links_found(logger, len(internal_links))
        
        # Extract and store page data
        page_data = extract_page_data(url, content)
        
        # Log extraction results
        log_extraction_results(logger, page_data['title'], page_data['content'])
        
        # Remove PDF links from page data if present
        if 'pdf_links' in page_data:
            page_data.pop('pdf_links')
        
        # Add the processed page data to our collection
        pages_data.append(page_data)
        
        # Recursively crawl internal links
        for link in internal_links:
            # Skip links that have already been visited
            if link in visited_urls:
                log_url_skip(logger, link, "already visited URL")
                continue
                
            # Skip links that would exceed the depth limit
            if depth + 1 > MAX_DEPTH:
                log_url_skip(logger, link, "URL due to depth limit")
                continue
                
            # Add random delay between requests (1-2 seconds)
            delay = 1 + random.random()
            time.sleep(delay)
            
            # Crawl the link
            crawl_page(link, depth + 1, visited_urls, pages_data)
    
    # Start crawling from the base URL
    crawl_page(BASE_URL, 0, visited_urls, pages_data)
    
    # Log crawl statistics
    log_crawl_statistics(logger, visited_urls, pages_data, url_visit_count)
    
    # Format and enrich output data
    formatted_output = {
        "metadata": {
            "crawl_date": datetime.datetime.now().isoformat(),
            "base_url": BASE_URL,
            "max_depth": MAX_DEPTH,
            "total_pages": len(pages_data),
            "version": "1.0"
        },
        "pages": pages_data
    }
    
    # Save output to JSON
    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(formatted_output, json_file, indent=2, ensure_ascii=False)
    
    # Log output information
    log_output_info(logger, output_json_path, formatted_output["metadata"])
    
    # Basic validation of output data
    validation_results = {
        "total_pages": len(pages_data),
        "pages_with_title": sum(1 for page in pages_data if page.get("title")),
        "pages_with_content": sum(1 for page in pages_data if page.get("content")),
        "empty_titles": [page["url"] for page in pages_data if not page.get("title")],
        "empty_content": [page["url"] for page in pages_data if not page.get("content")]
    }
    
    # Log validation results
    log_validation_results(logger, validation_results)
    
    # Log completion
    log_completion(logger, output_json_path, log_file_path)
