
# 🧭 Project Blueprint: Top-3 Match Rewriting Pipeline

This document outlines the full step-by-step plan to implement the feature described in `top3matches_spec.md`, including incremental task breakdown and LLM code generation prompts.

---

## ✅ Specification Recap

See `top3matches_spec.md` for complete functional requirements.

---

## 🧩 Step-by-Step Breakdown

### Iteration 1: Mid-sized Milestones

1. Update `index.query()` to return top 3 matches.
2. Add `get_user_prompt_multi()` in `prompts.py`.
3. Update `rewrite_utils.py` to handle multiple passages.
4. Refactor `/ask` endpoint in `main.py`.
5. Update `log_interaction()` to support new fields.
6. Alter SQLite schema to log JSON fields.
7. Add `test_ask.py` to verify end-to-end behavior.

---

### Iteration 2: Atomic Developer Tasks

#### ✅ Step 1: Modify `index.py`
- Accept `top_k` as input, default to 3.
- Return list of top_k `{text, score}` dicts.

#### ✅ Step 2: Add `get_user_prompt_multi()` in `prompts.py`
- Accept list of (text, score) tuples.
- Return a formatted multi-passage prompt.

#### ✅ Step 3: Update `rewrite_utils.py`
- Accept list of passages.
- Build multi-passage user prompt.
- Keep existing Hugging Face call.

#### ✅ Step 4: Update `/ask` endpoint
- Query → filter → rewrite → respond with all debug info.
- Remove `/debug/ask`.

#### ✅ Step 5: Extend logging
- Add `raw_passages` and `filtered_out` as JSON-encoded columns.

#### ✅ Step 6: Modify `init_db()` migration logic
- Add columns if not already present.

#### ✅ Step 7: Add test_ask.py
- Use httpx to test end-to-end flow.

---

## ✅ LLM Code Generation Prompts

### Prompt 1: Modify `index.py`

```
You are working in `index.py`. Modify the `query()` method in `HuggingFaceIndex` to return the top 3 matches with scores. Instead of a single dictionary with `text` and `score`, return a list of up to 3 items, each being a dict like `{ "text": ..., "score": ... }`. Ensure the results come sorted by score descending. The interface should still accept `top_k` with a default of 3.
```

---

### Prompt 2: Add `get_user_prompt_multi()` in `prompts.py`

```
Add a new function `get_user_prompt_multi()` to `prompts.py`. It should accept a list of `(text, score)` tuples and a question. It should return a string formatted as a prompt for the LLM, with passages labeled and sorted by score. Use this structure:

"You have the following passages retrieved from a knowledge base..."

Include each passage as:
"Passage 1 (Score: 0.85): [text]"

Put the question at the end.
```

---

### Prompt 3: Rewrite `rewrite_answer()` in `rewrite_utils.py`

```
In `rewrite_utils.py`, update `rewrite_answer()` to accept a list of passage dictionaries, not a single passage string. Pass this list to `get_user_prompt_multi()` to build the user prompt. Keep the system prompt the same. Continue sending the full payload to Hugging Face API and extract the `generated_text` as before.
```

---

### Prompt 4: Refactor `main.py` `/ask` endpoint

```
In `main.py`, merge the `/debug/ask` logic into `/ask`. Do the following:

1. Query index with top_k=3.
2. Filter out passages with score < SIMILARITY_THRESHOLD.
3. If any passages remain, send them to `rewrite_answer()`.
4. If none remain, construct a fallback message.
5. Return a JSON response including: question, final_response, score (top retained), response_type, raw_passages, filtered_out.
```

---

### Prompt 5: Extend logging in `logging_utils.py`

```
Update `log_interaction()` in `logging_utils.py` to accept two new optional arguments: `raw_passages` and `filtered_out`. Serialize them as JSON strings. Add these to the `INSERT INTO` statement so they are stored in the database. Update logging output accordingly.
```

---

### Prompt 6: Alter `init_db()` to support schema migration

```
In `init_db()` in `logging_utils.py`, check if the `chat_logs` table has columns `raw_passages` and `filtered_out`. If not, add them using `ALTER TABLE` statements. This ensures compatibility with existing databases.
```

---

### Prompt 7: Write `test_ask.py`

```
Create `test_ask.py`. Use `httpx.AsyncClient` to send a POST request to `/ask` with a test question. Print the response. Ensure the response includes: raw_passages, filtered_out, final_response, and response_type. You may use dummy index data if needed.
```

---

## ✅ Conclusion

These steps allow safe, testable, incremental progress toward the final feature, and are structured to facilitate LLM-based development workflows.
