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
from bs4 import BeautifulSoup
from crawler_utils import (
    fetch_page, 
    extract_internal_links, 
    extract_page_data, 
    extract_pdf_text
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
    pdf_stats = {
        "total_detected": 0,
        "requires_download": 0,
        "extraction_attempted": 0,
        "extraction_succeeded": 0,
        "extraction_failed": 0
    }
    
    def crawl_page(url, depth, visited_urls, pages_data, pdf_stats, log_file):
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
        
        # Extract and store page data
        page_data = extract_page_data(url, content)
        
        # Log extraction results
        log_message = f"  Extracted title: '{page_data['title']}'"
        print(log_message)
        log_file.write(log_message + "\n")
        
        content_preview = page_data['content'][:100] + "..." if len(page_data['content']) > 100 else page_data['content']
        log_message = f"  Content preview: {content_preview}"
        print(log_message)
        log_file.write(log_message + "\n")
        
        # Process PDF links
        pdf_links = page_data.pop('pdf_links', [])  # Remove from page_data and get the list
        if pdf_links:
            pdf_stats["total_detected"] += len(pdf_links)
            log_message = f"  Found {len(pdf_links)} PDF links on page"
            print(log_message)
            log_file.write(log_message + "\n")
            
            # Process each PDF link
            for pdf_link in pdf_links:
                pdf_url = pdf_link['url']
                pdf_text = pdf_link['text']
                
                if pdf_link['requires_download']:
                    pdf_stats["requires_download"] += 1
                    log_message = f"  Skipping PDF that requires download: {pdf_text} ({pdf_url})"
                    print(log_message)
                    log_file.write(log_message + "\n")
                    continue
                
                # Try to extract text from the PDF
                log_message = f"  Attempting to extract text from PDF: {pdf_text} ({pdf_url})"
                print(log_message)
                log_file.write(log_message + "\n")
                
                pdf_stats["extraction_attempted"] += 1
                success, pdf_content = extract_pdf_text(pdf_url)
                
                if success:
                    pdf_stats["extraction_succeeded"] += 1
                    # Add PDF text to page data
                    if "pdf_text" not in page_data:
                        page_data["pdf_text"] = {}
                    
                    page_data["pdf_text"][pdf_url] = {
                        "title": pdf_text,
                        "content": pdf_content
                    }
                    
                    pdf_preview = pdf_content[:100] + "..." if len(pdf_content) > 100 else pdf_content
                    log_message = f"  Successfully extracted PDF text. Preview: {pdf_preview}"
                    print(log_message)
                    log_file.write(log_message + "\n")
                else:
                    pdf_stats["extraction_failed"] += 1
                    log_message = f"  Failed to extract PDF text: {pdf_content}"
                    print(log_message)
                    log_file.write(log_message + "\n")
        
        # Add the processed page data to our collection
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
            crawl_page(link, depth + 1, visited_urls, pages_data, pdf_stats, log_file)
    
    # Start crawling from the base URL
    with open(log_file_path, "a") as log_file:
        crawl_page(BASE_URL, 0, visited_urls, pages_data, pdf_stats, log_file)
        
        # Log crawl statistics
        log_message = f"\nCrawl Statistics:"
        log_message += f"\n  Total pages visited: {len(visited_urls)}"
        log_message += f"\n  Total pages with data: {len(pages_data)}"
        log_message += f"\n  Total PDF links detected: {pdf_stats['total_detected']}"
        log_message += f"\n  PDFs requiring download (skipped): {pdf_stats['requires_download']}"
        log_message += f"\n  PDF text extraction attempts: {pdf_stats['extraction_attempted']}"
        log_message += f"\n  Successful PDF extractions: {pdf_stats['extraction_succeeded']}"
        log_message += f"\n  Failed PDF extractions: {pdf_stats['extraction_failed']}"
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
    
    # Content extraction has been implemented ✓
    # PDF handling has been implemented ✓
    
    # Save output to JSON
    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(pages_data, json_file, indent=2, ensure_ascii=False)
    
    # TODO: Validate results
    
    # Log completion
    with open(log_file_path, "a") as log_file:
        log_file.write(f"\nMetropole Crawler completed at: {datetime.datetime.now()}\n")
        log_file.write(f"Output saved to: {output_json_path}\n")
        log_file.write(f"Total pages extracted: {len(pages_data)}\n")
    
    print(f"Crawling complete!")
    print(f"Output saved to: {output_json_path}")
    print(f"Log saved to: {log_file_path}")
