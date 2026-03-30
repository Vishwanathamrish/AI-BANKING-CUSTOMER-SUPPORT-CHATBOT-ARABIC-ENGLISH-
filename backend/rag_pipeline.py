"""
RAG Pipeline Module - Complete Retrieval-Augmented Generation implementation

This module orchestrates the entire RAG pipeline:
- Document loading
- Text chunking
- Embedding generation
- Vector storage
- Retrieval
- LLM response generation
"""

import os
import logging
import time
from typing import List, Dict, Optional, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv

from .embeddings import EmbeddingService
from .vector_store import VectorStoreManager
from .intent_detection import IntentDetector, BankingIntent, get_intent_detector
from .tools import BankingTools, get_banking_tools
from .normalizer import get_normalizer, normalize_response
from .response_validator import get_validator, clean_response, validate_response, validate_bullet_count, extract_bullets
from .intent_formatter import get_intent_formatter, format_response_by_intent
from .loan_generator import get_loan_generator, generate_loan_response

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Complete RAG pipeline for question answering.
    
    Attributes:
        embeddings_service: Service for generating embeddings
        vector_store_manager: Manager for FAISS vector store
        llm: Language model instance
        text_splitter: Text splitting configuration
        similarity_threshold: Minimum confidence threshold
    """
    
    def __init__(
        self,
        embeddings_service: EmbeddingService,
        vector_store_manager: VectorStoreManager,
        model_name: str = "llama-3.1-8b-instant",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        similarity_threshold: float = 0.5
    ):
        """
        Initialize the RAG pipeline.
        
        Args:
            embeddings_service: EmbeddingService instance
            vector_store_manager: VectorStoreManager instance
            model_name: Groq LLM model to use
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            similarity_threshold: Minimum confidence score
        """
        self.embeddings_service = embeddings_service
        self.vector_store_manager = vector_store_manager
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.similarity_threshold = similarity_threshold
        
        # Initialize intent detector and tools
        self.intent_detector = get_intent_detector()
        self.banking_tools = get_banking_tools()
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize LLM and text splitter."""
        try:
            # Import Groq service
            from .groq_llm import get_groq_service
            
            # Initialize Groq LLM with deterministic parameters
            self.llm = get_groq_service(
                model_name=self.model_name,
                temperature=0.2,  # Low temperature for deterministic output
                max_tokens=300  # Controlled output length
            )
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            logger.info(f"Initialized RAG pipeline with Groq model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error initializing RAG components: {e}")
            raise
    
    def load_and_process_documents(self, documents: List[Document]) -> bool:
        """
        Load documents and create vector index.
        
        Args:
            documents: List of raw documents
            
        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Processing {len(documents)} documents")
            
            # Split documents into chunks
            split_docs = self.text_splitter.split_documents(documents)
            logger.info(f"Split into {len(split_docs)} chunks")
            
            # Create vector index
            success = self.vector_store_manager.create_index(split_docs)
            
            if success:
                logger.info("Documents processed and indexed successfully")
            else:
                logger.error("Failed to create vector index")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing documents: {e}")
            return False
    
    def retrieve_context(self, query: str, k: int = 3) -> Tuple[List[Document], float]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query
            k: Number of documents to retrieve
            
        Returns:
            Tuple of (relevant documents, confidence score)
        """
        if self.vector_store_manager.index is None:
            logger.error("Cannot retrieve: No index loaded")
            return [], 0.0
        
        try:
            # Search with scores
            results = self.vector_store_manager.similarity_search_with_score(query, k=k)
            
            if not results:
                return [], 0.0
            
            # Extract documents and scores
            docs = [doc for doc, score in results]
            
            # Calculate average confidence (convert distance to similarity)
            # FAISS returns L2 distance, lower = more similar
            avg_distance = sum(score for _, score in results) / len(results)
            
            # Convert to similarity score (simple heuristic)
            # This is approximate - production systems should use cosine similarity
            confidence = 1.0 / (1.0 + avg_distance)
            
            logger.debug(f"Retrieved {len(docs)} documents with confidence: {confidence:.3f}")
            
            return docs, confidence
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return [], 0.0
    
    def _is_banking_query(self, query: str) -> bool:
        """
        CRITICAL DOMAIN FILTER - Check if query is banking-related.
        
        ENHANCED VERSION with comprehensive keyword coverage.
        Supports English + Arabic with flexible matching.
        
        Args:
            query: User query
            
        Returns:
            True if banking-related, False otherwise
        """
        query_lower = query.lower()
        
        # DEBUG LOGGING
        logger.debug(f"🔍 Checking if query is banking: {query[:60]}")
        
        # Comprehensive banking keywords (ENGLISH + ARABIC) - EXPANDED
        banking_keywords = [
            # Core banking - ENGLISH
            "account", "bank account", "open account", "bank", "banking",
            "balance", "minimum balance", "account balance",
            "loan", "loans", "credit", "debit", "card", "atm",
            "transfer", "transaction", "interest", "deposit", "withdrawal",
            "payment", "emi", "finance", "financing",
            
            # Account-specific - ENGLISH
            "open account", "close account", "savings account", "current account",
            "checking account", "account opening", "activate account",
            "bank statement", "account statement", "passbook",
            
            # Card-specific - ENGLISH
            "atm card", "debit card", "credit card", "card activation",
            "activate card", "block card", "lost card", "stolen card",
            "pin", "cvv", "card pin", "atm pin",
            
            # Balance & Money - ENGLISH
            "balance check", "check balance", "account balance",
            "minimum balance", "average balance", "balance inquiry",
            "money", "cash", "fund", "funds",
            
            # Digital Banking - ENGLISH
            "online banking", "mobile banking", "internet banking",
            "app", "application", "login", "register", "signup",
            
            # Transfer & Payment - ENGLISH
            "money transfer", "fund transfer", "wire transfer",
            "international transfer", "local transfer", "remittance",
            "bill payment", "utility payment",
            
            # Loan-specific - ENGLISH
            "personal loan", "auto loan", "home loan", "mortgage",
            "borrow", "borrowing", "loan application", "loan approval",
            
            # UAE-specific - ENGLISH
            "uae", "emirates id", "aed", "dirham", "dhs",
            
            # Core banking - ARABIC (EXPANDED)
            "حساب", "بنك", "مصرف", "قرض", "قروض", "تمويل", "ائتمان", "بطاقة", "بطاقات",
            "فائدة", "قسط", "رصيد", "معاملات", "تحويل", "دفع", "مدفوعات",
            "إيداع", "سحب", "سحوبات", "إيداعات",
            
            # Account-specific - ARABIC
            "فتح حساب", "إغلاق حساب", "حساب توفير", "حساب جاري",
            "كشف حساب", "دفتر توفير", "تفعيل حساب",
            
            # Card-specific - ARABIC (CRITICAL FOR EMERGENCY)
            "بطاقة الصراف", "بطاقة الائتمان", "بطاقة خصم", "بطاقتي", "بطاقة",
            "تفعيل بطاقة", "حظر بطاقة", "بطاقة مفقودة", "بطاقة مسروقة", "مفقودة", "مسروقة",
            "احظر", "احظرها", "فوراً", "سرعة",
            "رقم سري", "رمز أمان", "كود سري",
            
            # Balance - ARABIC
            "الرصيد", "التحقق من الرصيد", "كشف الرصيد",
            "الحد الأدنى للرصيد", "استعلام الرصيد",
            
            # Transfer - ARABIC
            "تحويل أموال", "تحويل نقدي", "حوالة", "تحويل داخلي",
            "تحويل خارجي", "تحويل دولي",
            
            # Digital Banking - ARABIC
            "الخدمات المصرفية", "المصرفية الإلكترونية", "التطبيقات المصرفية",
            "تسجيل الدخول", "كلمة المرور", "اسم المستخدم", "تسجيل", "اشتراك",
            
            # Loan-specific - ARABIC (EXPANDED)
            "قرض شخصي", "قرض سيارة", "قرض عقاري", "رهن", "اقتراض",
            "طلب قرض", "موافقة القرض", "مستندات القرض", "أوراق القرض",
            "القروض الشخصية", "شخصية", "عن القروض", "أخبرني عن",
            
            # Services - ARABIC
            "احتيال", "نصب", "غير مصرح", "فرع", "راتب", "تمويل شخصي",
            
            # UAE-specific - ARABIC
            "الإمارات", "هوية إماراتية", "درهم", "د.إ"
        ]
        
        # Check if any banking keyword exists in query
        is_banking = any(keyword in query_lower for keyword in banking_keywords)
        
        # DEBUG: Log which keywords matched
        if not is_banking:
            matched_keywords = [kw for kw in banking_keywords if kw in query_lower]
            logger.warning(f"⚠️ NO BANKING KEYWORDS MATCHED in: '{query[:60]}'")
            logger.warning(f"⚠️ Query lowercased: '{query_lower}'")
            logger.warning(f"⚠️ Checking for 'transfer': {'transfer' in query_lower}")
            logger.warning(f"⚠️ Checking for 'money': {'money' in query_lower}")
        else:
            matched_kws = [kw for kw in banking_keywords if kw in query_lower]
            logger.info(f"✅ Banking keywords matched: {matched_kws[:5]}")
        
        # ADDITIONAL CHECK: If query contains Arabic characters, be more permissive
        # This prevents false negatives for legitimate Arabic banking queries
        has_arabic = any('\u0621' <= char <= '\u064A' for char in query)
        if has_arabic and not is_banking:
            # Check for common Arabic banking patterns
            arabic_banking_patterns = [
                r".*بطاقة.*",  # Anything with "card"
                r".*قرض.*",   # Anything with "loan"
                r".*حساب.*",  # Anything with "account"
                r".*رصيد.*",  # Anything with "balance"
                r".*بنك.*",   # Anything with "bank"
                r".*مصرف.*",  # Anything with "bank"
                r".*تمويل.*", # Anything with "finance"
            ]
            import re
            for pattern in arabic_banking_patterns:
                if re.search(pattern, query):
                    is_banking = True
                    logger.debug(f"✅ Query matched Arabic banking pattern: {pattern}")
                    break
        
        # DEBUG LOGGING
        if is_banking:
            logger.debug(f"✅ Query DETECTED as banking: {query[:60]}")
        else:
            logger.debug(f"❌ Query NOT detected as banking: {query[:60]}")
        
        return is_banking
    
    def _is_loan_query(self, query: str) -> bool:
        """
        CENTRALIZED LOAN DETECTION - Authoritative check for loan queries.
        
        This is the SINGLE source of truth for detecting loan queries.
        All loan-related queries MUST go through this function.
        
        Args:
            query: User query
            
        Returns:
            True if loan-related, False otherwise
        """
        query_lower = query.lower()
        
        # Comprehensive loan keywords - ALL variations
        loan_keywords = [
            # Core loan terms
            "loan", "loans", "personal loan", "auto loan", "home loan",
            "car loan", "mortgage", "borrow", "borrowing", "borrower",
            
            # Loan-specific terms
            "emi", "interest rate", "loan interest", "apr", "finance",
            "financing", "loan application", "apply for loan", "apply loan",
            
            # Repayment terms
            "repay", "repayment", "early settlement", "full settlement",
            "close loan", "pay off loan", "prepay", "foreclosure",
            
            # Loan documents & process
            "loan documents", "loan approval", "loan tenure", "loan amount",
            "loan balance", "loan details", "loan information", "about loans"
        ]
        
        # Check if ANY loan keyword exists in query
        is_loan = any(keyword in query_lower for keyword in loan_keywords)
        
        if is_loan:
            logger.debug(f"✅ Loan query detected: contains loan keyword")
        
        return is_loan
    
    def _is_account_query(self, query: str) -> bool:
        """
        ACCOUNT QUERY DETECTOR - Identify account-related queries.
        
        This ensures account queries get proper LLM fallback when RAG fails.
        
        Args:
            query: User query
            
        Returns:
            True if account-related, False otherwise
        """
        query_lower = query.lower()
        
        # Comprehensive account keywords
        account_keywords = [
            # Core account terms
            "account", "accounts", "bank account", "open account",
            "savings account", "current account", "checking account",
            
            # Account actions
            "open an account", "opening an account", "create account",
            "setup account", "set up account", "start account",
            "close account", "closing account",
            
            # Account-specific
            "account opening", "account setup", "account creation",
            "new account", "first account",
            
            # Arabic account terms
            "فتح حساب", "حساب بنكي", "حساب توفير", "حساب جاري"
        ]
        
        # Check if ANY account keyword exists in query
        is_account = any(keyword in query_lower for keyword in account_keywords)
        
        if is_account:
            logger.debug(f"✅ Account query detected: contains account keyword")
        
        return is_account
    
    def _generate_domain_restricted_response(self, language: str) -> Dict:
        """
        Generate response for non-banking queries (domain restriction).
        
        IMPROVED: More polite and helpful message.
        
        Args:
            language: Response language
            
        Returns:
            Dictionary with domain restriction message
        """
        if language.lower() in ["arabic", "ar"]:
            message = "أنا هنا للمساعدة في الخدمات المصرفية مثل الحسابات والبطاقات والقروض. هل يمكنك طرح سؤال مصرفي؟"
        else:
            message = "I can help with banking services like accounts, cards, and loans. Could you please ask a banking-related question?"
        
        return {
            "answer": message,
            "confidence": 1.0,
            "source_documents": [],
            "language": language,
            "fallback": False,
            "domain_restricted": True,
            "response_type": "domain_filter",
            "intent": "non_banking"
        }
    
    def generate_response(
        self,
        query: str,
        chat_history: List[Tuple[str, str]],
        language: str = "English"
    ) -> Dict:
        """
        Generate response using RAG with intent detection and tool integration.
        
        Args:
            query: User query
            chat_history: Previous conversation
            language: Response language preference
            
        Returns:
            Dictionary containing answer, confidence, and metadata
        """
        start_time = time.time()
        
        try:
            # STEP 0: CRITICAL - Check if query is banking-related FIRST
            # This prevents legitimate banking queries from being misclassified as small talk
            logger.info(f"🔍 STEP 0: Checking if '{query[:50]}' is banking query...")
            is_banking_result = self._is_banking_query(query)
            logger.info(f"🔍 Banking check result: {is_banking_result}")
            
            if not is_banking_result:
                logger.info(f"⛔ Non-banking query detected: {query[:50]}")
                return self._generate_domain_restricted_response(language)
            
            # STEP 1: Now check for small talk and greetings (ONLY for banking queries)
            # CRITICAL: Be VERY conservative - if it has banking keywords, skip small talk entirely
            has_banking_keyword = any(kw in query.lower() for kw in ['transfer', 'money', 'account', 'card', 'loan', 'balance', 'bank'])
            
            if has_banking_keyword:
                logger.info(f"💰 Query has banking keyword - SKIPPING small talk check")
                small_talk_intent = None
            else:
                small_talk_intent = self.intent_detector.detect_small_talk(query)
            
            if small_talk_intent:
                logger.info(f"✅ Small talk detected: {small_talk_intent.value}")
                response_time = (time.time() - start_time) * 1000
                
                return {
                    "answer": self.intent_detector.get_small_talk_response(small_talk_intent, language),
                    "confidence": 0.95,
                    "source_documents": [],
                    "language": language,
                    "fallback": False,
                    "intent": f"small_talk_{small_talk_intent.value}",
                    "response_time_ms": response_time,
                    "mode": "small_talk"
                }
            
            # STEP 1: CRITICAL - Domain Filter (BANKING ONLY)
            logger.info(f"🔍 STEP 1: Checking if '{query[:50]}' is banking query...")
            is_banking_result = self._is_banking_query(query)
            logger.info(f"🔍 Banking check result: {is_banking_result}")
            
            if not is_banking_result:
                logger.info(f"⛔ Non-banking query detected: {query[:50]}")
                return self._generate_domain_restricted_response(language)
            
            # STEP 1: CENTRALIZED LOAN DETECTION (BEFORE INTENT)
            # This is the SINGLE authoritative check for loans
            if self._is_loan_query(query):
                logger.info(f"💰 Loan query detected - BYPASSING RAG, using LLM directly")
                
                # Detect intent for logging purposes only
                intent, intent_confidence, _ = self.intent_detector.detect_intent(query)
                
                # ALWAYS use LLM for loans - never depend on dataset
                answer = self._generate_general_knowledge_response(query, language)
                
                # Validate and clean response
                answer = clean_response(answer)
                            
                # CRITICAL VALIDATION FOR LOANS
                fallback_phrases = [
                    "i cannot find", "unable to find", "please rephrase",
                    "contact support", "speak to our team", "don't have information"
                ]
                            
                has_fallback = any(phrase in answer.lower() for phrase in fallback_phrases)
                            
                if not answer or len(answer.strip()) == 0:
                    logger.error("❌ Loan query got empty response - REGENERATING")
                    answer = self._generate_general_knowledge_response(query, language)
                    answer = clean_response(answer)
                elif has_fallback:
                    logger.error("❌ Loan query got fallback text - REGENERATING")
                    answer = self._generate_general_knowledge_response(query, language)
                    answer = clean_response(answer)
                else:
                    # CRITICAL: Validate bullet count (3-4 bullets required)
                    bullet_validation = validate_bullet_count(answer)
                    bullet_count = bullet_validation['bullet_count']
                                
                    if bullet_validation['needs_regeneration']:
                        logger.warning(f"⚠️ Loan query has only {bullet_count} bullets - REGENERATING for complete response")
                        # Regenerate once more to get full 3-4 bullets
                        answer = self._generate_general_knowledge_response(query, language)
                        answer = clean_response(answer)
                        # Re-validate
                        bullet_validation = validate_bullet_count(answer)
                        bullet_count = bullet_validation['bullet_count']
                        logger.info(f"✅ Regenerated loan response: {bullet_count} bullets")
                    else:
                        logger.info(f"✅ Loan query validated: {bullet_count} bullets")
                
                response_time = (time.time() - start_time) * 1000
                
                return {
                    "answer": answer,
                    "confidence": 0.85,
                    "source_documents": [],
                    "language": language,
                    "fallback": False,
                    "intent": intent.value,
                    "response_time_ms": response_time,
                    "mode": "llm_loan_direct"
                }
            
            # STEP 2: Normal flow for NON-loan queries
            # Step 2: Detect intent
            intent, intent_confidence, matched_keywords = self.intent_detector.detect_intent(query)
            logger.info(f"Detected intent: {intent.value} (confidence: {intent_confidence:.2f})")
            
            # Step 2: Check if escalation needed
            if self.intent_detector.needs_escalation(query):
                logger.info("Escalation detected - routing to human support")
                return self._generate_escalation_response(language, intent)
            
            # Step 3: Try tool-based response for specific intents (HIGH PRIORITY)
            tool_response = self._try_tool_response(query, intent, language)
            if tool_response:
                logger.info(f"Tool response generated for intent: {intent.value}")
                response_time = (time.time() - start_time) * 1000
                tool_response['response_time_ms'] = response_time
                tool_response['intent'] = intent.value
                return tool_response
            
            # Step 4: Retrieve context from FAQ (ONLY for non-loan queries)
            # Loans are already handled above and won't reach here
            context_docs, confidence = self.retrieve_context(query)
            
            # Build context from retrieved documents
            context = "\n\n".join([doc.page_content for doc in context_docs]) if context_docs else ""
            
            # CRITICAL FIX: ALWAYS use LLM, even without context
            # If no context found, still generate response using general banking knowledge
            has_context = bool(context_docs) and len(context.strip()) > 0
            
            # CRITICAL ACCOUNT QUERY FIX: Use LLM for account queries when RAG fails
            is_account = self._is_account_query(query)
            
            # For non-loan queries: use RAG if context exists, otherwise LLM
            if has_context:
                logger.info(f"Using FAQ-based RAG mode (confidence: {confidence:.3f})")
                # Use RAG mode with context
                answer = self._generate_rag_response(query, context, language)
            else:
                # 🔥 CRITICAL FIX: Account queries get LLM response instead of fallback
                if is_account:
                    logger.info(f"No FAQ context - using LLM for account query")
                else:
                    logger.info(f"No FAQ context found - using LLM general knowledge mode")
                
                # ALWAYS generate response using LLM (no fallback!)
                answer = self._generate_general_knowledge_response(query, language)
            
            # Validate and clean response
            answer = clean_response(answer)
            
            # CRITICAL CHECK: Ensure we got a real response
            if not answer or not answer.strip():
                logger.error(f"❌ Got EMPTY response from LLM for query: {query[:50]}")
                # Force regenerate
                answer = self._generate_general_knowledge_response(query, language)
                answer = clean_response(answer)
            
            # Check for fallback phrases that indicate LLM failed
            fallback_phrases = [
                "i apologize", "i'm having trouble", "trouble finding",
                "rephrase your question", "cannot find", "unable to find",
                "don't have information", "contact support", "speak to our team"
            ]
            
            answer_lower = answer.lower()
            has_fallback_phrase = any(phrase in answer_lower for phrase in fallback_phrases)
            
            if has_fallback_phrase:
                logger.warning(f"⚠️ Response contains fallback phrases - REGENERATING")
                answer = self._generate_general_knowledge_response(query, language)
                answer = clean_response(answer)
            
            # CRITICAL: Validate bullet count for ALL responses (3-4 bullets required)
            bullet_validation = validate_bullet_count(answer)
            bullet_count = bullet_validation['bullet_count']
            
            if bullet_validation['needs_regeneration']:
                logger.warning(f"⚠️ Response has only {bullet_count} bullets - REGENERATING for complete answer")
                # Regenerate with RAG or general knowledge depending on context availability
                if has_context:
                    answer = self._generate_rag_response(query, context, language)
                else:
                    answer = self._generate_general_knowledge_response(query, language)
                answer = clean_response(answer)
                # Re-validate
                bullet_validation = validate_bullet_count(answer)
                bullet_count = bullet_validation['bullet_count']
                logger.info(f"✅ Regenerated response: {bullet_count} bullets")
            else:
                logger.info(f"✅ Response validated: {bullet_count} bullets")
            
            # Quick validation check
            validation = validate_response(answer)
            if not validation['valid']:
                logger.warning(f"Response validation issues: {validation['issues']}")
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "answer": answer,
                "confidence": confidence,
                "source_documents": context_docs if has_context else [],
                "language": language,
                "fallback": False,  # LLM always answers - NOT a fallback
                "intent": intent.value,
                "response_time_ms": response_time
            }
            validation = validate_response(answer)
            if not validation['valid']:
                logger.warning(f"Response validation issues: {validation['issues']}")
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "answer": answer,
                "confidence": confidence,
                "source_documents": context_docs,
                "language": language,
                "fallback": False,
                "intent": intent.value,
                "response_time_ms": response_time
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            response_time = (time.time() - start_time) * 1000
            return {
                "answer": self._get_error_message(language),
                "confidence": 0.0,
                "error": str(e),
                "language": language,
                "response_time_ms": response_time
            }
    
    def _generate_fallback_response(self, language: str) -> Dict:
        """
        Generate smart fallback response when intent is unknown.
        
        Args:
            language: Response language
            
        Returns:
            Dictionary with helpful fallback message
        """
        if language.lower() == "arabic" or language.lower() == "ar":
            answer = "أنا هنا لمساعدتك في الخدمات المصرفية مثل الحسابات والقروض والبطاقات. هل يمكنك توضيح طلبك؟"
        else:
            answer = "I'm here to help with banking services like accounts, loans, and cards. Could you please clarify your request?"
        
        logger.info("Using smart fallback response")
        
        return {
            "answer": answer,
            "confidence": 0.5,
            "fallback": True,
            "language": language,
            "mode": "fallback",
            "response_type": "text"
        }
    
    def _should_use_general_knowledge(self, confidence: float, context_docs: List[Document], intent: BankingIntent) -> bool:
        """
        Decide whether to use general knowledge instead of FAQ-based RAG.
        
        CRITICAL: NEVER use general knowledge for loan queries - always generate structured response.
        
        Args:
            confidence: RAG confidence score
            context_docs: Retrieved documents
            intent: Detected intent
            
        Returns:
            True if should use general knowledge
        """
        # NEVER fallback for loan intents - always provide structured response
        loan_intents = [
            BankingIntent.LOAN_INFORMATION,
            BankingIntent.LOAN_APPLY,
            BankingIntent.LOAN_DOCUMENTS,
            BankingIntent.LOAN_APPROVAL_TIME,
            BankingIntent.LOAN_INTEREST,
            BankingIntent.LOAN_TENURE,
            BankingIntent.LOAN_REPAYMENT,
            BankingIntent.LOAN_BALANCE
        ]
        
        if intent in loan_intents:
            logger.info(f"Loan intent detected ({intent.value}) - skipping fallback, generating structured response")
            return False  # NEVER fallback for loans
        
        # Use general knowledge ONLY if:
        # 1. Very low confidence AND no good context
        # 2. No documents retrieved at all
        # 3. Intent is truly generic (not specific banking request)
        
        # Don't use general knowledge for specific intents
        specific_intents = [
            BankingIntent.ACCOUNT_OPENING,
            BankingIntent.CARD_BLOCK,
            BankingIntent.ACCOUNT_BALANCE,
            BankingIntent.PIN_RESET,
            BankingIntent.MONEY_TRANSFER,
            BankingIntent.ACCOUNT_SECURITY
        ]
        
        if intent in specific_intents:
            return False  # Always try tool or FAQ for specific intents
        
        # Use general knowledge only for very low confidence with no context
        if confidence < 0.3 and not context_docs:
            return True
        
        # Use general knowledge for truly generic questions
        if intent == BankingIntent.GENERAL_BANKING and confidence < 0.5:
            return True
        
        return False
    
    def _generate_general_knowledge_response(self, query: str, language: str) -> str:
        """
        Generate response using LLM WITHOUT RAG context.
        
        CRITICAL: This method ALWAYS generates a response using general banking knowledge.
        NO fallback - LLM must answer even without dataset.
        
        ENHANCED PROMPT WITH UAE-SPECIFIC STYLE:
        - Professional tone
        - Correct terminology (EN + AR)
        - Consistent formatting
        - EXACTLY 3-4 bullet points required
        """
        template = """You are a professional UAE banking assistant.

MANDATORY RULES - EVERY RESPONSE MUST:
1. Have EXACTLY 3-4 bullet points using "•"
2. Each bullet = ONE complete sentence (10-20 words)
3. NO paragraphs, NO explanations before/after bullets
4. NO bank names - use "our bank" or "the bank"
5. ALWAYS UAE context (AED, Emirates ID)
6. Focus on actionable steps only
7. Professional, clear, helpful tone

CRITICAL FOR ARABIC RESPONSES:
• Use formal Modern Standard Arabic (MSA)
• Write complete sentences with proper grammar
• Include all necessary details (no truncation)
• Use correct UAE banking terminology
• Example: "بطاقة الهوية الإماراتية" NOT "الرقم القومي"

STYLE GUIDELINES:

FOR ENGLISH:
✅ Use: "Emirates ID", "mobile app", "visit a branch", "submit documents"
❌ Avoid: robotic phrases, repetition, incomplete sentences

FOR ARABIC:
✅ Use: بطاقة الهوية الإماراتية، جواز السفر، تطبيق البنك، تحويل الأموال، كشف الحساب
❌ Avoid: الرقم القومي (Egyptian), unnatural translations, incomplete answers

LOAN QUERIES TEMPLATE (Arabic):
• يمكنك التقديم على القرض عبر الموقع الإلكتروني أو تطبيق البنك
• تقديم بطاقة الهوية الإماراتية وإثبات الدخل
• اختيار مبلغ القرض وفترة السداد المناسبة
• تتم الموافقة عادة خلال 1–3 أيام عمل

LOAN QUERIES TEMPLATE (English):
• You can apply for the loan via the bank's website or mobile app
• Submit your Emirates ID and proof of income documents
• Choose the loan amount and repayment period that suits you
• Approval is typically completed within 1-3 business days

ACCOUNT QUERIES TEMPLATE (Arabic):
• يمكنك فتح الحساب عبر التطبيق أو بزيارة أحد الفروع
• تقديم بطاقة الهوية الإماراتية وجواز السفر ساري المفعول
• تعبئة نموذج فتح الحساب وإدخال البيانات المطلوبة
• سيتم تفعيل الحساب بعد التحقق من المستندات

ACCOUNT QUERIES TEMPLATE (English):
• You can open an account via the mobile app or by visiting a branch
• Submit your Emirates ID and valid passport copy
• Complete the account opening form with required details
• The account will be activated after document verification

TRANSFER QUERIES TEMPLATE (Arabic):
• استخدم خدمة التحويل عبر تطبيق البنك أو الموقع الإلكتروني
• أدخل بيانات المستفيد ورقم الحساب الصحيح
• حدد المبلغ بالدرهم وأكّد العملية
• يتم التحويل فوراً أو خلال يوم عمل واحد

TRANSFER QUERIES TEMPLATE (English):
• Use the transfer service via the bank's app or website
• Enter the beneficiary details and correct account number
• Specify the amount in AED and confirm the transaction
• Transfer is completed instantly or within one business day

FORMAT REQUIREMENTS:
• Action step (how/where to start the process)
• Required information/documents needed
• Additional detail or option available
• Final outcome or next step timeline

Question: {question}

Answer in {language} (EXACTLY 3-4 complete bullets, professional UAE banking tone):"""
        
        # Build system prompt
        system_prompt = template.format(language=language, question="")
        
        # Generate response using Groq
        result = self.llm.generate_with_context(
            system_prompt=system_prompt,
            user_query=query,
            language=language
        )
        
        answer = result.strip() if result else ""
        
        # Apply intent-based formatting
        answer = format_response_by_intent(self.intent_detector.detect_intent(query)[0], answer, language)
        
        return answer
    
    def _generate_rag_response(self, query: str, context: str, language: str) -> str:
        """
        Generate response using LLM with RAG context.
        
        ENHANCED PROMPT WITH UAE-SPECIFIC STYLE:
        - Professional tone
        - Correct terminology (EN + AR)
        - Consistent formatting
        - EXACTLY 3-4 bullet points required
        """
        template = """You are a professional UAE banking assistant.

MANDATORY RULES - EVERY RESPONSE MUST:
1. Have EXACTLY 3-4 bullet points using "•"
2. Each bullet = ONE complete sentence (10-20 words)
3. NO paragraphs, NO explanations before/after bullets
4. NO bank names - use "our bank" or "the bank"
5. ALWAYS UAE context (AED, Emirates ID)
6. Focus on actionable steps only
7. Professional, clear, helpful tone

CRITICAL FOR ARABIC RESPONSES:
• Use formal Modern Standard Arabic (MSA)
• Write complete sentences with proper grammar
• Include all necessary details (no truncation)
• Use correct UAE banking terminology
• Example: "بطاقة الهوية الإماراتية" NOT "الرقم القومي"

STYLE GUIDELINES:

FOR ENGLISH:
✅ Use: "Emirates ID", "mobile app", "visit a branch", "submit documents"
❌ Avoid: robotic phrases, repetition, incomplete sentences

FOR ARABIC:
✅ Use: بطاقة الهوية الإماراتية، جواز السفر، تطبيق البنك، تحويل الأموال، كشف الحساب
❌ Avoid: الرقم القومي (Egyptian), unnatural translations, incomplete answers

Context from FAQ:
{context}

Question: {question}

Answer in {language} (EXACTLY 3-4 complete bullets, professional UAE banking tone):"""
        
        # Build system prompt with context
        system_prompt = template.format(language=language, context=context, question="")
        
        # Generate response using Groq
        result = self.llm.generate_with_context(
            system_prompt=system_prompt,
            user_query=query,
            context=context,
            language=language
        )
        
        answer = result.strip() if result else ""
        
        # Apply intent-based formatting
        answer = format_response_by_intent(self.intent_detector.detect_intent(query)[0], answer, language)
        
        return answer
    
    def _is_hallucination_detected(self, answer: str, context: str) -> bool:
        """
        Detect potential hallucinations in generated answer.
        
        Args:
            answer: Generated answer
            context: Source context
            
        Returns:
            True if hallucination detected
        """
        # Simple heuristic checks
        hallucination_indicators = [
            "i think",
            "probably",
            "might be",
            "not sure",
            "guess",
            "perhaps"
        ]
        
        answer_lower = answer.lower()
        
        # Check if answer contains uncertainty phrases
        for indicator in hallucination_indicators:
            if indicator in answer_lower:
                return True
        
        # Check if answer is much longer than context (potential fabrication)
        if len(answer) > len(context) * 3:
            return True
        
        return False
    
    def _try_tool_response(self, query: str, intent: BankingIntent, language: str) -> Optional[Dict]:
        """
        Try to generate response using banking tools.
        
        NOTE: Loan queries now use LLM generation instead of tool responses
        to maintain consistent bullet-point format across all intents.
        
        Args:
            query: User query
            intent: Detected intent
            language: Response language
            
        Returns:
            Tool response dictionary or None
        """
        try:
            # Skip loan generator - let LLM handle all responses for consistency
            # This ensures unified 3-4 bullet format across ALL intents
            
            # Only use tools for non-loan intents that need executable actions
            if intent in [BankingIntent.CARD_BLOCK, BankingIntent.CARD_LOST]:
                # These still need tool responses for emergency actions
                pass
            else:
                # Let LLM generate all other responses including loans
                return None
            
            tool_result = None
            
            # Map intents to tools
            intent_to_tool = {
                BankingIntent.CARD_BLOCK: lambda: self.banking_tools.block_card(),
                BankingIntent.ACCOUNT_BALANCE: lambda: self.banking_tools.check_balance(),  # Changed from BALANCE_CHECK
                BankingIntent.LOAN_INFORMATION: lambda: self.banking_tools.loan_information(),
                BankingIntent.LOAN_REPAYMENT: lambda: self.banking_tools.early_repayment_info(),  # NEW
                BankingIntent.LOAN_BALANCE: lambda: self.banking_tools.check_balance_guide(),  # NEW
                BankingIntent.ACCOUNT_OPENING: lambda: self.banking_tools.open_account_steps(),
                BankingIntent.PIN_RESET: lambda: self.banking_tools.reset_pin_guide(),
                BankingIntent.MONEY_TRANSFER: lambda: self.banking_tools.transfer_money_guide(),
                BankingIntent.ACCOUNT_SECURITY: lambda: self.banking_tools.secure_account_guide()  # NEW
            }
            
            if intent in intent_to_tool:
                tool_result = intent_to_tool[intent]()
                
                if tool_result and tool_result.get('success'):
                    # Format tool result as natural language response with structured data
                    action = tool_result.get('action', 'unknown')
                    
                    # Create concise user-friendly message
                    if action == 'loan_information':
                        loan_type = tool_result.get('loan_type', 'personal')
                        details = tool_result.get('details', {})
                        answer = f"Here are the {loan_type} loan details:\n\n"
                        answer += f"Interest Rate: {details.get('interest_rate', 'N/A')}\n"
                        answer += f"Max Amount: {details.get('max_amount', 'N/A')}\n"
                        answer += f"Tenure: {details.get('tenure', 'N/A')}\n"
                        if details.get('requirements'):
                            answer += "\nRequirements:\n"
                            for req in details['requirements']:
                                answer += f"• {req}\n"
                        
                        # Normalize to strict format
                        answer = normalize_response(answer, language)
                        
                        return {
                            "answer": answer,
                            "confidence": 0.85,
                            "source_documents": [],
                            "language": language,
                            "fallback": False,
                            "mode": "tool",
                            "response_type": "loan",
                            "data": {
                                "loan_type": loan_type,
                                "interest_rate": details.get('interest_rate'),
                                "max_amount": details.get('max_amount'),
                                "tenure": details.get('tenure'),
                                "requirements": details.get('requirements', []),
                                "processing_fee": details.get('processing_fee'),
                                "next_steps": tool_result.get('next_steps', [])
                            },
                            "tool_used": action
                        }
                    
                    elif action == 'block_card':
                        answer = "Your card can be blocked immediately:\n\n"
                        answer += "Call 24/7 hotline: 800-BANK\n\n"
                        answer += "Or use mobile app:\n"
                        instructions = tool_result.get('instructions', [])
                        for instr in instructions[1:6]:  # Skip first line, take next 5
                            answer += f"{instr}\n"
                        
                        # Normalize to strict format
                        answer = normalize_response(answer, language)
                        
                        return {
                            "answer": answer,
                            "confidence": 0.9,
                            "source_documents": [],
                            "language": language,
                            "fallback": False,
                            "mode": "tool",
                            "response_type": "card",
                            "data": {
                                "action": "block_card",
                                "emergency_contact": tool_result.get('emergency_contact'),
                                "replacement_time": tool_result.get('replacement_time'),
                                "instructions": instructions
                            },
                            "tool_used": action
                        }
                    
                    elif action == 'check_balance':
                        methods = tool_result.get('methods', [])
                        answer = "You can check your balance through:\n\n"
                        for i, method in enumerate(methods[:3], 1):
                            answer += f"{i}. {method.get('method')}\n"
                        
                        # Normalize to strict format
                        answer = normalize_response(answer, language)
                        
                        return {
                            "answer": answer,
                            "confidence": 0.85,
                            "source_documents": [],
                            "language": language,
                            "fallback": False,
                            "mode": "tool",
                            "response_type": "balance",
                            "data": {
                                "methods": methods
                            },
                            "tool_used": action
                        }
                    
                    elif action == 'early_repayment':  # NEW - Short answer for loan repayment
                        answer = "Yes, early repayment is allowed:\n\n"
                        answer += "• Partial or full settlement available\n"
                        answer += "• Early settlement fee may apply\n"
                        answer += "• Contact bank for exact charges\n"
                        
                        # Normalize to strict format
                        answer = normalize_response(answer, language)
                        
                        return {
                            "answer": answer,
                            "confidence": 0.85,
                            "source_documents": [],
                            "language": language,
                            "fallback": False,
                            "mode": "tool",
                            "response_type": "text",  # Simple text response
                            "data": None,
                            "tool_used": action
                        }
                    
                    elif action == 'check_balance_guide':  # NEW - Guide for checking loan balance
                        answer = "You can check your loan balance:\n\n"
                        answer += "• Mobile banking app\n"
                        answer += "• Internet banking\n"
                        answer += "• Visit branch or ATM\n"
                        answer += "• Call customer support\n"
                        
                        # Normalize to strict format
                        answer = normalize_response(answer, language)
                        
                        return {
                            "answer": answer,
                            "confidence": 0.85,
                            "source_documents": [],
                            "language": language,
                            "fallback": False,
                            "mode": "tool",
                            "response_type": "text",  # Simple text response
                            "data": None,
                            "tool_used": action
                        }
                    
                    elif action == 'open_account':
                        account_type = tool_result.get('account_type', 'savings')
                        methods = tool_result.get('methods', [])
                        answer = f"To open a {account_type} account in UAE:\n\n"
                        if methods:
                            online_method = methods[0]
                            steps = online_method.get('steps', [])[:5]  # First 5 steps
                            for step in steps:
                                answer += f"• {step}\n"
                        
                        answer += "\nRequired Documents:\n"
                        for doc in tool_result.get('required_documents', [])[:3]:
                            answer += f"• {doc}\n"
                        
                        # Normalize to strict format
                        answer = normalize_response(answer, language)
                        
                        return {
                            "answer": answer,
                            "confidence": 0.85,
                            "source_documents": [],
                            "language": language,
                            "fallback": False,
                            "mode": "tool",
                            "response_type": "account",
                            "data": {
                                "account_type": account_type,
                                "methods": methods,
                                "required_documents": tool_result.get('required_documents', []),
                                "minimum_balance": tool_result.get('minimum_balance', {}),
                                "time_required": methods[0].get('time_required') if methods else None
                            },
                            "tool_used": action
                        }
                    
                    elif action == 'secure_account':  # NEW
                        guidelines = tool_result.get('guidelines', [])
                        answer = "To secure your bank account:\n\n"
                        for guideline in guidelines[:3]:  # Top 3 categories
                            answer += f"{guideline.get('title')}:\n"
                            for point in guideline.get('points', [])[:2]:  # 2 points each
                                answer += f"• {point}\n"
                            answer += "\n"
                        
                        # Normalize to strict format
                        answer = normalize_response(answer, language)
                        
                        return {
                            "answer": answer,
                            "confidence": 0.85,
                            "source_documents": [],
                            "language": language,
                            "fallback": False,
                            "mode": "tool",
                            "response_type": "security",
                            "data": {
                                "title": tool_result.get('title'),
                                "guidelines": guidelines,
                                "emergency_contact": tool_result.get('emergency_contact')
                            },
                            "tool_used": action
                        }
                    
                    # Default for other tools
                    instructions = tool_result.get('instructions', [])
                    if not instructions:
                        methods = tool_result.get('methods', [])
                        if methods:
                            instructions = []
                            for method in methods:
                                instructions.append(f"**{method.get('method', 'Method')}**:")
                                instructions.extend(method.get('steps', []))
                    
                    answer = "\n".join([f"• {step}" if not step.startswith("**") else step for step in instructions[:8]]) if instructions else str(tool_result)
                    
                    return {
                        "answer": answer,
                        "confidence": 0.85,
                        "source_documents": [],
                        "language": language,
                        "fallback": False,
                        "mode": "tool",
                        "response_type": "text",
                        "data": tool_result,
                        "tool_used": action
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in tool response: {e}")
            return None
    
    def _generate_escalation_response(self, language: str, intent: BankingIntent) -> Dict:
        """
        Generate escalation response for complex queries.
        
        Args:
            language: Response language
            intent: Detected intent
            
        Returns:
            Dictionary with escalation message
        """
        if language.lower() == "arabic" or language.lower() == "ar":
            answer = "أفهم أن هذا الأمر مهم. دعني أحولك إلى أحد ممثلي خدمة العملاء للمساعدة الشخصية. يرجى الاتصال بـ 800-BANK."
        else:
            answer = "I understand this is important. Let me connect you to a customer support representative for personalized assistance. Please call 800-BANK."
        
        return {
            "answer": answer,
            "confidence": 1.0,
            "fallback": False,
            "language": language,
            "mode": "escalation",
            "intent": intent.value,
            "escalation_recommended": True,
            "contact_number": "800-BANK"
        }
    
    def _get_error_message(self, language: str) -> str:
        """
        Get error message in specified language.
        
        Args:
            language: Response language
            
        Returns:
            Error message string
        """
        if language.lower() == "arabic" or language.lower() == "ar":
            return "عذراً، حدث خطأ. يرجى المحاولة مرة أخرى."
        else:
            return "Sorry, an error occurred. Please try again."
    
    def save_index(self, index_name: str = "faiss_index") -> bool:
        """Save the vector index."""
        return self.vector_store_manager.save_index(index_name)
    
    def load_index(self, index_name: str = "faiss_index") -> bool:
        """Load the vector index."""
        return self.vector_store_manager.load_index(index_name)
