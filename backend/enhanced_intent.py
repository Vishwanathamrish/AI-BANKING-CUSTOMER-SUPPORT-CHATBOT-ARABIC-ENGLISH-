"""
Enhanced Intent Detection - Hybrid ML + Rule-based approach

This module provides advanced intent detection combining:
- Rule-based keyword matching (fast, deterministic)
- ML-based classification using sentence transformers
- Confidence scoring and thresholding
- Arabic NLP support
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class BankingIntent(Enum):
    """Enhanced banking intents with expanded coverage."""
    ACCOUNT_OPENING = "account_opening"
    CARD_BLOCK = "card_block"
    CARD_REPLACEMENT = "card_replacement"
    BALANCE_CHECK = "balance_check"
    ACCOUNT_BALANCE = "account_balance"
    LOAN_INFORMATION = "loan_information"
    LOAN_APPLICATION = "loan_application"
    ONLINE_BANKING = "online_banking"
    MOBILE_BANKING = "mobile_banking"
    ATM_SERVICES = "atm_services"
    MONEY_TRANSFER = "money_transfer"
    INTERNATIONAL_TRANSFER = "international_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    WORKING_HOURS = "working_hours"
    BRANCH_LOCATION = "branch_location"
    PIN_RESET = "pin_reset"
    PASSWORD_RESET = "password_reset"
    FRAUD_REPORT = "fraud_report"
    COMPLAINT = "complaint"
    FEES_CHARGES = "fees_charges"
    KYC_UPDATE = "kyc_update"
    CHECKBOOK_REQUEST = "checkbook_request"
    ACCOUNT_CLOSURE = "account_closure"
    GENERAL_BANKING = "general_banking_question"
    HUMAN_SUPPORT = "human_support"


class EnhancedIntentDetector:
    """
    Advanced intent detector with hybrid approach.
    
    Features:
    - Multi-language support (EN/AR)
    - Confidence scoring
    - Keyword + semantic similarity
    - Escalation detection
    """
    
    # Enhanced keywords for each intent (bilingual)
    INTENT_KEYWORDS = {
        BankingIntent.ACCOUNT_OPENING: {
            "en": [
                "open account", "new account", "create account", "start account",
                "apply account", "setup account", "bank account", "savings account",
                "current account", "business account"
            ],
            "ar": [
                "فتح حساب", "حساب جديد", "إنشاء حساب", "تأسيس حساب",
                "طلب حساب", "إعداد حساب", "حساب بنكي", "حساب توفير",
                "حساب جاري", "حساب تجاري"
            ]
        },
        BankingIntent.CARD_BLOCK: {
            "en": [
                "block card", "lost card", "stolen card", "missing card",
                "card lost", "freeze card", "disable card", "cancel card",
                "stolen debit card", "lost credit card"
            ],
            "ar": [
                "حظر البطاقة", "بطاقة مفقودة", "بطاقة مسروقة", "بطاقة في عداد المفقودين",
                "تجميد البطاقة", "تعطيل البطاقة", "إلغاء البطاقة"
            ]
        },
        BankingIntent.LOAN_INFORMATION: {
            "en": [
                "loan", "personal loan", "auto loan", "home loan", "mortgage",
                "borrow money", "loan application", "loan eligibility", "interest rate loan",
                "car loan", "house loan", "loan calculator", "emi"
            ],
            "ar": [
                "قرض", "قرض شخصي", "قرض سيارة", "قرض منزل", "رهن عقاري",
                "اقتراض مال", "طلب قرض", "أهلية القرض", "معدل فائدة القرض",
                "قرض سيارة", "قرض منزل"
            ]
        },
        BankingIntent.MONEY_TRANSFER: {
            "en": [
                "transfer money", "send money", "wire transfer", "fund transfer",
                "domestic transfer", "local transfer", "payment", "remit"
            ],
            "ar": [
                "تحويل أموال", "إرسال مال", "تحويل مصرفي", "تحويل أموال",
                "تحويل محلي", "دفع", "إرسال"
            ]
        },
        BankingIntent.INTERNATIONAL_TRANSFER: {
            "en": [
                "international transfer", "swift transfer", "foreign transfer",
                "overseas transfer", "cross border transfer", "ibans"
            ],
            "ar": [
                "تحويل دولي", "تحويل سويفت", "تحويل خارجي",
                "تحويل عبر الحدود"
            ]
        },
        BankingIntent.PIN_RESET: {
            "en": [
                "reset pin", "forgot pin", "change pin", "new pin",
                "pin reset", "atm pin", "card pin", "security code"
            ],
            "ar": [
                "إعادة تعيين الرمز السري", "نسيت الرمز", "تغيير الرمز",
                "رمز جديد", "رمز الصراف الآلي"
            ]
        },
        BankingIntent.FRAUD_REPORT: {
            "en": [
                "fraud", "scam", "unauthorized transaction", "suspicious",
                "stolen identity", "fake transaction", "hacked", "phishing"
            ],
            "ar": [
                "احتيال", "عملية احتيالية", "معاملة غير مصرح بها", "مشبوه",
                "سرقة الهوية", "معاملة مزورة"
            ]
        },
        BankingIntent.ONLINE_BANKING: {
            "en": [
                "online banking", "internet banking", "login", "username",
                "password", "digital banking", "e-banking", "portal"
            ],
            "ar": [
                "الخدمات المصرفية عبر الإنترنت", "الصرف الآلي عبر الإنترنت",
                "تسجيل الدخول", "اسم المستخدم", "كلمة المرور"
            ]
        },
        BankingIntent.BALANCE_CHECK: {
            "en": [
                "check balance", "account balance", "view balance", "see balance",
                "balance inquiry", "how much money", "available balance"
            ],
            "ar": [
                "التحقق من الرصيد", "رصيد الحساب", "عرض الرصيد",
                "الاستعلام عن الرصيد", "كم المال"
            ]
        },
        BankingIntent.WORKING_HOURS: {
            "en": [
                "working hours", "open time", "close time", "branch timing",
                "bank hours", "when open", "operating hours"
            ],
            "ar": [
                "ساعات العمل", "وقت الفتح", "وقت الإغلاق", "توقيت الفرع",
                "ساعات البنك"
            ]
        }
    }
    
    # Escalation keywords
    ESCALATION_KEYWORDS = {
        "en": [
            "complaint", "lawyer", "legal", "sue", "court", "manager",
            "supervisor", "human agent", "customer service representative",
            "speak to person", "talk to human", "escalate"
        ],
        "ar": [
            "شكوى", "محامي", "قانوني", "مدير", "مشرف",
            "وكيل بشري", "التحدث مع شخص", "ممثل خدمة العملاء"
        ]
    }
    
    def __init__(self, use_ml: bool = True):
        """
        Initialize enhanced intent detector.
        
        Args:
            use_ml: Whether to use ML-based classification (requires sentence-transformers)
        """
        self.use_ml = use_ml
        self._compile_patterns()
        
        # Try to load ML model if requested
        self.ml_model = None
        if use_ml:
            try:
                from sentence_transformers import SentenceTransformer
                self.ml_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("Loaded ML model for intent detection")
            except ImportError:
                logger.warning("sentence-transformers not installed. Using rule-based only.")
                self.use_ml = False
        
        logger.info("Enhanced intent detector initialized")
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for better performance."""
        self.intent_patterns = {}
        
        for intent, lang_keywords in self.INTENT_KEYWORDS.items():
            # Combine EN and AR keywords
            all_keywords = lang_keywords.get("en", []) + lang_keywords.get("ar", [])
            pattern = '|'.join([re.escape(keyword) for keyword in all_keywords])
            self.intent_patterns[intent] = re.compile(pattern, re.IGNORECASE | re.UNICODE)
        
        # Escalation pattern
        escalation_keywords = self.ESCALATION_KEYWORDS["en"] + self.ESCALATION_KEYWORDS["ar"]
        escalation_pattern = '|'.join([re.escape(kw) for kw in escalation_keywords])
        self.escalation_pattern = re.compile(escalation_pattern, re.IGNORECASE | re.UNICODE)
    
    def detect_intent(self, text: str) -> Tuple[BankingIntent, float, List[str]]:
        """
        Detect user intent using hybrid approach.
        
        Args:
            text: User input text
            
        Returns:
            Tuple of (detected intent, confidence score, matched keywords)
        """
        if not text or not text.strip():
            return BankingIntent.GENERAL_BANKING, 0.0, []
        
        # Get rule-based results
        rule_intent, rule_confidence, rule_keywords = self._rule_based_detection(text)
        
        # Get ML-based results if available
        ml_intent = None
        ml_confidence = 0.0
        
        if self.use_ml and self.ml_model:
            ml_intent, ml_confidence = self._ml_based_detection(text)
        
        # Combine results (weighted average)
        if ml_intent and ml_confidence > 0.6:
            # Use ML if high confidence
            if ml_confidence > rule_confidence:
                final_intent = ml_intent
                final_confidence = ml_confidence * 0.9  # Slight discount
                final_keywords = rule_keywords  # Still use rule-based keywords
            else:
                final_intent = rule_intent
                final_confidence = rule_confidence
                final_keywords = rule_keywords
        else:
            # Fall back to rule-based
            final_intent = rule_intent
            final_confidence = rule_confidence
            final_keywords = rule_keywords
        
        logger.debug(f"Final intent: {final_intent.value} (confidence: {final_confidence:.2f})")
        return final_intent, final_confidence, final_keywords
    
    def _rule_based_detection(self, text: str) -> Tuple[BankingIntent, float, List[str]]:
        """Rule-based intent detection."""
        text_lower = text.lower()
        matched_intents = []
        
        # Check each intent pattern
        for intent, pattern in self.intent_patterns.items():
            matches = pattern.findall(text_lower)
            if matches:
                unique_matches = list(set(matches))
                # Calculate confidence based on number of unique matches
                confidence = min(len(unique_matches) * 0.35 + 0.4, 0.95)
                matched_intents.append((intent, confidence, unique_matches))
        
        # Return best match
        if matched_intents:
            matched_intents.sort(key=lambda x: x[1], reverse=True)
            best_intent, confidence, keywords = matched_intents[0]
            return best_intent, confidence, keywords
        
        # Default to general banking question
        return BankingIntent.GENERAL_BANKING, 0.5, []
    
    def _ml_based_detection(self, text: str) -> Tuple[Optional[BankingIntent], float]:
        """
        ML-based intent detection using sentence embeddings.
        
        Args:
            text: User input text
            
        Returns:
            Tuple of (intent, confidence)
        """
        try:
            # Generate embedding for input text
            text_embedding = self.ml_model.encode([text])[0]
            
            # Compare with intent prototypes (pre-computed embeddings for intent labels)
            best_intent = None
            best_similarity = 0.0
            
            for intent in BankingIntent:
                # Generate embedding for intent label
                intent_text = intent.value.replace("_", " ")
                intent_embedding = self.ml_model.encode([intent_text])[0]
                
                # Calculate cosine similarity
                similarity = np.dot(text_embedding, intent_embedding) / (
                    np.linalg.norm(text_embedding) * np.linalg.norm(intent_embedding)
                )
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_intent = intent
            
            # Convert similarity to confidence (calibrated)
            confidence = best_similarity if best_similarity > 0.5 else 0.0
            
            return best_intent, confidence
            
        except Exception as e:
            logger.error(f"ML detection failed: {e}")
            return None, 0.0
    
    def needs_escalation(self, text: str) -> bool:
        """Check if query requires human escalation."""
        if not text:
            return False
        
        matches = self.escalation_pattern.findall(text.lower())
        return len(matches) > 0
    
    def get_intent_description(self, intent: BankingIntent) -> str:
        """Get human-readable description for intent."""
        descriptions = {
            BankingIntent.ACCOUNT_OPENING: "Account Opening Inquiry",
            BankingIntent.CARD_BLOCK: "Card Blocking Request",
            BankingIntent.CARD_REPLACEMENT: "Card Replacement Request",
            BankingIntent.BALANCE_CHECK: "Balance Check Request",
            BankingIntent.ACCOUNT_BALANCE: "Account Balance Inquiry",
            BankingIntent.LOAN_INFORMATION: "Loan Information Request",
            BankingIntent.LOAN_APPLICATION: "Loan Application",
            BankingIntent.ONLINE_BANKING: "Online Banking Support",
            BankingIntent.MOBILE_BANKING: "Mobile Banking Support",
            BankingIntent.ATM_SERVICES: "ATM Services Inquiry",
            BankingIntent.MONEY_TRANSFER: "Money Transfer Request",
            BankingIntent.INTERNATIONAL_TRANSFER: "International Transfer Request",
            BankingIntent.CREDIT_CARD: "Credit Card Inquiry",
            BankingIntent.DEBIT_CARD: "Debit Card Inquiry",
            BankingIntent.WORKING_HOURS: "Working Hours Inquiry",
            BankingIntent.BRANCH_LOCATION: "Branch Location Inquiry",
            BankingIntent.PIN_RESET: "PIN Reset Request",
            BankingIntent.PASSWORD_RESET: "Password Reset Request",
            BankingIntent.FRAUD_REPORT: "Fraud Report",
            BankingIntent.COMPLAINT: "Customer Complaint",
            BankingIntent.FEES_CHARGES: "Fees and Charges Inquiry",
            BankingIntent.KYC_UPDATE: "KYC Update Request",
            BankingIntent.CHECKBOOK_REQUEST: "Checkbook Request",
            BankingIntent.ACCOUNT_CLOSURE: "Account Closure Request",
            BankingIntent.GENERAL_BANKING: "General Banking Question",
            BankingIntent.HUMAN_SUPPORT: "Human Support Request"
        }
        
        return descriptions.get(intent, "Unknown Intent")


# Singleton instance
_enhanced_detector = None


def get_enhanced_intent_detector(use_ml: bool = True) -> EnhancedIntentDetector:
    """Get or create singleton enhanced intent detector instance."""
    global _enhanced_detector
    if _enhanced_detector is None:
        _enhanced_detector = EnhancedIntentDetector(use_ml=use_ml)
    return _enhanced_detector


def detect_intent(text: str) -> Tuple[BankingIntent, float, List[str]]:
    """Convenience function to detect intent."""
    detector = get_enhanced_intent_detector()
    return detector.detect_intent(text)
