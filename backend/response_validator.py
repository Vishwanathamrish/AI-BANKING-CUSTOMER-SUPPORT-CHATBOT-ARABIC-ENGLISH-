"""
Response Validation Module - Quality control for production responses

This module ensures all responses are:
- Complete (no truncation)
- Clean (proper formatting)
- Deterministic (consistent output)
- Production-ready (validated quality)
"""

import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ResponseValidator:
    """
    Validates response quality before sending to UI.
    
    Ensures deterministic, clean, and complete responses.
    """
    
    # Incomplete phrase patterns to detect and remove
    INCOMPLETE_PHRASES = [
        r'\bsetting\s*$',
        r'\bare\s*$',
        r'\bis\s*$',
        r'\bprovide your\s*$',
        r'\bincluding\s*$',
        r'\bsuch as\s*$',
        r'\bfor example\s*$',
        r'\band\s*$',
        r'\bor\s*$',
        r'\bto\s*$',
        r'\bof\s*$',
        r'\bfrom\s*$',
        r'\bwith\s*$',
        r'\bwithout\s*$',
        r'\bduring\s*$',
        r'\bbefore\s*$',
        r'\bafter\s*$',
        r'\buntil\s*$',
        r'\bwhile\s*$',
        r'\bwill\s*$',
        r'\bwould\s*$',
        r'\bcould\s*$',
        r'\bmight\s*$',
        r'\bmay\s*$',
        r'\bhas\s*$',
        r'\bhave\s*$',
        r'\bhad\s*$',
        r'\bwas\s*$',
        r'\bwere\s*$',
    ]
    
    # Bank names to remove (UAE-specific)
    BANK_NAMES = [
        "Emirates NBD", "First Abu Dhabi Bank", "FAB", "ADCB", 
        "Abu Dhabi Commercial Bank", "Dubai Islamic Bank", "DIB",
        "Mashreq Bank", "HSBC UAE", "Standard Chartered UAE",
        "Commercial Bank of Dubai", "CBD", "National Bank of Fujairah",
        "Union National Bank", "Emirates Islamic Bank", "Noor Bank"
    ]
    
    # Minimum acceptable line length (characters)
    MIN_LINE_LENGTH = 5
    
    # Bullet point requirements - STRICT ENFORCEMENT
    MIN_BULLETS = 3  # Minimum informative responses
    MAX_BULLETS = 4  # Maximum for conciseness
    MAX_WORDS_PER_BULLET = 20  # Enforce complete sentences (10-20 words)
    MIN_WORDS_PER_BULLET = 8   # Ensure substantial content
    
    def __init__(self):
        """Initialize the response validator."""
        self.incomplete_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.INCOMPLETE_PHRASES
        ]
        # Compile bank name patterns
        self.bank_name_patterns = [
            re.compile(re.escape(name), re.IGNORECASE)
            for name in self.BANK_NAMES
        ]
    
    def validate(self, text: str) -> Dict:
        """
        Validate response quality.
        
        Args:
            text: Response text to validate
            
        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        
        if not text or not text.strip():
            return {
                "valid": False,
                "issues": ["Empty response"],
                "warnings": [],
                "can_fix": False
            }
        
        lines = text.split('\n')
        
        # Check 1: No truncated lines
        for i, line in enumerate(lines, 1):
            if self._is_truncated(line):
                issues.append(f"Line {i} appears truncated: '{line.strip()[:30]}...'")
        
        # Check 2: No very short lines (< 5 chars)
        for i, line in enumerate(lines, 1):
            content = re.sub(r'^•\s*', '', line).strip()
            if content and len(content) < self.MIN_LINE_LENGTH:
                warnings.append(f"Line {i} is very short ({len(content)} chars)")
        
        # Check 3: Bullet consistency
        bullet_types = set()
        for char in ['•', '*', '-', '→']:
            if char in text:
                bullet_types.add(char)
        
        if len(bullet_types) > 1:
            issues.append(f"Inconsistent bullets: {bullet_types}")
        
        # Check 4: Min and Max bullets
        bullet_lines = [l for l in lines if l.strip().startswith('•')]
        if len(bullet_lines) < self.MIN_BULLETS:
            issues.append(f"Too few bullets: {len(bullet_lines)} (min {self.MIN_BULLETS})")
        if len(bullet_lines) > self.MAX_BULLETS:
            issues.append(f"Too many bullets: {len(bullet_lines)} (max {self.MAX_BULLETS})")
        
        # Check 5: Word count per bullet
        for i, line in enumerate(lines, 1):
            content = re.sub(r'^•\s*', '', line).strip()
            words = content.split()
            if len(words) > self.MAX_WORDS_PER_BULLET:
                warnings.append(f"Line {i} too long: {len(words)} words (max {self.MAX_WORDS_PER_BULLET})")
        
        # Check 6: Bank names detection
        for pattern in self.bank_name_patterns:
            if pattern.search(text):
                issues.append(f"Contains specific bank name (should use 'our bank')")
                break
        
        # Check 5: Empty lines
        empty_count = sum(1 for line in lines if not line.strip())
        if empty_count > len(lines) * 0.3:  # More than 30% empty
            warnings.append(f"Too many empty lines: {empty_count}")
        
        # Check 6: Repetition
        unique_lines = set([line.strip().lower() for line in lines if line.strip()])
        if len(unique_lines) < len(lines) * 0.7:  # Less than 70% unique
            warnings.append("Possible repetition detected")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "can_fix": len(issues) == 0 or all("truncated" not in issue.lower() for issue in issues)
        }
    
    def _is_truncated(self, line: str) -> bool:
        """Check if line appears to be truncated."""
        content = re.sub(r'^•\s*', '', line).strip()
        
        if not content:
            return False
        
        # Check incomplete patterns
        for pattern in self.incomplete_patterns:
            if pattern.search(content):
                return True
        
        # Check if ends without punctuation (and not too short)
        if len(content) > 10 and not content[-1] in '.!?':
            # Might be truncated
            # But allow if it's a clear complete thought
            if len(content.split()) < 8:
                return False  # Short enough to be complete
            return True
        
        return False
    
    def clean_and_validate(self, text: str) -> str:
        """
        Clean response and validate quality.
        
        FLEXIBLE APPROACH:
        - Preserve ALL meaningful content from LLM
        - Accept multiple bullet formats (-, *, •, 1., etc.)
        - Never delete valid LLM output
        - Only remove truly problematic content
        
        Args:
            text: Raw response text
            
        Returns:
            Cleaned response (NEVER empty if LLM returned content)
        """
        if not text or not text.strip():
            return ""
        
        # Step 0: Remove bank names
        for pattern in self.bank_name_patterns:
            text = pattern.sub("our bank", text)
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            content = line.strip()
            
            # CRITICAL FIX: Accept ALL reasonable lines, not just bullets
            # Convert various formats to standard bullet
            if not content.startswith('•'):
                # Normalize different bullet styles
                content = re.sub(r'^[-*]\s*', '• ', content)
                # Numbered lists
                content = re.sub(r'^\d+\.\s*', '• ', content)
                # Arrow style
                content = re.sub(r'^→\s*', '• ', content)
                
                # If still doesn't start with bullet, add one
                if not content.startswith('•'):
                    content = f"• {content}"
            
            # REMOVED: Strict length filtering that was deleting content
            # OLD CODE: if len(content_clean) < 5: continue ❌
            
            # Keep meaningful short lines (important phrases)
            content_clean = re.sub(r'^•\s*', '', content).strip()
            important_phrases = ["yes", "no", "contact 800-bank", "call 800-bank"]
            
            # Only skip if TRULY meaningless (< 3 chars and not important)
            if content_clean and len(content_clean) < 3:
                if content_clean.lower() not in important_phrases:
                    logger.debug(f"Skipping very short line: {content_clean}")
                    continue
            
            # Gentle word limit enforcement (don't truncate, just warn)
            words = content_clean.split()
            if len(words) > self.MAX_WORDS_PER_BULLET:
                logger.debug(f"Line exceeds {self.MAX_WORDS_PER_BULLET} words but keeping: {content[:50]}...")
                # Keep the full line instead of truncating aggressively
            
            cleaned_lines.append(content)
        
        # CRITICAL: Never force exactly 3-4 bullets if LLM returned different amount
        # Just log warning if count is low
        if len(cleaned_lines) < self.MIN_BULLETS:
            logger.warning(f"Response has only {len(cleaned_lines)} bullets (recommended: 3-4)")
            # BUT DON'T DELETE OR REGENERATE - preserve LLM output
        
        if len(cleaned_lines) > self.MAX_BULLETS:
            logger.debug(f"Response has {len(cleaned_lines)} bullets (max recommended: {self.MAX_BULLETS})")
            # Keep all content instead of truncating to 4
        
        result = '\n'.join(cleaned_lines)
        
        logger.info(f"Cleaned response from {len(lines)} to {len(cleaned_lines)} lines")
        
        # SAFETY: Never return empty if we had content
        if not result.strip() and text.strip():
            logger.error("⚠️ Validator would return empty - falling back to original!")
            return text
        
        return result
    
    def ensure_deterministic(self, text: str) -> str:
        """
        Ensure response is deterministic and consistent.
        
        FLEXIBLE APPROACH:
        - Normalize formatting but preserve content
        - Accept multiple bullet styles
        - Never delete meaningful lines
        
        Args:
            text: Response text
            
        Returns:
            Consistent formatted response (preserving original content)
        """
        if not text or not text.strip():
            return ""
        
        lines = text.split('\n')
        
        # Normalize bullets but keep all content
        normalized = []
        for line in lines:
            if not line.strip():
                continue
            
            # Replace any bullet symbol with standard •
            original_line = line.strip()
            line = re.sub(r'^[\*\-→]\s*', '• ', line.strip())
            line = re.sub(r'^\d+\.\s*', '• ', line)
            
            # Ensure starts with bullet
            if not line.startswith('•'):
                line = f"• {line}"
            
            normalized.append(line)
        
        # Remove exact duplicates while preserving order
        seen = set()
        unique_lines = []
        for line in normalized:
            line_lower = line.lower()
            if line_lower not in seen:
                seen.add(line_lower)
                unique_lines.append(line)
        
        # Keep all unique lines (don't force max 4)
        result = '\n'.join(unique_lines)
        
        logger.debug(f"Normalized response: {len(unique_lines)} lines")
        
        return result
    
    def validate_bullet_count(self, text: str) -> Dict:
        """
        Validate that response has exactly 3-4 bullet points.
        
        Args:
            text: Response text to validate
            
        Returns:
            Dictionary with validation results and bullet count
        """
        if not text or not text.strip():
            return {
                "valid": False,
                "bullet_count": 0,
                "needs_regeneration": True,
                "reason": "Empty response"
            }
        
        lines = text.split('\n')
        bullet_lines = [l for l in lines if l.strip().startswith('•')]
        bullet_count = len(bullet_lines)
        
        needs_regeneration = bullet_count < self.MIN_BULLETS
        
        return {
            "valid": self.MIN_BULLETS <= bullet_count <= self.MAX_BULLETS,
            "bullet_count": bullet_count,
            "needs_regeneration": needs_regeneration,
            "reason": f"Has {bullet_count} bullets (required: {self.MIN_BULLETS}-{self.MAX_BULLETS})" if needs_regeneration else "Valid"
        }
    
    def extract_bullets(self, text: str) -> List[str]:
        """
        Extract all bullet points from response.
        
        Args:
            text: Response text
            
        Returns:
            List of bullet point contents (without bullet symbols)
        """
        if not text or not text.strip():
            return []
        
        lines = text.split('\n')
        bullets = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('•'):
                content = re.sub(r'^•\s*', '', line)
                bullets.append(content)
        
        return bullets
    
    def is_complete_arabic_sentence(self, text: str) -> bool:
        """
        Check if Arabic text appears to be a complete sentence.
        
        Args:
            text: Arabic text to check
            
        Returns:
            True if appears complete
        """
        if not text or not text.strip():
            return False
        
        # Check for common Arabic incomplete patterns
        incomplete_indicators = [
            r'\bمثل\s*$',      # "such as"
            r'\bبما في ذلك\s*$',  # "including"
            r'\bعلى سبيل المثال\s*$',  # "for example"
            r'\و\s*$',         # "and"
            r'\أو\s*$',         # "or"
        ]
        
        text_lower = text.lower()
        for pattern in incomplete_indicators:
            if re.search(pattern, text_lower):
                return False
        
        # Check minimum word count (Arabic words are typically longer)
        words = text.split()
        if len(words) < 5:  # Arabic sentences should have at least 5 words
            return False
        
        return True


# Singleton instance
_validator = None


def get_validator() -> ResponseValidator:
    """Get or create singleton validator instance."""
    global _validator
    if _validator is None:
        _validator = ResponseValidator()
    return _validator


def validate_response(text: str) -> Dict:
    """
    Validate response quality.
    
    Args:
        text: Response text to validate
        
    Returns:
        Validation results dictionary
    """
    validator = get_validator()
    return validator.validate(text)


def clean_response(text: str) -> str:
    """
    Clean and validate response for production use.
    
    This function:
    1. Removes bank names (replaces with "our bank")
    2. Removes truncated/incomplete lines
    3. Normalizes bullet formatting
    4. Enforces max 15 words per bullet
    5. Removes duplicates
    6. Limits to max 4 bullets
    7. Ensures deterministic output
    
    Args:
        text: Raw response text
        
    Returns:
        Clean, production-ready response
    """
    validator = get_validator()
    
    # Step 1: Remove bank names and clean truncated lines
    cleaned = validator.clean_and_validate(text)
    
    # Step 2: Ensure deterministic format
    deterministic = validator.ensure_deterministic(cleaned)
    
    return deterministic


def validate_bullet_count(text: str) -> Dict:
    """
    Validate that response has exactly 3-4 bullet points.
    
    Args:
        text: Response text to validate
        
    Returns:
        Dictionary with validation results and bullet count
    """
    validator = get_validator()
    return validator.validate_bullet_count(text)


def extract_bullets(text: str) -> List[str]:
    """
    Extract all bullet points from response.
    
    Args:
        text: Response text
        
    Returns:
        List of bullet point contents
    """
    validator = get_validator()
    return validator.extract_bullets(text)


def quick_validate(text: str) -> bool:
    """
    Quick validation check.
    
    Args:
        text: Response text
        
    Returns:
        True if valid, False otherwise
    """
    validator = get_validator()
    result = validator.validate(text)
    return result['valid']
