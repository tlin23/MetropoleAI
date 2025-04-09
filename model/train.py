#!/usr/bin/env python3
"""
Script to train the model by building the index from text extracted from the metropole website.
Usage: python -m model.train
"""



import os
import logging
from model.index import build_index_from_texts
from model.utils import get_latest_metropole_data, extract_website_texts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def train_model(index_dir: str = "model/index") -> None:
    """
    Train the model by building the index from text extracted from the metropole website.
    
    Args:
        index_dir: Directory to save the index
    """
    logger.info("Starting model training process...")
    all_texts = []
    
    # Extract text from metropole website
    metropole_pages = get_latest_metropole_data()
    
    if metropole_pages:
        website_texts = extract_website_texts(metropole_pages)
        all_texts.extend(website_texts)
    
    if not all_texts:
        logger.error("No text could be extracted from any source. Aborting.")
        return
    
    # Save all extracted text chunks for debugging
    debug_path = os.path.join(index_dir, "chunks.txt")
    with open(debug_path, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(all_texts):
            f.write(f"--- Chunk {i+1} ---\n{chunk}\n\n")
    logger.info(f"Saved chunks to {debug_path}")
    
    # Build the index from the extracted texts
    logger.info(f"Building index from {len(all_texts)} text chunks...")
    index = build_index_from_texts(all_texts, index_dir)
    
    logger.info(f"Model training complete. Index saved to {index_dir}")
    logger.info(f"Total documents indexed: {len(all_texts)}")

if __name__ == "__main__":
    # Run the training process
    train_model()
