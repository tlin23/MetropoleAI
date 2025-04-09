# load app from terminal: uvicorn main:app --reload 

from fastapi import FastAPI
from model.index import load_index
from utils.logging_utils import init_db, log_interaction
from utils.app_utils import AskRequest

app = FastAPI()

# Initialize database on startup
init_db()

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
    
    query_engine = index.as_query_engine()
    response = query_engine.query(request.question)
    answer = str(response).strip()

    if not answer:
        answer = "No information found for this question."
    
    log_interaction(request.question, answer)
    return {"answer": answer}
