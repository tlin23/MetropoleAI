# load app from terminal: uvicorn main:app --reload 

from fastapi import FastAPI
from model.index import init_settings, load_index, SIMILARITY_THRESHOLD
from model.rewrite_utils import rewrite_answer
from utils.logging_utils import init_db, log_interaction
from utils.app_utils import AskRequest

app = FastAPI()

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
    if not index:
        answer = "No documents indexed yet."
        log_interaction(request.question, answer, score=0.0, response_type="error")
        return {"answer": answer}
    
    # Query now returns a dictionary with text and score
    query_result = index.query(request.question)
    raw_passage = query_result["text"]
    score = query_result["score"]

    if not raw_passage:
        answer = "No information found for this question."
        log_interaction(request.question, answer, score=0.0, response_type="error")
        return {"answer": answer}
    
    # Determine if we should rewrite the answer based on the similarity score
    if score >= SIMILARITY_THRESHOLD:
        # Try to rewrite the answer
        rewritten_answer = await rewrite_answer(request.question, raw_passage)
        
        if rewritten_answer:
            # Successfully rewrote the answer
            log_interaction(request.question, rewritten_answer, score=score, response_type="rewrite")
            return {"answer": rewritten_answer}
        else:
            # Failed to rewrite, use the raw passage as a fallback
            log_interaction(request.question, raw_passage, score=score, response_type="direct")
            return {"answer": raw_passage}
    else:
        # Score is below threshold, return a fallback message
        fallback_message = f"No strong match found in index. Query: '{request.question}'. Consider checking content coverage or reindexing."
        log_interaction(request.question, fallback_message, score=score, response_type="fallback")
        return {"answer": fallback_message}

@app.post("/debug/ask")
async def debug_ask(request: AskRequest):
    """
    Debug endpoint that returns detailed information about the query and response.
    This endpoint should be secured before production deployment.
    """
    if not index:
        return {
            "question": request.question,
            "score": 0.0,
            "response_type": "error",
            "raw_passage": None,
            "final_response": "No documents indexed yet."
        }
    
    # Query returns a dictionary with text and score
    query_result = index.query(request.question)
    raw_passage = query_result["text"]
    score = query_result["score"]
    
    if not raw_passage:
        return {
            "question": request.question,
            "score": 0.0,
            "response_type": "error",
            "raw_passage": None,
            "final_response": "No information found for this question."
        }
    
    # Determine response type and final response based on score
    if score >= SIMILARITY_THRESHOLD:
        # Try to rewrite the answer
        rewritten_answer = await rewrite_answer(request.question, raw_passage)
        
        if rewritten_answer:
            # Successfully rewrote the answer
            final_response = rewritten_answer
            response_type = "rewrite"
        else:
            # Failed to rewrite, use the raw passage as a fallback
            final_response = raw_passage
            response_type = "direct"
    else:
        # Score is below threshold, return a fallback message
        final_response = f"No strong match found in index. Query: '{request.question}'. Consider checking content coverage or reindexing."
        response_type = "fallback"
    
    # Log the interaction
    log_interaction(request.question, final_response, score=score, response_type=response_type)
    
    return {
        "question": request.question,
        "score": score,
        "response_type": response_type,
        "raw_passage": raw_passage,
        "final_response": final_response
    }
