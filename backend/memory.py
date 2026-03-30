"""
Memory Module - Manages conversation history and context

This module provides conversation memory management using LangChain's
ConversationBufferMemory with persistence capabilities.
"""

import logging
from typing import List, Tuple, Dict, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class ConversationMemoryManager:
    """
    Manager for conversation history and memory.
    
    Attributes:
        conversations: Dictionary storing conversation memories by ID
        max_history_length: Maximum number of messages to retain
    """
    
    def __init__(self, max_history_length: int = 10):
        """
        Initialize the conversation memory manager.
        
        Args:
            max_history_length: Maximum messages to keep in history
        """
        self.conversations: Dict[str, ConversationBufferMemory] = {}
        self.max_history_length = max_history_length
        logger.info("Initialized conversation memory manager")
    
    def create_conversation(self, conversation_id: Optional[str] = None) -> str:
        """
        Create a new conversation session.
        
        Args:
            conversation_id: Optional custom ID
            
        Returns:
            Conversation ID
        """
        if conversation_id is None:
            conversation_id = str(uuid4())
        
        # Initialize empty conversation history as a list of tuples
        self.conversations[conversation_id] = []
        logger.info(f"Created new conversation: {conversation_id}")
        
        return conversation_id
    
    def get_memory(self, conversation_id: str) -> Optional[List[Tuple[str, str]]]:
        """
        Get conversation history for a specific conversation.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            List of (user_message, ai_response) tuples or None if not found
        """
        history = self.conversations.get(conversation_id)
        
        if history is None:
            logger.warning(f"Conversation not found: {conversation_id}")
        
        return history
    
    def add_message(self, conversation_id: str, user_message: str, ai_response: str) -> bool:
        """
        Add a message pair to conversation history.
        
        Args:
            conversation_id: Conversation identifier
            user_message: User's message
            ai_response: AI's response
            
        Returns:
            bool: Success status
        """
        history = self.get_memory(conversation_id)
        
        if history is None:
            # Auto-create conversation if it doesn't exist
            conversation_id = self.create_conversation()
            history = self.conversations[conversation_id]
        
        try:
            # Add message pair to history
            history.append((user_message, ai_response))
            
            # Trim history if needed
            self._trim_history_by_id(conversation_id)
            
            logger.debug(f"Added message to conversation: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding message to memory: {e}")
            return False
    
    def get_history(self, conversation_id: str) -> List[Tuple[str, str]]:
        """
        Get conversation history as list of message pairs.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            List of (user_message, ai_message) tuples
        """
        history = self.get_memory(conversation_id)
        
        if history is None:
            return []
        
        logger.debug(f"Retrieved {len(history)} message pairs")
        return history
    
    def _trim_history_by_id(self, conversation_id: str):
        """
        Trim conversation history to maximum length.
        
        Args:
            conversation_id: Conversation identifier
        """
        try:
            history = self.conversations[conversation_id]
            
            if len(history) > self.max_history_length:
                # Keep only the most recent messages
                self.conversations[conversation_id] = history[-self.max_history_length:]
                logger.debug("Trimmed conversation history")
        except Exception as e:
            logger.error(f"Error trimming history: {e}")
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """
        Clear conversation history.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            bool: Success status
        """
        memory = self.get_memory(conversation_id)
        
        if memory is None:
            return False
        
        try:
            memory.clear()
            logger.info(f"Cleared conversation: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing conversation: {e}")
            return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete entire conversation session.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            bool: Success status
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Deleted conversation: {conversation_id}")
            return True
        
        logger.warning(f"Conversation not found for deletion: {conversation_id}")
        return False
    
    def get_conversation_count(self) -> int:
        """
        Get number of active conversations.
        
        Returns:
            int: Number of conversations
        """
        return len(self.conversations)
    
    def cleanup_old_conversations(self, max_conversations: int = 100):
        """
        Remove oldest conversations if exceeding limit.
        
        Args:
            max_conversations: Maximum conversations to keep
        """
        if len(self.conversations) > max_conversations:
            # Remove oldest conversations (FIFO)
            keys_to_remove = list(self.conversations.keys())[:len(self.conversations) - max_conversations]
            
            for key in keys_to_remove:
                del self.conversations[key]
            
            logger.info(f"Cleaned up {len(keys_to_remove)} old conversations")
