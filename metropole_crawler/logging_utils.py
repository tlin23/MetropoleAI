"""
Logging utilities for the Metropole Webcrawler.

This module provides functions for setting up and using a logger
that can write to both a file and the console.
"""

import os
import logging
import datetime
from typing import Dict, List, Set, Optional, Any, Tuple

def setup_crawler_logger(log_file_path: str) -> logging.Logger:
    """
    Set up a logger for the crawler that writes to both a file and the console.
    
    Args:
        log_file_path (str): Path to the log file
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create logger
    logger = logging.getLogger("metropole_crawler")
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers = []
    
    # Create file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter for file handler (with timestamp)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Create simpler formatter for console (without timestamp)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_crawler_start(logger: logging.Logger, base_url: str, max_depth: int) -> None:
    """
    Log crawler start information.
    
    Args:
        logger (logging.Logger): Logger to use
        base_url (str): Starting URL for the crawler
        max_depth (int): Maximum crawl depth
    """
    logger.info(f"Metropole Crawler started at: {datetime.datetime.now()}")
    logger.info(f"Starting URL: {base_url}")
    logger.info(f"Max depth: {max_depth}")
    logger.info("---")

def log_url_visit(logger: logging.Logger, url: str, depth: int, attempt: int) -> None:
    """
    Log a URL visit.
    
    Args:
        logger (logging.Logger): Logger to use
        url (str): URL being visited
        depth (int): Current depth level
        attempt (int): Visit attempt number
    """
    logger.info(f"Visiting URL (depth {depth}): {url} (attempt #{attempt})")

def log_url_skip(logger: logging.Logger, url: str, reason: str, attempt: Optional[int] = None) -> None:
    """
    Log a skipped URL.
    
    Args:
        logger (logging.Logger): Logger to use
        url (str): URL being skipped
        reason (str): Reason for skipping
        attempt (int, optional): Visit attempt number
    """
    if attempt:
        logger.info(f"  Skipping {reason}: {url} (attempt #{attempt})")
    else:
        logger.info(f"  Skipping {reason}: {url}")

def log_fetch_error(logger: logging.Logger, error_message: str) -> None:
    """
    Log a page fetch error.
    
    Args:
        logger (logging.Logger): Logger to use
        error_message (str): Error message
    """
    logger.error(f"  Failed: {error_message}")

def log_extraction_results(logger: logging.Logger, title: str, content: str) -> None:
    """
    Log extraction results.
    
    Args:
        logger (logging.Logger): Logger to use
        title (str): Extracted title
        content (str): Extracted content
    """
    logger.info(f"  Extracted title: '{title}'")
    
    content_preview = content[:100] + "..." if len(content) > 100 else content
    logger.info(f"  Content preview: {content_preview}")

def log_links_found(logger: logging.Logger, count: int) -> None:
    """
    Log number of internal links found.
    
    Args:
        logger (logging.Logger): Logger to use
        count (int): Number of links found
    """
    logger.info(f"  Found {count} internal links")

def log_crawl_statistics(
    logger: logging.Logger, 
    visited_urls: Set[str], 
    pages_data: List[Dict[str, Any]], 
    url_visit_count: Dict[str, int]
) -> None:
    """
    Log crawl statistics.
    
    Args:
        logger (logging.Logger): Logger to use
        visited_urls (set): Set of visited URLs
        pages_data (list): List of page data dictionaries
        url_visit_count (dict): Dictionary of URL visit counts
    """
    # Log basic statistics
    logger.info("\n" + "="*50)
    logger.info("Crawl Statistics:")
    logger.info(f"  Total pages visited: {len(visited_urls)}")
    logger.info(f"  Total pages with data: {len(pages_data)}")
    
    # Log URL visit counts to check for duplicates
    logger.info("\nURL Visit Attempts:")
    
    # Find URLs with multiple visit attempts
    multiple_visits = {url: count for url, count in url_visit_count.items() if count > 1}
    if multiple_visits:
        logger.info("  URLs attempted to be visited multiple times:")
        
        for url, count in sorted(multiple_visits.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"    {url}: {count} attempts")
    else:
        logger.info("  No URLs were attempted to be visited multiple times.")
    
    logger.info("="*50)

def log_output_info(
    logger: logging.Logger, 
    output_path: str, 
    metadata: Dict[str, Any]
) -> None:
    """
    Log output information.
    
    Args:
        logger (logging.Logger): Logger to use
        output_path (str): Path to the output file
        metadata (dict): Output metadata
    """
    logger.info("Formatting output with metadata structure...")
    logger.info(f"Metadata: {metadata}")
    logger.info(f"Number of pages: {metadata['total_pages']}")
    logger.info(f"Saved formatted output to {output_path}")

def log_validation_results(
    logger: logging.Logger, 
    validation_results: Dict[str, Any]
) -> None:
    """
    Log validation results.
    
    Args:
        logger (logging.Logger): Logger to use
        validation_results (dict): Validation results dictionary
    """
    logger.info("\nOutput Validation Results:")
    
    # Log summary statistics
    logger.info(f"  Total pages: {validation_results['total_pages']}")
    logger.info(f"  Valid pages: {validation_results['valid_pages']}/{validation_results['total_pages']} ({(validation_results['valid_pages']/validation_results['total_pages']*100) if validation_results['total_pages'] > 0 else 0:.1f}%)")
    logger.info(f"  Problematic pages: {validation_results['problematic_pages']}/{validation_results['total_pages']} ({(validation_results['problematic_pages']/validation_results['total_pages']*100) if validation_results['total_pages'] > 0 else 0:.1f}%)")
    
    # Log field presence statistics
    if 'pages_with_url' in validation_results:
        logger.info(f"  Pages with URL: {validation_results['pages_with_url']}/{validation_results['total_pages']}")
    logger.info(f"  Pages with title: {validation_results['pages_with_title']}/{validation_results['total_pages']}")
    logger.info(f"  Pages with content: {validation_results['pages_with_content']}/{validation_results['total_pages']}")
    
    # Log missing URLs
    if 'missing_url' in validation_results and validation_results["missing_url"]:
        logger.warning(f"  Pages with missing URLs: {len(validation_results['missing_url'])}")
        for url in validation_results["missing_url"]:
            logger.warning(f"    - {url}")
    
    # Log malformed URLs
    if 'malformed_urls' in validation_results and validation_results["malformed_urls"]:
        logger.warning(f"  Pages with malformed URLs: {len(validation_results['malformed_urls'])}")
        for url in validation_results["malformed_urls"]:
            logger.warning(f"    - {url}")
    
    # Log empty titles
    if validation_results["empty_titles"]:
        logger.warning(f"  Pages with empty titles: {len(validation_results['empty_titles'])}")
        for url in validation_results["empty_titles"]:
            logger.warning(f"    - {url}")
    
    # Log empty content
    if validation_results["empty_content"]:
        logger.warning(f"  Pages with empty content: {len(validation_results['empty_content'])}")
        for url in validation_results["empty_content"]:
            logger.warning(f"    - {url}")
    
    # Log short content (warning, not error)
    if 'short_content' in validation_results and validation_results["short_content"]:
        logger.warning(f"  Pages with suspiciously short content: {len(validation_results['short_content'])}")
        for url_info in validation_results["short_content"]:
            url, length = url_info
            logger.warning(f"    - {url} ({length} characters)")

def log_completion(
    logger: logging.Logger, 
    output_path: str, 
    log_path: str
) -> None:
    """
    Log crawler completion.
    
    Args:
        logger (logging.Logger): Logger to use
        output_path (str): Path to the output file
        log_path (str): Path to the log file
    """
    logger.info("\n" + "="*50)
    logger.info(f"Metropole Crawler completed at: {datetime.datetime.now()}")
    logger.info(f"Output saved to: {output_path}")
    logger.info(f"Log saved to: {log_path}")
    logger.info("="*50)
    logger.info("Crawling complete!")
