"""
Groq LLM Service Module - Handles text generation using Groq API

This module provides a wrapper around Groq's LLM API with error handling
and configurable parameters for the UAE banking chatbot.
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class GroqLLMService:
    """
    Service for generating text responses using Groq API.
    
    Attributes:
        model_name: The LLM model to use (default: llama-3.1-8b-instant)
        temperature: Controls randomness (0.0-1.0)
        max_tokens: Maximum tokens in response
        client: Groq client instance
    """
    
    def __init__(
        self, 
        model_name: str = "llama-3.1-8b-instant",
        temperature: float = 0.2,
        max_tokens: int = 200
    ):
        """
        Initialize the Groq LLM service.
        
        Args:
            model_name: Name of the Groq model to use
            temperature: Sampling temperature for response generation (0.1-0.2 recommended for banking)
            max_tokens: Maximum number of tokens in response (150-200 recommended for short bullets)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
        
        # Strict parameters for consistent output
        if temperature > 0.2:
            logger.warning(f"Temperature {temperature} may cause inconsistent outputs. Recommended: 0.1-0.2")
        if max_tokens > 250:
            logger.warning(f"max_tokens {max_tokens} may cause verbose responses. Recommended: 150-200")
        
        # Verify API key is present
        if not os.getenv("GROQ_API_KEY"):
            logger.error("Groq API key not found in environment variables")
            raise ValueError("GROQ_API_KEY environment variable is required")
    
    @property
    def client(self):
        """
        Get or create the Groq client instance.
        
        Returns:
            Groq: Configured client instance
        """
        if self._client is None:
            try:
                from groq import Groq
                self._client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                logger.info(f"Initialized Groq client with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                raise
        return self._client
    
    def generate_response(
        self,
        messages: list[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of message dictionaries with role and content
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Generated response text or None if failed
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
                stream=False
            )
            
            final_answer = response.choices[0].message.content.strip()
            logger.debug(f"Generated response of length: {len(final_answer)}")
            return final_answer
            
        except Exception as e:
            logger.error(f"Error generating Groq response: {e}")
            return None
    
    def generate_with_context(
        self,
        system_prompt: str,
        user_query: str,
        context: Optional[str] = None,
        language: str = "English"
    ) -> Optional[str]:
        """
        Generate a response with system prompt and optional context.
        
        Args:
            system_prompt: System instruction for the AI
            user_query: User's question or message
            context: Optional context from RAG retrieval
            language: Response language preference
            
        Returns:
            Generated response text or None if failed
        """
        try:
            # Build messages array
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add context if provided (as assistant message for better control)
            if context:
                messages.append({
                    "role": "assistant",
                    "content": f"Context:\n{context}"
                })
            
            # Add user query
            messages.append({
                "role": "user",
                "content": user_query
            })
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False
            )
            
            final_answer = response.choices[0].message.content.strip()
            logger.debug(f"Generated contextual response of length: {len(final_answer)}")
            return final_answer
            
        except Exception as e:
            logger.error(f"Error generating contextual Groq response: {e}")
            return None


# Singleton instance
_groq_service = None


def get_groq_service(
    model_name: str = "llama-3.1-8b-instant",
    temperature: float = 0.2,
    max_tokens: int = 200
) -> GroqLLMService:
    """
    Get or create singleton Groq service instance.
    
    Args:
        model_name: Model to use
        temperature: Sampling temperature
        max_tokens: Maximum response tokens
        
    Returns:
        GroqLLMService instance
    """
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqLLMService(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
    return _groq_service
