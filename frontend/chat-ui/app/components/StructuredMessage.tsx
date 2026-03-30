'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { 
  Building, 
  CreditCard, 
  DollarSign, 
  FileText, 
  CheckCircle2, 
  AlertCircle,
  ArrowRight,
  Clock,
  Phone
} from 'lucide-react';
import { clsx } from 'clsx';

interface LoanData {
  loan_type: string;
  interest_rate: string;
  max_amount: string;
  tenure: string;
  requirements: string[];
  processing_fee?: string;
  next_steps?: string[];
}

interface CardData {
  action: string;
  emergency_contact: string;
  replacement_time: string;
  instructions: string[];
}

interface AccountData {
  account_type: string;
  methods: any[];
  required_documents: string[];
  minimum_balance: Record<string, string>;
  time_required?: string;
}

interface BalanceData {
  methods: any[];
}

interface StructuredMessageProps {
  type: 'text' | 'loan' | 'account' | 'card' | 'balance';
  data: any;
  language: 'en' | 'ar';
}

export function StructuredMessage({ type, data, language }: StructuredMessageProps) {
  const isRTL = language === 'ar';

  if (type === 'loan') {
    return <LoanCard data={data as LoanData} language={language} />;
  } else if (type === 'card') {
    return <CardBlockCard data={data as CardData} language={language} />;
  } else if (type === 'account') {
    return <AccountCard data={data as AccountData} language={language} />;
  } else if (type === 'balance') {
    return <BalanceCard data={data as BalanceData} language={language} />;
  }
  
  return null;
}

function LoanCard({ data, language }: { data: LoanData; language: 'en' | 'ar' }) {
  const labels = {
    en: {
      title: 'Loan Information',
      interestRate: 'Interest Rate',
      maxAmount: 'Maximum Amount',
      tenure: 'Tenure',
      processingFee: 'Processing Fee',
      requirements: 'Requirements',
      nextSteps: 'Next Steps',
      apply: 'Apply Now'
    },
    ar: {
      title: 'معلومات القرض',
      interestRate: 'معدل الفائدة',
      maxAmount: 'الحد الأقصى للمبلغ',
      tenure: 'المدة',
      processingFee: 'رسوم المعالجة',
      requirements: 'المتطلبات',
      nextSteps: 'الخطوات التالية',
      apply: 'قدم الآن'
    }
  };

  const t = labels[language];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-2xl bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-blue-200 dark:border-blue-900 overflow-hidden"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-3">
        <div className="flex items-center gap-2">
          <Building className="w-5 h-5 text-white" />
          <h3 className="text-lg font-semibold text-white">{t.title}</h3>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        {/* Key Details Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
            <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">{t.interestRate}</p>
            <p className="text-sm font-semibold text-blue-700 dark:text-blue-300">{data.interest_rate}</p>
          </div>
          <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
            <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">{t.maxAmount}</p>
            <p className="text-sm font-semibold text-blue-700 dark:text-blue-300">{data.max_amount}</p>
          </div>
          <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
            <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">{t.tenure}</p>
            <p className="text-sm font-semibold text-blue-700 dark:text-blue-300">{data.tenure}</p>
          </div>
          {data.processing_fee && (
            <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
              <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">{t.processingFee}</p>
              <p className="text-sm font-semibold text-blue-700 dark:text-blue-300">{data.processing_fee}</p>
            </div>
          )}
        </div>

        {/* Requirements */}
        {data.requirements && data.requirements.length > 0 && (
          <div className="mt-3">
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <FileText className="w-4 h-4" />
              {t.requirements}
            </h4>
            <ul className="space-y-1">
              {data.requirements.map((req, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                  <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>{req}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Next Steps */}
        {data.next_steps && data.next_steps.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <ArrowRight className="w-4 h-4" />
              {t.nextSteps}
            </h4>
            <div className="space-y-2">
              {data.next_steps.map((step, idx) => (
                <div key={idx} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}

function CardBlockCard({ data, language }: { data: CardData; language: 'en' | 'ar' }) {
  const labels = {
    en: {
      title: 'Block Your Card',
      emergency: 'Emergency Contact',
      callNow: 'Call Now',
      replacement: 'Replacement Time',
      steps: 'Steps to Block'
    },
    ar: {
      title: 'حظر بطاقتك',
      emergency: 'جهة اتصال الطوارئ',
      callNow: 'اتصل الآن',
      replacement: 'وقت الاستبدال',
      steps: 'خطوات الحظر'
    }
  };

  const t = labels[language];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-2xl bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-red-200 dark:border-red-900 overflow-hidden"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-red-600 to-red-700 px-4 py-3">
        <div className="flex items-center gap-2">
          <CreditCard className="w-5 h-5 text-white" />
          <h3 className="text-lg font-semibold text-white">{t.title}</h3>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Emergency Contact */}
        <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Phone className="w-5 h-5 text-red-600" />
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400">{t.emergency}</p>
                <p className="text-lg font-bold text-red-700 dark:text-red-300">{data.emergency_contact}</p>
              </div>
            </div>
            <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors">
              {t.callNow}
            </button>
          </div>
        </div>

        {/* Replacement Time */}
        <div className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <Clock className="w-4 h-4 text-blue-500" />
          <span>{t.replacement}: <span className="font-semibold">{data.replacement_time}</span></span>
        </div>

        {/* Steps */}
        {data.instructions && data.instructions.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">{t.steps}</h4>
            <ol className="space-y-1">
              {data.instructions.slice(0, 5).map((step, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                  <span className="flex-shrink-0 w-5 h-5 bg-red-100 dark:bg-red-900/30 text-red-600 rounded-full flex items-center justify-center text-xs font-semibold">
                    {idx + 1}
                  </span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </motion.div>
  );
}

function AccountCard({ data, language }: { data: AccountData; language: 'en' | 'ar' }) {
  const labels = {
    en: {
      title: 'Open Account',
      documents: 'Required Documents',
      minBalance: 'Minimum Balance',
      timeRequired: 'Time Required',
      methods: 'How to Apply'
    },
    ar: {
      title: 'فتح حساب',
      documents: 'المستندات المطلوبة',
      minBalance: 'الرصيد الأدنى',
      timeRequired: 'الوقت المطلوب',
      methods: 'كيفية التقديم'
    }
  };

  const t = labels[language];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-2xl bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-green-200 dark:border-green-900 overflow-hidden"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 px-4 py-3">
        <div className="flex items-center gap-2">
          <Building className="w-5 h-5 text-white" />
          <h3 className="text-lg font-semibold text-white">{t.title}</h3>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Required Documents */}
        {data.required_documents && (
          <div>
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <FileText className="w-4 h-4" />
              {t.documents}
            </h4>
            <ul className="space-y-1">
              {data.required_documents.map((doc, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                  <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>{doc}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Minimum Balance */}
        {data.minimum_balance && Object.keys(data.minimum_balance).length > 0 && (
          <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
            <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">{t.minBalance}</p>
            <div className="space-y-1">
              {Object.entries(data.minimum_balance).map(([type, amount]) => (
                <div key={type} className="flex justify-between text-sm">
                  <span className="text-gray-700 dark:text-gray-300 capitalize">{type}:</span>
                  <span className="font-semibold text-green-700 dark:text-green-300">{amount}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Time Required */}
        {data.time_required && (
          <div className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <Clock className="w-4 h-4 text-blue-500" />
            <span>{t.timeRequired}: <span className="font-semibold">{data.time_required}</span></span>
          </div>
        )}
      </div>
    </motion.div>
  );
}

function BalanceCard({ data, language }: { data: BalanceData; language: 'en' | 'ar' }) {
  const labels = {
    en: {
      title: 'Check Balance',
      methods: 'Available Methods'
    },
    ar: {
      title: 'التحقق من الرصيد',
      methods: 'الطرق المتاحة'
    }
  };

  const t = labels[language];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-2xl bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-purple-200 dark:border-purple-900 overflow-hidden"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-4 py-3">
        <div className="flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-white" />
          <h3 className="text-lg font-semibold text-white">{t.title}</h3>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">{t.methods}</h4>
        <div className="space-y-2">
          {data.methods && data.methods.map((method, idx) => (
            <div key={idx} className="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-lg">
              <p className="text-sm font-semibold text-purple-700 dark:text-purple-300 mb-2">
                {method.method}
              </p>
              {method.steps && method.steps.length > 0 && (
                <ol className="space-y-1">
                  {method.steps.slice(0, 4).map((step: string, stepIdx: number) => (
                    <li key={stepIdx} className="flex items-start gap-2 text-xs text-gray-700 dark:text-gray-300">
                      <span className="flex-shrink-0 w-4 h-4 bg-purple-100 dark:bg-purple-900/30 text-purple-600 rounded-full flex items-center justify-center text-[10px] font-semibold">
                        {stepIdx + 1}
                      </span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ol>
              )}
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
