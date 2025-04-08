# load app from terminal: uvicorn main:app --reload 

from fastapi import FastAPI
from pydantic import BaseModel
from utils.index_utils import load_index

import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Load index into memory once on app startup
index = load_index()

@app.get("/ping")
async def ping():
    return {"status": "ok"}

class AskRequest(BaseModel):
    question: str

def fallback_response(question: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if you're using GPT-4
        messages=[
            {"role": "system", "content": "You are a helpful assistant for apartment residents."},
            {"role": "user", "content": question}
        ],
        temperature=0.7
    )

    answer = response['choices'][0]['message']['content']
    return "This is based on general knowledge and not specific to the building.\n" + answer

# 
@app.post("/ask")
async def ask(request: AskRequest):
    if not index:
        return {"answer": "No documents indexed yet."}
    
    query_engine = index.as_query_engine()
    response = query_engine.query(request.question)
    answer = str(response).strip()

    if not answer:
        return {"answer": fallback_response(request.question)}

    return {"answer": str(response)}



