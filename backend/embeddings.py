"""
Embeddings Module - Handles text embedding generation using Sentence Transformers

This module provides a wrapper around sentence-transformers API with error handling
and configurable parameters.
"""

import os
import logging
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using Sentence Transformers.
    
    Attributes:
        model_name: The embedding model to use (default: all-MiniLM-L6-v2)
        chunk_size: Number of texts to process in each batch
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", chunk_size: int = 16):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence-transformer embedding model
            chunk_size: Batch size for processing embeddings
        """
        self.model_name = model_name
        self.chunk_size = chunk_size
        self._model = None
        
        logger.info(f"Initialized embedding service with model: {model_name}")
    
    @property
    def model(self) -> SentenceTransformer:
        """
        Get or create the sentence-transformer model instance.
        
        Returns:
            SentenceTransformer: Configured model instance
        """
        if self._model is None:
            try:
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded sentence-transformer model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize embedding model: {e}")
                raise
        return self._model
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding, or None if failed
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True).tolist()
            logger.debug(f"Generated embedding for text of length: {len(text)}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True).tolist()
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return []
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            int: Dimension of the embedding vectors
        """
        # all-MiniLM-L6-v2 produces 384-dimensional vectors
        if "all-MiniLM-L6-v2" in self.model_name:
            return 384
        else:
            # Default fallback for other sentence-transformer models
            return 384
