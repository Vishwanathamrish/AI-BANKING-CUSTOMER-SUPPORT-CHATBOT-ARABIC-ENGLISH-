"""
Intent Detection Module - Classifies user intent for banking queries

This module uses a rule-based approach combined with keyword matching
to identify user intents for banking-specific queries.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class BankingIntent(Enum):
    """Supported banking intents."""
    # Account intents (fine-grained)
    ACCOUNT_OPENING = "account_opening"
    ACCOUNT_DOCUMENTS = "account_documents"  # NEW
    ACCOUNT_ONLINE = "account_online"  # NEW
    
    # Card intents (fine-grained)
    CARD_BLOCK = "card_block"
    CARD_LOST = "card_lost"  # NEW
    
    # Loan intents (fine-grained)
    LOAN_INFORMATION = "loan_information"
    LOAN_APPLY = "loan_apply"  # NEW - For loan applications
    LOAN_DOCUMENTS = "loan_documents"  # NEW
    LOAN_APPROVAL_TIME = "loan_approval_time"  # NEW
    LOAN_INTEREST = "loan_interest"  # NEW - For interest rates
    LOAN_TENURE = "loan_tenure"  # NEW - For loan duration
    LOAN_REPAYMENT = "loan_repayment"
    LOAN_BALANCE = "loan_balance"
    
    # Other intents
    ONLINE_BANKING = "online_banking"
    ATM_SERVICES = "atm_services"
    MONEY_TRANSFER = "money_transfer"
    CREDIT_CARD = "credit_card"
    ACCOUNT_BALANCE = "account_balance"
    WORKING_HOURS = "working_hours"
    PIN_RESET = "pin_reset"
    FRAUD_REPORT = "fraud_report"
    ACCOUNT_SECURITY = "account_security"
    GENERAL_BANKING = "general_banking_question"


class SmallTalkIntent(Enum):
    """Small talk and conversational intents."""
    GREETING = "greeting"
    FAREWELL = "farewell"
    THANKS = "thanks"
    AFFIRMATIVE = "affirmative"
    NEGATIVE = "negative"
    HOW_ARE_YOU = "how_are_you"
    SMALL_TALK = "small_talk"


class IntentDetector:
    """
    Intent detection service for banking queries.
    
    Uses keyword-based pattern matching to classify user intents.
    """
    
    # Intent keywords mapping (case-insensitive)
    INTENT_KEYWORDS = {
        BankingIntent.ACCOUNT_OPENING: [
            "open account", "new account", "create account", "start account",
            "account opening", "apply account", "setup account", "opening a bank account"
        ],
        BankingIntent.ACCOUNT_DOCUMENTS: [  # NEW
            "account documents", "documents required", "required documents",
            "what documents", "need documents", "documents needed"
        ],
        BankingIntent.ACCOUNT_ONLINE: [  # NEW
            "open account online", "online account", "internet account",
            "mobile app account", "digital account opening"
        ],
        BankingIntent.CARD_BLOCK: [
            "block card", "stolen card", "missing card",
            "freeze card", "disable card", "cancel card",
            "card stolen", "card lost"
        ],
        BankingIntent.CARD_LOST: [  # NEW
            "lost card", "lost my card", "card is lost",
            "misplaced card", "can't find card"
        ],
        BankingIntent.ACCOUNT_BALANCE: [
            "check balance", "account balance", "view balance", "see balance",
            "balance inquiry", "how much money", "my balance"
        ],
        BankingIntent.LOAN_INFORMATION: [
            "loan", "personal loan", "auto loan", "home loan", "mortgage",
            "borrow money", "loan application", "loan eligibility",
            "loan details", "loan information", "tell me about loans", "about loans"
        ],
        BankingIntent.LOAN_APPLY: [  # NEW - Application-specific
            "apply loan", "apply for loan", "loan apply", "get loan",
            "take loan", "request loan", "start loan", "new loan",
            "how to apply for personal loan", "how do i apply for loan",
            "apply for a loan", "applying for loan", "loan application process"
        ],
        BankingIntent.LOAN_DOCUMENTS: [  # NEW
            "loan documents", "documents for loan", "required documents loan",
            "what documents needed loan", "loan paperwork", "documents required loan"
        ],
        BankingIntent.LOAN_APPROVAL_TIME: [  # NEW
            "loan approval time", "how long loan takes", "loan processing time",
            "when loan approved", "loan timeline", "loan days", "approval days"
        ],
        BankingIntent.LOAN_INTEREST: [  # NEW - Interest rate specific
            "loan interest rate", "interest rate loan", "loan rate", 
            "loan interest", "percentage rate loan", "apr loan"
        ],
        BankingIntent.LOAN_TENURE: [  # NEW - Duration specific
            "loan tenure", "loan duration", "loan period", "loan term",
            "how many years loan", "loan years", "loan months"
        ],
        BankingIntent.LOAN_REPAYMENT: [  # NEW
            "repay loan", "early repayment", "foreclosure", "close loan",
            "prepay loan", "partially repay", "full settlement", "loan settlement",
            "pay off loan", "clear loan", "early closure"
        ],
        BankingIntent.LOAN_BALANCE: [  # NEW
            "check loan balance", "loan balance", "outstanding loan",
            "how much loan left", "remaining loan", "loan amount due",
            "view loan balance", "see loan balance"
        ],
        BankingIntent.ONLINE_BANKING: [
            "online banking", "internet banking", "mobile app", "login",
            "password", "username", "digital banking", "e-banking"
        ],
        BankingIntent.ATM_SERVICES: [
            "atm", "cash withdrawal", "withdraw cash", "atm card", "debit card",
            "cash deposit", "atm machine"
        ],
        BankingIntent.MONEY_TRANSFER: [
            "transfer money", "send money", "wire transfer", "international transfer",
            "remittance", "payment", "fund transfer"
        ],
        BankingIntent.CREDIT_CARD: [
            "credit card", "apply credit card", "credit card limit", 
            "credit card bill", "credit card payment"
        ],
        BankingIntent.PIN_RESET: [
            "reset pin", "forgot pin", "change pin", "new pin",
            "pin reset", "atm pin"
        ],
        BankingIntent.FRAUD_REPORT: [
            "fraud", "scam", "unauthorized transaction", "suspicious",
            "stolen identity", "fake transaction"
        ],
        BankingIntent.ACCOUNT_SECURITY: [  # NEW
            "secure account", "protect account", "account security",
            "safe account", "hack", "hacked", "security concern"
        ],
        BankingIntent.WORKING_HOURS: [
            "working hours", "open time", "close time", "branch timing",
            "bank hours", "when open"
        ]
    }
    
    # Escalation keywords - SMART LOGIC: Only for true emergencies and complex issues
    ESCALATION_KEYWORDS = [
        # Legal threats - MUST escalate
        "lawyer", "legal action", "sue", "court case", "filing complaint",
        "central bank complaint", "regulatory complaint",
        
        # Complex fraud cases - MUST escalate  
        "identity theft", "large fraud", "cybercrime", "police report fraud",
        
        # Explicit human request - MUST escalate
        "speak to human", "talk to person", "human agent", "real person",
        "customer service representative", "branch manager"
    ]
    
    # Arabic escalation keywords
    ARABIC_ESCALATION_KEYWORDS = [
        # Legal threats
        "محامي", "إجراء قانوني", "قضية", "محكمة", "تقديم شكوى",
        "شكوى للبنك المركزي", "شكوى للجهات الرقابية",
        
        # Complex fraud
        "سرقة الهوية", "احتيال كبير", "جريمة إلكترونية", "تقرير شرطة",
        
        # Explicit human request
        "أتحدث مع موظف", "ممثل خدمة عملاء", "مدير الفرع", "شخص حقيقي",
        "وكيل بشري"
    ]
    
    # DO NOT escalate for these - handle with normal banking responses
    NON_ESCALATION_KEYWORDS = [
        # General complaints - handle normally
        "complaint about service", "not satisfied", "unhappy with",
        
        # Simple requests - handle normally
        "how to", "can i", "what is", "tell me about",
        
        # Urgent but routine - handle with emergency templates
        "lost card", "stolen card", "block my card"  # These use emergency templates, not escalation
    ]
    
    # Arabic non-escalation keywords
    ARABIC_NON_ESCALATION_KEYWORDS = [
        # General complaints
        "شكوى على الخدمة", "غير راضي", "غير راضٍ عن",
        
        # Simple requests
        "كيف", "هل يمكن", "ما هو", "أخبرني عن",
        
        # Urgent but routine
        "بطاقة مفقودة", "بطاقة مسروقة", "حظر بطاقتي"  # Emergency templates, not escalation
    ]
    
    # Arabic keywords for loan intents (NEW)
    ARABIC_LOAN_KEYWORDS = {
        BankingIntent.LOAN_INFORMATION: [  # NEW - General loan info
            "قرض", "قروض", "القرض الشخصي", "القروض الشخصية", "تمويل", "تمويل شخصي"
        ],
        BankingIntent.LOAN_APPLY: [
            "تقديم قرض", "طلب قرض", "الحصول على قرض", "أريد قرض", "كيف أقوم بطلب قرض"
        ],
        BankingIntent.LOAN_DOCUMENTS: [
            "مستندات القرض", "الأوراق المطلوبة للقرض", "وثائق القرض", "ما هي مستندات القرض"
        ],
        BankingIntent.LOAN_APPROVAL_TIME: [
            "مدة الموافقة على القرض", "كم يستغرق القرض", "وقت الموافقة على القرض", "متى يتم الموافقة على القرض"
        ],
        BankingIntent.LOAN_INTEREST: [
            "نسبة فائدة القرض", "فائدة القرض", "معدل الربح للقرض", "كم نسبة الفائدة"
        ],
        BankingIntent.LOAN_TENURE: [
            "مدة القرض", "فترة القرض", "كم سنة القرض", "مدة سداد القرض"
        ],
        BankingIntent.LOAN_REPAYMENT: [
            "سداد القرض", "دفع القرض", "إغلاق القرض", "التسوية المبكرة", "كيف أسدد القرض"
        ]
    }
    
    # Arabic keywords for card intents (CRITICAL FOR EMERGENCY)
    ARABIC_CARD_KEYWORDS = {
        BankingIntent.CARD_LOST: [  # NEW - Lost card specific
            "بطاقة مفقودة", "بطاقتي مفقودة", "ضاعت بطاقتي", "فقدت بطاقتي", "البطاقة ضائعة"
        ],
        BankingIntent.CARD_BLOCK: [  # Enhanced with more Arabic phrases
            "احظر البطاقة", "حظر بطاقتي", "بطاقة مسروقة", "سرقة البطاقة", 
            "تجميد البطاقة", "إلغاء البطاقة", "عطّل البطاقة", "احظرها فوراً"
        ]
    }
    
    def __init__(self):
        """Initialize the intent detector."""
        self._compile_patterns()
        logger.info("Intent detector initialized")
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for better performance."""
        self.intent_patterns = {}
        
        for intent, keywords in self.INTENT_KEYWORDS.items():
            # Create pattern from keywords
            pattern = '|'.join([re.escape(keyword) for keyword in keywords])
            self.intent_patterns[intent] = re.compile(pattern, re.IGNORECASE)
        
        # Escalation pattern
        escalation_pattern = '|'.join([re.escape(kw) for kw in self.ESCALATION_KEYWORDS])
        self.escalation_pattern = re.compile(escalation_pattern, re.IGNORECASE)
    
    def detect_intent(self, text: str) -> Tuple[BankingIntent, float, List[str]]:
        """
        Detect user intent from input text with enhanced loan handling.
        
        CRITICAL: ALL loan-related queries MUST map to loan intents.
        This ensures they bypass RAG and get LLM responses.
        
        Args:
            text: User input text
            
        Returns:
            Tuple of (detected intent, confidence score, matched keywords)
        """
        if not text or not text.strip():
            return BankingIntent.GENERAL_BANKING, 0.0, []
        
        text_lower = text.lower()
        
        # STEP 1: CRITICAL - Check for ANY loan-related keywords FIRST (HIGHEST PRIORITY)
        # This ensures ALL loan queries are caught BEFORE any other logic
        comprehensive_loan_keywords = [
            "loan", "personal loan", "auto loan", "home loan", "car loan",
            "mortgage", "borrow money", "loan application", "apply for loan", 
            "apply loan", "get loan", "take loan", "request loan",
            "loan documents", "documents for loan", "loan paperwork",
            "loan approval", "approval time loan", "how long loan",
            "loan interest", "interest rate loan", "loan rate", "apr loan",
            "loan tenure", "loan duration", "loan period", "loan term",
            "loan repayment", "repay loan", "early settlement", 
            "prepay loan", "close loan", "pay off loan",
            "loan balance", "check loan", "loan amount", "loan details",
            "outstanding loan", "remaining loan", "loan left"
        ]
        
        # BROADER MATCHING: Also check for individual components
        primary_loan_words = ["loan", "loans", "borrow", "borrowing", "mortgage", "finance", "emi"]
        action_words = ["apply", "application", "get", "take", "request", "need", "want"]
        
        is_loan_query = any(keyword in text_lower for keyword in comprehensive_loan_keywords)
        
        # ADDITIONAL CHECK 1: If "apply" + any loan word exists separately
        if not is_loan_query:
            has_action = any(action in text_lower for action in action_words)
            has_loan = any(loan_word in text_lower for loan_word in primary_loan_words)
            if has_action and has_loan:
                is_loan_query = True
                logger.info(f"✅ Loan query detected via action+loan pattern")
        
        # ADDITIONAL CHECK 2: CRITICAL - If query contains "loan" at all, ALWAYS treat as loan query
        if "loan" in text_lower or "loans" in text_lower:
            is_loan_query = True
            logger.info(f"✅ Loan query forced - contains 'loan' keyword")
        
        if is_loan_query:
            logger.info(f"✅ Loan query detected - ensuring proper loan intent mapping")
        
        matched_intents = []
        
        # STEP 2: CRITICAL - If loan query detected, SKIP all other intent pattern matching
        # This prevents "apply" or other intents from overriding loan intent
        if is_loan_query:
            # Directly add loan intent with high confidence
            matched_intents.append((BankingIntent.LOAN_INFORMATION, 0.9, ["loan query detected"]))
            logger.info(f"⚡ Skipping other intent patterns - loan query takes priority")
            
            # BUT still check for specific loan sub-intents to provide better accuracy
            # Check for LOAN_APPLY keywords
            apply_keywords = ["apply", "application", "get loan", "take loan", "request loan"]
            if any(kw in text_lower for kw in apply_keywords):
                matched_intents.append((BankingIntent.LOAN_APPLY, 0.85, ["apply for loan"]))
                logger.info(f"🎯 Specific loan sub-intent detected: LOAN_APPLY")
            
            # Check for LOAN_DOCUMENTS keywords
            doc_keywords = ["documents", "required documents", "what documents", "paperwork"]
            if any(kw in text_lower for kw in doc_keywords) and ("loan" in text_lower or "documents" in text_lower):
                matched_intents.append((BankingIntent.LOAN_DOCUMENTS, 0.85, ["loan documents"]))
                logger.info(f"🎯 Specific loan sub-intent detected: LOAN_DOCUMENTS")
            
            # Check for LOAN_APPROVAL_TIME keywords
            time_keywords = ["how long", "approval time", "time does", "takes", "how many days"]
            if any(kw in text_lower for kw in time_keywords):
                matched_intents.append((BankingIntent.LOAN_APPROVAL_TIME, 0.85, ["loan approval time"]))
                logger.info(f"🎯 Specific loan sub-intent detected: LOAN_APPROVAL_TIME")
            
            # Check for LOAN_INTEREST keywords
            interest_keywords = ["interest", "interest rate", "rate", "percentage", "apr"]
            if any(kw in text_lower for kw in interest_keywords):
                matched_intents.append((BankingIntent.LOAN_INTEREST, 0.85, ["loan interest"]))
                logger.info(f"🎯 Specific loan sub-intent detected: LOAN_INTEREST")
            
            # Check for LOAN_REPAYMENT keywords
            repay_keywords = ["repay", "repayment", "early settlement", "close loan", "pay off", "settlement"]
            if any(kw in text_lower for kw in repay_keywords):
                matched_intents.append((BankingIntent.LOAN_REPAYMENT, 0.85, ["loan repayment"]))
                logger.info(f"🎯 Specific loan sub-intent detected: LOAN_REPAYMENT")
        else:
            # Only check other intents if NOT a loan query
            # Check each intent pattern
            for intent, pattern in self.intent_patterns.items():
                matches = pattern.findall(text_lower)
                if matches:
                    # Calculate confidence based on number of matches
                    confidence = min(len(matches) * 0.3 + 0.4, 0.95)
                    matched_intents.append((intent, confidence, matches))
        
        # Check Arabic keywords for loan AND card intents (enhanced detection)
        is_arabic = any('\u0621' <= char <= '\u064A' for char in text)
        if is_arabic:
            # Check loan keywords
            for intent, keywords in self.ARABIC_LOAN_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in text:
                        # Boost confidence for Arabic matches
                        confidence = 0.85
                        matched_intents.append((intent, confidence, [keyword]))
                        logger.debug(f"Arabic loan keyword matched: {keyword}")
            
            # Check card keywords (CRITICAL FOR EMERGENCY)
            for intent, keywords in self.ARABIC_CARD_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in text:
                        # High confidence for emergency card blocking
                        confidence = 0.95
                        matched_intents.append((intent, confidence, [keyword]))
                        logger.info(f"🚨 ARABIC CARD EMERGENCY detected: {intent.value} - keyword: {keyword}")
        
        # Check for escalation
        escalation_matches = self.escalation_pattern.findall(text_lower)
        if escalation_matches:
            logger.info(f"Detected escalation keywords: {escalation_matches}")
        
        # STEP 3: CRITICAL - If loan query detected but no loan intent matched, force it
        if is_loan_query and not any('loan' in i.value for i, c, k in matched_intents):
            # Force LOAN_INFORMATION intent to ensure it gets handled properly
            logger.info(f"Forcing loan intent for query: {text[:50]}")
            matched_intents.append((BankingIntent.LOAN_INFORMATION, 0.8, ["loan keyword match"]))
        
        # Return best match
        if matched_intents:
            # Sort by confidence
            matched_intents.sort(key=lambda x: x[1], reverse=True)
            best_intent, confidence, keywords = matched_intents[0]
            
            # SPECIAL HANDLING FOR LOANS:
            # If multiple loan intents detected, prefer specific over general
            loan_intents = [i for i, c, k in matched_intents if 'loan' in i.value]
            if len(loan_intents) > 1 and BankingIntent.LOAN_INFORMATION in loan_intents:
                # Prefer specific loan sub-intent over general LOAN_INFORMATION
                specific_loan = next((i for i in loan_intents if i != BankingIntent.LOAN_INFORMATION), None)
                if specific_loan:
                    best_intent = specific_loan
                    logger.info(f"Prioritized specific loan intent: {best_intent.value}")
            
            logger.debug(f"Detected intent: {best_intent.value} (confidence: {confidence:.2f})")
            return best_intent, confidence, keywords
        
        # Default to general banking question
        logger.debug("No specific intent detected, using general_banking_question")
        return BankingIntent.GENERAL_BANKING, 0.5, []
    
    def detect_small_talk(self, text: str) -> Optional[SmallTalkIntent]:
        """
        Detect if query is small talk or conversational.
        
        Args:
            text: User input text
            
        Returns:
            SmallTalkIntent if detected, None otherwise
        """
        if not text:
            return None
        
        text_lower = text.lower().strip()
        
        # GREETINGS - English and Arabic
        greetings = [
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "مرحبا", "أهلا", "السلام عليكم", "صباح الخير", "مساء الخير"
        ]
        
        # FAREWELLS
        farewells = [
            "bye", "goodbye", "see you", "take care", "farewell",
            "وداعا", "مع السلامة", "إلى اللقاء"
        ]
        
        # THANKS
        thanks = [
            "thanks", "thank you", "thank u", "thx", "cheers", "appreciate",
            "شكرا", "شكر لك", "جزاك الله خيرا"
        ]
        
        # AFFIRMATIVE
        affirmative = [
            "yes", "yeah", "yep", "sure", "ok", "okay", "correct", "right",
            "نعم", "أكيد", "بالطبع"
        ]
        
        # NEGATIVE
        negative = [
            "no", "nope", "nah", "don't", "doesn't", "can't", "won't",
            "لا", "مو", "مش"
        ]
        
        # HOW ARE YOU
        how_are_you = [
            "how are you", "how're you", "how is it going", "what's up", "how about you",
            "كيف حالك", "كيف الحال", "شلونك"
        ]
        
        # Check each category
        if any(word in text_lower for word in greetings):
            logger.debug(f"✅ Detected greeting: {text[:40]}")
            return SmallTalkIntent.GREETING
        
        if any(word in text_lower for word in farewells):
            logger.debug(f"✅ Detected farewell: {text[:40]}")
            return SmallTalkIntent.FAREWELL
        
        if any(word in text_lower for word in thanks):
            logger.debug(f"✅ Detected thanks: {text[:40]}")
            return SmallTalkIntent.THANKS
        
        if any(word in text_lower for word in affirmative):
            logger.debug(f"✅ Detected affirmative: {text[:40]}")
            return SmallTalkIntent.AFFIRMATIVE
        
        if any(word in text_lower for word in negative):
            logger.debug(f"✅ Detected negative: {text[:40]}")
            return SmallTalkIntent.NEGATIVE
        
        if any(phrase in text_lower for phrase in how_are_you):
            logger.debug(f"✅ Detected how_are_you: {text[:40]}")
            return SmallTalkIntent.HOW_ARE_YOU
        
        # Check if very short (1-3 words) - likely small talk
        # BUT EXCLUDE banking keywords - don't misclassify emergency requests!
        words = text_lower.split()
        if len(words) <= 3 and len(text_lower) <= 20:
            # CRITICAL: Check if it contains banking keywords before classifying as small talk
            banking_keywords = [
                "card", "lost", "block", "stolen", "emergency",
                "loan", "account", "balance", "money", "transfer",
                "بطاقة", "مفقودة", "احظر", "مسروقة", "قرض", "حساب", "رصيد"
            ]
            
            has_banking_keyword = any(kw in text_lower for kw in banking_keywords)
            
            if has_banking_keyword:
                logger.debug(f"⚠️ Short query but contains banking keyword - NOT small talk: {text[:40]}")
                return None  # NOT small talk - let it go through normal banking flow
            
            logger.debug(f"✅ Very short query classified as small talk: {text[:40]}")
            return SmallTalkIntent.SMALL_TALK
        
        return None
    
    def get_small_talk_response(self, intent: SmallTalkIntent, language: str = "en") -> str:
        """
        Get appropriate response for small talk intents.
        
        Args:
            intent: SmallTalkIntent enum
            language: Response language ('en' or 'ar')
            
        Returns:
            Friendly conversational response
        """
        responses = {
            SmallTalkIntent.GREETING: {
                "en": "Hello! 👋 How can I assist you with your banking needs today?",
                "ar": "مرحباً! 👋 كيف يمكنني مساعدتك في احتياجاتك المصرفية اليوم؟"
            },
            SmallTalkIntent.FAREWELL: {
                "en": "Goodbye! Have a great day! Feel free to return if you need any banking assistance.",
                "ar": "وداعاً! أتمنى لك يوماً رائعاً! لا تتردد في العودة إذا احتجت إلى أي مساعدة مصرفية."
            },
            SmallTalkIntent.THANKS: {
                "en": "You're welcome! 😊 Let me know if you need any banking assistance.",
                "ar": "عفواً! 😊 أخبرني إذا كنت بحاجة إلى أي مساعدة مصرفية."
            },
            SmallTalkIntent.AFFIRMATIVE: {
                "en": "Great! How can I help you with your banking today?",
                "ar": "رائع! كيف يمكنني مساعدتك في الخدمات المصرفية اليوم؟"
            },
            SmallTalkIntent.NEGATIVE: {
                "en": "No problem! Feel free to ask if you have any banking questions.",
                "ar": "لا مشكلة! لا تتردد في السؤال إذا كان لديك أي استفسارات مصرفية."
            },
            SmallTalkIntent.HOW_ARE_YOU: {
                "en": "I'm doing well, thank you! 😊 I'm here to help with your banking needs. What can I do for you today?",
                "ar": "أنا بخير، شكراً! 😊 أنا هنا لمساعدتك في احتياجاتك المصرفية. ماذا يمكنني أن أفعل لك اليوم؟"
            },
            SmallTalkIntent.SMALL_TALK: {
                "en": "I'm here to help with banking services like accounts, cards, and loans. How can I assist you?",
                "ar": "أنا هنا لمساعدتك في الخدمات المصرفية مثل الحسابات والبطاقات والقروض. كيف يمكنني مساعدتك؟"
            }
        }
        
        return responses.get(intent, {}).get(language, responses[SmallTalkIntent.SMALL_TALK]["en"])
    
    def needs_escalation(self, text: str) -> bool:
        """
        Check if query requires human escalation - SMART LOGIC.
        
        CRITERIA FOR ESCALATION:
        1. Legal threats or regulatory complaints
        2. Complex fraud cases (identity theft, cybercrime)
        3. Explicit request for human agent
        
        DO NOT ESCALATE FOR:
        - General service complaints (handle normally)
        - Lost/stolen cards (use emergency templates)
        - Routine banking queries (even if urgent)
        
        Args:
            text: User input text
            
        Returns:
            True if escalation needed
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check English escalation keywords
        escalation_matches = [kw for kw in self.ESCALATION_KEYWORDS if kw in text_lower]
        
        # Check Arabic escalation keywords
        arabic_escalation_matches = [kw for kw in self.ARABIC_ESCALATION_KEYWORDS if kw in text]
        
        # Check non-escalation keywords (override escalation)
        non_escalation_matches = [kw for kw in self.NON_ESCALATION_KEYWORDS if kw in text_lower]
        arabic_non_escalation = [kw for kw in self.ARABIC_NON_ESCALATION_KEYWORDS if kw in text]
        
        # If contains non-escalation keywords, DO NOT escalate (handle normally)
        if non_escalation_matches or arabic_non_escalation:
            logger.info(f"Query contains non-escalation keywords - handling normally")
            return False
        
        # Only escalate if clear escalation intent detected (EN or AR)
        if escalation_matches or arabic_escalation_matches:
            logger.info(f"Escalation required due to: {escalation_matches + arabic_escalation_matches}")
            return True
        
        return False
    
    def get_intent_description(self, intent: BankingIntent) -> str:
        """
        Get human-readable description for intent.
        
        Args:
            intent: BankingIntent enum
            
        Returns:
            Description string
        """
        descriptions = {
            BankingIntent.ACCOUNT_OPENING: "Account Opening Inquiry",
            BankingIntent.CARD_BLOCK: "Card Blocking Request",
            BankingIntent.BALANCE_CHECK: "Balance Check Request",
            BankingIntent.LOAN_INFORMATION: "Loan Information Request",
            BankingIntent.ONLINE_BANKING: "Online Banking Support",
            BankingIntent.ATM_SERVICES: "ATM Services Inquiry",
            BankingIntent.MONEY_TRANSFER: "Money Transfer Request",
            BankingIntent.CREDIT_CARD: "Credit Card Inquiry",
            BankingIntent.ACCOUNT_BALANCE: "Account Balance Inquiry",
            BankingIntent.WORKING_HOURS: "Working Hours Inquiry",
            BankingIntent.PIN_RESET: "PIN Reset Request",
            BankingIntent.FRAUD_REPORT: "Fraud Report",
            BankingIntent.ACCOUNT_SECURITY: "Account Security Inquiry",  # NEW
            BankingIntent.GENERAL_BANKING: "General Banking Question"
        }
        
        return descriptions.get(intent, "Unknown Intent")


# Singleton instance
_intent_detector = None


def get_intent_detector() -> IntentDetector:
    """Get or create singleton intent detector instance."""
    global _intent_detector
    if _intent_detector is None:
        _intent_detector = IntentDetector()
    return _intent_detector


def detect_intent(text: str) -> Tuple[BankingIntent, float, List[str]]:
    """
    Convenience function to detect intent.
    
    Args:
        text: User input text
        
    Returns:
        Tuple of (intent, confidence, matched keywords)
    """
    detector = get_intent_detector()
    return detector.detect_intent(text)
