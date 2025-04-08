#!/usr/bin/env python3
"""
Script to train the model by building the index from PDFs in Google Drive.
Usage: python -m model.train
"""

import os
import logging
from typing import List
from config import FOLDER_ID
from utils.drive_utils import list_pdfs, download_pdf_and_extract_text
from model.index import build_index_from_texts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def train_model(folder_id: str = FOLDER_ID, index_dir: str = "model/index") -> None:
    """
    Train the model by building the index from PDFs in Google Drive.
    
    Args:
        folder_id: The ID of the Google Drive folder containing PDFs
        index_dir: Directory to save the index
    """
    logger.info("Starting model training process...")
    
    # Step 1: List all PDFs in the Google Drive folder
    logger.info(f"Listing PDFs in Google Drive folder: {folder_id}")
    pdf_files = list_pdfs(folder_id)
    
    if not pdf_files:
        logger.warning("No PDF files found in the specified folder.")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files.")
    
    # Step 2: Download and extract text from each PDF
    all_texts = []
    for pdf in pdf_files:
        logger.info(f"Processing PDF: {pdf['name']} (ID: {pdf['id']})")
        text = download_pdf_and_extract_text(pdf['id'])
        
        if not text:
            logger.warning(f"Failed to extract text from PDF: {pdf['name']}")
            continue
        
        # Split text into chunks (optional, depending on your needs)
        # For simplicity, we'll use a basic paragraph-based approach
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        logger.info(f"Extracted {len(paragraphs)} paragraphs from {pdf['name']}")
        all_texts.extend(paragraphs)
    
    if not all_texts:
        logger.error("No text could be extracted from any PDF. Aborting.")
        return
    
    # Step 3: Build the index from the extracted texts
    logger.info(f"Building index from {len(all_texts)} text chunks...")
    index = build_index_from_texts(all_texts, index_dir)
    
    logger.info(f"Model training complete. Index saved to {index_dir}")
    logger.info(f"Total documents indexed: {len(all_texts)}")

if __name__ == "__main__":
    # Check if service account file exists
    if not os.path.exists('service_account.json'):
        logger.error("service_account.json file not found. Please create this file with your Google Drive API credentials.")
        exit(1)
    
    # Check if FOLDER_ID is set
    if not FOLDER_ID:
        logger.error("FOLDER_ID environment variable not set. Please set this to the ID of your Google Drive folder.")
        exit(1)
    
    # Run the training process
    train_model()
