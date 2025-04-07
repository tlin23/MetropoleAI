from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core.schema import Document
from llama_index.core.embeddings import MockEmbedding
import os

# Build an index from a list of raw text strings
def build_index_from_texts(texts: list[str], index_dir="index") -> VectorStoreIndex:
    # Use a mock embedding model that doesn't require external API keys
    embed_model = MockEmbedding(embed_dim=1536)  # Using a standard embedding dimension
    documents = [Document(text=t) for t in texts]
    index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    index.storage_context.persist(index_dir)
    return index

# Load the index from disk
def load_index(index_dir="index") -> VectorStoreIndex | None:
    if os.path.exists(index_dir):
        # Use the same mock embedding model
        embed_model = MockEmbedding(embed_dim=1536)
        storage_context = StorageContext.from_defaults(persist_dir=index_dir)
        return load_index_from_storage(storage_context, embed_model=embed_model)
    return None
