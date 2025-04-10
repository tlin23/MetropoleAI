
# 📐 Specification – Improve Metropole.AI Chatbot Responses
**Generated:** 2025-04-09

---

## ✅ Goal

Improve the quality and clarity of the chatbot responses by:
- Selecting only the best-matching passage for a question.
- Rewriting that passage into a conversational, helpful answer using a hosted open-source LLM.
- Returning debug metadata during development for better tuning and transparency.

---

## 🧠 Architecture Overview

### 1. Retrieval
- **Library**: LlamaIndex with `HuggingFaceEmbedding` (`all-MiniLM-L6-v2`)
- **Vector store**: ChromaDB (persistent)
- **Query strategy**: Select top-1 result based on similarity score
- **Threshold**: Minimum similarity threshold of `0.7` (env-configurable)

### 2. Rewriting
- **Model**: [`HuggingFaceH4/zephyr-7b-beta`](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta)
- **Hosting**: Hugging Face Inference API
- **Prompt format**:
  ```
  System Prompt:
  You are a helpful assistant for residents at The Metropole building in Seattle.
  Always speak clearly, stay friendly but focused, and avoid overly general language.

  User Prompt:
  Rewrite the following passage into a clear, helpful answer for a resident’s question.

  Passage: {{retrieved_text}}
  Question: {{user_question}}
  ```

### 3. API Changes

#### `/ask` (POST)
- Accepts:
  ```json
  { "question": "..." }
  ```
- Returns:
  ```json
  { "answer": "..." }
  ```
- Behavior:
  - Retrieve top passage and score
  - If score ≥ threshold:
    - Call `rewrite_answer()` to rewrite passage
    - Return rewritten answer
  - If score < threshold:
    - Return fallback:
      `"No strong match found in index. Query: '{{user_question}}'. Consider checking content coverage or reindexing."`

#### `/debug/ask` (POST)
- Accepts same JSON as `/ask`
- Returns:
  ```json
  {
    "question": "...",
    "score": 0.84,
    "response_type": "rewrite",
    "raw_passage": "...",
    "final_response": "..."
  }
  ```
- Note: Public for now, must be locked down before production

---

## ⚙️ Environment Variables

```env
HF_API_TOKEN=your_token
SIMILARITY_THRESHOLD=0.7
```

---

## 📁 Files to Add/Update

### `model/rewrite_utils.py`

```python
import os
import httpx

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

async def rewrite_answer(question: str, passage: str) -> str:
    payload = {
        "inputs": {
            "text": f"Rewrite the following passage into a clear, helpful answer for a resident’s question.\n\nPassage:\n{passage}\n\nQuestion:\n{question}"
        },
        "parameters": {"max_new_tokens": 300},
        "options": {"use_cache": True, "wait_for_model": True}
    }
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(HF_MODEL_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("generated_text", "").strip()
    except Exception:
        return None
```

### `index.py`
Update `query()` to return:
```python
{ "text": best_passage, "score": similarity_score }
```

---

## 🗃️ Logging

Extend `log_interaction()` to include:
- `score` (float)
- `response_type` (e.g. `"rewrite"`, `"fallback"`, `"error"`)

---

## ⚠️ Error Handling

- Retry Hugging Face request once
- If both fail, return:
  ```text
  "Sorry, I couldn’t generate a response right now. Please try again shortly."
  ```

---

## 🧪 Testing Plan

| Scenario                        | Expected Result                                 |
|--------------------------------|--------------------------------------------------|
| High similarity (≥ threshold)  | Returns rewritten answer                         |
| Low similarity (< threshold)   | Returns fallback message                         |
| Model call fails               | Retries once, then fallback error message        |
| `/debug/ask`                   | Returns full metadata + rewritten output         |
| Threshold change (via env var) | Influences rewrite behavior without redeploying  |

---

## 🔐 Security TODO
- Lock down `/debug/ask` with an API key or dev-only flag before production.

---

## 🚧 Deferred Features
- Caching for (question, passage) pairs
- Multi-turn memory
- Integration with fallback general knowledge LLM
- Display score/confidence in frontend (optional)
