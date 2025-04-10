"""
Utilities for rewriting retrieved passages into conversational, helpful answers.
"""

import os
import logging
import httpx
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API token from environment variable
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

async def rewrite_answer(question: str, passage: str) -> Optional[str]:
    """
    Rewrite a retrieved passage into a conversational, helpful answer using Hugging Face API.
    
    Args:
        question: The user's question
        passage: The retrieved passage to rewrite
        
    Returns:
        The rewritten answer, or None if the API call fails
    """
    if not HF_API_TOKEN:
        logger.error("HF_API_TOKEN environment variable not set")
        return None
    
    # System prompt and user prompt
    system_prompt = "You are a helpful assistant for residents at The Metropole building in Seattle. Always speak clearly, stay friendly but focused, and avoid overly general language."
    user_prompt = f"Rewrite the following passage into a clear, helpful answer for a resident's question.\n\nPassage: {passage}\n\nQuestion: {question}"
    
    # Prepare the payload
    payload = {
        "inputs": {
            "system": system_prompt,
            "text": user_prompt
        },
        "parameters": {"max_new_tokens": 300},
        "options": {"use_cache": True, "wait_for_model": True}
    }
    
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    # Try the API call with one retry
    for attempt in range(2):  # Try twice (original + 1 retry)
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(HF_MODEL_URL, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Extract the generated text
                generated_text = data.get("generated_text", "").strip()
                if generated_text:
                    logger.info(f"Successfully rewrote answer on attempt {attempt + 1}")
                    return generated_text
                else:
                    logger.warning(f"Empty response from Hugging Face API on attempt {attempt + 1}")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error on attempt {attempt + 1}: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Request error on attempt {attempt + 1}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
        
        # If this was the first attempt, log that we're retrying
        if attempt == 0:
            logger.info("Retrying Hugging Face API call...")
    
    # If we get here, both attempts failed
    logger.error("Failed to rewrite answer after retry")
    return None
