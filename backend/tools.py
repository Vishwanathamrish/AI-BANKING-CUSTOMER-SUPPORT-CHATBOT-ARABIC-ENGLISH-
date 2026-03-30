"""
Banking Tools Module - Tool functions for banking operations

This module provides actionable tools for common banking requests
that can be called by the chatbot to assist users.
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class BankingTools:
    """
    Collection of banking-related tools that can be invoked.
    
    These tools provide structured responses for common banking tasks.
    """
    
    def __init__(self):
        """Initialize banking tools."""
        logger.info("Banking tools initialized")
        
        # Tool metadata
        self.tools_metadata = {
            "block_card": {
                "name": "Block Card",
                "description": "Immediately block a lost or stolen card",
                "parameters": ["card_type", "reason"]
            },
            "check_balance": {
                "name": "Check Balance",
                "description": "Check account balance information",
                "parameters": ["account_type"]
            },
            "loan_information": {
                "name": "Loan Information",
                "description": "Get details about loan products and eligibility",
                "parameters": ["loan_type"]
            },
            "early_repayment_info": {  # NEW
                "name": "Early Repayment",
                "description": "Get information about early loan repayment",
                "parameters": []
            },
            "check_balance_guide": {  # NEW
                "name": "Check Balance Guide",
                "description": "Guide for checking loan balance",
                "parameters": []
            },
            "open_account_steps": {
                "name": "Open Account",
                "description": "Get step-by-step account opening instructions",
                "parameters": ["account_type"]
            },
            "reset_pin_guide": {
                "name": "Reset PIN",
                "description": "Guide user through PIN reset process",
                "parameters": ["card_type"]
            },
            "transfer_money_guide": {
                "name": "Transfer Money",
                "description": "Provide money transfer instructions",
                "parameters": ["transfer_type", "amount"]
            },
            "secure_account_guide": {  # NEW
                "name": "Secure Account",
                "description": "Provide account security best practices",
                "parameters": []
            }
        }
    
    def block_card(self, card_type: str = "debit", reason: str = "lost") -> Dict:
        """
        Provide card blocking instructions.
        
        Args:
            card_type: Type of card (debit/credit)
            reason: Reason for blocking (lost/stolen/damaged)
            
        Returns:
            Dictionary with blocking instructions
        """
        logger.info(f"Blocking {card_type} card due to {reason}")
        
        return {
            "success": True,
            "action": "block_card",
            "instructions": [
                f"Call our 24/7 customer support hotline immediately at 800-BANK",
                f"Alternatively, use the mobile app:",
                "  1. Login to your account",
                "  2. Go to 'Card Services'",
                "  3. Select 'Block Card'",
                f"  4. Choose {card_type} card",
                f"  5. Select reason: {reason}",
                "  6. Confirm blocking",
                "",
                "Your card will be blocked immediately.",
                "A replacement card will be sent within 5-7 business days."
            ],
            "emergency_contact": "800-BANK",
            "replacement_time": "5-7 business days"
        }
    
    def check_balance(self, account_type: str = "savings") -> Dict:
        """
        Provide balance checking methods.
        
        Args:
            account_type: Type of account
            
        Returns:
            Dictionary with balance checking methods
        """
        logger.info(f"Checking balance for {account_type} account")
        
        return {
            "success": True,
            "action": "check_balance",
            "methods": [
                {
                    "method": "Mobile App",
                    "steps": [
                        "Login to mobile app",
                        "View dashboard",
                        "Balance displayed under account"
                    ]
                },
                {
                    "method": "Internet Banking",
                    "steps": [
                        "Login to internet banking portal",
                        "Navigate to 'Accounts'",
                        "Select your account",
                        "View available balance"
                    ]
                },
                {
                    "method": "ATM",
                    "steps": [
                        "Visit any of our ATMs",
                        "Insert your card",
                        "Enter PIN",
                        "Select 'Balance Inquiry'"
                    ]
                },
                {
                    "method": "Phone Banking",
                    "steps": [
                        "Call 800-BANK",
                        "Follow automated prompts",
                        "Select 'Account Information'",
                        "Listen to your balance"
                    ]
                }
            ]
        }
    
    def loan_information(self, loan_type: str = "personal") -> Dict:
        """
        Provide loan product information.
        
        Args:
            loan_type: Type of loan (personal/auto/home)
            
        Returns:
            Dictionary with loan details
        """
        logger.info(f"Providing information for {loan_type} loan")
        
        loan_info = {
            "personal": {
                "interest_rate": "Starting from 5.99% per annum",
                "max_amount": "Up to 200,000 AED",
                "tenure": "Up to 5 years",
                "requirements": [
                    "Salary certificate",
                    "Emirates ID",
                    "Passport copy",
                    "Bank statements (last 3 months)"
                ],
                "processing_fee": "1,500 AED"
            },
            "auto": {
                "interest_rate": "Starting from 3.99% per annum",
                "max_amount": "Up to 80% of car value",
                "tenure": "Up to 7 years",
                "requirements": [
                    "Valid UAE driving license",
                    "Salary certificate",
                    "Emirates ID",
                    "Car registration",
                    "Insurance policy"
                ],
                "processing_fee": "999 AED"
            },
            "home": {
                "interest_rate": "Starting from 4.49% per annum",
                "max_amount": "Up to 85% of property value",
                "tenure": "Up to 25 years",
                "requirements": [
                    "Salary certificate",
                    "Emirates ID",
                    "Passport copy",
                    "Property documents",
                    "Bank statements (last 6 months)"
                ],
                "processing_fee": "5,000 AED or 1% of loan amount"
            }
        }
        
        selected_loan = loan_info.get(loan_type.lower(), loan_info["personal"])
        
        return {
            "success": True,
            "action": "loan_information",
            "loan_type": loan_type,
            "details": selected_loan,
            "next_steps": [
                "Visit our website to calculate EMI",
                "Apply online through mobile app",
                "Visit nearest branch for detailed consultation"
            ]
        }
    
    def open_account_steps(self, account_type: str = "savings") -> Dict:
        """
        Provide account opening instructions.
        
        Args:
            account_type: Type of account to open
            
        Returns:
            Dictionary with step-by-step instructions
        """
        logger.info(f"Opening {account_type} account")
        
        return {
            "success": True,
            "action": "open_account",
            "account_type": account_type,
            "methods": [
                {
                    "method": "Online",
                    "steps": [
                        "Visit our website or download mobile app",
                        "Click on 'Open Account'",
                        f"Select '{account_type.title()} Account'",
                        "Fill in personal details",
                        "Upload required documents:",
                        "  - Emirates ID (front & back)",
                        "  - Passport copy with visa page",
                        "  - Salary certificate (for some accounts)",
                        "Complete video KYC verification",
                        "Receive account details instantly"
                    ],
                    "time_required": "15-20 minutes"
                },
                {
                    "method": "Branch Visit",
                    "steps": [
                        "Visit any of our branches",
                        "Collect account opening form",
                        "Fill in required details",
                        "Submit along with documents:",
                        "  - Original Emirates ID",
                        "  - Original Passport",
                        "  - Salary certificate",
                        "Make initial deposit",
                        "Receive welcome kit with debit card and cheque book"
                    ],
                    "time_required": "30-45 minutes"
                }
            ],
            "required_documents": [
                "Emirates ID (original + copy)",
                "Passport with valid visa (original + copy)",
                "Salary certificate (if employed)",
                "Trade license (if business owner)"
            ],
            "minimum_balance": {
                "savings": "1,000 AED",
                "current": "5,000 AED"
            }
        }
    
    def reset_pin_guide(self, card_type: str = "debit") -> Dict:
        """
        Provide PIN reset instructions.
        
        Args:
            card_type: Type of card
            
        Returns:
            Dictionary with PIN reset guide
        """
        logger.info(f"Resetting PIN for {card_type} card")
        
        return {
            "success": True,
            "action": "reset_pin",
            "card_type": card_type,
            "methods": [
                {
                    "method": "Mobile App",
                    "steps": [
                        "Login to mobile app",
                        "Go to 'Card Services'",
                        "Select 'PIN Reset'",
                        f"Choose your {card_type} card",
                        "Verify with OTP",
                        "Set new 4-digit PIN",
                        "Confirm PIN"
                    ]
                },
                {
                    "method": "ATM",
                    "steps": [
                        "Visit any of our ATMs",
                        "Insert your card",
                        "Enter existing PIN (if known)",
                        "Select 'PIN Services'",
                        "Choose 'Generate PIN'",
                        "Follow on-screen instructions",
                        "Collect PIN mailer or set instantly"
                    ]
                },
                {
                    "method": "Customer Care",
                    "steps": [
                        "Call 800-BANK",
                        "Verify your identity",
                        "Request PIN reset",
                        "Receive PIN via SMS or post"
                    ]
                }
            ],
            "important_notes": [
                "Never share your PIN with anyone",
                "Avoid using obvious numbers like birth year",
                "Change PIN regularly for security"
            ]
        }
    
    def transfer_money_guide(self, transfer_type: str = "local", amount: float = 0) -> Dict:
        """
        Provide money transfer instructions.
        
        Args:
            transfer_type: Type of transfer (local/international)
            amount: Transfer amount
            
        Returns:
            Dictionary with transfer guide
        """
        logger.info(f"Transferring {amount} via {transfer_type} transfer")
        
        limits = {
            "local": {
                "min": "1 AED",
                "max": "50,000 AED per day",
                "fee": "Free for amounts < 10,000 AED"
            },
            "international": {
                "min": "100 AED",
                "max": "50,000 AED per day (higher with approval)",
                "fee": "From 25 AED + correspondent bank charges"
            }
        }
        
        selected_limits = limits.get(transfer_type.lower(), limits["local"])
        
        return {
            "success": True,
            "action": "transfer_money",
            "transfer_type": transfer_type,
            "amount": amount,
            "limits": selected_limits,
            "methods": [
                {
                    "method": "Mobile App",
                    "steps": [
                        "Login to mobile app",
                        "Go to 'Transfers'",
                        f"Select '{transfer_type.title()} Transfer'",
                        "Add beneficiary (if new)",
                        "Enter amount and details",
                        "Review and confirm",
                        "Receive confirmation SMS"
                    ],
                    "processing_time": "Instant for local, 1-3 days international"
                },
                {
                    "method": "Internet Banking",
                    "steps": [
                        "Login to internet banking",
                        "Navigate to 'Fund Transfer'",
                        "Select transfer type",
                        "Enter beneficiary details",
                        "Input amount",
                        "Authenticate with OTP",
                        "Confirm transfer"
                    ]
                },
                {
                    "method": "Branch Visit",
                    "steps": [
                        "Visit nearest branch",
                        "Fill transfer form",
                        "Submit with ID",
                        "Make payment",
                        "Receive receipt"
                    ],
                    "note": "Required for large international transfers >50,000 AED"
                }
            ],
            "required_details": {
                "local": ["Beneficiary name", "Account number", "Bank code"],
                "international": [
                    "Beneficiary name",
                    "Account number/IBAN",
                    "SWIFT/BIC code",
                    "Bank name and address",
                    "Purpose of transfer"
                ]
            }
        }
    
    def secure_account_guide(self) -> Dict:
        """
        Provide account security best practices.
        
        Returns:
            Dictionary with security guidelines
        """
        logger.info("Providing account security guide")
        
        return {
            "success": True,
            "action": "secure_account",
            "title": "Secure Your Bank Account",
            "guidelines": [
                {
                    "title": "Enable Strong Authentication",
                    "points": [
                        "Use biometric login (fingerprint/face recognition)",
                        "Enable OTP for all transactions",
                        "Never share OTP with anyone"
                    ]
                },
                {
                    "title": "Password Security",
                    "points": [
                        "Use strong password (8+ characters, numbers, symbols)",
                        "Change password every 3 months",
                        "Don't use obvious passwords like birth year"
                    ]
                },
                {
                    "title": "Transaction Safety",
                    "points": [
                        "Verify beneficiary details before transfer",
                        "Set transaction limits",
                        "Enable SMS alerts for all transactions"
                    ]
                },
                {
                    "title": "Avoid Fraud",
                    "points": [
                        "Never click suspicious links in emails/SMS",
                        "Bank never asks for password via phone",
                        "Report suspicious calls to 800-BANK"
                    ]
                }
            ],
            "emergency_contact": "800-BANK",
            "report_fraud": "Call immediately if you suspect fraud"
        }
    
    def early_repayment_info(self) -> Dict:
        """
        Provide information about early loan repayment.
        
        Returns:
            Dictionary with early repayment information
        """
        logger.info("Providing early repayment information")
        
        return {
            "success": True,
            "action": "early_repayment",
            "allowed": True,
            "summary": "Early repayment is allowed with applicable fees",
            "details": {
                "partial_settlement": True,
                "full_settlement": True,
                "early_settlement_fee": "2% of outstanding amount or AED 500, whichever is higher",
                "notice_period": "7 business days",
                "conditions": [
                    "No overdue payments",
                    "Minimum 6 EMI paid",
                    "Written request required"
                ]
            },
            "next_steps": [
                "Submit written request at nearest branch",
                "Pay outstanding amount plus settlement fee",
                "Collect NOC and release securities"
            ]
        }
    
    def check_balance_guide(self) -> Dict:
        """
        Provide guide for checking loan balance.
        
        Returns:
            Dictionary with balance checking methods
        """
        logger.info("Providing balance check guide")
        
        return {
            "success": True,
            "action": "check_balance_guide",
            "methods": [
                {
                    "method": "Mobile Banking App",
                    "steps": [
                        "Login to mobile app",
                        "Go to 'Loans' section",
                        "Select your loan account",
                        "View outstanding balance"
                    ]
                },
                {
                    "method": "Internet Banking",
                    "steps": [
                        "Login to internet banking",
                        "Navigate to 'Accounts' > 'Loans'",
                        "Click on loan account number",
                        "View balance and details"
                    ]
                },
                {
                    "method": "ATM",
                    "steps": [
                        "Insert debit card at ATM",
                        "Enter PIN",
                        "Select 'Balance Inquiry'",
                        "Choose loan account"
                    ]
                },
                {
                    "method": "Customer Service",
                    "steps": [
                        "Call 800-BANK",
                        "Verify identity with customer service",
                        "Request loan balance information"
                    ]
                },
                {
                    "method": "Branch Visit",
                    "steps": [
                        "Visit nearest branch with Emirates ID",
                        "Meet with customer service representative",
                        "Request loan balance statement"
                    ]
                }
            ]
        }
    
    def get_available_tools(self) -> List[Dict]:
        """
        Get list of available tools with descriptions.
        
        Returns:
            List of tool metadata
        """
        return [
            {
                "name": key,
                "description": value["description"],
                "parameters": value["parameters"]
            }
            for key, value in self.tools_metadata.items()
        ]


# Singleton instance
_banking_tools = None


def get_banking_tools() -> BankingTools:
    """Get or create singleton banking tools instance."""
    global _banking_tools
    if _banking_tools is None:
        _banking_tools = BankingTools()
    return _banking_tools


def invoke_tool(tool_name: str, **kwargs) -> Dict:
    """
    Convenience function to invoke a banking tool.
    
    Args:
        tool_name: Name of tool to invoke
        **kwargs: Tool parameters
        
    Returns:
        Tool execution result
    """
    tools = get_banking_tools()
    
    if hasattr(tools, tool_name):
        method = getattr(tools, tool_name)
        return method(**kwargs)
    else:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }
