"""
Loan Response Generator Module - Dynamic responses for loan intents

This module generates context-aware, intent-specific responses for loan queries.
Supports both English and Arabic with professional banking tone.
"""

import logging
from typing import Dict, Optional
from .intent_detection import BankingIntent

logger = logging.getLogger(__name__)


class LoanResponseGenerator:
    """
    Generates dynamic loan responses based on specific intent.
    
    Features:
    - Intent-specific templates (not static)
    - Bilingual support (EN/AR)
    - Professional UAE banking tone
    - Strict 3-4 bullet format
    """
    
    # English response templates by intent - WITH COMPLIANCE LANGUAGE
    EN_TEMPLATES = {
        BankingIntent.LOAN_APPLY: {
            "bullets": [
                "Apply online via our website or mobile app with your Emirates ID",
                "Submit passport copy, salary certificate, and bank statements",
                "Choose loan amount and tenure based on your eligibility",
                "Approval typically completed within 1–3 working days (subject to bank approval)",
                "Terms and conditions apply to all loan applications"
            ]
        },
        BankingIntent.LOAN_DOCUMENTS: {
            "bullets": [
                "Provide valid Emirates ID (original and photocopy)",
                "Submit passport copy with UAE residence visa page",
                "Share salary certificate and last 3 months bank statements",
                "Additional documents may be requested based on eligibility assessment",
                "All documents subject to verification and bank approval"
            ]
        },
        BankingIntent.LOAN_APPROVAL_TIME: {
            "bullets": [
                "Loan approval usually completed within 1–3 working days",
                "Processing time depends on document verification and eligibility",
                "Pre-approved customers may receive instant approval in some cases",
                "You will receive SMS or email confirmation upon approval decision",
                "Timeline subject to bank approval and completeness of application"
            ]
        },
        BankingIntent.LOAN_INTEREST: {
            "bullets": [
                "Personal loan interest rates starting from 5.99% per annum (reducing balance)",
                "Interest rate depends on salary amount and employer category",
                "Reducing balance rate applied on outstanding principal amount",
                "Contact us for personalized rate calculation based on your profile",
                "Rates subject to bank approval and terms and conditions apply"
            ]
        },
        BankingIntent.LOAN_TENURE: {
            "bullets": [
                "Personal loan tenure available up to 5 years maximum (60 months)",
                "Auto loans available for up to 7 years period (84 months)",
                "Home loans available for up to 25 years duration (300 months)",
                "Choose flexible tenure based on your repayment capacity and eligibility",
                "Tenure options subject to bank approval and age criteria"
            ]
        },
        BankingIntent.LOAN_REPAYMENT: {
            "bullets": [
                "Repay loan early through mobile app or by visiting any branch",
                "Early settlement fees may apply as per bank policy and terms",
                "Final settlement amount calculated at time of closure",
                "Collect No Objection Certificate (NOC) after complete loan settlement",
                "Terms and conditions apply to all early repayment transactions"
            ]
        },
        BankingIntent.LOAN_BALANCE: {
            "bullets": [
                "Check loan balance via mobile banking app instantly",
                "View outstanding amount through internet banking portal",
                "Visit nearest branch with Emirates ID for detailed statement",
                "Call customer service at 800-BANK for balance inquiry assistance",
                "Available for eligible account holders only"
            ]
        },
        BankingIntent.LOAN_INFORMATION: {
            "bullets": [
                "Personal loans available starting from 5.99% per annum for eligible customers",
                "Loan amounts up to 200,000 AED based on salary and eligibility criteria",
                "Flexible tenure options from 1 to 5 years to suit your needs",
                "Quick approval process with minimal documentation required",
                "All loan products subject to bank approval and terms and conditions"
            ]
        }
    }
    
    # Arabic response templates by intent - WITH COMPLIANCE LANGUAGE & NATURAL PHRASES
    AR_TEMPLATES = {
        BankingIntent.LOAN_APPLY: {
            "bullets": [
                "قدّم طلب القرض عبر موقعنا الإلكتروني أو تطبيق الهاتف المحمول باستخدام بطاقة الهوية الإماراتية",
                "أرسل نسخة من جواز السفر مع تأشيرة الإقامة وشهادة الراتب والكشوفات المصرفية",
                "اختر مبلغ القرض ومدة السداد المناسبة لاحتياجاتك وفقاً للأهلية",
                "تتم الموافقة على القرض عادة خلال 1-3 أيام عمل (خاضعة لموافقة البنك)",
                "تطبق الشروط والأحكام على جميع طلبات التمويل والقروض"
            ]
        },
        BankingIntent.LOAN_DOCUMENTS: {
            "bullets": [
                "قدّم نسخة صالحة من بطاقة الهوية الإماراتية (الأصل والصورة)",
                "أرسل نسخة من جواز السفر مع صفحة تأشيرة الإقامة سارية المفعول",
                "وفّر شهادة الراتب والكشوفات المصرفية لآخر 3 أشهر",
                "قد تُطلب مستندات إضافية بناءً على تقييم الأهتمان والائتمان",
                "جميع المستندات خاضعة للتحقق وموافقة البنك النهائية"
            ]
        },
        BankingIntent.LOAN_APPROVAL_TIME: {
            "bullets": [
                "تتم الموافقة على القرض عادة خلال فترة 1-3 أيام عمل",
                "يعتمد وقت المعالجة على التحقق من المستندات واستكمال الأهلية",
                "العملاء المؤهلون مسبقاً قد يحصلون على موافقة فورية في بعض الحالات",
                "ستصلك رسالة نصية أو بريد إلكتروني عند صدور قرار الموافقة",
                "الجدول الزمني خاضع لموافقة البنك واكتمال الطلب"
            ]
        },
        BankingIntent.LOAN_INTEREST: {
            "bullets": [
                "تبدأ نسبة فائدة القرض الشخصي من 5.99% سنوياً (على الرصيد المتناقص)",
                "تعتمد نسبة الفائدة على مبلغ الراتب وفئة صاحب العمل",
                "يُطبق معدل الربح المتناقص على المبلغ الأصلي المستحق",
                "تواصل معنا لحساب النسبة المخصصة لك بناءً على ملفك المالي",
                "النسب خاضعة لموافقة البنك وتطبق الشروط والأحكام"
            ]
        },
        BankingIntent.LOAN_TENURE: {
            "bullets": [
                "مدة القرض الشخصي متاحة حتى 5 سنوات كحد أقصى (60 شهراً)",
                "قروض السيارات متاحة لمدة تصل إلى 7 سنوات (84 شهراً)",
                "القروض العقارية متاحة لمدة تصل إلى 25 سنة (300 شهر)",
                "اختر المدة المرنة المناسبة لقدتك المالية على السداد وأهليتك",
                "خيارات المدة خاضعة لموافقة البنك وشروط السن المحددة"
            ]
        },
        BankingIntent.LOAN_REPAYMENT: {
            "bullets": [
                "يمكن سداد القرض مبكراً عبر تطبيق الهاتف المحمول أو بزيارة أي فرع",
                "قد تُرسوم تسوية مبكرة وفقاً لسياسة البنك والشروط المعمول بها",
                "يتم احتساب مبلغ التسوية النهائي عند وقت الإغلاق الفعلي",
                "استلم خطاب عدم مديونية (NOC) بعد سداد القرض بالكامل",
                "تطبق الشروط والأحكام على جميع معاملات السداد المبكر"
            ]
        },
        BankingIntent.LOAN_BALANCE: {
            "bullets": [
                "تحقق من رصيد القرض فوراً عبر تطبيق الخدمات المصرفية المحمولة",
                "اعرض المبلغ المستحق التفصيلي عبر بوابة الخدمات المصرفية الإلكترونية",
                "زر أقرب فرع مصرفي مع بطاقة الهوية الإماراتية للحصول على كشف تفصيلي",
                "اتصل بخدمة العملاء على 800-BANK للمساعدة في الاستعلام عن الرصيد",
                "الخدمة متاحة لحاملي الحسابات المؤهلين فقط"
            ]
        },
        BankingIntent.LOAN_INFORMATION: {
            "bullets": [
                "القروض الشخصية متاحة بنسبة فائدة تبدأ من 5.99% سنوياً للعملاء المؤهلين",
                "مبالغ القروض تصل حتى 200,000 درهم بناءً على الراتب ومعايير الأهلية",
                "خيارات مدة سداد مرنة من 1 إلى 5 سنوات لتناسب احتياجاتك المالية",
                "عملية موافقة سريعة مع الحد الأدنى من المستندات المطلوبة للإجراءات",
                "جميع منتجات القروض خاضعة لموافقة البنك وتطبق عليها الشروط والأحكام"
            ]
        }
    }
    
    def __init__(self):
        """Initialize the loan response generator."""
        logger.info("Loan response generator initialized")
    
    def generate_response(
        self, 
        intent: BankingIntent,
        language: str = "English"
    ) -> Optional[str]:
        """
        Generate dynamic loan response based on intent.
        
        Args:
            intent: Detected loan intent
            language: Response language (English/Arabic)
            
        Returns:
            Formatted bullet-point response or None
        """
        # Select template based on language
        if language.lower() in ["arabic", "ar"]:
            templates = self.AR_TEMPLATES
        else:
            templates = self.EN_TEMPLATES
        
        # Get template for specific intent
        if intent not in templates:
            logger.warning(f"No template for loan intent: {intent}")
            # Fallback to general loan info
            intent = BankingIntent.LOAN_INFORMATION
        
        template = templates[intent]
        bullets = template["bullets"]
        
        # Format as bullet points
        formatted = "\n".join([f"• {bullet}" for bullet in bullets])
        
        logger.debug(f"Generated {language} response for {intent.value}")
        return formatted
    
    def get_template(self, intent: BankingIntent, language: str = "English") -> list:
        """
        Get raw template bullets for an intent.
        
        Args:
            intent: Loan intent
            language: Response language
            
        Returns:
            List of bullet strings
        """
        if language.lower() in ["arabic", "ar"]:
            templates = self.AR_TEMPLATES
        else:
            templates = self.EN_TEMPLATES
        
        if intent not in templates:
            return templates[BankingIntent.LOAN_INFORMATION]["bullets"]
        
        return templates[intent]["bullets"]


# Singleton instance
_generator = None


def get_loan_generator() -> LoanResponseGenerator:
    """Get or create singleton loan response generator."""
    global _generator
    if _generator is None:
        _generator = LoanResponseGenerator()
    return _generator


def generate_loan_response(
    intent: BankingIntent,
    language: str = "English"
) -> Optional[str]:
    """
    Generate loan response for given intent.
    
    Args:
        intent: Detected loan intent
        language: Response language
        
    Returns:
        Formatted response string
    """
    generator = get_loan_generator()
    return generator.generate_response(intent, language)
