# ✅ Metropole Webcrawler – Development TODO Checklist

Use this list to track step-by-step progress. Each item should be fully tested before marking as complete.

---

## 📁 Project Setup

- [x] Create project folder and initialize virtual environment
- [x] Install dependencies: `requests`, `beautifulsoup4`, `lxml`, `html2text`, `tqdm`
- [x] Create `requirements.txt` file
- [x] Create `metropole_crawler.py` module
- [x] Create `data/` output folder
- [x] Define empty `run_crawler()` function

---

## 🌐 Web Crawling Framework

- [x] Implement function to fetch a page using `requests`
- [x] Extract all internal links within `sites.google.com/view/metropoleballard/*`
- [x] Filter and normalize URLs (remove fragments, trailing slashes, etc.)
- [x] Add 1–2 second random delay between requests
- [x] Implement recursive crawl logic with max depth = 2
- [x] Track and avoid revisiting URLs

---

## 📝 HTML Content Extraction

- [x] Extract `<title>` or first `<h1>` as page title
- [x] Use BeautifulSoup + `html2text` to extract visible content
- [x] Remove navigation/headers/footers/boilerplate elements
- [x] Strip excessive whitespace and short fragments
- [x] Store results in a dictionary: `title`, `url`, `content`

---


## 💾 Output Handling

- [x] Combine all collected page data into a list of dictionaries
- [x] Add timestamped filename: `metropole_site_data_<timestamp>.json`
- [x] Save structured JSON output to `data/` folder

---

## 🪵 Logging System

- [x] Initialize `crawl_log_<timestamp>.txt` file in `data/` folder
- [x] Log crawl start and end times
- [x] Log each visited and skipped URL (with reasons)
- [x] Create structured logging module (`logging_utils.py`)
- [x] Implement proper Python logging with file and console output
- [x] Log path to final output JSON file

---

## 🧪 Validation Checks

- [x] Check that each record contains `title`, `url`, and `content`
- [x] Log any missing/empty/malformed fields
- [x] Count and report total valid entries
- [x] Report any validation issues in the log file

---

## 🔗 Final Integration & Testing

- [x] Wire all components inside `run_crawler()`
- [x] Ensure end-to-end execution runs cleanly
- [x] Test with expected output and edge cases
- [x] Print final summary to console and log

---

## ✅ Done!

- [x] Final review of output JSON and logs
- [x] Confirm data is ready for ingestion into LLM index
- [x] Refactor logging system into separate module
- [ ] Optional: Add CLI arguments for base URL and depth
