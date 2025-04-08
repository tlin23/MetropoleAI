"""
Tests for the metropole_crawler.py module
"""

import os
import json
import datetime
import pytest
from unittest.mock import patch, MagicMock, call, mock_open

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metropole_crawler import (
    run_crawler,
    BASE_URL,
    DOMAIN,
    MAX_DEPTH,
    MAX_RETRIES,
    RETRY_DELAY,
    DATA_DIR
)

class TestRunCrawler:
    """Tests for the run_crawler function"""
    
    @patch('metropole_crawler.os.makedirs')
    @patch('metropole_crawler.setup_crawler_logger')
    @patch('metropole_crawler.crawl_page')
    @patch('metropole_crawler.log_crawler_start')
    @patch('metropole_crawler.log_crawl_statistics')
    @patch('metropole_crawler.log_output_info')
    @patch('metropole_crawler.validate_crawled_data')
    @patch('metropole_crawler.log_validation_results')
    @patch('metropole_crawler.log_completion')
    @patch('metropole_crawler.open', new_callable=mock_open)
    @patch('metropole_crawler.json.dump')
    def test_run_crawler_basic(self, mock_json_dump, mock_file_open, mock_log_completion, 
                              mock_log_validation, mock_validate, mock_log_output, 
                              mock_log_stats, mock_log_start, mock_crawl_page, 
                              mock_setup_logger, mock_makedirs):
        """Test basic crawler workflow"""
        # Setup mocks
        mock_logger = MagicMock()
        mock_setup_logger.return_value = mock_logger
        
        # Mock crawl_page to populate pages_data
        def mock_crawl_func(url, depth, visited_urls, pages_data, url_visit_count, logger, *args, **kwargs):
            visited_urls.add(url)
            visited_urls.add(f"{url}/page1")
            pages_data.append({"url": url, "title": "Home", "content": "Home content"})
            pages_data.append({"url": f"{url}/page1", "title": "Page 1", "content": "Page 1 content"})
            url_visit_count[url] = 1
            url_visit_count[f"{url}/page1"] = 1
        
        mock_crawl_page.side_effect = mock_crawl_func
        
        # Mock validation results
        mock_validate.return_value = {
            "total_pages": 2,
            "valid_pages": 2,
            "problematic_pages": 0,
            "pages_with_url": 2,
            "pages_with_title": 2,
            "pages_with_content": 2,
            "missing_url": [],
            "empty_titles": [],
            "empty_content": [],
            "short_content": [],
            "malformed_urls": []
        }
        
        # Call the function
        run_crawler()
        
        # Assertions
        mock_makedirs.assert_called_once_with(DATA_DIR, exist_ok=True)
        mock_setup_logger.assert_called_once()
        mock_log_start.assert_called_once_with(mock_logger, BASE_URL, MAX_DEPTH)
        
        # Check crawl_page call
        mock_crawl_page.assert_called_once()
        args, kwargs = mock_crawl_page.call_args
        assert args[0] == BASE_URL  # url
        assert args[1] == 0  # depth
        assert isinstance(args[2], set)  # visited_urls
        assert isinstance(args[3], list)  # pages_data
        assert isinstance(args[4], dict)  # url_visit_count
        assert args[5] == mock_logger  # logger
        assert args[6] == MAX_DEPTH  # max_depth
        assert args[7] == MAX_RETRIES  # max_retries
        assert args[8] == RETRY_DELAY  # retry_delay
        assert args[9] == DOMAIN  # domain
        
        # Check that statistics and validation were logged
        mock_log_stats.assert_called_once()
        mock_validate.assert_called_once()
        mock_log_validation.assert_called_once()
        
        # Check that output file was created
        mock_file_open.assert_called_once()
        mock_json_dump.assert_called_once()
        
        # Check that completion was logged
        mock_log_completion.assert_called_once()
    
    @patch('metropole_crawler.os.makedirs')
    @patch('metropole_crawler.setup_crawler_logger')
    @patch('metropole_crawler.crawl_page')
    @patch('metropole_crawler.log_crawler_start')
    def test_run_crawler_error_handling(self, mock_log_start, mock_crawl_page, 
                                       mock_setup_logger, mock_makedirs):
        """Test error handling in crawler workflow"""
        # Setup mocks
        mock_logger = MagicMock()
        mock_setup_logger.return_value = mock_logger
        
        # Make crawl_page raise an exception
        mock_crawl_page.side_effect = Exception("Test error")
        
        # Call the function
        run_crawler()
        
        # Assertions
        mock_makedirs.assert_called_once_with(DATA_DIR, exist_ok=True)
        mock_setup_logger.assert_called_once()
        mock_log_start.assert_called_once()
        mock_crawl_page.assert_called_once()
        
        # Check that error was logged
        mock_logger.error.assert_called_once()
        args, _ = mock_logger.error.call_args
        assert "Unexpected error during crawling" in args[0]
        assert "Test error" in args[0]


class TestCircularReferences:
    """Tests for handling circular references in website structure"""
    
    @patch('crawler_utils.fetch_page')
    @patch('crawler_utils.extract_internal_links')
    @patch('crawler_utils.extract_page_data')
    @patch('crawler_utils.time.sleep')  # Mock sleep to speed up test
    def test_circular_references(self, mock_sleep, mock_extract_data, mock_extract_links, mock_fetch):
        """Test handling of circular references between pages"""
        from crawler_utils import crawl_page
        from tests.fixtures.sample_html import HTML_CIRCULAR_REF_1, HTML_CIRCULAR_REF_2
        
        # Setup mocks
        mock_fetch.side_effect = [
            (True, HTML_CIRCULAR_REF_1),  # First call returns page1 with link to page2
            (True, HTML_CIRCULAR_REF_2)   # Second call returns page2 with link back to page1
        ]
        
        # Setup links for circular reference
        mock_extract_links.side_effect = [
            ["https://sites.google.com/view/metropoleballard/page2"],  # Page1 links to Page2
            ["https://sites.google.com/view/metropoleballard/page1"]   # Page2 links back to Page1
        ]
        
        # Setup page data
        mock_extract_data.side_effect = [
            {"url": "https://sites.google.com/view/metropoleballard/page1", 
             "title": "Page 1", 
             "content": "Page 1 content"},
            {"url": "https://sites.google.com/view/metropoleballard/page2", 
             "title": "Page 2", 
             "content": "Page 2 content"}
        ]
        
        # Setup test data
        url = "https://sites.google.com/view/metropoleballard/page1"
        depth = 0
        visited_urls = set()
        pages_data = []
        url_visit_count = {}
        logger = MagicMock()
        domain = "sites.google.com/view/metropoleballard"
        
        # Call the function
        crawl_page(url, depth, visited_urls, pages_data, url_visit_count, logger, 
                  max_depth=2, domain=domain)
        
        # Assertions
        assert len(visited_urls) == 2  # Both pages should be visited exactly once
        assert "https://sites.google.com/view/metropoleballard/page1" in visited_urls
        assert "https://sites.google.com/view/metropoleballard/page2" in visited_urls
        
        assert len(pages_data) == 2  # Both pages should have data
        assert pages_data[0]["url"] == "https://sites.google.com/view/metropoleballard/page1"
        assert pages_data[1]["url"] == "https://sites.google.com/view/metropoleballard/page2"
        
        # Verify mock calls
        assert mock_fetch.call_count == 2  # Each page fetched once
        assert mock_extract_links.call_count == 2
        assert mock_extract_data.call_count == 2
        
        # Check that each URL was only visited once despite the circular reference
        assert url_visit_count["https://sites.google.com/view/metropoleballard/page1"] == 1
        assert url_visit_count["https://sites.google.com/view/metropoleballard/page2"] == 1
