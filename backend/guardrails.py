"""
Guardrails and Safety Module - Production-grade response validation

This module provides:
- Hallucination detection
- Content filtering
- Response validation
- Compliance checking
- Safe fallback generation
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety classification levels."""
    SAFE = "safe"
    CAUTION = "caution"
    UNSAFE = "unsafe"
    CRITICAL = "critical"


class GuardrailsManager:
    """
    Manages safety guardrails for AI responses.
    
    Features:
    - Hallucination detection
    - Sensitive content filtering
    - Financial advice validation
    - Compliance checking
    - Fallback response generation
    """
    
    # Sensitive topics that require caution
    SENSITIVE_TOPICS = {
        "financial_advice": [
            "invest", "investment", "stock", "trading", "forex", "cryptocurrency",
            "bitcoin", "crypto", "gambling", "betting", "lottery"
        ],
        "legal_matters": [
            "lawsuit", "court", "legal action", "sue", "attorney", "lawyer",
            "prosecute", "charges", "arrest", "crime"
        ],
        "personal_info": [
            "password", "pin", "cvv", "card number", "account number",
            "social security", "national id", "credit card details"
        ],
        "medical_emergency": [
            "hospital", "emergency", "ambulance", "doctor", "medical",
            "health crisis", "injury", "accident"
        ],
        "threats_violence": [
            "kill", "hurt", "attack", "weapon", "bomb", "threat",
            "violence", "harm", "suicide", "self-harm"
        ]
    }
    
    # Phrases indicating uncertainty (potential hallucination)
    UNCERTAINTY_PHRASES = [
        "i think", "i believe", "probably", "maybe", "might be",
        "not sure", "possibly", "perhaps", "i guess", "as far as i know",
        "to the best of my knowledge", "if i'm not wrong"
    ]
    
    # Absolute claims to watch for (potential hallucination)
    ABSOLUTE_CLAIMS = [
        "always", "never", "guaranteed", "100%", "certainly",
        "definitely", "without a doubt", "absolutely"
    ]
    
    # UAE banking compliance keywords
    COMPLIANCE_KEYWORDS = {
        "uae_regulations": [
            "central bank", "uae central bank", "cbuae", "regulation",
            "compliance", "sharia compliant", "islamic finance"
        ],
        "kyc_aml": [
            "kyc", "aml", "anti-money laundering", "know your customer",
            "due diligence", "sanctions", "pep", "beneficial owner"
        ]
    }
    
    def __init__(self):
        """Initialize guardrails manager."""
        logger.info("Guardrails manager initialized")
        
        # Compile regex patterns
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for efficiency."""
        self.sensitive_patterns = {}
        
        for category, keywords in self.SENSITIVE_TOPICS.items():
            pattern = '|'.join([r'\b' + re.escape(kw) + r'\b' for kw in keywords])
            self.sensitive_patterns[category] = re.compile(pattern, re.IGNORECASE)
        
        # Uncertainty pattern
        uncertainty_pattern = '|'.join([re.escape(phrase) for phrase in self.UNCERTAINTY_PHRASES])
        self.uncertainty_pattern = re.compile(uncertainty_pattern, re.IGNORECASE)
        
        # Absolute claims pattern
        absolute_pattern = '|'.join([re.escape(kw) for kw in self.ABSOLUTE_CLAIMS])
        self.absolute_pattern = re.compile(absolute_pattern, re.IGNORECASE)
    
    def validate_response(
        self,
        response: str,
        context: str = "",
        query: str = ""
    ) -> Tuple[SafetyLevel, List[str], str]:
        """
        Validate AI response for safety and accuracy.
        
        Args:
            response: Generated response text
            context: RAG context used
            query: Original user query
            
        Returns:
            Tuple of (safety level, list of issues, validated/safe response)
        """
        issues = []
        safety_level = SafetyLevel.SAFE
        final_response = response
        
        # Check 1: Hallucination detection
        hallucination_score = self._detect_hallucination(response, context)
        if hallucination_score > 0.7:
            issues.append(f"High hallucination risk detected ({hallucination_score:.2f})")
            safety_level = SafetyLevel.UNSAFE
            final_response = self._generate_safe_fallback(query)
        
        # Check 2: Sensitive content
        sensitive_categories = self._check_sensitive_content(response)
        if sensitive_categories:
            for category in sensitive_categories:
                issues.append(f"Sensitive content detected: {category}")
                
                if category == "financial_advice":
                    safety_level = max(safety_level, SafetyLevel.CAUTION, key=lambda x: x.value)
                    final_response = self._add_financial_disclaimer(final_response)
                
                elif category == "personal_info":
                    safety_level = SafetyLevel.CRITICAL
                    final_response = self._block_personal_info_request()
                
                elif category == "medical_emergency":
                    safety_level = SafetyLevel.CRITICAL
                    final_response = self._redirect_to_emergency_services()
                
                elif category == "threats_violence":
                    safety_level = SafetyLevel.CRITICAL
                    final_response = self._handle_threat_content()
        
        # Check 3: Compliance check
        compliance_issues = self._check_compliance(response, query)
        if compliance_issues:
            issues.extend(compliance_issues)
            safety_level = max(safety_level, SafetyLevel.CAUTION, key=lambda x: x.value)
            final_response = self._add_compliance_disclaimer(final_response)
        
        # Check 4: Factual consistency with context
        if context:
            consistency_check = self._check_context_consistency(response, context)
            if not consistency_check["consistent"]:
                issues.append("Response inconsistent with provided context")
                safety_level = max(safety_level, SafetyLevel.CAUTION, key=lambda x: x.value)
        
        logger.info(f"Response validation: {safety_level.value}, Issues: {len(issues)}")
        
        return safety_level, issues, final_response
    
    def _detect_hallucination(self, response: str, context: str) -> float:
        """
        Detect potential hallucination in response.
        
        Returns:
            Hallucination probability score (0-1)
        """
        score = 0.0
        
        response_lower = response.lower()
        
        # Check for uncertainty phrases
        uncertainty_matches = self.uncertainty_pattern.findall(response_lower)
        score += len(uncertainty_matches) * 0.1
        
        # Check for absolute claims without context support
        absolute_matches = self.absolute_pattern.findall(response_lower)
        score += len(absolute_matches) * 0.15
        
        # Check if response is much longer than context (fabrication risk)
        if context and len(response) > len(context) * 2:
            score += 0.2
        
        # Check for specific numbers/facts not in context
        if context:
            numbers_in_response = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?%?', response)
            numbers_in_context = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?%?', context)
            
            unsupported_numbers = set(numbers_in_response) - set(numbers_in_context)
            if len(unsupported_numbers) > 2:
                score += 0.3
        
        return min(score, 1.0)
    
    def _check_sensitive_content(self, text: str) -> List[str]:
        """Check for sensitive content categories."""
        detected_categories = []
        
        text_lower = text.lower()
        
        for category, pattern in self.sensitive_patterns.items():
            if pattern.search(text_lower):
                detected_categories.append(category)
        
        return detected_categories
    
    def _check_compliance(self, response: str, query: str) -> List[str]:
        """Check for regulatory compliance issues."""
        issues = []
        
        text_lower = (response + " " + query).lower()
        
        # Check for UAE regulation mentions
        for reg_category, keywords in self.COMPLIANCE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Verify the information is accurate
                    if not self._verify_compliance_info(keyword, response):
                        issues.append(f"Potentially inaccurate {reg_category} information")
        
        return issues
    
    def _verify_compliance_info(self, keyword: str, response: str) -> bool:
        """Verify compliance-related information is accurate."""
        # Simplified verification - in production, use knowledge base
        safe_phrases = {
            "central bank": ["uae central bank regulations", "cbuae guidelines"],
            "kyc": ["standard kyc requirements", "kyc documentation"],
            "aml": ["aml procedures", "anti-money laundering policies"]
        }
        
        for safe_phrase in safe_phrases.get(keyword, []):
            if safe_phrase in response.lower():
                return True
        
        # Default to cautious approach
        return False
    
    def _check_context_consistency(
        self,
        response: str,
        context: str
    ) -> Dict:
        """Check if response is consistent with provided context."""
        result = {
            "consistent": True,
            "confidence": 1.0,
            "issues": []
        }
        
        # Simple keyword overlap check
        response_words = set(response.lower().split())
        context_words = set(context.lower().split())
        
        # Remove stopwords
        stopwords = {"the", "a", "an", "is", "are", "be", "to", "for", "with"}
        response_words -= stopwords
        context_words -= stopwords
        
        # Calculate overlap
        overlap = len(response_words & context_words) / max(len(response_words), 1)
        
        if overlap < 0.3:
            result["consistent"] = False
            result["confidence"] = overlap
            result["issues"].append(f"Low context overlap: {overlap:.2f}")
        
        return result
    
    def _generate_safe_fallback(self, query: str) -> str:
        """Generate safe fallback response."""
        # Detect language
        is_arabic = any('\u0600' <= c <= '\u06FF' for c in query)
        
        if is_arabic:
            return """عذرًا، لا أملك معلومات كافية للإجابة على هذا السؤال بدقة. 

للحصول على معلومات دقيقة، يرجى:
• الاتصال بخدمة العملاء على 800-BANK
• زيارة أقرب فرع
• التحقق من موقعنا الإلكتروني الرسمي

نحن هنا لمساعدتك بمعلومات موثوقة."""
        else:
            return """I apologize, but I don't have sufficient information to answer this question accurately.

For accurate information, please:
• Contact customer service at 800-BANK
• Visit your nearest branch
• Check our official website

We're here to help you with verified information."""
    
    def _add_financial_disclaimer(self, response: str) -> str:
        """Add financial advice disclaimer."""
        disclaimer = "\n\n⚠️ **Important**: This information is for general guidance only and does not constitute financial advice. Please consult with our qualified financial advisors for personalized recommendations."
        
        return response + disclaimer
    
    def _block_personal_info_request(self) -> str:
        """Block requests for sensitive personal information."""
        return """🔒 **Security Alert**: For your security, I cannot accept or process sensitive personal information such as passwords, PINs, CVV codes, or full account numbers through this chat.

If you need to update sensitive information, please:
• Use our secure mobile app
• Visit a branch in person
• Call our secure hotline at 800-BANK

Your security is our priority."""
    
    def _redirect_to_emergency_services(self) -> str:
        """Redirect medical emergencies to appropriate services."""
        return """🚨 **Emergency Notice**: If this is a medical emergency, please immediately:

• Call UAE Emergency Services: **998** (Ambulance)
• Call Police: **999**
• Visit the nearest hospital emergency room

For non-emergency health insurance queries, please contact our insurance department at 800-BANK."""
    
    def _handle_threat_content(self) -> str:
        """Handle threatening or violent content."""
        return """⚠️ **Important**: We take all threats and violent statements seriously. Such content may be reported to authorities as required by UAE law.

If you're experiencing distress or having thoughts of self-harm, please seek help:
• UAE Psychological Support: 800-4673 (HOPE)
• National Mental Health Programme: 800-4673

For other concerns, we encourage you to communicate respectfully with our customer service team at 800-BANK."""
    
    def _add_compliance_disclaimer(self, response: str) -> str:
        """Add compliance disclaimer for regulated topics."""
        disclaimer = "\n\nℹ️ **Note**: Information provided is based on current UAE Central Bank regulations and bank policies. Terms and conditions apply. Please verify with official sources."
        
        return response + disclaimer
    
    def get_safety_report(self, response: str, context: str = "") -> Dict:
        """
        Generate comprehensive safety report for a response.
        
        Args:
            response: AI response text
            context: Source context
            
        Returns:
            Detailed safety report dictionary
        """
        safety_level, issues, validated_response = self.validate_response(
            response, context
        )
        
        return {
            "safety_level": safety_level.value,
            "issues_found": issues,
            "issue_count": len(issues),
            "hallucination_score": self._detect_hallucination(response, context),
            "sensitive_categories": self._check_sensitive_content(response),
            "requires_review": safety_level in [SafetyLevel.UNSAFE, SafetyLevel.CRITICAL],
            "validated_response": validated_response,
            "original_response": response
        }


# Singleton instance
_guardrails_manager = None


def get_guardrails_manager() -> GuardrailsManager:
    """Get or create singleton guardrails manager instance."""
    global _guardrails_manager
    if _guardrails_manager is None:
        _guardrails_manager = GuardrailsManager()
    return _guardrails_manager


def validate_response(response: str, context: str = "", query: str = "") -> Tuple[SafetyLevel, List[str], str]:
    """Convenience function to validate response."""
    manager = get_guardrails_manager()
    return manager.validate_response(response, context, query)
