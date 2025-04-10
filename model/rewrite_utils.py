"""
Utilities for rewriting retrieved passages into conversational, helpful answers.
"""

import os
import logging
import httpx
from typing import Optional, List, Dict, Union
from model.prompts import SYSTEM_PROMPT, get_user_prompt, get_user_prompt_multi

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API token from environment variable
HF_API_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

async def rewrite_answer(question: str, passages: List[Dict[str, Union[str, float]]]) -> Optional[str]:
    """
    Rewrite retrieved passages into a conversational, helpful answer using Hugging Face API.
    
    Args:
        question: The user's question
        passages: List of dictionaries with 'text' and 'score' keys
        
    Returns:
        The rewritten answer, or None if the API call fails
    """
    if not HF_API_TOKEN:
        logger.error("HF_TOKEN environment variable not set")
        return None
    
    # Get prompts from the prompts module
    system_prompt = SYSTEM_PROMPT
    user_prompt = get_user_prompt_multi(passages, question)
    
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
                await response.raise_for_status()
                data = await response.json()
                
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
