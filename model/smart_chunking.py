#!/usr/bin/env python3
"""
Smart chunking module for Metropole chatbot.
This module implements improved chunking logic for the Metropole chatbot,
breaking long text into semantically focused, metadata-rich chunks.
"""

import os
import re
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
import spacy
from transformers import AutoTokenizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load spaCy model for sentence segmentation
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("spaCy model not found. Downloading en_core_web_sm...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# Load tokenizer for token counting
#tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")

# Define section heading patterns
SECTION_HEADING_PATTERNS = [
    r'^#\s+', r'^##\s+', r'^###\s+',  # Markdown headings
    r'^Board\s+\d{4}',  # Board 2024
    r'^Newsletter',
    r'^Blog',
    r'^Contact',
    r'^Security',
    r'^Waste\s+&\s+Recycling'
]

# Define contact info patterns
CONTACT_INFO_PATTERNS = [
    r'Unit\s+\d+',  # Unit 22
    r'Seat\s+\d+',  # Seat 5
    r'\(\d{4}\)',   # (2024)
    r'@',           # Email
    r'\d{3}[-\s]?\d{3}[-\s]?\d{4}'  # Phone number
]

def load_metropole_pages(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Load and validate Metropole pages from JSON data.
    
    Args:
        pages: List of page dictionaries from JSON
        
    Returns:
        List of validated and cleaned page dictionaries
    """
    valid_pages = []
    
    for page in pages:
        # Check for required fields
        if not all(key in page for key in ['title', 'url', 'content']):
            logger.warning(f"Skipping page missing required fields: {page.get('url', 'unknown')}")
            continue
            
        # Clean and normalize fields
        cleaned_page = {
            'title': page['title'].strip(),
            'url': page['url'].strip(),
            'content': page['content'].strip()
        }
        
        # Skip pages with empty content
        if not cleaned_page['content']:
            logger.warning(f"Skipping page with empty content: {cleaned_page['url']}")
            continue
            
        valid_pages.append(cleaned_page)
    
    logger.info(f"Loaded {len(valid_pages)} valid pages out of {len(pages)} total")
    return valid_pages

def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text
    """
    # Remove markdown headers (e.g., "# Heading" -> "Heading")
    text = re.sub(r'^#+ +', '', text, flags=re.MULTILINE)
    
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n{2,}', '\n', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_breadcrumb(title: str, content: str) -> str:
    """
    Extract breadcrumb from title or content headings.
    
    Args:
        title: Page title
        content: Page content
        
    Returns:
        Breadcrumb string
    """
    # Check title first
    for pattern in SECTION_HEADING_PATTERNS:
        if re.search(pattern, title, re.IGNORECASE):
            return title
    
    # Check first few lines of content
    first_lines = content.split('\n')[:5]
    for line in first_lines:
        for pattern in SECTION_HEADING_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                return line.strip()
    
    # Fallback to title
    return title

def split_sentences(text: str) -> List[str]:
    """
    Split text into sentences using spaCy.
    
    Args:
        text: Text to split
        
    Returns:
        List of sentences
    """
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    return sentences

def is_contact_info(text: str) -> bool:
    """
    Check if text contains contact information.
    
    Args:
        text: Text to check
        
    Returns:
        True if text contains contact info, False otherwise
    """
    # Count matches of contact info patterns
    match_count = 0
    for pattern in CONTACT_INFO_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            match_count += 1
    
    # If we have at least 2 matches, consider it contact info
    return match_count >= 2

def count_tokens(text: str) -> int:
    """
    Count tokens in text using the tokenizer.
    
    Args:
        text: Text to count tokens for
        
    Returns:
        Number of tokens
    """
    return len(tokenizer.encode(text))

def chunk_sentences(sentences: List[str], max_tokens: int = 512) -> List[List[str]]:
    """
    Group sentences into chunks based on token limit.
    
    Args:
        sentences: List of sentences
        max_tokens: Maximum tokens per chunk
        
    Returns:
        List of sentence groups (chunks)
    """
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    i = 0
    while i < len(sentences):
        sentence = sentences[i]
        sentence_tokens = count_tokens(sentence)
        
        # Handle very long sentences
        if sentence_tokens > max_tokens:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
                current_tokens = 0
            
            # Add long sentence as its own chunk
            chunks.append([sentence])
            i += 1
            continue
        
        # Check if adding this sentence would exceed the token limit
        if current_tokens + sentence_tokens <= max_tokens:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
            i += 1
        else:
            # Start a new chunk
            chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0
        
        # Check for contact info patterns
        if i < len(sentences) and is_contact_info('\n'.join(sentences[i:i+4])):
            # If we have a current chunk, save it
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
                current_tokens = 0
            
            # Create a contact info chunk (up to 4 lines)
            contact_chunk = []
            contact_tokens = 0
            
            for j in range(i, min(i+4, len(sentences))):
                contact_sentence = sentences[j]
                contact_tokens += count_tokens(contact_sentence)
                contact_chunk.append(contact_sentence)
                
                if contact_tokens > max_tokens:
                    break
            
            chunks.append(contact_chunk)
            i += len(contact_chunk)
            current_chunk = []
            current_tokens = 0
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def format_chunks(chunks: List[List[str]], breadcrumb: str, url: str) -> List[Dict]:
    """
    Format chunks with metadata.
    
    Args:
        chunks: List of sentence groups
        breadcrumb: Breadcrumb string
        url: Source URL
        
    Returns:
        List of formatted chunks with metadata
    """
    formatted_chunks = []
    
    for chunk_sentences in chunks:
        # Join sentences into a single text
        text = ' '.join(chunk_sentences)
        
        # Prepend breadcrumb
        prefixed_text = f"{breadcrumb} > {text}"
        
        # Count tokens
        token_count = count_tokens(prefixed_text)
        
        # Create chunk with metadata
        chunk = {
            "text": prefixed_text,
            "metadata": {
                "breadcrumb": breadcrumb,
                "source_url": url,
                "tokens": token_count
            }
        }
        
        formatted_chunks.append(chunk)
    
    return formatted_chunks

def write_chunks_debug(chunks: List[Dict], path: str) -> None:
    """
    Write chunks to a debug file.
    
    Args:
        chunks: List of chunks with metadata
        path: Path to write to
    """
    with open(path, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"--- Chunk {i+1} ---\n")
            f.write(f"{chunk['text']}\n")
            f.write(f"[breadcrumb={chunk['metadata']['breadcrumb']}, ")
            f.write(f"source_url={chunk['metadata']['source_url']}, ")
            f.write(f"tokens={chunk['metadata']['tokens']}]\n\n")
    
    logger.info(f"Saved {len(chunks)} chunks to {path}")

def smart_chunk_metropole_pages(pages: List[Dict[str, Any]], max_tokens: int = 512, 
                               debug_path: Optional[str] = None) -> List[str]:
    """
    Process Metropole pages into smart chunks.
    
    Args:
        pages: List of page dictionaries
        max_tokens: Maximum tokens per chunk
        debug_path: Optional path to write debug file
        
    Returns:
        List of chunk texts
    """
    all_chunks = []
    
    # Load and validate pages
    valid_pages = load_metropole_pages(pages)
    
    for page in valid_pages:
        title = page['title']
        url = page['url']
        content = page['content']
        
        # Clean content
        cleaned_content = clean_text(content)
        
        # Extract breadcrumb
        breadcrumb = extract_breadcrumb(title, cleaned_content)
        
        # Split content into sentences
        sentences = split_sentences(cleaned_content)
        
        # Group sentences into chunks
        sentence_chunks = chunk_sentences(sentences, max_tokens)
        
        # Format chunks with metadata
        page_chunks = format_chunks(sentence_chunks, breadcrumb, url)
        
        all_chunks.extend(page_chunks)
    
    # Write debug file if path is provided
    if debug_path:
        write_chunks_debug(all_chunks, debug_path)
    
    # Return only the text part of each chunk
    return [chunk["text"] for chunk in all_chunks]
