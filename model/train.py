#!/usr/bin/env python3
"""
Script to train the model by building the index from text extracted from the metropole website.
Usage: python -m model.train
"""

import os
import json
import logging
import glob
from typing import List, Dict, Any
from model.index import build_index_from_texts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_latest_metropole_data() -> List[Dict[str, Any]]:
    """
    Get the latest crawled data from the metropole website.
    
    Returns:
        List of page data dictionaries containing url, title, and content
    """
    logger.info("Getting latest metropole website data...")
    
    # Find the most recent JSON file in the metropole_crawler/data directory
    data_dir = "metropole_crawler/data"
    json_files = glob.glob(f"{data_dir}/metropole_site_data_*.json")
    
    if not json_files:
        logger.warning("No metropole website data found.")
        return []
    
    # Sort files by modification time (newest first)
    latest_file = max(json_files, key=os.path.getmtime)
    logger.info(f"Found latest metropole data file: {latest_file}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pages = data.get('pages', [])
        logger.info(f"Loaded {len(pages)} pages from metropole website data")
        return pages
    except Exception as e:
        logger.error(f"Error loading metropole website data: {str(e)}")
        return []

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
        website_texts = []
        for page in metropole_pages:
            title = page.get('title', '')
            content = page.get('content', '')
            url = page.get('url', '')
            
            if content:
                # Add title and URL as context
                formatted_content = f"Title: {title}\nURL: {url}\n\n{content}"
                # Split content into paragraphs
                paragraphs = [p for p in formatted_content.split('\n\n') if p.strip()]
                website_texts.extend(paragraphs)
        
        logger.info(f"Extracted {len(website_texts)} text chunks from metropole website")
        all_texts.extend(website_texts)
    
    if not all_texts:
        logger.error("No text could be extracted from any source. Aborting.")
        return
    
    # Build the index from the extracted texts
    logger.info(f"Building index from {len(all_texts)} text chunks...")
    index = build_index_from_texts(all_texts, index_dir)
    
    logger.info(f"Model training complete. Index saved to {index_dir}")
    logger.info(f"Total documents indexed: {len(all_texts)}")

if __name__ == "__main__":
    # Run the training process
    train_model()
