"""
Utility functions for the Metropole Webcrawler.

This module contains helper functions for fetching pages, extracting links,
content extraction, text cleaning, and other utilities used by the main crawler.
"""

import requests
import html2text
import re
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

def extract_page_title(soup):
    """
    Extract the page title from HTML content.
    Prefers <title> tag, falls back to first <h1> tag.
    
    Args:
        soup (BeautifulSoup): Parsed HTML content
        
    Returns:
        str: Page title or empty string if not found
    """
    # Try to get the title from the <title> tag
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    
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
        "Log Out"
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
    h2t.ignore_links = False  # Keep links in the text, but format them as Markdown
    h2t.ignore_images = True  # Ignore images
    h2t.ignore_tables = False # Keep tables
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
