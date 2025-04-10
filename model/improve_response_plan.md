
# Improve Metropole.AI Chatbot Response – Blueprint

## 🚀 Goal
Enhance the Metropole chatbot response pipeline by integrating a hosted LLM to rewrite retrieved content into user-friendly answers, with safe, testable, and modular implementation steps.

---

## 📊 Phase Overview

### Phase 1: Prep & Refactor Retrieval
1. Update `index.query()` to return dict (`text`, `score`)
2. Add `SIMILARITY_THRESHOLD` via env var
3. Log score + response type to SQLite
4. Add `/debug/ask` endpoint for transparent dev

### Phase 2: Rewrite Layer
5. Create `model/rewrite_utils.py` with `rewrite_answer()`
6. Use Hugging Face token securely and send API request
7. Add retry logic (1 retry)
8. Return fallback error message on failure

### Phase 3: Routing Logic & Integration
9. Update `/ask` to:
   - Query index
   - Rewrite if score ≥ threshold
   - Log response
10. Update `/debug/ask` with metadata return
11. Confirm `/ask` and `/debug/ask` match the spec

### Phase 4: Testing
12. Test: high score → rewrite used
13. Test: low score → fallback
14. Test: model fails → retry, then error
15. Test: `/debug/ask` metadata is returned
16. Test: threshold changes take effect

### Phase 5: Final Polish
17. TODO comment to secure `/debug/ask`
18. (Deferred) Add caching
19. (Deferred) Add frontend integration
20. Document config + logging in `README`

---

## 🧩 Right-Sized Steps (Prompt-Ready)

### Step 1: Refactor Index Query
```text
Update `query()` to return:
{
  "text": "...",
  "score": 0.84
}
```

### Step 2: Add Threshold from ENV
```text
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
```

### Step 3: Extend Logging
```text
Add `score` and `response_type` to `log_interaction()` and DB.
```

### Step 4: Rewrite Utility
```text
Create `rewrite_answer(question, passage)` using Hugging Face API.
- Use token from `HF_API_TOKEN`
- Retry once
- Return None on fail
```

### Step 5: `/ask` Integration
```text
If score ≥ threshold:
- Call `rewrite_answer()`
- Return rewritten answer
Else:
- Return fallback
```

### Step 6: `/debug/ask`
```text
Return full context:
{
  "question": "...",
  "score": 0.83,
  "response_type": "rewrite",
  "raw_passage": "...",
  "final_response": "..."
}
```

### Step 7: Tests
```text
- High score: rewritten answer
- Low score: fallback
- Model fail: retry then fallback
- /debug/ask: metadata present
- ENV threshold works
```

---

## ✏️ Prompts Recap

### Prompt 1: Refactor Query
```text
Update the `query()` method in `HuggingFaceIndex` (in index.py) to return a dictionary with the best-matching text and its similarity score instead of a plain string.
```

### Prompt 2: Threshold Config
```text
Load a similarity threshold from env variable `SIMILARITY_THRESHOLD`, defaulting to 0.7.
```

### Prompt 3: Log Enhancements
```text
Extend `log_interaction()` to include `score` and `response_type`.
```

### Prompt 4: Rewrite Utility
```text
Create `rewrite_answer()` in `model/rewrite_utils.py` that:
- Sends prompt to Hugging Face
- Uses bearer token
- Returns rewritten text or None
```

### Prompt 5: Rewrite Decision Logic
```text
In `/ask`, rewrite only if score ≥ threshold, else fallback.
```

### Prompt 6: Debug Route
```text
Create `/debug/ask` POST route that returns:
- question, score, response_type, raw_passage, final_response
```

### Prompt 7: Testing Plan
```text
Write test cases for rewrite logic, fallback logic, model failure, and threshold behavior.
```

---

## ✅ Deliverables
- Clean, modular codebase
- Rewrite-integrated chatbot logic
- Logging + observability
- Debug tools for development
- Fully testable endpoints

---

## 🔐 Reminder
> Secure `/debug/ask` before production!

---

## 📅 Next Steps
Would you like help generating the code for one of the prompt chunks now?
