import openai
from pydantic import BaseModel
from config import OPENAI_API_KEY

class AskRequest(BaseModel):
    question: str

def fallback_response(question: str) -> str:
    """
    Generate a fallback response using OpenAI when the index doesn't have an answer.
    
    Args:
        question: The user's question
        
    Returns:
        A string containing the fallback response
    """
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
