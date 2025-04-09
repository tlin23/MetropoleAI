import os
import re
import json
import glob
from typing import List, Dict, Any
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from nltk.tokenize import sent_tokenize

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
    
def smart_chunk(text: str, max_tokens: int = 100) -> List[str]:
    """
    Splits text into semantically coherent chunks, capped at approx max_tokens length.
    """
    # Split by newlines to preserve structure
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Group lines into sections based on headings or empty lines
    chunks = []
    current = []

    for line in lines:
        if re.match(r"^#{1,6} ", line) or line.endswith(':') or line.isupper():
            if current:
                chunks.append(" ".join(current))
                current = []
        current.append(line)
    if current:
        chunks.append(" ".join(current))

    # Split long sections into smaller chunks using sentences
    refined_chunks = []
    for chunk in chunks:
        sentences = sent_tokenize(chunk)
        buffer = ""
        for sentence in sentences:
            if len(buffer.split()) + len(sentence.split()) <= max_tokens:
                buffer += " " + sentence
            else:
                if buffer:
                    refined_chunks.append(buffer.strip())
                buffer = sentence
        if buffer:
            refined_chunks.append(buffer.strip())

    return refined_chunks

def extract_website_texts(metropole_pages: Dict[str, Any]) -> List[str]:
    # General-purpose splitter
    default_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ])

    website_texts = []
    for page in metropole_pages:
        content = page.get("content", "")
        title = page.get("title", "").lower()

        if content:
            if "board" in title or "roster" in content.lower():
                split_docs = markdown_splitter.split_text(content)
            else:
                split_docs = default_splitter.create_documents([content])
            
            # Convert LangChain Document objects into strings
            for doc in split_docs:
                text_chunk = doc.page_content
                website_texts.append(text_chunk)

    logger.info(f"Extracted {len(website_texts)} text chunks from metropole website")
    return website_texts