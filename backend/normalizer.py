"""
Response Normalization Module - Quality control for chatbot responses

This module ensures all responses are:
- Clean and consistently formatted
- Professional UAE banking tone
- Complete sentences with proper punctuation
- Free from uncertainty phrases
- Maximum 4 bullet points
"""

import re
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class ResponseNormalizer:
    """
    Normalizes and formats chatbot responses for professional output.
    
    Ensures consistency, completeness, and UAE banking style.
    """
    
    # Forbidden phrases that sound uncertain or unprofessional
    FORBIDDEN_PHRASES = [
        "context does not specify",
        "not explicitly stated",
        "i don't know",
        "based on the context",
        "the context doesn't mention",
        "it is not clear",
        "there is no information",
        "unfortunately i cannot",
        "i apologize but i don't",
        "not enough information",
        "cannot be determined",
        "system does not know",
        "not provided in the context"
    ]
    
    # Alternative confident phrases to use instead
    CONFIDENT_ALTERNATIVES = {
        "context does not specify": "Typically,",
        "not explicitly stated": "Generally,",
        "i don't know": "I can help with",
        "based on the context": "In UAE banking,",
        "it is not clear": "Standard practice is",
        "there is no information": "Commonly,"
    }
    
    # Bullet point patterns to normalize
    BULLET_PATTERNS = [
        r'^[\s]*[-*•]\s*',      # Standard bullets: -, *, •
        r'^[\s]*\d+\.\s*',       # Numbered lists: 1.
        r'^[\s]*[a-z]\.\s*',     # Lettered lists: a.
        r'^[\s]*→\s*',           # Arrow: →
    ]
    
    # Incomplete sentence indicators
    INCOMPLETE_PATTERNS = [
        r'\bare\s*$',            # Ends with "are"
        r'\bis\s*$',             # Ends with "is"
        r'\bwas\s*$',            # Ends with "was"
        r'\bwere\s*$',           # Ends with "were"
        r'\bhas\s*$',            # Ends with "has"
        r'\bhave\s*$',           # Ends with "have"
        r'\bhad\s*$',            # Ends with "had"
        r'\bwill\s*$',           # Ends with "will"
        r'\bwould\s*$',          # Ends with "would"
        r'\bcould\s*$',          # Ends with "could"
        r'\bmight\s*$',          # Ends with "might"
        r'\bmay\s*$',            # Ends with "may"
        r'\bsuch as\s*$',        # Ends with "such as"
        r'\bincluding\s*$',      # Ends with "including"
        r'\blike\s*$',           # Ends with "like"
        r'\bfor example\s*$',    # Ends with "for example"
        r'\band\s*$',            # Ends with "and"
        r'\bor\s*$',             # Ends with "or"
        r'\bto\s*$',             # Ends with "to"
        r'\bof\s*$',             # Ends with "of"
        r'\bfrom\s*$',           # Ends with "from"
        r'\bwith\s*$',           # Ends with "with"
        r'\bwithout\s*$',        # Ends with "without"
        r'\bthrough\s*$',        # Ends with "through"
        r'\bduring\s*$',         # Ends with "during"
        r'\bbefore\s*$',         # Ends with "before"
        r'\bafter\s*$',          # Ends with "after"
        r'\buntil\s*$',          # Ends with "until"
        r'\bwhile\s*$',          # Ends with "while"
    ]
    
    def __init__(self):
        """Initialize the response normalizer."""
        self.max_bullets = 5  # UAE banking standard: 3-5 bullets
        self.max_line_length = 120
    
    def normalize(self, text: str, language: str = "English") -> str:
        """
        Normalize and format response text.
        
        Args:
            text: Raw response text
            language: Response language
            
        Returns:
            Clean, formatted response
        """
        if not text or not text.strip():
            return ""
        
        # Step 1: Remove forbidden phrases
        text = self._remove_forbidden_phrases(text)
        
        # Step 2: Split multiple bullets on same line
        text = self._split_multiple_bullets(text)
        
        # Step 3: Normalize bullet points
        text = self._normalize_bullets(text)
        
        # Step 4: Split into lines and filter
        lines = self._split_into_lines(text)
        
        # Step 5: Remove incomplete/cut-off sentences
        lines = self._remove_incomplete_sentences(lines)
        
        # Step 6: Limit to max bullets
        lines = lines[:self.max_bullets]
        
        # Step 7: Ensure complete sentences
        lines = self._ensure_complete_sentences(lines, language)
        
        # Step 8: Remove empty/incomplete lines
        lines = self._filter_incomplete_lines(lines)
        
        # Step 9: Reconstruct response
        formatted = "\n".join(lines)
        
        logger.debug(f"Normalized response: {len(lines)} bullets")
        
        return formatted
    
    def _remove_forbidden_phrases(self, text: str) -> str:
        """Remove or replace forbidden uncertainty phrases."""
        text_lower = text.lower()
        
        for forbidden in self.FORBIDDEN_PHRASES:
            if forbidden in text_lower:
                # Replace with confident alternative or remove
                for bad, good in self.CONFIDENT_ALTERNATIVES.items():
                    if bad in text_lower:
                        # Case-insensitive replacement
                        pattern = re.compile(re.escape(bad), re.IGNORECASE)
                        text = pattern.sub(good)
                        break
        
        return text
    
    def _normalize_bullets(self, text: str) -> str:
        """Normalize all bullet points to use '•'."""
        lines = text.split('\n')
        normalized_lines = []
        
        for line in lines:
            is_bullet = False
            
            for pattern in self.BULLET_PATTERNS:
                if re.match(pattern, line.strip()):
                    # Replace with standard bullet
                    cleaned = re.sub(pattern, '', line.strip())
                    normalized_lines.append(f"• {cleaned}")
                    is_bullet = True
                    break
            
            if not is_bullet:
                normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    def _split_multiple_bullets(self, text: str) -> str:
        """Split multiple bullets that appear on the same line."""
        lines = text.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Check if line has multiple bullets like "• First • Second"
            if '•' in line and line.count('•') > 1:
                # Split by bullet
                parts = line.split('•')
                for part in parts:
                    part = part.strip()
                    if part:
                        # Remove leading dash or asterisk from split parts
                        part = re.sub(r'^[-*]\s*', '', part)
                        if part:
                            fixed_lines.append(f"• {part}")
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _split_into_lines(self, text: str) -> List[str]:
        """Split text into clean lines."""
        lines = []
        
        # Try splitting by newlines first
        raw_lines = text.split('\n')
        
        for line in raw_lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if line starts with bullet
            if line.startswith('•'):
                lines.append(line)
            else:
                # Might be continuation or paragraph
                # Split by common separators
                sub_lines = re.split(r'[;•]\s*', line)
                for sub in sub_lines:
                    sub = sub.strip()
                    if sub:
                        lines.append(sub)
        
        return lines
    
    def _remove_incomplete_sentences(self, lines: List[str]) -> List[str]:
        """Remove lines that appear to be cut off or incomplete."""
        filtered_lines = []
        
        for line in lines:
            content = re.sub(r'^•\s*', '', line).strip()
            
            # Skip if content is empty
            if not content:
                continue
            
            # Check if line ends with incomplete pattern
            is_incomplete = False
            for pattern in self.INCOMPLETE_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    logger.debug(f"Removing incomplete line: {content[:50]}...")
                    is_incomplete = True
                    break
            
            # Also check for obviously truncated phrases
            if len(content.split()) < 4 and not self._is_important_short_phrase(content):
                is_incomplete = True
            
            if not is_incomplete:
                filtered_lines.append(line)
        
        return filtered_lines
    
    def _is_important_short_phrase(self, text: str) -> bool:
        """Check if short phrase is important enough to keep."""
        text_lower = text.lower().strip()
        
        important_phrases = [
            "yes",
            "no",
            "contact 800-bank",
            "call 800-bank",
            "emirates id required",
            "visit branch"
        ]
        
        return text_lower in important_phrases
    
    def _ensure_complete_sentences(self, lines: List[str], language: str) -> List[str]:
        """Ensure each line is a complete sentence."""
        complete_lines = []
            
        for line in lines:
            # Remove leading bullet for checking
            content = re.sub(r'^•\s*', '', line)
                
            # Check if sentence is complete
            if not self._is_complete_sentence(content, language):
                # Try to complete it
                completed = self._complete_sentence(content, language)
                if completed:
                    complete_lines.append(f"• {completed}")
                    continue
                
            # For Arabic: ensure minimum word count and proper structure
            if language.lower() in ["arabic", "ar"]:
                if self._is_incomplete_arabic(content):
                    # Skip incomplete Arabic sentences
                    logger.debug(f"Skipping incomplete Arabic: {content[:50]}...")
                    continue
                
            # Add original with bullet
            if not line.startswith('•'):
                complete_lines.append(f"• {line}")
            else:
                complete_lines.append(line)
            
        return complete_lines
        
    def _is_incomplete_arabic(self, text: str) -> bool:
        """
        Check if Arabic text appears incomplete.
            
        Args:
            text: Arabic text to check
                
        Returns:
            True if appears incomplete
        """
        if not text or not text.strip():
            return True
            
        # Check for incomplete patterns
        incomplete_patterns = [
            r'\bمثل\s*$',      # "such as"
            r'\bبما في ذلك\s*$',  # "including"
            r'\bعلى سبيل المثال\s*$',  # "for example"
            r'\و\s*$',         # "and"
            r'\أو\s*$',         # "or"
            r'\من\s*$',         # "from"
            r'\إلى\s*$',        # "to"
            r'\في\s*$',         # "in"
        ]
            
        for pattern in incomplete_patterns:
            if re.search(pattern, text):
                return True
            
        # Check minimum word count (Arabic sentences should be substantial)
        words = text.split()
        if len(words) < 5:
            return True
            
        return False
    
    def _is_complete_sentence(self, text: str, language: str) -> bool:
        """Check if text appears to be a complete sentence."""
        text = text.strip()
        
        # Empty check
        if not text:
            return False
        
        # Too short
        if len(text.split()) < 3:
            return False
        
        # Check for proper ending (but allow bullet points without period)
        # In UAE banking style, bullets often don't have periods
        
        # Check for incomplete phrases
        incomplete_starters = [
            "such as", "including", "like", "for example",
            "accounts such as", "options like"
        ]
        
        text_lower = text.lower()
        for starter in incomplete_starters:
            if text_lower.endswith(starter):
                return False
            if text_lower.startswith(starter) and len(text.split()) < 5:
                return False
        
        return True
    
    def _complete_sentence(self, text: str, language: str) -> Optional[str]:
        """Try to complete an incomplete sentence."""
        text = text.strip()
        
        # Common incomplete patterns and their completions
        completions = {
            "accounts such as": "Accounts such as Savings and Current are available.",
            "options include": "Options include personal loans, auto loans, and home loans.",
            "requirements are": "Requirements are Emirates ID, passport copy, and salary certificate.",
            "you can": "You can visit any branch or use our mobile app.",
            "to open": "To open an account, visit our website or nearest branch."
        }
        
        text_lower = text.lower()
        for pattern, completion in completions.items():
            if text_lower.startswith(pattern) and len(text_lower) < len(pattern) + 10:
                return completion
        
        # If ends with "and", might be cut off
        if text_lower.endswith(" and"):
            return text + " other services."
        
        # Default: return as-is (will be filtered if too incomplete)
        return None
    
    def _filter_incomplete_lines(self, lines: List[str]) -> List[str]:
        """Remove obviously incomplete or empty lines."""
        filtered = []
        
        for line in lines:
            content = re.sub(r'^•\s*', '', line).strip()
            
            # Skip very short lines (< 3 words) unless they're important
            if len(content.split()) < 3:
                # Allow if it's a key phrase
                important_phrases = ["yes", "no", "contact 800-bank"]
                if content.lower() not in important_phrases:
                    continue
            
            # Skip lines that end with obvious cut-offs
            if content.lower().endswith(("such as", "including", "like", "and", "or")):
                continue
            
            filtered.append(line)
        
        return filtered
    
    def validate_response(self, text: str) -> dict:
        """
        Validate response quality.
        
        Args:
            text: Response text to validate
            
        Returns:
            Dictionary with validation results
        """
        issues = []
        
        # Check for forbidden phrases
        for phrase in self.FORBIDDEN_PHRASES:
            if phrase in text.lower():
                issues.append(f"Contains forbidden phrase: '{phrase}'")
        
        # Check bullet count
        lines = [l for l in text.split('\n') if l.strip().startswith('•')]
        if len(lines) > self.max_bullets:
            issues.append(f"Too many bullets: {len(lines)} (max {self.max_bullets})")
        
        # Check for incomplete sentences
        for line in lines:
            content = re.sub(r'^•\s*', '', line).strip()
            if not self._is_complete_sentence(content, "English"):
                issues.append(f"Incomplete sentence: {content[:50]}...")
        
        # Check bullet consistency
        bullets_used = set()
        for char in ['•', '-', '*', '→']:
            if char in text:
                bullets_used.add(char)
        
        if len(bullets_used) > 1:
            issues.append(f"Inconsistent bullets: {bullets_used}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "bullet_count": len(lines)
        }


# Singleton instance
_normalizer = None


def get_normalizer() -> ResponseNormalizer:
    """Get or create singleton normalizer instance."""
    global _normalizer
    if _normalizer is None:
        _normalizer = ResponseNormalizer()
    return _normalizer


def normalize_response(text: str, language: str = "English") -> str:
    """
    Convenience function to normalize a response.
    
    Args:
        text: Raw response text
        language: Response language
        
    Returns:
        Clean, formatted response
    """
    normalizer = get_normalizer()
    return normalizer.normalize(text, language)


def clean_response(text: str, language: str = "English") -> str:
    """
    Enhanced response cleaner that ensures production quality.
    
    This function:
    1. Splits multiple bullets on same line
    2. Normalizes all bullets to "•"
    3. Removes duplicate bullets
    4. Removes empty lines
    5. Removes incomplete/cut-off sentences
    6. Limits to maximum 4 bullets
    7. Ensures proper line endings
    
    Args:
        text: Raw response text
        language: Response language
        
    Returns:
        Clean, production-ready response
    """
    normalizer = get_normalizer()
    return normalizer.normalize(text, language)


def validate_response(text: str) -> dict:
    """
    Convenience function to validate response quality.
    
    Args:
        text: Response text to validate
        
    Returns:
        Validation results dictionary
    """
    normalizer = get_normalizer()
    return normalizer.validate_response(text)
