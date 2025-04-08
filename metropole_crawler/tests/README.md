# Metropole Crawler Tests

This directory contains tests for the Metropole Crawler project.

## Test Structure

- `fixtures/`: Contains test fixtures and sample data
- `test_crawler_utils_network.py`: Tests for network and HTML processing functions
- `test_crawler_utils_crawling.py`: Tests for crawling logic and data validation
- `test_metropole_crawler.py`: Tests for the main crawler workflow and circular reference handling
- `conftest.py`: Shared pytest fixtures

## Running Tests

To run all tests:

```bash
cd metropole_crawler
python -m pytest
```

To run a specific test file:

```bash
python -m pytest tests/test_crawler_utils_network.py
```

To run a specific test:

```bash
python -m pytest tests/test_crawler_utils_network.py::TestFetchPage::test_fetch_page_success
```

## Test Coverage

### Network and HTML Processing Functions

- `fetch_page`: Tests for successful and failed page fetches, handling of HTTP errors, and timeouts
- `extract_internal_links`: Tests for link extraction from HTML, domain filtering, and handling of various link types
- `extract_page_title`: Tests for title extraction from HTML with different structures
- `clean_text`: Tests for text cleaning and boilerplate removal
- `extract_content`: Tests for content extraction from HTML
- `extract_page_data`: Tests for structured data extraction

### Crawling Logic

- `crawl_page`: Tests for depth limiting, URL deduplication, retry logic, and recursive crawling
- `validate_crawled_data`: Tests for data validation with various input scenarios

### Main Crawler Workflow

- `run_crawler`: Tests for the overall crawler workflow, including directory creation, file output, and error handling

### Circular Reference Handling

- Tests for proper handling of circular references in website structure, ensuring each URL is only visited once
