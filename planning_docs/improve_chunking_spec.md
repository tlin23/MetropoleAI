# 🧠 Metropole Chatbot: Smart Chunking Specification

## 📌 Objective

Improve the quality and relevance of chatbot responses by enhancing the way website text is chunked and indexed for semantic search. Specifically, we aim to break long blobs of text into semantically focused, metadata-rich chunks that are easier to match with user queries.

---

## ✅ Summary of Requirements

| Feature | Description |
|--------|-------------|
| Chunking approach | Sentence-based, semantically focused |
| Target size | ~512 tokens per chunk (configurable) |
| Entity detection | Rule-based parsing for common patterns (e.g., board members, contact info) |
| Hierarchy | Add **breadcrumb-style context** (e.g., `Board 2024 > Frederic Wehman`) |
| Metadata | Store `breadcrumb`, `source_url`, and `token_count` per chunk |
| Source structure | Freeform text extracted from Metropole Google Site JSON |
| Output format | JSON-compatible list of chunks for LlamaIndex ingestion |

---

## 🧱 Architecture Overview

### Input
- JSON from `get_latest_metropole_data()`, where each page has:
  ```json
  {
    "url": "https://sites.google.com/view/metropoleballard/board-2024",
    "title": "Board 2024",
    "content": "Freeform extracted text..."
  }
  ```

### Output
A list of structured chunks like:
```json
{
  "text": "Board 2024 > Frederic Wehman, iii: Unit 22, Seat 5 (2024)...",
  "metadata": {
    "breadcrumb": "Board 2024",
    "source_url": "https://sites.google.com/view/metropoleballard/board-2024",
    "tokens": 147
  }
}
```

---

## ⚙️ Chunking Algorithm (Step-by-step)

### 1. Load and Iterate Pages
- Loop over each page in the JSON.
- Extract: `title`, `url`, `content`.

### 2. Preprocess Content
- Use `spaCy` (`en_core_web_sm`) for:
  - Sentence segmentation
  - Named entity recognition (if useful)
- Clean up formatting artifacts (extra `\n`, markdown hashes, etc.).

### 3. Heading Detection (Breadcrumb Builder)
- Look for section titles via patterns (regex):
  ```python
  SECTION_HEADING_PATTERNS = [
      r'^#\s+', r'^Board\s+\d{4}', r'^Newsletter', r'^Blog'
  ]
  ```
- Extract breadcrumb prefix from page title or heading (e.g., `Board 2024`).

### 4. Chunk Construction
- Group consecutive sentences into chunks with a **soft token limit** (default: 512).
  - Use `len(tokenizer.encode(text))` to measure tokens (e.g., with HuggingFace tokenizer).
- If board/contact info pattern is detected (e.g., lines with name + unit + phone), treat as standalone chunk.

### 5. Chunk Formatting
- Each chunk includes:
  - Prefixed breadcrumb (e.g., `"Board 2024 > Frederic Wehman"`)
  - Source URL
  - Token count

---

## 🧰 Dependencies

- Python 3.8+
- `spaCy` (`pip install spacy && python -m spacy download en_core_web_sm`)
- `transformers` (for token counting with sentence transformers like `all-MiniLM-L6-v2`)
- Optional: `tiktoken` if using OpenAI tokenization

---

## ❗ Error Handling

| Risk | Strategy |
|------|----------|
| Page missing `title`, `url`, or `content` | Skip with warning log |
| Chunk exceeds token limit | Split into smaller groups of sentences |
| Malformed lines (e.g., missing delimiters) | Fallback to sentence chunking |
| Encoding errors | Use UTF-8 safe decoding with replacement |

---

## 🧪 Testing Plan

| Test | Purpose |
|------|---------|
| **Unit test for chunker** | Input mock page, check # of chunks, breadcrumb formatting, token counts |
| **Edge case: One-liner board contact** | Ensure it becomes a standalone chunk |
| **Multi-section page** | Ensure headings update breadcrumbs correctly |
| **Very short/long content** | Ensure fallback behavior is robust |
| **Manual test** | Ask “Who is Frederic Wehman?” and confirm correct chunk surfaces |

---

## 🧩 Integration Points

### Replace this in `train.py`:
```python
website_texts = extract_website_texts(metropole_pages)
```

### With:
```python
website_texts = smart_chunk_metropole_pages(metropole_pages)
```

Where `smart_chunk_metropole_pages()` is your new chunking function that returns `[chunk["text"] for chunk in chunks]`, and optionally writes `chunks.txt` with both `text` and `metadata`.

---

## 🛠️ Future Improvements

- Add special logic for:
  - Blog posts (e.g., “2025 Annual Meeting”)
  - Manual sections (e.g., “Security”, “Waste & Recycling”)
- Use full LLM for structural tagging if rule-based proves limiting
- Index chunk metadata for response-time citations or filters