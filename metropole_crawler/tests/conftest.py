"""
Pytest configuration and fixtures for metropole_crawler tests
"""

import pytest
import logging
from unittest.mock import MagicMock

@pytest.fixture
def mock_logger():
    """
    Fixture that provides a mock logger for testing
    """
    logger = MagicMock(spec=logging.Logger)
    return logger

@pytest.fixture
def sample_pages_data():
    """
    Fixture that provides sample page data for testing
    """
    return [
        {
            "url": "https://sites.google.com/view/metropoleballard/home",
            "title": "Metropole Ballard - Home",
            "content": "This is the home page content with sufficient length to pass validation."
        },
        {
            "url": "https://sites.google.com/view/metropoleballard/about",
            "title": "Metropole Ballard - About",
            "content": "This is the about page content with sufficient length to pass validation."
        },
        {
            "url": "https://sites.google.com/view/metropoleballard/contact",
            "title": "Metropole Ballard - Contact",
            "content": "This is the contact page content with sufficient length to pass validation."
        }
    ]

@pytest.fixture
def sample_validation_results():
    """
    Fixture that provides sample validation results for testing
    """
    return {
        "total_pages": 3,
        "valid_pages": 3,
        "problematic_pages": 0,
        "pages_with_url": 3,
        "pages_with_title": 3,
        "pages_with_content": 3,
        "missing_url": [],
        "empty_titles": [],
        "empty_content": [],
        "short_content": [],
        "malformed_urls": []
    }
