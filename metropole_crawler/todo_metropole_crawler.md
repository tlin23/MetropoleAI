# ✅ Metropole Webcrawler – Development TODO Checklist

Use this list to track step-by-step progress. Each item should be fully tested before marking as complete.

---

## 📁 Project Setup

- [ ] Create project folder and initialize virtual environment
- [ ] Install dependencies: `requests`, `beautifulsoup4`, `lxml`, `html2text`, `PyMuPDF` or `pdfminer.six`, `tqdm`
- [ ] Create `requirements.txt` file
- [ ] Create `metropole_crawler.py` module
- [ ] Create `data/` output folder
- [ ] Define empty `run_crawler()` function

---

## 🌐 Web Crawling Framework

- [ ] Implement function to fetch a page using `requests`
- [ ] Extract all internal links within `sites.google.com/view/metropoleballard/*`
- [ ] Filter and normalize URLs (remove fragments, trailing slashes, etc.)
- [ ] Add 1–2 second random delay between requests
- [ ] Implement recursive crawl logic with max depth = 2
- [ ] Track and avoid revisiting URLs

---

## 📝 HTML Content Extraction

- [ ] Extract `<title>` or first `<h1>` as page title
- [ ] Use BeautifulSoup + `html2text` to extract visible content
- [ ] Remove navigation/headers/footers/boilerplate elements
- [ ] Strip excessive whitespace and short fragments
- [ ] Store results in a dictionary: `title`, `url`, `content`

---

## 📎 PDF Handling

- [ ] Identify all `.pdf` links on the page
- [ ] Skip PDFs that require download
- [ ] Attempt to extract text from inline/viewable PDFs using PyMuPDF or pdfminer
- [ ] Skip and log password-protected/corrupt PDFs
- [ ] Store PDF text in `"pdf_text"` field in page dictionary

---

## 💾 Output Handling

- [ ] Combine all collected page data into a list of dictionaries
- [ ] Add timestamped filename: `metropole_site_data_<timestamp>.json`
- [ ] Save structured JSON output to `data/` folder

---

## 🪵 Logging System

- [ ] Initialize `crawl_log_<timestamp>.txt` file in `data/` folder
- [ ] Log crawl start and end times
- [ ] Log each visited and skipped URL (with reasons)
- [ ] Log PDF issues (e.g., unreadable or corrupt)
- [ ] Log path to final output JSON file

---

## 🧪 Validation Checks

- [ ] Check that each record contains `title`, `url`, and `content`
- [ ] Log any missing/empty/malformed fields
- [ ] Count and report total valid entries
- [ ] Report any validation issues in the log file

---

## 🔗 Final Integration & Testing

- [ ] Wire all components inside `run_crawler()`
- [ ] Ensure end-to-end execution runs cleanly
- [ ] Test with expected output and edge cases
- [ ] Print final summary to console and log

---

## ✅ Done!

- [ ] Final review of output JSON and logs
- [ ] Confirm data is ready for ingestion into LLM index
- [ ] Optional: refactor or document for future CLI/API triggers