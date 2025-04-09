#!/usr/bin/env python3
"""
Metropole Webcrawler - A structured webcrawler for the Metropole Ballard website.

This module implements a webcrawler that extracts visible text content
from the Metropole Ballard website, applies text cleanup, and outputs structured data
in JSON format for downstream ingestion by LLM systems.
"""

import os
import json
import datetime
from typing import Dict, List, Any, Set
from crawler_utils import (
    validate_crawled_data,
    crawl_page
)
from logging_utils import (
    setup_crawler_logger,
    log_crawler_start,
    log_crawl_statistics,
    log_output_info,
    log_validation_results,
    log_completion
)

# Constants
BASE_URL = "https://sites.google.com/view/metropoleballard"
DOMAIN = "sites.google.com/view/metropoleballard"
MAX_DEPTH = 1
MAX_RETRIES = 2
RETRY_DELAY = 2  # seconds
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
    
    # Start crawling from the base URL
    try:
        crawl_page(BASE_URL, 0, visited_urls, pages_data, url_visit_count, logger, 
                  MAX_DEPTH, MAX_RETRIES, RETRY_DELAY, DOMAIN)
    except Exception as e:
        logger.error(f"Unexpected error during crawling: {str(e)}")
    
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
    
    # Comprehensive validation of output data
    validation_results = validate_crawled_data(pages_data)
    
    # Log validation results
    log_validation_results(logger, validation_results)
    
    # Log completion
    log_completion(logger, output_json_path, log_file_path)

if __name__ == "__main__":
    print("Starting crawler...")
    run_crawler()
    print("Crawler finished!")
