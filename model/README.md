# Metropole.AI Chatbot Model

This directory contains the model components for the Metropole.AI chatbot, including the vector index, retrieval logic, and response rewriting functionality.

## Overview

The Metropole.AI chatbot uses a two-stage approach to answer questions:

1. **Retrieval**: Using LlamaIndex with HuggingFace embeddings to find the most relevant passage from the indexed content.
2. **Rewriting**: Using a hosted LLM (Zephyr-7b-beta) to rewrite the retrieved passage into a conversational, helpful answer.

## Configuration

The system can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SIMILARITY_THRESHOLD` | Minimum similarity score required to rewrite a passage | `0.7` |
| `HF_TOKEN` | Hugging Face API token for accessing the rewrite model | (required) |
| `DB_PATH` | Path to the SQLite database for logging | `chat_logs.db` |

### Setting Environment Variables

```bash
# Example .env file
SIMILARITY_THRESHOLD=0.75
HF_TOKEN=your_huggingface_token
DB_PATH=/path/to/logs.db
```

## Logging

The system logs all interactions to a SQLite database with the following schema:

```sql
CREATE TABLE chat_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    question TEXT,
    response TEXT,
    score REAL,
    response_type TEXT
)
```

### Response Types

The `response_type` field in the logs can have the following values:

- `rewrite`: The response was rewritten by the LLM
- `direct`: The raw passage was returned (usually when rewrite fails)
- `fallback`: The score was below the threshold, so a fallback message was returned
- `error`: An error occurred during processing

### Querying Logs

You can query the logs using SQLite:

```bash
sqlite3 chat_logs.db "SELECT * FROM chat_logs ORDER BY timestamp DESC LIMIT 10"
```

Or to get statistics on response types:

```bash
sqlite3 chat_logs.db "SELECT response_type, COUNT(*) FROM chat_logs GROUP BY response_type"
```

## API Endpoints

### `/ask` (POST)

Regular endpoint for answering questions.

**Request:**
```json
{
  "question": "What are the pool hours?"
}
```

**Response:**
```json
{
  "answer": "The pool is open from 6am to 10pm Monday through Friday, and 8am to 9pm on weekends. Don't forget to bring your key fob to access the pool area!"
}
```

### `/debug/ask` (POST)

Debug endpoint that returns additional metadata.

**Request:**
```json
{
  "question": "What are the pool hours?"
}
```

**Response:**
```json
{
  "question": "What are the pool hours?",
  "score": 0.85,
  "response_type": "rewrite",
  "raw_passage": "The pool is open from 6am to 10pm on weekdays, and 8am to 9pm on weekends. Residents must have their key fob to access the pool area.",
  "final_response": "The pool is open from 6am to 10pm Monday through Friday, and 8am to 9pm on weekends. Don't forget to bring your key fob to access the pool area!"
}
```

> **Security Note**: The `/debug/ask` endpoint should be secured before production deployment.

## Testing

Run the tests with pytest:

```bash
pytest tests/test_rewrite.py -v
```

The tests cover:
- Rewrite functionality
- Fallback logic
- Error handling
- Threshold behavior
- Debug endpoint
