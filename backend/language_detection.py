"""
Language Detection Module - Automatically detects user language

This module uses langdetect to identify whether input text is in English or Arabic.
"""

import logging
from typing import Optional
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Set seed for consistent results
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


class LanguageDetector:
    """
    Service for detecting text language.
    
    Supports:
    - English (en)
    - Arabic (ar)
    """
    
    # Language codes we support
    SUPPORTED_LANGUAGES = {"en", "ar"}
    
    # Mapping from language codes to display names
    LANGUAGE_NAMES = {
        "en": "English",
        "ar": "Arabic"
    }
    
    @staticmethod
    def detect(text: str) -> Optional[str]:
        """
        Detect the language of input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Language code ('en' or 'ar') or None if undetectable
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for language detection")
            return None
        
        try:
            # Detect language
            detected_lang = detect(text)
            
            # Check if we support this language
            if detected_lang in LanguageDetector.SUPPORTED_LANGUAGES:
                logger.debug(f"Detected language: {detected_lang}")
                return detected_lang
            else:
                # Default to English for unsupported languages
                logger.warning(f"Unsupported language detected: {detected_lang}, defaulting to English")
                return "en"
                
        except LangDetectException as e:
            logger.error(f"Language detection failed: {e}")
            # Default to English on error
            return "en"
        except Exception as e:
            logger.error(f"Unexpected error in language detection: {e}")
            return "en"
    
    @staticmethod
    def get_language_name(language_code: str) -> str:
        """
        Get human-readable language name.
        
        Args:
            language_code: Language code (en/ar)
            
        Returns:
            Language name in English
        """
        return LanguageDetector.LANGUAGE_NAMES.get(language_code, "English")
    
    @staticmethod
    def is_arabic(text: str) -> bool:
        """
        Check if text is in Arabic.
        
        Args:
            text: Input text
            
        Returns:
            True if Arabic, False otherwise
        """
        lang = LanguageDetector.detect(text)
        return lang == "ar"
    
    @staticmethod
    def is_english(text: str) -> bool:
        """
        Check if text is in English.
        
        Args:
            text: Input text
            
        Returns:
            True if English, False otherwise
        """
        lang = LanguageDetector.detect(text)
        return lang == "en"
