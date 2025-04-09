"""
Index utilities for building and loading vector indices.
"""

import os
import logging
from typing import List, Optional

from llama_index.core import VectorStoreIndex, Document
from llama_index.core.storage import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default model for sentence embeddings
DEFAULT_MODEL = "all-MiniLM-L6-v2"
DEFAULT_INDEX_DIR = "model/index"

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
    
    def as_query_engine(self):
        """
        Return a query engine for the index.
        """
        if self.index is None:
            logger.warning("No index available for querying")
            return self
        
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
        if self.index is None:
            return "No documents indexed yet."
        
        from llama_index.core.response_synthesizers import get_response_synthesizer
        
        # Create a response synthesizer that just returns the text
        response_synthesizer = get_response_synthesizer(
            response_mode="no_text",  # Just return the nodes without generating text
        )
        
        # Create a query engine with similarity top k and the response synthesizer
        query_engine = self.index.as_query_engine(
            similarity_top_k=top_k,
            response_synthesizer=response_synthesizer
        )
        
        # Get response
        response = query_engine.query(query_text)
        
        # Extract source nodes
        source_nodes = response.source_nodes
        
        if not source_nodes:
            return "No relevant information found."
        
        # Format the response with the source texts
        relevant_texts = [node.node.text for node in source_nodes]
        formatted_response = "\n\n".join([f"ANSWER {i+1}:\n{text}" for i, text in enumerate(relevant_texts)])
        
        return formatted_response

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
