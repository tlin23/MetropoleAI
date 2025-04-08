"""
Utility functions for the Metropole Webcrawler.

This module contains helper functions for fetching pages, extracting links,
and other utilities used by the main crawler.
"""

import requests
from bs4 import BeautifulSoup

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
