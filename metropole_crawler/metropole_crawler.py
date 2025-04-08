"""
Metropole Webcrawler - A structured webcrawler for the Metropole Ballard website.

This module implements a webcrawler that extracts visible text content and PDF data
from the Metropole Ballard website, applies text cleanup, and outputs structured data
in JSON format for downstream ingestion by LLM systems.
"""

import os
import json
import time
import random
import datetime
import html2text
import fitz  # PyMuPDF
from tqdm import tqdm
from crawler_utils import fetch_page, extract_internal_links

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
    with open(log_file_path, "w") as log_file:
        log_file.write(f"Metropole Crawler started at: {datetime.datetime.now()}\n")
        log_file.write(f"Starting URL: {BASE_URL}\n")
        log_file.write(f"Max depth: {MAX_DEPTH}\n\n")
    
    print(f"Starting Metropole Crawler...")
    print(f"Base URL: {BASE_URL}")
    print(f"Max depth: {MAX_DEPTH}")
    
    # Initialize data structures
    visited_urls = set()
    pages_data = []
    url_visit_count = {}  # Dictionary to track how many times each URL is visited
    
    def crawl_page(url, depth, visited_urls, pages_data, log_file):
        """
        Recursively crawl pages starting from the given URL up to the specified depth.
        
        Args:
            url (str): URL to crawl
            depth (int): Current depth level
            visited_urls (set): Set of already visited URLs
            pages_data (list): List to store page data
            log_file (file): Log file handle
            
        Returns:
            None
        """
        # Track URL visit attempts (for debugging)
        url_visit_count[url] = url_visit_count.get(url, 0) + 1
        
        # Check if URL has already been visited
        if url in visited_urls:
            log_message = f"  Skipping already visited URL: {url} (attempt #{url_visit_count[url]})"
            print(log_message)
            log_file.write(log_message + "\n")
            return
        
        # Check if we've reached the maximum depth
        if depth > MAX_DEPTH:
            log_message = f"  Skipping URL due to depth limit: {url}"
            print(log_message)
            log_file.write(log_message + "\n")
            return
        
        # Add URL to visited set
        visited_urls.add(url)
        
        # Log the visit
        log_message = f"Visiting URL (depth {depth}): {url} (attempt #{url_visit_count[url]})"
        print(log_message)
        log_file.write(log_message + "\n")
        
        # Fetch the page
        success, content = fetch_page(url)
        if not success:
            log_message = f"  Failed: {content}"
            print(log_message)
            log_file.write(log_message + "\n")
            return
        
        # Extract internal links
        internal_links = extract_internal_links(url, content, DOMAIN)
        log_message = f"  Found {len(internal_links)} internal links"
        print(log_message)
        log_file.write(log_message + "\n")
        
        # Store page data (placeholder for now, will be expanded in step 3)
        page_data = {
            "url": url,
            "title": "",  # Will be extracted in step 3
            "content": ""  # Will be extracted in step 3
        }
        pages_data.append(page_data)
        
        # Recursively crawl internal links
        for link in internal_links:
            # Skip links that have already been visited
            if link in visited_urls:
                log_message = f"  Skipping already visited URL: {link}"
                print(log_message)
                log_file.write(log_message + "\n")
                continue
                
            # Skip links that would exceed the depth limit
            if depth + 1 > MAX_DEPTH:
                log_message = f"  Skipping URL due to depth limit: {link}"
                print(log_message)
                log_file.write(log_message + "\n")
                continue
                
            # Add random delay between requests (1-2 seconds)
            delay = 1 + random.random()
            time.sleep(delay)
            
            # Crawl the link
            crawl_page(link, depth + 1, visited_urls, pages_data, log_file)
    
    # Start crawling from the base URL
    with open(log_file_path, "a") as log_file:
        crawl_page(BASE_URL, 0, visited_urls, pages_data, log_file)
        
        # Log crawl statistics
        log_message = f"\nCrawl Statistics:"
        log_message += f"\n  Total pages visited: {len(visited_urls)}"
        log_message += f"\n  Total pages with data: {len(pages_data)}"
        print(log_message)
        log_file.write(log_message + "\n")
        
        # Log URL visit counts to check for duplicates
        log_message = f"\nURL Visit Attempts:"
        log_file.write(log_message + "\n")
        
        # Find URLs with multiple visit attempts
        multiple_visits = {url: count for url, count in url_visit_count.items() if count > 1}
        if multiple_visits:
            log_message = f"  URLs attempted to be visited multiple times:"
            print(log_message)
            log_file.write(log_message + "\n")
            
            for url, count in sorted(multiple_visits.items(), key=lambda x: x[1], reverse=True):
                log_message = f"    {url}: {count} attempts"
                print(log_message)
                log_file.write(log_message + "\n")
        else:
            log_message = f"  No URLs were attempted to be visited multiple times."
            print(log_message)
            log_file.write(log_message + "\n")
    
    # TODO: Implement content extraction
    
    # TODO: Implement PDF handling
    
    # TODO: Save output to JSON
    
    # TODO: Validate results
    
    # Log completion
    with open(log_file_path, "a") as log_file:
        log_file.write(f"\nMetropole Crawler completed at: {datetime.datetime.now()}\n")
        log_file.write(f"Output saved to: {output_json_path}\n")
    
    print(f"Crawling complete!")
    print(f"Output saved to: {output_json_path}")
    print(f"Log saved to: {log_file_path}")
