# load app from terminal: uvicorn main:app --reload 
import os
import json

from fastapi import FastAPI
from model.index import init_settings, load_index, SIMILARITY_THRESHOLD
from model.rewrite_utils import rewrite_answer
from utils.logging_utils import init_db, log_interaction
from utils.app_utils import AskRequest
from dotenv import load_dotenv

app = FastAPI()

#load environment variables defined in .env
load_dotenv()

# Initialize database on startup
init_db()

# Initialize LlamaIndex settings to use HuggingFace embeddings and no LLM
init_settings()

# Load index into memory once on app startup
index = load_index()

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/ask")
async def ask(request: AskRequest):
    """
    Enhanced endpoint that retrieves top 3 matches, filters by similarity threshold,
    and returns detailed information about the query and response.
    """
    if not index:
        final_response = "No documents indexed yet."
        log_interaction(request.question, final_response, score=0.0, response_type="error")
        return {
            "question": request.question,
            "score": 0.0,
            "response_type": "error",
            "raw_passages": [],
            "filtered_out": [],
            "final_response": final_response
        }
    
    # Query now returns a list of dictionaries with text and score
    raw_passages = index.query(request.question, top_k=3)
    
    if not raw_passages:
        final_response = "No information found for this question."
        log_interaction(request.question, final_response, score=0.0, response_type="error")
        return {
            "question": request.question,
            "score": 0.0,
            "response_type": "error",
            "raw_passages": [],
            "filtered_out": [],
            "final_response": final_response
        }
    
    # Filter passages based on similarity threshold
    retained_passages = []
    filtered_out = []
    
    for passage in raw_passages:
        if passage["score"] >= SIMILARITY_THRESHOLD:
            retained_passages.append(passage)
        else:
            filtered_out.append(passage)
    
    # Sort retained passages by score (highest first)
    retained_passages.sort(key=lambda x: x["score"], reverse=True)
    
    # Get the highest score (if any passages were retained)
    top_score = retained_passages[0]["score"] if retained_passages else 0.0
    
    # Determine response type and final response
    if retained_passages:
        # Try to rewrite the answer using all retained passages
        rewritten_answer = await rewrite_answer(request.question, retained_passages)
        
        if rewritten_answer:
            # Successfully rewrote the answer
            final_response = rewritten_answer
            response_type = "rewrite"
        else:
            # Failed to rewrite, use the top passage as a fallback
            final_response = retained_passages[0]["text"]
            response_type = "direct"
    else:
        # No passages above threshold, return a fallback message
        final_response = f"No strong match found in index. Query: '{request.question}'. Consider checking content coverage or reindexing."
        response_type = "fallback"
    
    # Log the interaction with raw_passages and filtered_out as JSON strings
    log_interaction(
        request.question, 
        final_response, 
        score=top_score, 
        response_type=response_type,
        raw_passages=json.dumps(retained_passages),
        filtered_out=json.dumps(filtered_out)
    )
    
    return {
        "question": request.question,
        "score": top_score,
        "response_type": response_type,
        "raw_passages": retained_passages,
        "filtered_out": filtered_out,
        "final_response": final_response
    }
