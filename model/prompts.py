"""
Prompts used for rewriting retrieved passages into conversational, helpful answers.
"""
from typing import List, Dict, Union

# System prompt for the rewriting model
SYSTEM_PROMPT = """
    You are a helpful assistant for residents at The Metropole building in Seattle. 
    Always speak clearly, stay friendly but focused, and avoid overly general language.
"""

# Template for the user prompt
def get_user_prompt(passage: str, question: str) -> str:
    """
    Generate the user prompt for the rewriting model.
    
    Args:
        passage: The retrieved passage to rewrite
        question: The user's question
        
    Returns:
        The formatted user prompt
    """
    return f"""
        Rewrite the following passage into a clear, helpful answer for a resident's question.\n\n
        
        Passage: {passage}\n\n
        
        Question: {question}
    """

# Template for the user prompt with multiple passages
def get_user_prompt_multi(passages: List[Dict[str, Union[str, float]]], question: str) -> str:
    """
    Generate the user prompt for the rewriting model with multiple passages.
    
    Args:
        passages: List of dictionaries with 'text' and 'score' keys
        question: The user's question
        
    Returns:
        The formatted user prompt with multiple passages
    """
    # Sort passages by score in descending order
    sorted_passages = sorted(passages, key=lambda x: x["score"], reverse=True)
    
    # Format each passage with its score
    formatted_passages = ""
    for i, passage in enumerate(sorted_passages, 1):
        formatted_passages += f"Passage {i} (Score: {passage['score']:.2f}):\n{passage['text']}\n\n"
    
    return f"""
        You have the following passages retrieved from a knowledge base. Use the most relevant information to answer the resident's question clearly and helpfully.

        {formatted_passages}
        Question: {question}
    """
