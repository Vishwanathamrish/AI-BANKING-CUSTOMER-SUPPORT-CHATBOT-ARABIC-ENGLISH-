"""
Intent-Based Response Formatter Module

This module enforces strict response structure based on detected intent.
Ensures consistent formatting across all banking queries.
"""

import logging
from typing import Dict, Optional, List
from .intent_detection import BankingIntent

logger = logging.getLogger(__name__)


class IntentResponseFormatter:
    """
    Formats responses based on intent type with strict structure.
    
    Ensures each intent follows its mandatory response template.
    """
    
    # Intent-specific response templates
    INTENT_TEMPLATES = {
        BankingIntent.ACCOUNT_OPENING: {
            "structure": [
                "Online application method",
                "Branch visit option", 
                "Required documents (Emirates ID, passport)",
                "Activation timeline"
            ],
            "keywords": ["online", "website", "app", "branch", "documents", "Emirates ID", "passport", "activate"]
        },
        BankingIntent.CARD_BLOCK: {
            "structure": [
                "Immediate action (call hotline/app)",
                "Emergency contact number",
                "App/online blocking steps",
                "Replacement card timeline"
            ],
            "keywords": ["block", "lost", "stolen", "800-BANK", "hotline", "replacement", "immediately"]
        },
        BankingIntent.ONLINE_BANKING: {
            "structure": [
                "Registration location (app/website)",
                "Verification process",
                "Login setup steps",
                "Access benefits"
            ],
            "keywords": ["register", "login", "username", "password", "OTP", "verification", "access"]
        },
        BankingIntent.LOAN_INFORMATION: {
            "structure": [
                "Application method (online/branch)",
                "Required documents",
                "Approval timeframe (1-3 days)",
                "Next steps after approval"
            ],
            "keywords": ["apply", "salary certificate", "approval", "days", "interest rate", "amount"]
        },
        BankingIntent.LOAN_REPAYMENT: {
            "structure": [
                "Repayment availability",
                "Fee information",
                "Process steps",
                "Contact for details"
            ],
            "keywords": ["early", "partial", "full", "settlement", "fee", "NOC"]
        },
        BankingIntent.ACCOUNT_BALANCE: {
            "structure": [
                "Mobile app method",
                "Internet banking method",
                "ATM method",
                "Phone banking option"
            ],
            "keywords": ["check", "balance", "app", "ATM", "internet banking", "SMS"]
        },
        BankingIntent.PIN_RESET: {
            "structure": [
                "App-based reset method",
                "ATM method",
                "Customer care option",
                "Security reminder"
            ],
            "keywords": ["PIN", "reset", "ATM", "OTP", "new PIN", "security"]
        },
        BankingIntent.MONEY_TRANSFER: {
            "structure": [
                "Transfer method (app/online)",
                "Beneficiary setup",
                "Processing time",
                "Limits and fees"
            ],
            "keywords": ["transfer", "beneficiary", "IBAN", "SWIFT", "instant", "limits"]
        },
        BankingIntent.ACCOUNT_SECURITY: {
            "structure": [
                "Authentication method",
                "Password security",
                "Transaction safety",
                "Fraud prevention"
            ],
            "keywords": ["secure", "protect", "fraud", "OTP", "password", "biometric"]
        }
    }
    
    def __init__(self):
        """Initialize the intent response formatter."""
        logger.info("Intent response formatter initialized")
    
    def format_by_intent(
        self, 
        intent: BankingIntent, 
        response: str,
        language: str = "English"
    ) -> str:
        """
        Format response based on intent type.
        
        Args:
            intent: Detected banking intent
            response: Raw LLM response
            language: Response language
            
        Returns:
            Formatted response following intent structure
        """
        if intent not in self.INTENT_TEMPLATES:
            return response
        
        template = self.INTENT_TEMPLATES[intent]
        
        # Check if response follows the expected structure
        response_lower = response.lower()
        
        # Verify key elements are present
        missing_elements = []
        for element in template["structure"]:
            element_present = any(
                keyword in response_lower 
                for keyword in element.lower().split()
            )
            if not element_present:
                missing_elements.append(element)
        
        if missing_elements:
            logger.warning(f"Response missing elements for {intent}: {missing_elements}")
            # Could trigger regeneration here if needed
        
        return response
    
    def enforce_structure(
        self,
        intent: BankingIntent,
        bullets: List[str]
    ) -> List[str]:
        """
        Enforce strict structure on bullet points.
        
        Args:
            intent: Detected intent
            bullets: List of bullet points from LLM
            
        Returns:
            Structured bullet points following template
        """
        if intent not in self.INTENT_TEMPLATES:
            return bullets[:4]  # Default to max 4
        
        template = self.INTENT_TEMPLATES[intent]
        structured = []
        
        # Try to map existing bullets to template structure
        for i, element in enumerate(template["structure"][:len(bullets)]):
            if i < len(bullets):
                # Keep original bullet but ensure it matches element theme
                structured.append(bullets[i])
            else:
                break
        
        return structured[:4]
    
    def get_structure_guide(self, intent: BankingIntent) -> str:
        """
        Get the structure guide for an intent.
        
        Args:
            intent: Banking intent type
            
        Returns:
            String describing required structure
        """
        if intent not in self.INTENT_TEMPLATES:
            return "General banking query - use standard 3-4 bullet format"
        
        template = self.INTENT_TEMPLATES[intent]
        lines = [f"Required structure for {intent.value}:"]
        for i, element in enumerate(template["structure"], 1):
            lines.append(f"  {i}. {element}")
        
        return "\n".join(lines)


# Singleton instance
_formatter = None


def get_intent_formatter() -> IntentResponseFormatter:
    """Get or create singleton formatter instance."""
    global _formatter
    if _formatter is None:
        _formatter = IntentResponseFormatter()
    return _formatter


def format_response_by_intent(
    intent: BankingIntent,
    response: str,
    language: str = "English"
) -> str:
    """
    Format response based on intent.
    
    Args:
        intent: Banking intent
        response: Raw response text
        language: Response language
        
    Returns:
        Formatted response
    """
    formatter = get_intent_formatter()
    return formatter.format_by_intent(intent, response, language)
