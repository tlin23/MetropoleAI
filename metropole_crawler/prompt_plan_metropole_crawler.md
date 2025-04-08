# 🧱 Metropole Webcrawler – Development Prompt Plan

## 🗺️ High-Level Phases

1. **Project Setup**
2. **Core Webcrawler Function**
3. **Content Extraction & Cleanup**
4. **Output Formatting**
5. **Logging**
6. **Validation & Testing**
7. **Integration & Finalization**

## 🔨 Phase Breakdown

### 1. Project Setup
- Initialize Python project and folder structure
- Add required dependencies: `requests`, `beautifulsoup4`, `lxml`, `tqdm`, `html2text`
- Create base module: `metropole_crawler.py`
- Add placeholder for `run_crawler()`

### 2. Webcrawler Framework
- Implement URL traversal logic (depth-limited, internal links only)
- Add 1–2 sec randomized delay between requests
- Track visited URLs to avoid loops

### 3. HTML Content Extraction
- For each page:
  - Extract title (prefer `<title>`, fallback to first `<h1>`)
  - Extract visible text
  - Clean HTML to remove nav/footer/boilerplate
- Return structured Python objects

### 4. Output Storage
- Format result into JSON with:
  - `title`, `url`, `content`
- Save to `data/` folder with timestamped filename

### 5. Logging System
- Write crawl stats, skipped pages, etc. to `.log` file

### 6. Validation
- Validate all fields per entry
- Report issues and flag empty or malformed records

### 7. Integration
- Wire everything through `run_crawler()`
- Test end-to-end crawl

## 🔁 Iterative Task Breakdown

| Step | Description |
|------|-------------|
| 1.1 | Initialize project + dependencies |
| 1.2 | Create `run_crawler()` stub |
| 2.1 | Fetch a single webpage |
| 2.2 | Extract internal links |
| 2.3 | Recursively crawl with depth limit |
| 3.1 | Extract and clean visible text |
| 3.2 | Extract page title |
| 4.1 | Format and save JSON output |
| 5.1 | Implement structured logging |
| 6.1 | Validate entries and content quality |
| 7.1 | Final integration and testing |

## 🤖 Code Generation Prompts

### 🏗️ Prompt 1: Project Setup
```text
Create a new Python module called `metropole_crawler.py`. Inside it, define a function `run_crawler()` that will eventually be used to crawl the Metropole Ballard website. The function should be empty for now. Create a `data/` folder if it doesn't already exist. Add a `requirements.txt` file including:
- requests
- beautifulsoup4
- lxml
- html2text
- tqdm
```

### 🧭 Prompt 2: Basic Crawl + Link Traversal
```text
In `metropole_crawler.py`, implement the following inside `run_crawler()`:

- Start from this URL: https://sites.google.com/view/metropoleballard/home
- Fetch HTML content using `requests`
- Parse it with `BeautifulSoup`
- Extract internal links (`href` within the base domain)
- Traverse these links recursively up to depth=2
- Keep a `visited_urls` set to avoid reprocessing
- Add a 1–2 second randomized delay between requests

Ensure the recursion logic is tested by printing out the URLs discovered at each depth.
```

### 📄 Prompt 3: Extract & Clean Text
```text
For each visited page:
- Extract the page `<title>` or the first `<h1>` as `title`
- Use BeautifulSoup and `html2text` to extract visible, readable text
- Remove navigation bars, headers/footers, and repeated elements like "Back to Top" or "Metropole HOA"
- Strip excessive whitespace and empty lines
- Return a Python dictionary with `url`, `title`, and `content`
```

### 💾 Prompt 4: Save JSON Output
```text
Once crawling is complete:
- Format all collected page data as a list of dictionaries
- Include: `title`, `url`, `content`
- Save to `data/metropole_site_data_<timestamp>.json`
- Use `datetime` to generate timestamp
```

### 🪵 Prompt 5: Add Logging System
```text
Implement logging in `run_crawler()`:
- Create a log file in `data/` named `crawl_log_<timestamp>.txt`
- Log: start/end time, total pages visited, pages skipped, and output file path
- Write logs to file and also print summary to console
```

### 🧪 Prompt 6: Validation & Quality Checks
```text
After crawling:
- For each entry in the collected data, check:
  - `url`, `title`, and `content` are non-empty
- Log a warning for any missing or malformed fields
- Log count of total entries, valid entries, and problematic ones
```

### 🔗 Prompt 7: Final Integration & Wiring
```text
Refactor your `run_crawler()` so it cleanly integrates:
- Depth-limited crawl with visited tracking
- Page content extraction and cleanup
- Structured logging
- Final output saving
- Validation report

Ensure everything runs sequentially and logs final success message with output paths.
```
