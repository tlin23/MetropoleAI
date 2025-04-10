"""
Prompts used for rewriting retrieved passages into conversational, helpful answers.
"""

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
