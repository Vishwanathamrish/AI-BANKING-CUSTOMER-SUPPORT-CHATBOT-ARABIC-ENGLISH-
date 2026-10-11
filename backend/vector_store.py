"""
Vector Store Module - Manages FAISS vector database operations

This module handles storing and retrieving embeddings using FAISS,
including persistence to disk.
"""

import os
import logging
from typing import List, Tuple, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from dotenv import load_dotenv

from .embeddings import EmbeddingService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manager for FAISS vector store operations.
    
    Attributes:
        embeddings_service: Service for generating embeddings
        vector_db_path: Path to save/load the vector database
        index: FAISS index instance
    """
    
    def __init__(self, embeddings_service: EmbeddingService, vector_db_path: str = "./vector_db"):
        """
        Initialize the vector store manager.
        
        Args:
            embeddings_service: EmbeddingService instance
            vector_db_path: Directory path for saving/loading vector DB
        """
        self.embeddings_service = embeddings_service
        self.vector_db_path = vector_db_path
        self.index: Optional[FAISS] = None
        
        # Ensure vector db directory exists
        os.makedirs(vector_db_path, exist_ok=True)
    
    def create_index(self, documents: List[Document]) -> bool:
        """
        Create a new FAISS index from documents.
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Creating FAISS index with {len(documents)} documents")
            
            self.index = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings_service
            )
            
            logger.info("FAISS index created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating FAISS index: {e}")
            return False
    
    def add_documents(self, documents: List[Document]) -> bool:
        """
        Add documents to existing index.
        
        Args:
            documents: List of Document objects to add
            
        Returns:
            bool: Success status
        """
        if self.index is None:
            logger.error("Cannot add documents: No index exists")
            return False
        
        try:
            self.index.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to index")
            return True
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False
    
    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            k: Number of results to return
            
        Returns:
            List of most relevant Document objects
        """
        if self.index is None:
            logger.error("Cannot search: No index loaded")
            return []
        
        try:
            docs = self.index.similarity_search(query, k=k)
            logger.debug(f"Found {len(docs)} similar documents")
            return docs
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def similarity_search_with_score(self, query: str, k: int = 3) -> List[Tuple[Document, float]]:
        """
        Search for similar documents with relevance scores.
        
        Args:
            query: Search query text
            k: Number of results to return
            
        Returns:
            List of tuples (Document, score) where lower score = more relevant
        """
        if self.index is None:
            logger.error("Cannot search: No index loaded")
            return []
        
        try:
            results = self.index.similarity_search_with_score(query, k=k)
            logger.debug(f"Found {len(results)} results with scores")
            return results
        except Exception as e:
            logger.error(f"Error in similarity search with score: {e}")
            return []
    
    def save_index(self, index_name: str = "faiss_index") -> bool:
        """
        Save the index to disk.
        
        Args:
            index_name: Name for the saved index
            
        Returns:
            bool: Success status
        """
        if self.index is None:
            logger.error("Cannot save: No index to save")
            return False
        
        try:
            save_path = os.path.join(self.vector_db_path, index_name)
            self.index.save_local(save_path)
            logger.info(f"Index saved to: {save_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            return False
    
    def load_index(self, index_name: str = "faiss_index") -> bool:
        """
        Load index from disk.
        
        Args:
            index_name: Name of the index to load
            
        Returns:
            bool: Success status
        """
        try:
            load_path = os.path.join(self.vector_db_path, index_name)
            
            if not os.path.exists(load_path):
                logger.warning(f"Index not found at: {load_path}")
                return False
            
            self.index = FAISS.load_local(
                folder_path=load_path,
                embeddings=self.embeddings_service
            )

            index_dimension = self.index.index.d
            embedding_dimension = self.embeddings_service.get_embedding_dimension()
            if index_dimension != embedding_dimension:
                logger.error(
                    "Vector index dimension mismatch: index=%s, embedding_model=%s. "
                    "Rebuild the index with initialize_vectorstore.py.",
                    index_dimension,
                    embedding_dimension,
                )
                self.index = None
                return False
            
            logger.info(f"Index loaded from: {load_path}")
            return True
            
        except Exception as e:
            logger.exception("Error loading index: %r", e)
            return False
    
    def index_exists(self, index_name: str = "faiss_index") -> bool:
        """
        Check if an index exists on disk.
        
        Args:
            index_name: Name of the index
            
        Returns:
            bool: True if index exists
        """
        index_path = os.path.join(self.vector_db_path, index_name)
        return os.path.exists(index_path)
    
    def get_document_count(self) -> int:
        """
        Get the number of documents in the index.
        
        Returns:
            int: Number of documents, or 0 if no index
        """
        if self.index is None:
            return 0
        
        try:
            return self.index.index.ntotal
        except Exception:
            return 0
