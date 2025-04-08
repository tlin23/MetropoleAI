"""
Tests for the crawling logic in crawler_utils.py
"""

import pytest
import logging
from unittest.mock import patch, MagicMock, call
from typing import Dict, List, Set, Any

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler_utils import (
    crawl_page,
    validate_crawled_data
)
from tests.fixtures.sample_html import (
    SIMPLE_HTML,
    HTML_WITH_LINKS,
    HTML_CIRCULAR_REF_1,
    HTML_CIRCULAR_REF_2
)

class TestCrawlPage:
    """Tests for the crawl_page function"""
    
    @patch('crawler_utils.fetch_page')
    @patch('crawler_utils.extract_internal_links')
    @patch('crawler_utils.extract_page_data')
    @patch('crawler_utils.log_url_visit')
    @patch('crawler_utils.log_links_found')
    @patch('crawler_utils.log_extraction_results')
    def test_crawl_page_basic(self, mock_log_extraction, mock_log_links, mock_log_visit, 
                             mock_extract_data, mock_extract_links, mock_fetch):
        """Test basic crawling functionality"""
        # Setup mocks
        mock_fetch.return_value = (True, SIMPLE_HTML)
        mock_extract_links.return_value = []  # No links to follow
        mock_extract_data.return_value = {
            "url": "https://example.com",
            "title": "Test Page",
            "content": "Test content"
        }
        
        # Setup test data
        url = "https://example.com"
        depth = 0
        visited_urls = set()
        pages_data = []
        url_visit_count = {}
        logger = MagicMock()
        
        # Call the function
        crawl_page(url, depth, visited_urls, pages_data, url_visit_count, logger)
        
        # Assertions
        assert url in visited_urls
        assert len(pages_data) == 1
        assert pages_data[0]["url"] == url
        assert pages_data[0]["title"] == "Test Page"
        assert pages_data[0]["content"] == "Test content"
        assert url_visit_count[url] == 1
        
        # Verify mock calls
        mock_fetch.assert_called_once_with(url)
        mock_log_visit.assert_called_once()
        mock_extract_links.assert_called_once()
        mock_log_links.assert_called_once()
        mock_extract_data.assert_called_once()
        mock_log_extraction.assert_called_once()
    
    @patch('crawler_utils.fetch_page')
    @patch('crawler_utils.log_url_skip')
    def test_crawl_page_already_visited(self, mock_log_skip, mock_fetch):
        """Test that already visited URLs are skipped"""
        # Setup test data
        url = "https://example.com"
        depth = 0
        visited_urls = {url}  # URL already in visited set
        pages_data = []
        url_visit_count = {url: 1}  # URL already visited once
        logger = MagicMock()
        
        # Call the function
        crawl_page(url, depth, visited_urls, pages_data, url_visit_count, logger)
        
        # Assertions
        assert len(pages_data) == 0  # No page data should be added
        assert url_visit_count[url] == 2  # Visit count should be incremented
        
        # Verify mock calls
        mock_fetch.assert_not_called()  # fetch_page should not be called
        mock_log_skip.assert_called_once()  # log_url_skip should be called
    
    @patch('crawler_utils.fetch_page')
    @patch('crawler_utils.log_url_skip')
    def test_crawl_page_depth_limit(self, mock_log_skip, mock_fetch):
        """Test that depth limit is enforced"""
        # Setup test data
        url = "https://example.com"
        depth = 3  # Exceeds default max_depth of 2
        visited_urls = set()
        pages_data = []
        url_visit_count = {}
        logger = MagicMock()
        
        # Call the function
        crawl_page(url, depth, visited_urls, pages_data, url_visit_count, logger, max_depth=2)
        
        # Assertions
        assert url not in visited_urls  # URL should not be added to visited set
        assert len(pages_data) == 0  # No page data should be added
        assert url_visit_count[url] == 1  # Visit count should be incremented
        
        # Verify mock calls
        mock_fetch.assert_not_called()  # fetch_page should not be called
        mock_log_skip.assert_called_once()  # log_url_skip should be called
    
    @patch('crawler_utils.fetch_page')
    @patch('crawler_utils.log_fetch_error')
    def test_crawl_page_fetch_error(self, mock_log_error, mock_fetch):
        """Test handling of fetch errors"""
        # Setup mocks
        mock_fetch.return_value = (False, "Error fetching page")
        
        # Setup test data
        url = "https://example.com"
        depth = 0
        visited_urls = set()
        pages_data = []
        url_visit_count = {}
        logger = MagicMock()
        
        # Call the function
        crawl_page(url, depth, visited_urls, pages_data, url_visit_count, logger)
        
        # Assertions
        assert url in visited_urls  # URL should still be added to visited set
        assert len(pages_data) == 0  # No page data should be added
        
        # Verify mock calls
        mock_fetch.assert_called()
        mock_log_error.assert_called_once()
    
    @patch('crawler_utils.fetch_page')
    @patch('crawler_utils.extract_internal_links')
    @patch('crawler_utils.extract_page_data')
    @patch('crawler_utils.time.sleep')  # Mock sleep to speed up test
    def test_crawl_page_recursive(self, mock_sleep, mock_extract_data, mock_extract_links, mock_fetch):
        """Test recursive crawling of internal links"""
        # Setup mocks for the first page
        mock_fetch.side_effect = [
            (True, HTML_WITH_LINKS),  # First call returns page with links
            (True, SIMPLE_HTML),      # Second call returns a simple page
            (True, SIMPLE_HTML)       # Third call returns a simple page
        ]
        
        # First page has two internal links
        mock_extract_links.side_effect = [
            ["https://example.com/page1", "https://example.com/page2"],  # First call
            [],  # Second call - no links
            []   # Third call - no links
        ]
        
        # Setup page data for each page
        mock_extract_data.side_effect = [
            {"url": "https://example.com", "title": "Home", "content": "Home content"},
            {"url": "https://example.com/page1", "title": "Page 1", "content": "Page 1 content"},
            {"url": "https://example.com/page2", "title": "Page 2", "content": "Page 2 content"}
        ]
        
        # Setup test data
        url = "https://example.com"
        depth = 0
        visited_urls = set()
        pages_data = []
        url_visit_count = {}
        logger = MagicMock()
        
        # Call the function
        crawl_page(url, depth, visited_urls, pages_data, url_visit_count, logger)
        
        # Assertions
        assert len(visited_urls) == 3  # All three URLs should be visited
        assert "https://example.com" in visited_urls
        assert "https://example.com/page1" in visited_urls
        assert "https://example.com/page2" in visited_urls
        
        assert len(pages_data) == 3  # All three pages should have data
        assert pages_data[0]["url"] == "https://example.com"
        assert pages_data[1]["url"] == "https://example.com/page1"
        assert pages_data[2]["url"] == "https://example.com/page2"
        
        # Verify mock calls
        assert mock_fetch.call_count == 3
        assert mock_extract_links.call_count == 3
        assert mock_extract_data.call_count == 3
        assert mock_sleep.call_count == 2  # Sleep should be called between requests
    
    @patch('crawler_utils.fetch_page')
    @patch('crawler_utils.extract_internal_links')
    @patch('crawler_utils.extract_page_data')
    @patch('crawler_utils.time.sleep')  # Mock sleep to speed up test
    def test_crawl_page_retry_logic(self, mock_sleep, mock_extract_data, mock_extract_links, mock_fetch):
        """Test retry logic for failed fetches"""
        # Setup mocks
        mock_fetch.side_effect = [
            (False, "Error fetching page"),  # First attempt fails
            (False, "Error fetching page"),  # Second attempt fails
            (True, SIMPLE_HTML)              # Third attempt succeeds
        ]
        
        mock_extract_links.return_value = []
        mock_extract_data.return_value = {
            "url": "https://example.com",
            "title": "Test Page",
            "content": "Test content"
        }
        
        # Setup test data
        url = "https://example.com"
        depth = 0
        visited_urls = set()
        pages_data = []
        url_visit_count = {}
        logger = MagicMock()
        
        # Call the function
        crawl_page(url, depth, visited_urls, pages_data, url_visit_count, logger, max_retries=2)
        
        # Assertions
        assert url in visited_urls
        assert len(pages_data) == 1
        
        # Verify mock calls
        assert mock_fetch.call_count == 3  # fetch_page should be called 3 times
        assert mock_sleep.call_count >= 2  # Sleep should be called between retries


class TestValidateCrawledData:
    """Tests for the validate_crawled_data function"""
    
    def test_validate_crawled_data_valid(self):
        """Test validation with valid data"""
        pages_data = [
            {"url": "https://example.com", "title": "Example", "content": "This is a valid page with sufficient content that exceeds the minimum length requirement for validation."},
            {"url": "https://example.com/page1", "title": "Page 1", "content": "This is another valid page with sufficient content that exceeds the minimum length requirement for validation."}
        ]
        
        results = validate_crawled_data(pages_data)
        
        assert results["total_pages"] == 2
        assert results["valid_pages"] == 2
        assert results["problematic_pages"] == 0
        assert results["pages_with_url"] == 2
        assert results["pages_with_title"] == 2
        assert results["pages_with_content"] == 2
        assert len(results["missing_url"]) == 0
        assert len(results["empty_titles"]) == 0
        assert len(results["empty_content"]) == 0
        assert len(results["short_content"]) == 0
        assert len(results["malformed_urls"]) == 0
    
    def test_validate_crawled_data_missing_url(self):
        """Test validation with missing URL"""
        pages_data = [
            {"title": "Example", "content": "This page is missing a URL."},
            {"url": "https://example.com/page1", "title": "Page 1", "content": "This is a valid page."}
        ]
        
        results = validate_crawled_data(pages_data)
        
        assert results["total_pages"] == 2
        assert results["valid_pages"] == 1
        assert results["problematic_pages"] == 1
        assert results["pages_with_url"] == 1
        assert len(results["missing_url"]) == 1
    
    def test_validate_crawled_data_malformed_url(self):
        """Test validation with malformed URL"""
        pages_data = [
            {"url": "not-a-valid-url", "title": "Example", "content": "This page has a malformed URL."},
            {"url": "https://example.com/page1", "title": "Page 1", "content": "This is a valid page."}
        ]
        
        results = validate_crawled_data(pages_data)
        
        assert results["total_pages"] == 2
        assert results["valid_pages"] == 1
        assert results["problematic_pages"] == 1
        assert results["pages_with_url"] == 2
        assert len(results["malformed_urls"]) == 1
        assert "not-a-valid-url" in results["malformed_urls"]
    
    def test_validate_crawled_data_empty_title(self):
        """Test validation with empty title"""
        pages_data = [
            {"url": "https://example.com", "title": "", "content": "This page has an empty title."},
            {"url": "https://example.com/page1", "title": "Page 1", "content": "This is a valid page."}
        ]
        
        results = validate_crawled_data(pages_data)
        
        assert results["total_pages"] == 2
        assert results["valid_pages"] == 1
        assert results["problematic_pages"] == 1
        assert results["pages_with_title"] == 1
        assert len(results["empty_titles"]) == 1
        assert "https://example.com" in results["empty_titles"]
    
    def test_validate_crawled_data_empty_content(self):
        """Test validation with empty content"""
        pages_data = [
            {"url": "https://example.com", "title": "Example", "content": ""},
            {"url": "https://example.com/page1", "title": "Page 1", "content": "This is a valid page."}
        ]
        
        results = validate_crawled_data(pages_data)
        
        assert results["total_pages"] == 2
        assert results["valid_pages"] == 1
        assert results["problematic_pages"] == 1
        assert results["pages_with_content"] == 1
        assert len(results["empty_content"]) == 1
        assert "https://example.com" in results["empty_content"]
    
    def test_validate_crawled_data_short_content(self):
        """Test validation with short content"""
        pages_data = [
            {"url": "https://example.com", "title": "Example", "content": "Short."},
            {"url": "https://example.com/page1", "title": "Page 1", "content": "This is a valid page with sufficient content that exceeds the minimum length requirement for validation."}
        ]
        
        results = validate_crawled_data(pages_data)
        
        assert results["total_pages"] == 2
        assert results["valid_pages"] == 2  # Short content is a warning, not an error
        assert results["problematic_pages"] == 0
        assert len(results["short_content"]) == 1
        assert results["short_content"][0][0] == "https://example.com"
