"""
Enhanced Banking Tools - Comprehensive banking operations

This module provides advanced banking tools including:
- Account services
- Card management
- Loan processing
- Transfer operations
- Fraud reporting
- Customer support
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class EnhancedBankingTools:
    """
    Advanced collection of banking tools for production use.
    
    Provides 15+ banking tools with detailed instructions.
    """
    
    def __init__(self):
        """Initialize enhanced banking tools."""
        logger.info("Enhanced banking tools initialized")
        
        # Tool metadata with descriptions
        self.tools_metadata = {
            "block_card": {
                "name": "Block Card",
                "description": "Immediately block a lost or stolen card",
                "category": "card_services",
                "urgency": "high"
            },
            "check_balance": {
                "name": "Check Balance",
                "description": "Check account balance information",
                "category": "account_services",
                "urgency": "normal"
            },
            "loan_information": {
                "name": "Loan Information",
                "description": "Get details about loan products and eligibility",
                "category": "loans",
                "urgency": "normal"
            },
            "open_account_steps": {
                "name": "Open Account",
                "description": "Get step-by-step account opening instructions",
                "category": "account_services",
                "urgency": "normal"
            },
            "reset_pin_guide": {
                "name": "Reset PIN",
                "description": "Guide user through PIN reset process",
                "category": "card_services",
                "urgency": "normal"
            },
            "transfer_money_guide": {
                "name": "Transfer Money",
                "description": "Provide money transfer instructions",
                "category": "transfers",
                "urgency": "normal"
            },
            "report_fraud": {
                "name": "Report Fraud",
                "description": "Report suspicious activity or fraud",
                "category": "security",
                "urgency": "critical"
            },
            "find_atm": {
                "name": "Find ATM",
                "description": "Locate nearest ATMs",
                "category": "atm_services",
                "urgency": "normal"
            },
            "branch_locator": {
                "name": "Find Branch",
                "description": "Locate nearest bank branches",
                "category": "branch_services",
                "urgency": "normal"
            },
            "credit_card_info": {
                "name": "Credit Card Info",
                "description": "Get credit card product information",
                "category": "cards",
                "urgency": "normal"
            },
            "fees_and_charges": {
                "name": "Fees & Charges",
                "description": "Get information about banking fees",
                "category": "general_info",
                "urgency": "normal"
            },
            "kyc_update": {
                "name": "KYC Update",
                "description": "Update KYC documents and information",
                "category": "account_services",
                "urgency": "normal"
            },
            "checkbook_request": {
                "name": "Request Checkbook",
                "description": "Request new checkbook issuance",
                "category": "account_services",
                "urgency": "normal"
            },
            "card_replacement": {
                "name": "Card Replacement",
                "description": "Request replacement for damaged/expired card",
                "category": "card_services",
                "urgency": "normal"
            },
            "account_closure": {
                "name": "Close Account",
                "description": "Get account closure procedure",
                "category": "account_services",
                "urgency": "normal"
            }
        }
    
    def block_card(self, card_type: str = "debit", reason: str = "lost") -> Dict:
        """Block lost or stolen card immediately."""
        logger.info(f"Blocking {card_type} card due to {reason}")
        
        return {
            "success": True,
            "action": "block_card",
            "priority": "high",
            "instructions": [
                f"🚨 Call our 24/7 emergency hotline immediately at 800-BANK (800-2265)",
                f"Alternatively, use the mobile app for instant blocking:",
                "  1. Login to your mobile banking app",
                "  2. Navigate to 'Cards' section",
                "  3. Select 'Card Management' or 'Card Services'",
                "  4. Choose 'Block/Freeze Card'",
                f"  5. Select your {card_type} card ending in XXXX",
                f"  6. Choose reason: {reason}",
                "  7. Confirm the action with OTP verification",
                "",
                "✅ Your card will be blocked IMMEDIATELY",
                "📬 A replacement card will be dispatched within 3-5 business days",
                "💳 Temporary virtual card available in app for urgent transactions"
            ],
            "emergency_contact": "800-BANK (800-2265)",
            "alternative_contact": "+971-4-XXX-XXXX (International)",
            "replacement_time": "3-5 business days",
            "temporary_card_available": True,
            "next_steps": [
                "Monitor your account for unauthorized transactions",
                "Update automatic payments with new card details once received",
                "Destroy old card if found (cut across chip and magnetic strip)"
            ]
        }
    
    def check_balance(self, account_type: str = "savings") -> Dict:
        """Provide multiple methods to check account balance."""
        logger.info(f"Checking balance for {account_type} account")
        
        return {
            "success": True,
            "action": "check_balance",
            "methods": [
                {
                    "method": "📱 Mobile App (Fastest)",
                    "steps": [
                        "Open mobile banking app",
                        "Login with credentials or biometric authentication",
                        "View dashboard - balances displayed prominently",
                        "Tap on specific account for detailed view",
                        "Available balance and ledger balance shown separately"
                    ],
                    "availability": "24/7",
                    "authentication": "Required"
                },
                {
                    "method": "💻 Internet Banking",
                    "steps": [
                        "Visit www.bankname.com",
                        "Click 'Login' and enter credentials",
                        "Navigate to 'Accounts' tab",
                        "Select your account type",
                        "View current balance and available balance"
                    ],
                    "availability": "24/7",
                    "authentication": "Required"
                },
                {
                    "method": "🏧 ATM",
                    "steps": [
                        "Visit any of our ATMs nationwide",
                        "Insert your debit card",
                        "Enter your 4-digit PIN",
                        "Select 'Balance Inquiry' from menu",
                        "Collect printed slip (optional)"
                    ],
                    "availability": "24/7",
                    "authentication": "Card + PIN",
                    "fee": "Free at our ATMs"
                },
                {
                    "method": "📞 Phone Banking",
                    "steps": [
                        "Call 800-BANK (800-2265)",
                        "Select language (English/Arabic)",
                        "Choose 'Account Information'",
                        "Verify identity with security questions",
                        "Listen to automated balance announcement"
                    ],
                    "availability": "24/7",
                    "authentication": "Phone banking PIN"
                },
                {
                    "method": "📍 Branch Visit",
                    "steps": [
                        "Visit nearest branch with Emirates ID",
                        "Take token for 'Account Services'",
                        "Meet with customer service representative",
                        "Request account balance statement"
                    ],
                    "availability": "Sun-Thu: 8AM-6PM",
                    "authentication": "Emirates ID required"
                }
            ],
            "balance_types": {
                "available_balance": "Amount you can withdraw immediately",
                "ledger_balance": "Total balance including pending transactions",
                "available_credit": "For credit cards - remaining credit limit"
            }
        }
    
    def loan_information(self, loan_type: str = "personal") -> Dict:
        """Provide comprehensive loan product information."""
        logger.info(f"Providing information for {loan_type} loan")
        
        loan_products = {
            "personal": {
                "name": "Personal Loan",
                "arabic_name": "قرض شخصي",
                "interest_rate": "Starting from 5.99% per annum (reducing rate)",
                "max_amount": "Up to 200,000 AED or 20x monthly salary",
                "tenure": "Flexible tenure up to 5 years (60 months)",
                "processing_fee": "1,500 AED (one-time)",
                "eligibility": {
                    "minimum_salary": "5,000 AED per month",
                    "age": "21-65 years",
                    "employment": "Salaried or Self-employed",
                    "nationality": "UAE Nationals and Expats"
                },
                "required_documents": [
                    "✓ Valid Emirates ID (original + copy)",
                    "✓ Passport with valid UAE visa (original + copy)",
                    "✓ Salary certificate (no objection certificate)",
                    "✓ Bank statements for last 3-6 months",
                    "✓ Trade license (for self-employed)"
                ],
                "features": [
                    "Quick approval within 24-48 hours",
                    "Flexible repayment options",
                    "Option to add reducing balance insurance",
                    "No early settlement penalty",
                    "Direct salary transfer required"
                ]
            },
            "auto": {
                "name": "Auto Loan / Car Finance",
                "arabic_name": "قرض سيارة",
                "interest_rate": "Starting from 3.99% per annum",
                "max_amount": "Up to 80% of car value (90% for UAE nationals)",
                "tenure": "Up to 7 years (84 months)",
                "processing_fee": "999 AED",
                "eligibility": {
                    "minimum_salary": "5,000 AED per month",
                    "age": "21-65 years",
                    "license": "Valid UAE driving license required"
                },
                "required_documents": [
                    "✓ Emirates ID and Passport copies",
                    "✓ Salary certificate",
                    "✓ Valid UAE driving license",
                    "✓ Car registration (if refinancing)",
                    "✓ Insurance policy quotation",
                    "✓ Invoice from dealer (for new cars)"
                ],
                "features": [
                    "Competitive profit rates",
                    "Coverage for new and used cars",
                    "Optional Takaful coverage",
                    "Quick disbursement to dealer"
                ]
            },
            "home": {
                "name": "Home Loan / Mortgage",
                "arabic_name": "قرض عقاري",
                "interest_rate": "Starting from 4.49% per annum",
                "max_amount": "Up to 85% of property value for expats, 90% for nationals",
                "tenure": "Up to 25 years (300 months)",
                "processing_fee": "5,000 AED or 1% of loan amount (whichever is higher)",
                "eligibility": {
                    "minimum_salary": "15,000 AED per month",
                    "age": "21-70 years at loan maturity",
                    "employment": "Minimum 2 years employment history"
                },
                "required_documents": [
                    "✓ Emirates ID, Passport, Visa copies",
                    "✓ Salary certificate (minimum 6 months)",
                    "✓ Bank statements (last 6 months)",
                    "✓ Property documents and NOC from developer",
                    "✓ Sale and Purchase Agreement",
                    "✓ Insurance policy"
                ],
                "features": [
                    "Fixed and variable rate options",
                    "Sharia-compliant Murabaha option available",
                    "Free property valuation",
                    "Flexible repayment structures"
                ]
            }
        }
        
        selected_loan = loan_products.get(loan_type.lower(), loan_products["personal"])
        
        return {
            "success": True,
            "action": "loan_information",
            "loan_type": loan_type,
            "product_details": selected_loan,
            "next_steps": [
                "🌐 Visit our website to use EMI calculator",
                "📱 Apply online through mobile app in 5 minutes",
                "📞 Call 800-BANK for pre-approval",
                "🏦 Visit nearest branch for detailed consultation"
            ],
            "special_offers": [
                "⚡ Fast-track approval for salary transfer customers",
                "🎉 Zero processing fee for premium customers",
                "💰 Discount on interest rate for existing customers"
            ]
        }
    
    def open_account_steps(self, account_type: str = "savings") -> Dict:
        """Provide detailed account opening instructions."""
        logger.info(f"Opening {account_type} account")
        
        account_types = {
            "savings": {
                "name": "Savings Account",
                "min_balance": "1,000 AED",
                "min_age": "18 years (13 years with guardian)",
                "features": ["Up to 4% annual profit", "Free debit card", "Mobile banking"]
            },
            "current": {
                "name": "Current Account",
                "min_balance": "5,000 AED",
                "min_age": "18 years",
                "features": ["Unlimited transactions", "Free cheque book", "Business banking"]
            },
            "salary": {
                "name": "Salary Transfer Account",
                "min_balance": "3,000 AED",
                "min_age": "21 years",
                "features": ["Higher profit rates", "Free life insurance", "Loan benefits"]
            }
        }
        
        account_info = account_types.get(account_type.lower(), account_types["savings"])
        
        return {
            "success": True,
            "action": "open_account",
            "account_type": account_type,
            "account_details": account_info,
            "methods": [
                {
                    "method": "📲 Online Account Opening (Recommended)",
                    "steps": [
                        "1. Download our mobile app or visit website",
                        "2. Click 'Open Account' button",
                        f"3. Select '{account_info['name']}'",
                        "4. Fill in personal details:",
                        "   - Full name (as per passport)",
                        "   - Date of birth",
                        "   - Nationality",
                        "   - Contact information",
                        "   - Residential address",
                        "5. Upload required documents:",
                        "   ✓ Emirates ID (front & back)",
                        "   ✓ Passport copy with valid visa page",
                        "   ✓ Recent photograph",
                        "   ✓ Salary certificate (for salary accounts)",
                        "6. Complete video KYC call (5-10 minutes)",
                        "7. Receive account number instantly via SMS",
                        "8. Make initial deposit via transfer or cash deposit"
                    ],
                    "time_required": "15-20 minutes (instant approval)",
                    "documents_needed": 4
                },
                {
                    "method": "🏦 Branch Visit",
                    "steps": [
                        "1. Locate nearest branch using branch locator",
                        "2. Collect account opening form",
                        "3. Fill in all required details",
                        "4. Submit form with original documents:",
                        "   ✓ Original Emirates ID",
                        "   ✓ Original Passport with visa",
                        "   ✓ Salary certificate (if applicable)",
                        "5. Meet with relationship manager",
                        "6. Make initial cash deposit",
                        "7. Receive welcome kit containing:",
                        "   - Debit card (mailed separately)",
                        "   - Cheque book (for current accounts)",
                        "   - Internet banking credentials"
                    ],
                    "time_required": "30-45 minutes",
                    "documents_needed": 3
                }
            ],
            "required_documents": [
                "📄 Emirates ID (original + photocopy)",
                "📄 Passport with valid UAE visa (original + photocopy)",
                "📄 Salary certificate (for salary transfer accounts)",
                "📄 Trade license (for business accounts)",
                "📄 Recent utility bill (for address proof)"
            ],
            "initial_deposit": {
                "savings": "1,000 AED",
                "current": "5,000 AED",
                "salary": "3,000 AED"
            },
            "benefits": [
                "✅ Free international debit card",
                "✅ 24/7 mobile and internet banking",
                "✅ Access to 1000+ ATMs nationwide",
                "✅ Competitive profit rates",
                "✅ Free life insurance (with salary transfer)"
            ]
        }
    
    def reset_pin_guide(self, card_type: str = "debit") -> Dict:
        """Provide PIN reset instructions through multiple channels."""
        logger.info(f"Resetting PIN for {card_type} card")
        
        return {
            "success": True,
            "action": "reset_pin",
            "card_type": card_type,
            "methods": [
                {
                    "method": "📱 Mobile App (Instant)",
                    "steps": [
                        "Login to mobile banking app",
                        "Go to 'Services' > 'Card Services'",
                        "Select 'PIN Management'",
                        f"Choose your {card_type} card",
                        "Click 'Generate PIN' or 'Reset PIN'",
                        "Verify with OTP sent to registered mobile",
                        "Set new 4-digit PIN (avoid obvious numbers)",
                        "Confirm PIN by re-entering"
                    ],
                    "time": "Instant",
                    "availability": "24/7"
                },
                {
                    "method": "🏧 ATM Machine",
                    "steps": [
                        "Visit any of our ATMs",
                        "Insert your card",
                        "If you know old PIN: Enter it",
                        "If forgotten: Press 'Forgot PIN'",
                        "Select 'PIN Services' > 'Generate PIN'",
                        "Verify with registered mobile number",
                        "Receive OTP via SMS",
                        "Enter OTP at ATM",
                        "Set new PIN or receive sealed PIN mailer"
                    ],
                    "time": "Immediate",
                    "availability": "24/7"
                },
                {
                    "method": "📞 Customer Care",
                    "steps": [
                        "Call 800-BANK (800-2265)",
                        "Select preferred language",
                        "Choose 'Card Services'",
                        "Verify identity with security questions",
                        "Request PIN reset",
                        "Receive temporary PIN via SMS",
                        "Change PIN at next ATM usage"
                    ],
                    "time": "5-10 minutes",
                    "availability": "24/7"
                },
                {
                    "method": "🏦 Branch Visit",
                    "steps": [
                        "Visit nearest branch with Emirates ID",
                        "Fill PIN reset request form",
                        "Submit form at counter",
                        "Receive instant PIN mailer",
                        "Activate PIN at any ATM"
                    ],
                    "time": "15-20 minutes",
                    "availability": "Branch timings"
                }
            ],
            "important_notes": [
                "⚠️ Never share your PIN with anyone including bank staff",
                "⚠️ Avoid using birth year, phone number, or sequential numbers",
                "⚠️ Change PIN every 3-6 months for security",
                "⚠️ If card swallowed by ATM, call 800-BANK immediately"
            ],
            "security_tips": [
                "Use combination of numbers that are easy for you to remember",
                "Don't write PIN on card or keep it in wallet",
                "Cover keypad when entering PIN at ATMs"
            ]
        }
    
    def transfer_money_guide(self, transfer_type: str = "local", amount: float = 0) -> Dict:
        """Comprehensive money transfer guide."""
        logger.info(f"Transfer guide: {transfer_type}, Amount: {amount}")
        
        transfer_limits = {
            "local": {
                "min": "1 AED",
                "max": "50,000 AED per day (100,000 for premium)",
                "fee": "Free for amounts < 10,000 AED; 10 AED above",
                "processing_time": "Instant to 2 hours"
            },
            "international": {
                "min": "100 AED",
                "max": "50,000 AED per day (higher with approval)",
                "fee": "From 25 AED + correspondent bank charges",
                "processing_time": "1-3 business days"
            },
            "swift": {
                "min": "1,000 AED",
                "max": "No upper limit (subject to compliance)",
                "fee": "From 50 AED + correspondent charges",
                "processing_time": "2-5 business days"
            }
        }
        
        limits = transfer_limits.get(transfer_type.lower(), transfer_limits["local"])
        
        return {
            "success": True,
            "action": "transfer_money",
            "transfer_type": transfer_type,
            "amount": amount,
            "limits": limits,
            "methods": [
                {
                    "method": "📱 Mobile App Transfer",
                    "steps": [
                        "Login to mobile banking app",
                        "Tap 'Transfers' on home screen",
                        f"Select '{transfer_type.title()} Transfer'",
                        "Add beneficiary (first time only):",
                        "  - Beneficiary name",
                        "  - Account number / IBAN",
                        "  - Bank code / SWIFT code",
                        "  - Account type",
                        "Verify beneficiary with OTP (takes 30 mins to activate)",
                        "Enter transfer amount",
                        "Review all details carefully",
                        "Authenticate with biometric/OTP",
                        "Receive confirmation SMS and reference number"
                    ],
                    "processing_time": limits["processing_time"],
                    "fee": limits["fee"]
                },
                {
                    "method": "💻 Internet Banking",
                    "steps": [
                        "Login to internet banking portal",
                        "Navigate to 'Payments & Transfers'",
                        "Choose transfer type",
                        "Add/manage beneficiaries",
                        "Initiate transfer",
                        "Authenticate with secure token/OTP",
                        "Save/print confirmation"
                    ],
                    "processing_time": limits["processing_time"],
                    "fee": limits["fee"]
                },
                {
                    "method": "🏦 Branch Transfer",
                    "steps": [
                        "Visit nearest branch",
                        "Fill wire transfer form",
                        "Provide beneficiary details",
                        "Submit with Emirates ID",
                        "Make payment at counter",
                        "Receive transaction receipt"
                    ],
                    "note": "Required for large transfers (>50,000 AED) or first-time international transfers",
                    "fee": "May have additional charges"
                }
            ],
            "required_details": {
                "local": [
                    "Beneficiary full name",
                    "Account number (IBAN preferred)",
                    "Bank name and branch",
                    "Account type (Savings/Current)"
                ],
                "international": [
                    "Beneficiary full name and address",
                    "Complete account number or IBAN",
                    "SWIFT/BIC code of beneficiary bank",
                    "Bank name and complete address",
                    "Purpose of remittance",
                    "Beneficiary's contact details"
                ]
            },
            "compliance_notes": [
                "⚠️ First-time beneficiaries require 30-minute cooling period",
                "⚠️ Large transfers may require additional documentation",
                "⚠️ All transfers subject to UAE Central Bank regulations",
                "⚠️ Purpose of transfer must be legitimate (not for prohibited activities)"
            ],
            "exchange_rates": "Real-time exchange rates applied for international transfers. Check app for current rates."
        }
    
    def report_fraud(self, fraud_type: str = "unauthorized_transaction") -> Dict:
        """Fraud reporting and immediate actions."""
        logger.warning(f"Fraud reported: {fraud_type}")
        
        return {
            "success": True,
            "action": "report_fraud",
            "priority": "CRITICAL",
            "immediate_actions": [
                "🚨 CALL 800-BANK IMMEDIATELY (24/7 fraud hotline)",
                "🚨 Block all cards linked to your account",
                "🚨 Change online banking passwords",
                "🚨 Enable transaction alerts if not already active"
            ],
            "reporting_steps": [
                "1. Call fraud department: 800-BANK ext. 2",
                "2. Provide details:",
                "   - Transaction date and time",
                "   - Transaction amount",
                "   - Merchant name (if known)",
                "   - How you discovered the fraud",
                "3. File police report (for amounts > 1000 AED)",
                "4. Submit fraud affidavit form",
                "5. Cooperate with investigation team",
                "6. Receive provisional credit within 10 days (if eligible)"
            ],
            "fraud_types_covered": [
                "Unauthorized card transactions",
                "Phishing scams",
                "Identity theft",
                "ATM skimming",
                "Online banking fraud",
                "Cheque fraud"
            ],
            "protection_measures": [
                "✅ Enable SMS/email alerts for all transactions",
                "✅ Use strong, unique passwords",
                "✅ Never share OTP or CVV with anyone",
                "✅ Regularly monitor account statements",
                "✅ Use secure networks for banking",
                "✅ Install antivirus on devices"
            ],
            "contact_info": {
                "fraud_hotline": "800-BANK (800-2265)",
                "email": "fraud@bankname.com",
                "hours": "24/7"
            },
            "investigation_timeline": "7-10 business days for preliminary investigation"
        }
    
    def find_atm(self, location: str = "Dubai") -> Dict:
        """Locate nearest ATMs."""
        return {
            "success": True,
            "action": "find_atm",
            "message": f"Finding ATMs near {location}...",
            "atm_features": [
                "✓ Cash withdrawal and deposit",
                "✓ Balance inquiry",
                "✓ PIN change",
                "✓ Mini statement",
                "✓ Bill payments",
                "✓ Mobile top-up"
            ],
            "limits": {
                "daily_withdrawal": "5,000 AED",
                "per_transaction": "2,500 AED",
                "foreign_cards": "Varies by issuing bank"
            },
            "how_to_find": [
                "📱 Use mobile app: Services > ATM Locator",
                "🌐 Visit website: Branch & ATM finder",
                "🗺️ Google Maps: Search '[Bank Name] ATM near me'",
                "📞 Call 800-BANK for nearest location"
            ]
        }
    
    def branch_locator(self, location: str = "Dubai") -> Dict:
        """Find nearest bank branches."""
        return {
            "success": True,
            "action": "branch_locator",
            "services_available": [
                "Account opening",
                "Loan applications",
                "Currency exchange",
                "Safe deposit boxes",
                "Notary services",
                "Attestation services"
            ],
            "branch_timings": {
                "sunday_thursday": "8:00 AM - 6:00 PM",
                "friday_saturday": "Closed (Some branches open Saturday 9 AM - 1 PM)",
                "ramadan": "Reduced hours (9 AM - 2 PM)"
            },
            "how_to_find": [
                "📱 Mobile app: Branch locator with map",
                "🌐 Website: Find a branch tool",
                "📞 Call 800-BANK for directions",
                "🗺️ Use Google Maps or Waze"
            ],
            "appointment_booking": "Book appointment online to avoid waiting"
        }
    
    def credit_card_info(self, card_category: str = "classic") -> Dict:
        """Credit card product information."""
        cards = {
            "classic": {
                "annual_fee": "199 AED (waived with 50k spend)",
                "rewards": "1 mile per 2 AED spent",
                "benefits": ["Airport lounge access", "Fuel surcharge waiver"]
            },
            "gold": {
                "annual_fee": "499 AED",
                "rewards": "2 miles per 1 AED spent",
                "benefits": ["Travel insurance", "Concierge service", "Golf privileges"]
            },
            "platinum": {
                "annual_fee": "1,499 AED",
                "rewards": "3 miles per 1 AED spent",
                "benefits": ["Unlimited lounge access", "Hotel upgrades", "Purchase protection"]
            }
        }
        
        selected = cards.get(card_category.lower(), cards["classic"])
        
        return {
            "success": True,
            "action": "credit_card_info",
            "card_type": card_category,
            "details": selected,
            "eligibility": {
                "min_salary": "5,000 AED",
                "age": "21-65 years",
                "documents": ["Emirates ID", "Passport", "Salary certificate", "Bank statements"]
            },
            "apply_methods": [
                "Apply online in 5 minutes",
                "Visit nearest branch",
                "Call telemarketing: 800-BANK"
            ]
        }
    
    def fees_and_charges(self) -> Dict:
        """Common banking fees and charges."""
        return {
            "success": True,
            "action": "fees_and_charges",
            "common_fees": {
                "account_maintenance": "Free for salary accounts, 25 AED/month others",
                "atm_withdrawal_own": "Free",
                "atm_withdrawal_other": "3.15 AED per transaction",
                "cheque_book": "Free (25 leaves)",
                "duplicate_statement": "50 AED",
                "card_replacement": "52.50 AED",
                "pin_regeneration": "Free",
                "fund_transfer_local": "Free up to 10k, 10 AED above",
                "fund_transfer_international": "From 25 AED",
                "cash_deposit_other_bank": "10 AED per 1000 AED",
                "account_closure_early": "100 AED (within 6 months)"
            },
            "note": "All fees inclusive of 5% VAT"
        }
    
    def kyc_update(self) -> Dict:
        """KYC update procedures."""
        return {
            "success": True,
            "action": "kyc_update",
            "when_required": [
                "Visa renewal",
                "Emirates ID renewal",
                "Change in employment",
                "Address change",
                "Periodic updates (every 2 years)"
            ],
            "update_methods": [
                {
                    "method": "Mobile App",
                    "steps": ["Login", "Profile", "Update KYC", "Upload documents", "Submit"]
                },
                {
                    "method": "Branch Visit",
                    "steps": ["Carry original documents", "Fill update form", "Submit to representative"]
                }
            ],
            "required_documents": [
                "Valid Emirates ID",
                "Valid passport with visa",
                "Salary certificate (if employed)",
                "Trade license (if business owner)"
            ]
        }
    
    def checkbook_request(self) -> Dict:
        """Request new checkbook."""
        return {
            "success": True,
            "action": "checkbook_request",
            "request_methods": [
                "Mobile app: Services > Checkbook Request",
                "Internet banking: Payments > Order Checkbook",
                "Call 800-BANK",
                "Visit branch"
            ],
            "delivery_time": "5-7 business days",
            "collection_point": "Your registered mailing address",
            "charges": "Free for first 2 books per year"
        }
    
    def card_replacement(self, reason: str = "damaged") -> Dict:
        """Card replacement service."""
        return {
            "success": True,
            "action": "card_replacement",
            "reason": reason,
            "replacement_process": [
                "Request via mobile app or call 800-BANK",
                "Pay replacement fee (if applicable)",
                "Old card gets deactivated",
                "New card delivered in 5-7 days",
                "Activate on receipt"
            ],
            "fee": "52.50 AED (free for damaged cards)",
            "expedited_delivery": "Available for 100 AED (2-3 days)"
        }
    
    def account_closure(self) -> Dict:
        """Account closure procedure."""
        return {
            "success": True,
            "action": "account_closure",
            "requirements": [
                "Zero or positive balance",
                "No pending transactions",
                "All loans cleared",
                "Return debit cards and cheque book"
            ],
            "closure_steps": [
                "Visit branch with Emirates ID",
                "Fill account closure form",
                "Submit unused cheques and cards",
                "Receive remaining balance (cash or transfer)",
                "Get closure confirmation letter"
            ],
            "processing_time": "Same day to 3 working days",
            "fees": "Free after 6 months, 100 AED before"
        }
    
    def get_available_tools(self) -> List[Dict]:
        """Get list of all available tools."""
        return [
            {
                "name": key,
                "description": value["description"],
                "category": value.get("category", "general"),
                "urgency": value.get("urgency", "normal")
            }
            for key, value in self.tools_metadata.items()
        ]


# Singleton instance
_enhanced_banking_tools = None


def get_enhanced_banking_tools() -> EnhancedBankingTools:
    """Get or create singleton enhanced banking tools instance."""
    global _enhanced_banking_tools
    if _enhanced_banking_tools is None:
        _enhanced_banking_tools = EnhancedBankingTools()
    return _enhanced_banking_tools
