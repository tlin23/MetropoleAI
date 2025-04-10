"""
Index utilities for building and loading vector indices.
"""

import os
import logging
from typing import List, Optional

from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.core.storage import StorageContext
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.vector_stores.chroma.base import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LlamaIndex settings - disable LLM usage
def init_settings():
    """Initialize LlamaIndex settings to use HuggingFace embeddings and no LLM."""
    # Explicitly disable LLM usage
    Settings.llm = None
    # Use HuggingFace embeddings by default
    Settings.embed_model = HuggingFaceEmbedding(model_name=DEFAULT_MODEL)
    logger.info("LlamaIndex settings initialized with HuggingFace embeddings and no LLM")

# Default model for sentence embeddings
DEFAULT_MODEL = "all-MiniLM-L6-v2"
DEFAULT_INDEX_DIR = "model/index"

# Load similarity threshold from environment variable, default to 0.7
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))

class HuggingFaceIndex:
    """
    A class that wraps LlamaIndex functionality with HuggingFace embeddings.
    """
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        """
        Initialize the index with a HuggingFace embedding model.
        
        Args:
            model_name: Name of the HuggingFace model to use for embeddings
        """
        self.embed_model = HuggingFaceEmbedding(model_name=model_name)
        self.index = None
        self.storage_context = None
    
    def add_texts(self, texts: List[str]):
        """
        Add texts to the index.
        
        Args:
            texts: List of text strings to add
        """
        # Convert texts to LlamaIndex Document objects
        documents = [Document(text=text) for text in texts]
        
        # Create vector store index
        self.index = VectorStoreIndex.from_documents(
            documents, 
            embed_model=self.embed_model,
            storage_context=self.storage_context,
            store_nodes_override=True
        )
    
    def query(self, query_text: str, top_k: int = 3) -> list:
        """
        Query the index with the given text and return the top matches with their similarity scores.
        
        Args:
            query_text: The text to query
            top_k: Number of top results to return (default: 3)
            
        Returns:
            A list of dictionaries, each with a matching text and its similarity score:
            [
                {"text": "best matching text", "score": 0.84},
                {"text": "second best match", "score": 0.76},
                {"text": "third best match", "score": 0.65}
            ]
        """
        if self.index is None:
            return [{"text": "No documents indexed yet.", "score": 0.0}]
        
        # Create a response synthesizer that doesn't generate text
        response_synthesizer = get_response_synthesizer(
            response_mode="no_text"
        )
        
        # Create a query engine using the global Settings.llm (which is None)
        query_engine = self.index.as_query_engine(
            similarity_top_k=top_k,
            response_synthesizer=response_synthesizer
        )

        # Query the engine
        response = query_engine.query(query_text)
        source_nodes = response.source_nodes

        if not source_nodes:
            return [{"text": "No relevant information found.", "score": 0.0}]

        # Convert all nodes to dictionaries with text and score
        results = []
        for node in source_nodes:
            text = node.node.text
            score = node.score if hasattr(node, 'score') else 0.0
            results.append({
                "text": text,
                "score": score
            })
        
        # Sort by score in descending order (highest scores first)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results

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
    
    # Create directory if it doesn't exist
    os.makedirs(index_dir, exist_ok=True)
    
    # Create Chroma client and collection
    chroma_client = chromadb.PersistentClient(path=index_dir)
    chroma_collection = chroma_client.get_or_create_collection("metropole")
    
    # Create vector store
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # Create storage context
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Create index
    index = HuggingFaceIndex()
    index.storage_context = storage_context
    index.add_texts(texts)
    
    # Save the model name for future reference
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
        # Check if model.txt exists
        if not os.path.exists(os.path.join(index_dir, "model.txt")):
            logger.warning(f"model.txt not found in {index_dir}")
            return None
        
        # Load the model name
        with open(os.path.join(index_dir, "model.txt"), "r") as f:
            model_name = f.read().strip()
        
        # Create Chroma client and collection
        chroma_client = chromadb.PersistentClient(path=index_dir)
        try:
            chroma_collection = chroma_client.get_collection("metropole")
        except ValueError:
            logger.warning(f"Collection 'metropole' not found in {index_dir}")
            return None
        
        # Create vector store
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        # Create storage context
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Load the index
        vector_index = VectorStoreIndex.from_vector_store(
            vector_store,
            embed_model=HuggingFaceEmbedding(model_name=model_name)
        )
        
        # Create and return the wrapper
        index = HuggingFaceIndex(model_name=model_name)
        index.index = vector_index
        index.storage_context = storage_context
        
        logger.info(f"Successfully loaded index from {index_dir}")
        return index
    except Exception as e:
        logger.error(f"Error loading index from {index_dir}: {e}")
        return None
