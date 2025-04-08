"""
Tests for the network and HTML processing functions in crawler_utils.py
"""

import pytest
import requests
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler_utils import (
    fetch_page,
    extract_internal_links,
    extract_page_title,
    clean_text,
    extract_content,
    extract_page_data
)
from tests.fixtures.sample_html import (
    SIMPLE_HTML,
    HTML_WITH_LINKS,
    HTML_NO_TITLE,
    HTML_WITH_ELEMENTS_TO_REMOVE,
    HTML_WITH_BOILERPLATE
)

class TestFetchPage:
    """Tests for the fetch_page function"""
    
    @patch('requests.get')
    def test_fetch_page_success(self, mock_get):
        """Test successful page fetch"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.text = SIMPLE_HTML
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the function
        success, content = fetch_page("https://example.com")
        
        # Assertions
        assert success is True
        assert content == SIMPLE_HTML
        mock_get.assert_called_once_with("https://example.com", timeout=10)
    
    @patch('requests.get')
    def test_fetch_page_connection_error(self, mock_get):
        """Test handling of connection errors"""
        # Setup mock to raise ConnectionError
        mock_get.side_effect = requests.ConnectionError("Connection refused")
        
        # Call the function
        success, error_message = fetch_page("https://example.com")
        
        # Assertions
        assert success is False
        assert "Connection refused" in error_message
        assert "Error fetching https://example.com" in error_message
    
    @patch('requests.get')
    def test_fetch_page_http_error(self, mock_get):
        """Test handling of HTTP errors"""
        # Setup mock to raise HTTPError
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Client Error")
        mock_get.return_value = mock_response
        
        # Call the function
        success, error_message = fetch_page("https://example.com")
        
        # Assertions
        assert success is False
        assert "404 Client Error" in error_message
    
    @patch('requests.get')
    def test_fetch_page_timeout(self, mock_get):
        """Test handling of timeout errors"""
        # Setup mock to raise Timeout
        mock_get.side_effect = requests.Timeout("Request timed out")
        
        # Call the function
        success, error_message = fetch_page("https://example.com")
        
        # Assertions
        assert success is False
        assert "Request timed out" in error_message
        assert "Error fetching https://example.com" in error_message


class TestExtractInternalLinks:
    """Tests for the extract_internal_links function"""
    
    def test_extract_internal_links_basic(self):
        """Test basic extraction of internal links"""
        domain = "sites.google.com/view/metropoleballard"
        url = f"https://{domain}/home"
        
        # Call the function
        links = extract_internal_links(url, HTML_WITH_LINKS, domain)
        
        # Assertions
        assert len(links) == 4  # Only internal links should be extracted
        assert "https://sites.google.com/view/metropoleballard/home" in links
        assert "https://sites.google.com/view/metropoleballard/about" in links
        assert "https://sites.google.com/view/metropoleballard/contact" in links
        assert "https://external-site.com" not in links  # External link should be excluded
    
    def test_extract_internal_links_relative(self):
        """Test extraction of relative links"""
        domain = "sites.google.com/view/metropoleballard"
        url = f"https://{domain}/home"
        
        # Call the function
        links = extract_internal_links(url, HTML_WITH_LINKS, domain)
        
        # Assertions
        assert "https://sites.google.com/view/metropoleballard/resources" in links
    
    def test_extract_internal_links_skip_invalid(self):
        """Test that invalid links are skipped"""
        domain = "sites.google.com/view/metropoleballard"
        url = f"https://{domain}/home"
        
        # Call the function
        links = extract_internal_links(url, HTML_WITH_LINKS, domain)
        
        # Assertions
        # These should be skipped
        for invalid_link in ["javascript:void(0)", "#", "mailto:info@example.com"]:
            assert invalid_link not in links
            assert not any(invalid_link in link for link in links)


class TestExtractPageTitle:
    """Tests for the extract_page_title function"""
    
    def test_extract_title_from_title_tag(self):
        """Test extraction of title from title tag"""
        soup = BeautifulSoup(SIMPLE_HTML, 'lxml')
        title = extract_page_title(soup)
        assert title == "Test Page Title"
    
    def test_extract_title_fallback_to_h1(self):
        """Test fallback to h1 when title tag is missing"""
        soup = BeautifulSoup(HTML_NO_TITLE, 'lxml')
        title = extract_page_title(soup)
        assert title == "Page Heading Only"
    
    def test_extract_title_empty(self):
        """Test handling of empty/missing title and h1"""
        html = "<html><body><p>No title or h1 here</p></body></html>"
        soup = BeautifulSoup(html, 'lxml')
        title = extract_page_title(soup)
        assert title == ""


class TestCleanText:
    """Tests for the clean_text function"""
    
    def test_clean_text_boilerplate_removal(self):
        """Test removal of boilerplate phrases"""
        text = "This is content. Back to Top. Metropole HOA. Copyright."
        cleaned = clean_text(text)
        assert "Back to Top" not in cleaned
        assert "Metropole HOA" not in cleaned
        assert "Copyright" not in cleaned
        assert "This is content" in cleaned
    
    def test_clean_text_whitespace_normalization(self):
        """Test whitespace normalization"""
        text = "Line 1\n\n\nLine 2\n\n\n\nLine 3    with    spaces"
        cleaned = clean_text(text)
        assert "Line 1\n\nLine 2\n\nLine 3 with spaces" == cleaned
    
    def test_clean_text_case_insensitive(self):
        """Test case-insensitive boilerplate removal"""
        text = "This is content. BACK TO TOP. metropole hoa. Copyright."
        cleaned = clean_text(text)
        assert "BACK TO TOP" not in cleaned
        assert "metropole hoa" not in cleaned
        assert "This is content" in cleaned


class TestExtractContent:
    """Tests for the extract_content function"""
    
    def test_extract_content_basic(self):
        """Test basic content extraction"""
        title, content = extract_content(SIMPLE_HTML)
        assert title == "Test Page Title"
        assert "This is a test paragraph with some content" in content
        assert "This is another paragraph with more content" in content
    
    def test_extract_content_remove_elements(self):
        """Test removal of navigation/footer elements"""
        title, content = extract_content(HTML_WITH_ELEMENTS_TO_REMOVE)
        assert title == "Page With Elements To Remove"
        assert "This is the main content that should be kept" in content
        assert "This is a header that should be removed" not in content
        assert "This is navigation that should be removed" not in content
        assert "This is a footer that should be removed" not in content
        assert "This is a sidebar that should be removed" not in content


class TestExtractPageData:
    """Tests for the extract_page_data function"""
    
    def test_extract_page_data(self):
        """Test creation of structured data from HTML content"""
        url = "https://example.com/page"
        page_data = extract_page_data(url, SIMPLE_HTML)
        
        assert page_data["url"] == url
        assert page_data["title"] == "Test Page Title"
        assert "This is a test paragraph with some content" in page_data["content"]
        assert "This is another paragraph with more content" in page_data["content"]
