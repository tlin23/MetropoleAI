---

# 🕷️ Metropole Crawler Specification (MVP)

## ✅ Overview

This module implements a structured, on-demand webcrawler for the [Metropole Ballard website](https://sites.google.com/view/metropoleballard/home). It extracts visible text content and PDF data from the site’s internal pages, applies text cleanup, and outputs structured data in JSON format for downstream ingestion by LLM systems (e.g., LlamaIndex).

---

## 📁 File: `metropole_crawler.py`

### Exposed Function
```python
def run_crawler() -> None:
    """
    Crawls Metropole Ballard website (depth 2), extracts content,
    saves structured text output to JSON file in /data,
    and writes a crawl log file with validation results.
    """
```

---

## 🧱 Architecture & Behavior

### Crawl Target
- **Start URL**: `https://sites.google.com/view/metropoleballard/home`
- **Domain Restriction**: Only crawl URLs within `sites.google.com/view/metropoleballard/*`
- **Crawl Depth Limit**: 2
  - Depth 0 = home page
  - Depth 1 = internal links from home
  - Depth 2 = links from depth-1 pages
- **Delay Between Requests**: 1–2 seconds randomized

---

### Content Extraction
For each page:
- Extract **visible text content only**
- Extract **page title** (from `<title>` or first `<h1>`)
- Extract text from **embedded or inline PDFs** (if renderable without download)
- **Skip** PDFs that require download or are password-protected/corrupt
- **Clean up content**:
  - Remove navigation, headers/footers, buttons like “Back to Top”
  - Strip excessive whitespace, blank lines, HTML noise
  - Remove repeated boilerplate ("Metropole HOA", etc.)
  - Filter out very short fragments (< 5 words)
  - English-only (assumed by default)

---

### Output

#### Folder
- Save files in a local `data/` folder (create if not present)

#### JSON File
- Filename format:  
  `metropole_site_data_<YYYY-MM-DD_HH-MM-SS>.json`
- Format:
```json
[
  {
    "title": "Building Rules",
    "url": "https://sites.google.com/view/metropoleballard/rules",
    "content": "Visible cleaned text...",
    "pdf_text": "PDF content if available, else omitted"
  },
  ...
]
```

---

## 🪵 Logging

#### Log File
- Saved to `crawl_log_<YYYY-MM-DD_HH-MM-SS>.txt` in the same `data/` folder

#### Contents
- Timestamp of crawl
- Pages visited
- Pages skipped (with reason)
- PDFs skipped (password/corrupt/download-required)
- Output JSON path
- Validation results (missing fields, empty content, etc.)

---

## 🧪 Testing & Validation

After crawl:
- ✅ Validate each JSON object has:
  - Non-empty `title`
  - Valid `url`
  - Non-empty `content`
- ✅ Log any missing or empty fields
- ✅ Confirm final JSON is parseable
- ✅ Count and report:
  - Pages crawled
  - Pages skipped
  - PDF issues

---

## 🔐 Privacy & Compliance
- Do **not extract or store** any personally identifiable information (PII)
- PDFs or content referencing individuals (e.g., email addresses) should be ignored if not anonymized
- All logs and outputs are local-only (no remote sync)

---

## ⚠️ Error Handling

- Retry failed requests up to 2 times (with backoff)
- Catch and log:
  - HTTP errors
  - Timeout errors
  - PDF parsing errors
- Skip and log:
  - Pages with no visible content
  - Duplicate pages (by URL)
  - Infinite link loops

---

## 🔧 Implementation Tools

- **Requests / HTTPX** – page fetch
- **BeautifulSoup** – HTML parsing
- **PyMuPDF** or **pdfminer.six** – inline PDF extraction
- **re / html2text / lxml** – for text cleanup
- **json, os, datetime, logging** – system I/O

---

## 🔁 Usage Example

In a training script or ingestion pipeline:
```python
from metropole_crawler import run_crawler

run_crawler()  # Saves clean site content to JSON for LLM ingestion
```

---

## 📦 Optional Future Enhancements
- Add support for external links
- Add a `--base_url` CLI flag or FastAPI trigger endpoint
- Sync new/changed content with diffing
- Extract layout structure (headings, sections) for better indexing
- Extract metadata for context-aware responses

---