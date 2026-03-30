"""
Vector Store Initialization Script

This script loads FAQ documents and creates the initial vector index.
Run this once before starting the chatbot to populate the knowledge base.
"""

import pandas as pd
from langchain_core.documents import Document
from backend.embeddings import EmbeddingService
from backend.vector_store import VectorStoreManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_faq_documents():
    """Load FAQ documents from CSV files."""
    documents = []
    
    # Load English FAQs
    try:
        logger.info("Loading English FAQs...")
        faq_en = pd.read_csv("data/faq_en.csv")
        
        for _, row in faq_en.iterrows():
            doc = Document(
                page_content=f"Question: {row['Question']}\nAnswer: {row['Answer']}",
                metadata={"source": "faq_en", "language": "en"}
            )
            documents.append(doc)
        
        logger.info(f"Loaded {len(faq_en)} English FAQ documents")
        
    except Exception as e:
        logger.error(f"Error loading English FAQs: {e}")
    
    # Load Arabic FAQs
    try:
        logger.info("Loading Arabic FAQs...")
        faq_ar = pd.read_csv("data/faq_ar.csv")
        
        for _, row in faq_ar.iterrows():
            doc = Document(
                page_content=f"Question: {row['Question']}\nAnswer: {row['Answer']}",
                metadata={"source": "faq_ar", "language": "ar"}
            )
            documents.append(doc)
        
        logger.info(f"Loaded {len(faq_ar)} Arabic FAQ documents")
        
    except Exception as e:
        logger.error(f"Error loading Arabic FAQs: {e}")
    
    return documents


def initialize_vector_store():
    """Initialize vector store with FAQ documents."""
    try:
        logger.info("=" * 50)
        logger.info("Starting Vector Store Initialization")
        logger.info("=" * 50)
        
        # Load documents
        documents = load_faq_documents()
        
        if not documents:
            logger.error("No documents loaded. Exiting.")
            return False
        
        logger.info(f"Total documents to process: {len(documents)}")
        
        # Initialize embedding service
        logger.info("Initializing embedding service...")
        embeddings_service = EmbeddingService()
        
        # Initialize vector store manager
        logger.info("Initializing vector store manager...")
        vector_store_manager = VectorStoreManager(embeddings_service)
        
        # Create index
        logger.info("Creating FAISS index...")
        success = vector_store_manager.create_index(documents)
        
        if not success:
            logger.error("Failed to create index")
            return False
        
        # Save index
        logger.info("Saving index to disk...")
        save_success = vector_store_manager.save_index("faiss_index")
        
        if not save_success:
            logger.error("Failed to save index")
            return False
        
        # Verify
        doc_count = vector_store_manager.get_document_count()
        logger.info(f"Vector store initialized with {doc_count} document chunks")
        
        logger.info("=" * 50)
        logger.info("✅ Vector Store Initialization Complete!")
        logger.info("=" * 50)
        
        return True
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = initialize_vector_store()
    
    if success:
        print("\n✓ Success! You can now start the chatbot.")
        print("\nTo start:")
        print("  Backend: uvicorn backend.main:app --reload")
        print("  Frontend: streamlit run frontend/streamlit_app.py")
    else:
        print("\n✗ Initialization failed. Check logs for details.")
