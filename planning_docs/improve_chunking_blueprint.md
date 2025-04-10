# 🔧 Metropole Chatbot: Smart Chunking — Implementation Blueprint

This document outlines a step-by-step blueprint for implementing improved chunking logic for the Metropole chatbot, based on the specification defined in `improve_chunking_spec.md`.

---

## 🧱 High-Level Blueprint

### Phase 1: Core Functionality (Chunking Logic)
- Parse JSON pages
- Split content into semantically meaningful chunks using `spaCy`
- Build breadcrumb prefixes using titles and section patterns
- Track token count and metadata
- Output clean, index-ready structured text blocks

### Phase 2: Integration
- Plug into the current `train.py` workflow
- Output debug-friendly chunk file (`chunks.txt`)
- Ensure compatibility with LlamaIndex ingestion

### Phase 3: Testing
- Build strong unit tests
- Validate output format, structure, metadata, edge cases

---

## 📦 Iterative Milestones

### ✅ Milestone 1: Page Parsing & Preprocessing
### ✅ Milestone 2: Sentence Segmentation + Metadata Extraction
### ✅ Milestone 3: Chunk Builder
### ✅ Milestone 4: Output Format & Debugging
### ✅ Milestone 5: Integration & Testing

---

## 🧩 Atomic Development Steps

1. Load JSON Pages
2. Clean Page Text
3. Extract Breadcrumb from Title or Heading
4. Split Content into Sentences using spaCy
5. Chunk Sentences by Token Limit
6. Attach Metadata and Breadcrumbs
7. Handle Edge Cases (Board Contacts)
8. Return Chunks + Write `chunks.txt`
9. Unit Tests for Each Core Function
10. Plug into `train.py` with Fallback
11. Run End-to-End Tests
12. Manual QA ("Who is Frederic Wehman")

---

## 🤖 Code-Generation Prompts

Each section is a prompt for a code-generation LLM to implement a single atomic function with test coverage.

---

### 🧪 Step 1: Load JSON Pages

```
You are writing a function that accepts a list of dictionaries representing pages from a JSON crawl of a website. Each dictionary contains keys: 'title', 'url', 'content'.

Write a function `load_metropole_pages(pages)` that:
- Accepts a list of page dictionaries
- Filters out any pages missing one of those keys
- Strips whitespace and normalizes each field
- Returns a cleaned list of pages with those fields

Also write a pytest test for this function with:
- One valid page
- One with missing title
- One with blank content
```

---

### 🧪 Step 2: Clean Page Text

```
Create a helper function `clean_text(text: str) -> str` that:
- Replaces multiple newlines with a single newline
- Removes leading markdown headers (e.g. "#", "###")
- Strips leading/trailing whitespace

Write a test that shows it correctly transforms a sample multiline string.
```

---

### 🧪 Step 3: Extract Breadcrumb from Title or Heading

```
Write a function `extract_breadcrumb(title: str, content: str) -> str` that:
- Uses regex to match known section heading patterns (e.g. "Board 2024", "Newsletter")
- If a match is found in the title or the first 5 lines of content, use that as the breadcrumb
- Otherwise fall back to the title itself

Include tests with:
- A "Board 2024" title
- A newsletter heading inside content
- A fallback case
```

---

### 🧪 Step 4: Split Content into Sentences using spaCy

```
Write a function `split_sentences(text: str) -> List[str]` using `spaCy` (`en_core_web_sm`) to:
- Segment the input into clean, trimmed sentences

Write tests for paragraphs with:
- Period-separated sentences
- Linebreaks between phrases
- Ellipses and abbreviations
```

---

### 🧪 Step 5: Chunk Sentences by Token Limit

```
Write `chunk_sentences(sentences: List[str], max_tokens: int) -> List[List[str]]`:
- Uses a Hugging Face tokenizer (e.g. `all-MiniLM-L6-v2`)
- Groups sentences into sublists such that total tokens ≤ max_tokens
- Starts a new chunk when adding the next sentence would exceed the limit

Write tests with:
- Short dummy sentences
- Sentences that together exceed the limit
```

---

### 🧪 Step 6: Attach Metadata and Breadcrumbs

```
Write `format_chunks(chunks: List[List[str]], breadcrumb: str, url: str) -> List[Dict]`:
- Joins each sentence group into a chunk text
- Prepends `breadcrumb >` to the first line of each chunk
- Adds metadata: breadcrumb, source_url, token count

Write tests to check:
- Prefix formatting
- Metadata values
```

---

### 🧪 Step 7: Handle Edge Cases (Board Contact Format)

```
Enhance `chunk_sentences` to detect standalone blocks like:
- Names followed by unit/email/phone

Use regex to break contact blocks into single chunks even if under token limit.

Write a test using a contact block like:
"Frederic Wehman, iii\nUnit 22\nemail\nphone"
```

---

### 🧪 Step 8: Return Chunks + Write `chunks.txt`

```
Write a function `write_chunks_debug(chunks: List[Dict], path: str)`:
- Writes each chunk’s text followed by metadata to the file
- Use a format like:
  --- Chunk 1 ---
  Text here...
  [breadcrumb=Board 2024, tokens=147]

Write a test using `tmp_path` to validate the output.
```

---

### 🧪 Step 9: Unit Tests for Core Functions

```
Create a test suite with pytest that runs:
- All functions created so far
- Edge cases for each (e.g. long names, malformed lines)

Use fixtures for reusable test pages.
```

---

### 🧪 Step 10: Plug into `train.py`

```
Replace the call to `extract_website_texts()` in `train.py` with your new function:
`smart_chunk_metropole_pages(pages) -> List[str]`

- Import the chunker
- Return only `chunk["text"]` for indexing
- Save full chunks (with metadata) to `chunks.txt`

Include a safety fallback to log and exit if chunking fails.
```

---

### 🧪 Step 11: Run End-to-End Tests

```
Run the entire `train.py` with metropole JSON input:
- Confirm `chunks.txt` is generated
- Confirm chunk count is higher than before
- Confirm smaller chunk sizes
```

---

### 🧪 Step 12: Manual QA: "Who is Frederic Wehman?"

```
Query the chatbot with:
"Who is Frederic Wehman?"

Confirm that the response:
- Matches the correct chunk
- Contains contact details
- Has a similarity score significantly above threshold
```