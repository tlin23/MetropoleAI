"""
Utility functions for the Metropole Webcrawler.

This module contains helper functions for fetching pages, extracting links,
content extraction, text cleaning, and other utilities used by the main crawler.
"""

import requests
import html2text
import re
import time
import random
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Set, Tuple, Optional
from logging_utils import (
    log_url_skip,
    log_url_visit,
    log_fetch_error,
    log_links_found,
    log_extraction_results
)

def fetch_page(url, timeout=10):
    """
    Fetch a webpage and return its HTML content.
    
    Args:
        url (str): URL to fetch
        timeout (int): Request timeout in seconds
        
    Returns:
        tuple: (success, html_content or error_message)
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return True, response.text
    except requests.RequestException as e:
        return False, f"Error fetching {url}: {str(e)}"

def extract_internal_links(url, html_content, domain):
    """
    Extract all internal links from the HTML content.
    
    Args:
        url (str): Current page URL
        html_content (str): HTML content of the page
        domain (str): Domain to restrict links to
        
    Returns:
        list: List of internal links
    """
    soup = BeautifulSoup(html_content, 'lxml')
    internal_links = []
    base_domain = "https://" + domain
    
    # Find all links in the page
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        
        # Skip invalid links
        if (not href or href.startswith('javascript:') or href == '#' or 
            href.startswith('mailto:') or href.startswith('tel:')):
            continue
        
        # Special handling for Google Sites relative URLs
        if href.startswith(f'/view/{domain.split("/")[2]}/'):
            # Extract the path after /view/domain-name/
            path = href.replace(f'/view/{domain.split("/")[2]}/', '')
            full_url = f"{base_domain}/{path}"
        elif href.startswith('/'):
            # Other relative URLs
            full_url = base_domain + href
        elif not href.startswith('http'):
            # For other relative paths, join with the current URL's directory
            base_path = '/'.join(url.split('/')[:-1]) + '/'
            full_url = base_path + href
        else:
            full_url = href
        
        # Only include links within our domain
        if domain in full_url:
            # Normalize URL
            normalized_url = full_url.split('#')[0].rstrip('/')
            
            # Skip problematic URLs
            if ('mailto:' in normalized_url or 
                f'/view/{domain.split("/")[2]}/view/{domain.split("/")[2]}/' in normalized_url):
                continue
            
            internal_links.append(normalized_url)
    
    # Remove duplicates and return
    return list(set(internal_links))

def extract_page_title(soup):
    """
    Extract the page title from HTML content.
    Prefers <title> tag, falls back to first <h1> tag.
    
    Args:
        soup (BeautifulSoup): Parsed HTML content
        
    Returns:
        str: Page title or empty string if not found
    """
    # # Try to get the title from the <title> tag
    # if soup.title and soup.title.string:
    #     return soup.title.string.strip()
    
    # Fall back to the first <h1> tag
    if soup.h1 and soup.h1.get_text():
        return soup.h1.get_text().strip()
    
    # If no title found, return empty string
    return ""

def clean_text(text):
    """
    Clean extracted text by removing excessive whitespace, 
    empty lines, and common boilerplate content.
    
    Args:
        text (str): Raw extracted text
        
    Returns:
        str: Cleaned text
    """
    # Remove common boilerplate phrases
    boilerplate = [
        "Back to Top",
        "Back to Home",
        "Metropole HOA",
        "Metropole Ballard",
        "Copyright",
        "All Rights Reserved",
        "Privacy Policy",
        "Terms of Service",
        "Contact Us",
        "Sign In",
        "Sign Out",
        "Log In",
        "Log Out",
        "Search this site",
        "Embedded Files",
        "Skip to main content",
        "Skip to navigation",
        "Google Sites",  
        "Report abuse",
        "Page details",  
        "Page updated",  
        "Google Sites",  
        "Report abuse"
    ]
    
    # Replace each boilerplate phrase with an empty string
    for phrase in boilerplate:
        text = re.sub(r'\b' + re.escape(phrase) + r'\b', '', text, flags=re.IGNORECASE)
    
    # Remove excessive whitespace and empty lines
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Replace multiple empty lines with a single empty line
    text = re.sub(r'[ \t]+', ' ', text)      # Replace multiple spaces/tabs with a single space
    text = text.strip()                       # Remove leading/trailing whitespace
    
    return text

def extract_content(html_content):
    """
    Extract and clean visible text content from HTML.
    
    Args:
        html_content (str): HTML content of the page
        
    Returns:
        tuple: (title, cleaned_content)
    """
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Extract title
    title = extract_page_title(soup)
    
    # Remove navigation, footer, and other non-content elements
    for element in soup.select('nav, footer, header, .navigation, .footer, .header, .menu, .sidebar'):
        element.decompose()
    
    # Convert HTML to plain text using html2text
    h2t = html2text.HTML2Text()
    h2t.ignore_links = True  # Keep links in the text, but format them as Markdown
    h2t.ignore_images = True  # Ignore images
    h2t.ignore_tables = True # Keep tables
    h2t.body_width = 0        # Don't wrap text
    
    content = h2t.handle(str(soup))
    
    # Clean the extracted text
    cleaned_content = clean_text(content)
    
    return title, cleaned_content


def extract_page_data(url, html_content):
    """
    Extract structured data from a webpage.
    
    Args:
        url (str): URL of the page
        html_content (str): HTML content of the page
        
    Returns:
        dict: Structured page data with url, title, and content
    """
    # Extract title and content
    title, content = extract_content(html_content)
    
    # Create structured data object
    page_data = {
        "url": url,
        "title": title,
        "content": content
    }
    
    return page_data


def validate_crawled_data(pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate the crawled data for completeness and quality.
    
    Args:
        pages_data (List[Dict[str, Any]]): List of page data dictionaries
        
    Returns:
        Dict[str, Any]: Validation results
    """
    total_pages = len(pages_data)
    valid_pages = 0
    problematic_pages = 0
    
    # Initialize validation result structure
    validation_results = {
        "total_pages": total_pages,
        "valid_pages": 0,
        "problematic_pages": 0,
        "pages_with_url": 0,
        "pages_with_title": 0,
        "pages_with_content": 0,
        "missing_url": [],
        "empty_titles": [],
        "empty_content": [],
        "short_content": [],
        "malformed_urls": []
    }
    
    # URL validation regex pattern
    url_pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*$')
    
    # Validate each page
    for page in pages_data:
        page_valid = True
        
        # Check URL
        if "url" not in page or not page["url"]:
            validation_results["missing_url"].append("Unknown URL (missing field)")
            page_valid = False
        else:
            validation_results["pages_with_url"] += 1
            # Check if URL is well-formed
            if not url_pattern.match(page["url"]):
                validation_results["malformed_urls"].append(page["url"])
                page_valid = False
        
        # Check title
        if "title" not in page or not page["title"]:
            url = page.get("url", "Unknown URL")
            validation_results["empty_titles"].append(url)
            page_valid = False
        else:
            validation_results["pages_with_title"] += 1
        
        # Check content
        if "content" not in page or not page["content"]:
            url = page.get("url", "Unknown URL")
            validation_results["empty_content"].append(url)
            page_valid = False
        else:
            validation_results["pages_with_content"] += 1
            # Check content length (less than 100 chars might indicate poor extraction)
            if len(page["content"]) < 100:
                url = page.get("url", "Unknown URL")
                validation_results["short_content"].append((url, len(page["content"])))
                # Short content is a warning, not an error
        
        # Update valid/problematic counts
        if page_valid:
            valid_pages += 1
        else:
            problematic_pages += 1
    
    # Update summary counts
    validation_results["valid_pages"] = valid_pages
    validation_results["problematic_pages"] = problematic_pages
    
    return validation_results


def crawl_page(url: str, depth: int, visited_urls: Set[str], pages_data: List[Dict[str, Any]], 
               url_visit_count: Dict[str, int], logger: Any, 
               max_depth: int = 2, max_retries: int = 2, retry_delay: int = 2, domain: str = None) -> None:
    """
    Recursively crawl pages starting from the given URL up to the specified depth.
    
    Args:
        url (str): URL to crawl
        depth (int): Current depth level
        visited_urls (set): Set of already visited URLs
        pages_data (list): List to store page data
        url_visit_count (dict): Dictionary to track URL visit attempts
        logger (logging.Logger): Logger instance
        max_depth (int, optional): Maximum crawl depth. Defaults to 2.
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 2.
        retry_delay (int, optional): Base delay between retries in seconds. Defaults to 2.
        domain (str, optional): Domain to restrict links to. Required for internal link extraction.
        
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
    if depth > max_depth:
        log_url_skip(logger, url, "URL due to depth limit")
        return
    
    # Add URL to visited set
    visited_urls.add(url)
    
    # Log the visit
    log_url_visit(logger, url, depth, url_visit_count[url])
    
    # Fetch the page with retries
    success = False
    content = None
    retries = 0
    
    while not success and retries <= max_retries:
        if retries > 0:
            # Add exponential backoff delay for retries
            backoff_delay = retry_delay * (2 ** (retries - 1))
            logger.info(f"  Retry #{retries} after {backoff_delay}s delay...")
            time.sleep(backoff_delay)
            
        success, content = fetch_page(url)
        
        if not success:
            retries += 1
            if retries <= max_retries:
                logger.warning(f"  Fetch failed: {content}. Retrying...")
            else:
                log_fetch_error(logger, f"{content} (after {max_retries} retries)")
                return
    
    # Extract internal links
    internal_links = extract_internal_links(url, content, domain)
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
        if depth + 1 > max_depth:
            log_url_skip(logger, link, "URL due to depth limit")
            continue
            
        # Add random delay between requests (1-2 seconds)
        delay = 1 + random.random()
        time.sleep(delay)
        
        # Crawl the link
        crawl_page(link, depth + 1, visited_urls, pages_data, url_visit_count, logger, 
                  max_depth, max_retries, retry_delay, domain)
