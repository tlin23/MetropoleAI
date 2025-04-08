"""
Index utilities for building and loading vector indices.
"""

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle
import logging
from typing import List, Dict, Optional, Union, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default model for sentence embeddings
DEFAULT_MODEL = "all-MiniLM-L6-v2"
DEFAULT_INDEX_DIR = "model/index"

class HuggingFaceIndex:
    """
    A class that wraps HuggingFace and FAISS functionality to provide
    similar capabilities to LlamaIndex.
    """
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        """
        Initialize the index with a sentence transformer model.
        
        Args:
            model_name: Name of the HuggingFace sentence transformer model to use
        """
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.texts = []
        self.storage_context = None
    
    def add_texts(self, texts: List[str]):
        """
        Add texts to the index.
        
        Args:
            texts: List of text strings to add
        """
        self.texts.extend(texts)
        embeddings = self.model.encode(texts)
        
        # Initialize FAISS index if it doesn't exist
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
        
        # Add embeddings to the index
        self.index.add(np.array(embeddings).astype('float32'))
    
    def as_query_engine(self):
        """
        Return self as a query engine to maintain compatibility with LlamaIndex API.
        """
        return self
    
    def query(self, query_text: str, top_k: int = 3) -> str:
        """
        Query the index with the given text.
        
        Args:
            query_text: The query text
            top_k: Number of top similar documents to retrieve
            
        Returns:
            str: Response from the query
        """
        if self.index is None or not self.texts:
            return "No documents indexed yet."
        
        # Encode the query
        query_embedding = self.model.encode([query_text])
        
        # Search the index
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k)
        
        # Get the most relevant texts
        relevant_texts = [self.texts[idx] for idx in indices[0]]
        
        # Combine the relevant texts into a response
        response = "\n\n".join([f"Document {i+1}:\n{text}" for i, text in enumerate(relevant_texts)])
        
        return response

class StorageContext:
    """
    A simple class to mimic LlamaIndex's StorageContext for persistence.
    """
    
    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
    
    @classmethod
    def from_defaults(cls, persist_dir: str):
        return cls(persist_dir)
    
    def persist(self, persist_dir: Optional[str] = None):
        """
        Save the storage context to disk.
        """
        if persist_dir is not None:
            self.persist_dir = persist_dir

# Build an index from a list of raw text strings
def build_index_from_texts(texts: List[str], index_dir: str = DEFAULT_INDEX_DIR) -> HuggingFaceIndex:
    """
    Build a vector index from a list of text strings and persist it to disk.
    
    Args:
        texts: List of text strings to index
        index_dir: Directory to save the index
        
    Returns:
        HuggingFaceIndex: The created index
    """
    logger.info(f"Building index from {len(texts)} texts")
    
    # Create index
    index = HuggingFaceIndex()
    index.add_texts(texts)
    
    # Create storage context
    storage_context = StorageContext(persist_dir=index_dir)
    index.storage_context = storage_context
    
    # Save index to disk
    os.makedirs(index_dir, exist_ok=True)
    
    # Save the FAISS index
    faiss.write_index(index.index, os.path.join(index_dir, "faiss.index"))
    
    # Save the texts
    with open(os.path.join(index_dir, "texts.pkl"), "wb") as f:
        pickle.dump(index.texts, f)
    
    # Save the model name
    with open(os.path.join(index_dir, "model.txt"), "w") as f:
        f.write(DEFAULT_MODEL)
    
    logger.info(f"Successfully saved index to {index_dir}")
    return index

# Load the index from disk
def load_index(index_dir: str = DEFAULT_INDEX_DIR) -> Optional[HuggingFaceIndex]:
    """
    Load a previously saved index from disk.
    
    Args:
        index_dir: Directory where the index is saved
        
    Returns:
        Optional[HuggingFaceIndex]: The loaded index, or None if not found
    """
    if not os.path.exists(index_dir):
        logger.warning(f"Index directory {index_dir} does not exist")
        return None
    
    try:
        # Load the model name
        with open(os.path.join(index_dir, "model.txt"), "r") as f:
            model_name = f.read().strip()
        
        # Create index with the saved model
        index = HuggingFaceIndex(model_name=model_name)
        
        # Load the FAISS index
        index.index = faiss.read_index(os.path.join(index_dir, "faiss.index"))
        
        # Load the texts
        with open(os.path.join(index_dir, "texts.pkl"), "rb") as f:
            index.texts = pickle.load(f)
        
        # Create storage context
        index.storage_context = StorageContext(persist_dir=index_dir)
        
        logger.info(f"Successfully loaded index from {index_dir}")
        return index
    except Exception as e:
        logger.error(f"Error loading index from {index_dir}: {e}")
        return None
