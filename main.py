# load app from terminal: uvicorn main:app --reload 

from fastapi import FastAPI
from model.index import init_settings, load_index
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
        log_interaction(request.question, answer)
        return {"answer": answer}
    
    answer = index.query(request.question)

    if not answer:
        answer = "No information found for this question."
    
    log_interaction(request.question, answer)
    return {"answer": answer}


