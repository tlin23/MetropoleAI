# ✅ Specification: Top-3 Match Rewriting in `/ask` Endpoint

## Overview
This update enhances the LLM-driven rewriting pipeline to:
- Retrieve the **top 3 most relevant matches** from the vector index
- **Filter out** passages below a similarity threshold
- If any remain, **synthesize a single rewritten answer** using the filtered matches
- If none remain, fallback to a default message **including info on filtered-out results**
- Merge `/debug/ask` into `/ask` to support detailed debugging in the MVP phase

---

## 🔧 Functional Requirements

### `/ask` Endpoint
- **Inputs**:
  - `question: str` (via `POST /ask` with `AskRequest`)
- **Outputs**:
  ```json
  {
    "question": "...",
    "score": 0.85,
    "response_type": "rewrite" | "fallback" | "error",
    "raw_passages": [
      {"text": "...", "score": 0.85},
      {"text": "...", "score": 0.77}
    ],
    "filtered_out": [
      {"text": "...", "score": 0.22}
    ],
    "final_response": "..."
  }
  ```

### Index Querying
- Use `top_k=3` in `index.query()`
- Return up to 3 passage+score pairs
- Filter out matches with `score < SIMILARITY_THRESHOLD`
- Sort remaining matches by score (descending)

### Rewriting Logic
- If one or more passages remain post-filter:
  - Synthesize a **single answer** using all remaining passages
  - LLM sees the **highest scored passage first**
- If no passages remain:
  - Use fallback message:
    > "No strong match found in index. Query: '{question}'. Consider checking content coverage or reindexing."
  - Append filtered matches with scores in the response

---

## 🧠 Prompt Design

### Format:
```text
You have the following passages retrieved from a knowledge base. Use the most relevant information to answer the resident's question clearly and helpfully.

Passage 1 (Score: 0.85):
...

Passage 2 (Score: 0.76):
...

Question: [user question]
```

- Constructed in `get_user_prompt_multi(passage_list: List[Tuple[str, float]], question: str)`

---

## 🧾 Data Handling

### Logging
Update `log_interaction()` to log:
- `question`
- `final_response`
- `score` (highest retained score)
- `response_type`
- `raw_passages`: JSON-encoded list of retained passages and scores
- `filtered_out`: JSON-encoded list of rejected passages and scores

### DB Schema
Alter `chat_logs` table to add:
- `raw_passages TEXT`
- `filtered_out TEXT`

---

## ⚠️ Error Handling

- If no index loaded, return early with:
  ```json
  {
    "final_response": "No documents indexed yet.",
    "response_type": "error"
  }
  ```
- If API call to HF model fails, fallback to raw passage(s) or fallback message
- Catch and log all exceptions in `rewrite_answer` and logging

---

## 🧪 Testing Plan

### New test file: `test_ask.py`
- Uses `httpx` or `requests` to send a sample question to `/ask`
- Verifies that:
  - Top 3 matches are returned and filtered
  - Rewriting occurs when appropriate
  - Response contains all expected debug fields

### Manual Tests
- Ask with known strong match → expect rewritten result
- Ask with no good matches → expect fallback with filtered info
- Inspect database (`chat_logs.db`) for correctly recorded logs

---

## 🧱 Refactoring Plan

### 1. `index.py`
- Modify `query()` to return a **list of top_k matches** with `text` and `score`

### 2. `rewrite_utils.py`
- Add `get_user_prompt_multi()` to format multiple passages

### 3. `prompts.py`
- Add helper for multi-passage formatting

### 4. `main.py`
- Remove `/debug/ask`
- Replace `/ask` logic with:
  - Query top 3
  - Filter
  - Rewrite or fallback
  - Return full debug info

### 5. `logging_utils.py`
- Alter schema to add `raw_passages` and `filtered_out` columns
- Update `log_interaction()` to serialize and save them

---

## 📂 File Changes Summary

| File             | Changes |
|------------------|---------|
| `index.py`       | Modify `query()` to return top 3 results |
| `prompts.py`     | Add `get_user_prompt_multi()` |
| `rewrite_utils.py` | Use new prompt builder |
| `main.py`        | Rewrite `/ask`, delete `/debug/ask` |
| `logging_utils.py` | Extend DB schema and log fields |
| `test_ask.py`    | New script to validate end-to-end behavior |
