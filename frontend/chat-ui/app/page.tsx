'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { 
  Send, Bot, User, Moon, Sun, Menu, X, Search,
  Building, CreditCard, DollarSign, FileText, KeyRound,
  Languages, MessageSquare, Plus, Trash2, MoreVertical,
  Share2, Edit2, Pin, Archive, Mic, Volume2, PhoneOff, Globe
} from 'lucide-react';
import { clsx } from 'clsx';
import { format } from 'date-fns';
import { StructuredMessage } from './components/StructuredMessage';
import { useTheme } from './ThemeContext';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  language?: string;
  confidence?: number;
  response_type?: 'text' | 'loan' | 'account' | 'card' | 'balance';
  data?: any;
}

interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messages: Message[];
  pinned?: boolean;
  archived?: boolean;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export default function ChatPage() {
  const { theme, toggleTheme } = useTheme()!;
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true); // Changed to true for always-visible sidebar
  const [language, setLanguage] = useState<'en' | 'ar'>('en');
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const [archivedChats, setArchivedChats] = useState<Conversation[]>([]);
  const [menuPosition, setMenuPosition] = useState<{ top: number; right: number } | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Voice features state
  const [isDictating, setIsDictating] = useState(false);
  const [isVoiceModeOpen, setIsVoiceModeOpen] = useState(false);
  const [voiceModeState, setVoiceModeState] = useState<'idle' | 'listening' | 'processing' | 'speaking'>('idle');
  const [voiceMuted, setVoiceMuted] = useState(false);
  const [voiceTranscript, setVoiceTranscript] = useState('');
  const [lastAiResponse, setLastAiResponse] = useState('');
  const [isMobile, setIsMobile] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Debug: Monitor menu state changes
  useEffect(() => {
    console.log('🟢 Menu State Changed:', { activeMenu, menuPosition });
  }, [activeMenu, menuPosition]);

  // Ensure sidebar is visible on initial load
  useEffect(() => {
    setSidebarOpen(true);
    console.log('📌 Sidebar forced open on mount');
  }, []);

  // Handle responsive placeholder for mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 480);
    };
    
    // Initial check
    checkMobile();
    
    // Listen for resize
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Debug: Monitor conversations state changes
  useEffect(() => {
    console.log('💬 Conversations updated:', conversations.length, 'total');
    conversations.forEach(conv => {
      console.log(`  - ${conv.id}: ${conv.messages.length} messages, title: "${conv.title}"`);
    });
  }, [conversations]);

  // CRITICAL FIX: Sync messages when switching conversations
  useEffect(() => {
    if (!currentConversationId) {
      setMessages([]);
      console.log('🔄 No conversation selected, cleared messages');
      return;
    }
    
    const conversation = conversations.find(conv => conv.id === currentConversationId);
    if (conversation) {
      // Force create new array reference to ensure re-render
      setMessages([...conversation.messages]);
      console.log('🔄 Synced messages from conversation:', currentConversationId, 'count:', conversation.messages.length);
    } else {
      console.warn('⚠️ Conversation not found in state:', currentConversationId);
    }
  }, [currentConversationId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Generate unique ID for conversations
  const generateId = () => {
    return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // Create a new conversation
  const createNewConversation = (firstMessage?: string) => {
    const id = generateId();
    const title = firstMessage ? firstMessage.slice(0, 50) : (language === 'en' ? 'New Chat' : 'محادثة جديدة');
    
    const newConversation: Conversation = {
      id,
      title,
      createdAt: new Date(),
      updatedAt: new Date(),
      messages: [],
    };
    
    console.log('🆕 Creating conversation:', id, 'title:', title);
    setConversations(prev => {
      const updated = [...prev, newConversation];
      console.log('💾 Saved to conversations state, total:', updated.length);
      return updated;
    });
    setCurrentConversationId(id);
    setMessages([]);
    
    return id;
  };

  // Load a specific conversation with safety checks
  const loadConversation = (conversationId: string) => {
    const conversation = conversations.find(conv => conv.id === conversationId);
    if (conversation) {
      setCurrentConversationId(conversationId);
      setMessages([...conversation.messages]); // Create a new array reference to trigger re-render
      console.log('✅ Loaded conversation:', conversationId, 'with', conversation.messages.length, 'messages');
    } else {
      console.error('❌ Conversation not found:', conversationId);
    }
  };

  // Clear all conversations
  const clearAllConversations = () => {
    setConversations([]);
    setCurrentConversationId(null);
    setMessages([]);
  };

  // Start a new chat (clear button click)
  const handleNewChat = () => {
    createNewConversation();
  };

  const quickActions = [
    { label: language === 'en' ? 'Open Account' : 'فتح حساب', query: language === 'en' ? 'How do I open a bank account?' : 'كيف أفتح حسابًا بنكيًا؟', icon: Building },
    { label: language === 'en' ? 'Block Card' : 'حظر البطاقة', query: language === 'en' ? 'I lost my card, block it immediately' : 'بطاقتي مفقودة، احظرها فوراً', icon: CreditCard },
    { label: language === 'en' ? 'Check Balance' : 'التحقق من الرصيد', query: language === 'en' ? 'How can I check my account balance?' : 'كيف يمكنني التحقق من رصيد حسابي؟', icon: DollarSign },
    { label: language === 'en' ? 'Loan Info' : 'معلومات القرض', query: language === 'en' ? 'Tell me about personal loans' : 'أخبرني عن القروض الشخصية', icon: FileText },
    { label: language === 'en' ? 'Reset PIN' : 'إعادة تعيين الرمز', query: language === 'en' ? 'How do I reset my ATM PIN?' : 'كيف يمكنني إعادة تعيين PIN للصراف الآلي؟', icon: KeyRound },
  ];

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim()) return;

    console.log('🚀 Starting sendMessage:', { messageText, currentConversationId });

    // Generate message objects
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    };

    let activeConversationId = currentConversationId;
    
    // CRITICAL FIX: Handle everything in ONE setConversations call to avoid race conditions
    if (!activeConversationId) {
      // Need to create new conversation AND add messages atomically
      const id = generateId();
      const title = messageText.slice(0, 50);
      
      console.log('🆕 Creating conversation and adding messages atomically:', id);
      
      setConversations(prev => {
        const newConv: Conversation = {
          id,
          title,
          createdAt: new Date(),
          updatedAt: new Date(),
          messages: [userMessage], // Add user message IMMEDIATELY on creation
        };
        
        const updated = [...prev, newConv];
        console.log('💾 Created conversation with initial message, total conversations:', updated.length);
        return updated;
      });
      
      setCurrentConversationId(id);
      setMessages([userMessage]); // Set local messages directly
      activeConversationId = id;
    } else {
      // Existing conversation - just add the message
      console.log('💬 Adding message to existing conversation:', activeConversationId);
      
      setConversations(prev => {
        const updated = prev.map(conv => {
          if (conv.id === activeConversationId) {
            // Update title if this is the first message
            const shouldUpdateTitle = conv.messages.length === 0 && userMessage.role === 'user';
            const newTitle = shouldUpdateTitle 
              ? userMessage.content.slice(0, 50) 
              : conv.title;
            
            const updatedConv = {
              ...conv,
              title: newTitle,
              updatedAt: new Date(),
              messages: [...conv.messages, userMessage],
            };
            console.log('📝 Added user message to conversation, now has:', updatedConv.messages.length, 'messages');
            return updatedConv;
          }
          return conv;
        });
        return updated;
      });
      
      setMessages(prev => [...prev, userMessage]);
    }
    
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: messageText,
        conversation_id: activeConversationId || undefined,
      });

      const data = response.data;

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        timestamp: new Date(),
        language: data.language,
        confidence: data.confidence,
        response_type: data.response_type || 'text',
        data: data.data || null,
      };

      // Add assistant response atomically
      setConversations(prev => {
        const updated = prev.map(conv => {
          if (conv.id === activeConversationId) {
            const updatedConv = {
              ...conv,
              updatedAt: new Date(),
              messages: [...conv.messages, assistantMessage],
            };
            console.log('📥 Added assistant response, conversation now has:', updatedConv.messages.length, 'messages');
            return updatedConv;
          }
          return conv;
        });
        return updated;
      });
      
      setMessages(prev => [...prev, assistantMessage]);
      
      if (!currentConversationId && data.conversation_id) {
        setCurrentConversationId(data.conversation_id);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: language === 'en' 
          ? 'Server error, please try again.' 
          : 'خطأ في الخادم، يرجى المحاولة مرة أخرى.',
        timestamp: new Date(),
      };
      
      setConversations(prev => {
        const updated = prev.map(conv => {
          if (conv.id === activeConversationId) {
            return {
              ...conv,
              updatedAt: new Date(),
              messages: [...conv.messages, errorMessage],
            };
          }
          return conv;
        });
        return updated;
      });
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // ========== VOICE FEATURES ==========
  
  // Initialize speech recognition and synthesis
  useEffect(() => {
    // Initialize SpeechRecognition
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
    }
    
    // Initialize SpeechSynthesis
    synthRef.current = window.speechSynthesis;
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
      if (synthRef.current) {
        synthRef.current.cancel();
      }
    };
  }, []);
  
  // Dictate Mode - Speech to Text for input field
  const toggleDictation = () => {
    if (!recognitionRef.current) {
      alert(language === 'en' 
        ? '⚠️ Speech recognition not supported. Please use Chrome or Edge.' 
        : '⚠️ التعرف الصوتي غير مدعوم. يرجى استخدام Chrome أو Edge.');
      return;
    }
    
    if (isDictating) {
      // Stop dictation
      recognitionRef.current.stop();
      setIsDictating(false);
    } else {
      // Start dictation
      recognitionRef.current.lang = language === 'en' ? 'en-US' : 'ar-AE';
      recognitionRef.current.start();
      setIsDictating(true);
      
      recognitionRef.current.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0].transcript)
          .join('');
        
        setInput(transcript);
        setVoiceTranscript(transcript);
      };
      
      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsDictating(false);
        if (event.error === 'no-speech') {
          alert(language === 'en'
            ? 'No speech detected. Please try again.'
            : 'لم يتم اكتشاف صوت. يرجى المحاولة مرة أخرى.');
        }
      };
      
      recognitionRef.current.onend = () => {
        setIsDictating(false);
      };
    }
  };
  
  // Voice Mode - Full-screen hands-free chat
  const openVoiceMode = () => {
    setIsVoiceModeOpen(true);
    setVoiceModeState('listening');
    startVoiceListening();
  };
  
  const closeVoiceMode = () => {
    setIsVoiceModeOpen(false);
    stopVoiceListening();
    if (synthRef.current) {
      synthRef.current.cancel();
    }
    setVoiceModeState('idle');
    setVoiceMuted(false);
  };
  
  const startVoiceListening = () => {
    if (!recognitionRef.current) return;
    
    try {
      recognitionRef.current.lang = language === 'en' ? 'en-US' : 'ar-AE';
      recognitionRef.current.start();
      setVoiceModeState('listening');
      
      recognitionRef.current.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0].transcript)
          .join('');
        
        setVoiceTranscript(transcript);
        
        // If final result, send to AI
        if (event.results[0].isFinal) {
          handleVoiceInput(transcript);
        }
      };
      
      recognitionRef.current.onerror = (event: any) => {
        console.error('Voice mode recognition error:', event.error);
        if (event.error !== 'aborted') {
          setVoiceModeState('idle');
        }
      };
    } catch (error) {
      console.error('Failed to start voice listening:', error);
    }
  };
  
  const stopVoiceListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (error) {
        // Already stopped
      }
    }
  };
  
  const handleVoiceInput = async (transcript: string) => {
    if (!transcript.trim()) return;
    
    stopVoiceListening();
    setVoiceModeState('processing');
    
    try {
      // Use the same sendMessage function as text chat
      await sendMessageToAPI(transcript);
    } catch (error) {
      console.error('Voice input error:', error);
      setVoiceModeState('idle');
    }
  };
  
  const sendMessageToAPI = async (messageText: string) => {
    if (!messageText.trim()) return;
    
    setIsLoading(true);
    setVoiceModeState('processing');
    
    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: messageText,
        conversation_id: currentConversationId || undefined,
        language: language,
      });
      
      const data = response.data;
      
      // Create user message
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: messageText,
        timestamp: new Date(),
      };
      
      // Create AI message
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        timestamp: new Date(),
        language: data.language,
        confidence: data.confidence,
        response_type: data.response_type || 'text',
        data: data.data,
      };
      
      // CRITICAL FIX: Update BOTH conversations and messages states
      // Update conversations state (for persistence)
      setConversations(prev => {
        if (!currentConversationId) {
          // Create new conversation if none exists
          const id = generateId();
          const title = messageText.slice(0, 50);
          const newConv: Conversation = {
            id,
            title,
            createdAt: new Date(),
            updatedAt: new Date(),
            messages: [userMessage, aiMessage],
          };
          setCurrentConversationId(id);
          console.log('🎙️ Voice mode: Created new conversation:', id);
          return [...prev, newConv];
        } else {
          // Add to existing conversation
          const updated = prev.map(conv => {
            if (conv.id === currentConversationId) {
              return {
                ...conv,
                updatedAt: new Date(),
                messages: [...conv.messages, userMessage, aiMessage],
              };
            }
            return conv;
          });
          console.log('🎙️ Voice mode: Added messages to conversation:', currentConversationId);
          return updated;
        }
      });
      
      // Update messages state (for display)
      setMessages(prev => [...prev, userMessage, aiMessage]);
      setLastAiResponse(data.answer);
      
      // Speak the response
      speakResponse(data.answer);
    } catch (error) {
      console.error('API error:', error);
      setVoiceModeState('idle');
    } finally {
      setIsLoading(false);
    }
  };
  
  const speakResponse = (text: string) => {
    if (!synthRef.current || voiceMuted) {
      setTimeout(() => {
        setVoiceModeState('idle');
        setTimeout(startVoiceListening, 700);
      }, 700);
      return;
    }
    
    // Cancel any ongoing speech
    synthRef.current.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === 'en' ? 'en-US' : 'ar-SA';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    
    // Select appropriate voice
    const voices = synthRef.current.getVoices();
    const preferredVoice = voices.find(voice => 
      language === 'en' 
        ? voice.lang.startsWith('en-US')
        : voice.lang.startsWith('ar')
    );
    
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }
    
    utterance.onstart = () => {
      setVoiceModeState('speaking');
    };
    
    utterance.onend = () => {
      setVoiceModeState('idle');
      // Auto-restart listening after pause
      setTimeout(startVoiceListening, 700);
    };
    
    utterance.onerror = () => {
      setVoiceModeState('idle');
      setTimeout(startVoiceListening, 700);
    };
    
    utteranceRef.current = utterance;
    synthRef.current.speak(utterance);
  };
  
  const toggleVoiceMute = () => {
    setVoiceMuted(!voiceMuted);
    if (!voiceMuted && synthRef.current) {
      synthRef.current.cancel();
    }
  };
  
  const switchVoiceLanguage = () => {
    setLanguage(language === 'en' ? 'ar' : 'en');
    stopVoiceListening();
    if (synthRef.current) {
      synthRef.current.cancel();
    }
    setTimeout(() => {
      startVoiceListening();
    }, 100);
  };
  
  // ====================================

  const clearChat = () => {
    clearAllConversations();
  };

  // Toggle menu for specific chat
  const toggleMenu = (chatId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setActiveMenu(activeMenu === chatId ? null : chatId);
  };

  // Handle share chat
  const handleShare = async (chatId: string) => {
    const conversation = conversations.find(conv => conv.id === chatId);
    if (!conversation) return;
    
    // Create shareable link or show modal
    const shareUrl = `${window.location.origin}?chat=${chatId}`;
    
    try {
      await navigator.clipboard.writeText(shareUrl);
      alert(language === 'en' 
        ? 'Chat link copied to clipboard!' 
        : 'تم نسخ رابط المحادثة إلى الحافظة!');
    } catch (error) {
      console.error('Failed to copy:', error);
    }
    
    setActiveMenu(null);
  };

  // Handle rename chat
  const handleRename = (chatId: string) => {
    const conversation = conversations.find(conv => conv.id === chatId);
    if (!conversation) return;
    
    const newName = prompt(
      language === 'en' ? 'Enter new chat name:' : 'أدخل اسمًا جديدًا للمحادثة:',
      conversation.title
    );
    
    if (newName && newName.trim()) {
      setConversations(prev => prev.map(conv => 
        conv.id === chatId 
          ? { ...conv, title: newName.trim() }
          : conv
      ));
    }
    
    setActiveMenu(null);
  };

  // Handle pin/unpin chat
  const handlePin = (chatId: string) => {
    setConversations(prev => prev.map(conv => 
      conv.id === chatId 
        ? { ...conv, pinned: !conv.pinned }
        : conv
    ));
    setActiveMenu(null);
  };

  // Handle archive chat
  const handleArchive = (chatId: string) => {
    const conversation = conversations.find(conv => conv.id === chatId);
    if (!conversation) return;
    
    // Move to archived chats
    setArchivedChats(prev => [...prev, { ...conversation, archived: true }]);
    
    // Remove from active conversations
    setConversations(prev => prev.filter(conv => conv.id !== chatId));
    
    // If this was current chat, switch to another or create new
    if (currentConversationId === chatId) {
      setCurrentConversationId(null);
      setMessages([]);
    }
    
    setActiveMenu(null);
  };

  // Handle unarchive chat
  const handleUnarchive = (chatId: string) => {
    const archivedChat = archivedChats.find(conv => conv.id === chatId);
    if (!archivedChat) return;
    
    // Move back to active conversations
    setConversations(prev => [...prev, { ...archivedChat, archived: false }]);
    
    // Remove from archived chats
    setArchivedChats(prev => prev.filter(conv => conv.id !== chatId));
    
    setActiveMenu(null);
  };

  // Handle delete archived chat
  const handleDeleteArchived = (chatId: string) => {
    const confirmDelete = confirm(
      language === 'en' 
        ? 'Are you sure you want to permanently delete this archived chat?' 
        : 'هل أنت متأكد أنك تريد حذف هذه المحادثة المؤرشفة نهائيًا؟'
    );
    
    if (!confirmDelete) {
      setActiveMenu(null);
      return;
    }
    
    // Remove from archived chats
    setArchivedChats(prev => prev.filter(conv => conv.id !== chatId));
    
    setActiveMenu(null);
  };

  // Handle delete chat
  const handleDelete = (chatId: string) => {
    const confirmDelete = confirm(
      language === 'en' 
        ? 'Are you sure you want to delete this chat?' 
        : 'هل أنت متأكد أنك تريد حذف هذه المحادثة؟'
    );
    
    if (!confirmDelete) {
      setActiveMenu(null);
      return;
    }
    
    // Remove from conversations
    setConversations(prev => prev.filter(conv => conv.id !== chatId));
    
    // If this was current chat, switch to another or create new
    if (currentConversationId === chatId) {
      setCurrentConversationId(null);
      setMessages([]);
    }
    
    setActiveMenu(null);
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      console.log('🔴 Document click detected');
      console.log('🔴 Click target:', e.target);
      
      // Check if click is on the menu button or inside dropdown
      const target = e.target as HTMLElement;
      const isMenuButton = target.closest('button[title*="options"]') || 
                          target.closest('button[title*="الخيارات"]');
      const isDropdown = target.closest('.fixed.py-1.w-48');
      
      if (isMenuButton || isDropdown) {
        console.log('🟢 Click is on menu button or dropdown - ignoring');
        return;
      }
      
      console.log('🔴 Closing menu because click is outside');
      setActiveMenu(null);
    };
    
    document.addEventListener('click', handleClickOutside);
    return () => {
      console.log('🔴 Cleaning up document click listener');
      document.removeEventListener('click', handleClickOutside);
    };
  }, []);

  // Sort conversations: pinned first, then by recent
  const sortedConversations = [...conversations].sort((a, b) => {
    // Pinned chats first
    if (a.pinned && !b.pinned) return -1;
    if (!a.pinned && b.pinned) return 1;
    
    // Then by most recent
    return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
  });

  // Filter chats based on search query
  const filteredChats = searchQuery.trim() 
    ? sortedConversations.filter(chat => 
        chat.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : sortedConversations;

  const isRTL = language === 'ar';

  return (
    <div className={clsx(
      "flex h-screen w-screen transition-colors duration-300 overflow-hidden",
      theme === 'dark' ? "bg-gray-900" : "bg-gray-50"
    )}>
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className={clsx(
              "text-gray-900 overflow-hidden shadow-xl flex-shrink-0 border-r flex flex-col",
              theme === 'dark' 
                ? "bg-gradient-to-b from-blue-900 to-blue-800 text-white border-none" 
                : "bg-gradient-to-b from-white to-gray-100 text-gray-900 border-gray-200"
            )}
          >
            <div className="p-4 h-full flex flex-col w-[280px]">
              <div className="flex items-center justify-between mb-6">
                <h2 className={clsx(
                  "text-lg font-semibold flex items-center gap-2",
                  theme === 'dark' ? "text-white" : "text-gray-900"
                )}>
                  <MessageSquare className="w-5 h-5" />
                  {language === 'en' ? 'Chat History' : 'سجل المحادثات'}
                </h2>
                <button
                  onClick={() => setSidebarOpen(false)}
                  className={clsx(
                    "p-2 hover:bg-white/10 rounded-lg transition-colors",
                    theme === 'dark' ? "text-white" : "text-gray-900"
                  )}
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <button
                onClick={handleNewChat}
                className={clsx(
                  "w-full flex items-center justify-center gap-2 px-4 py-3 border-2 rounded-xl transition-all mb-4 font-medium",
                  theme === 'dark' 
                    ? "bg-white/10 hover:bg-white/20 border-white/20 text-white" 
                    : "bg-blue-600 hover:bg-blue-700 border-blue-700 text-white"
                )}
              >
                <Plus className="w-5 h-5" />
                {language === 'en' ? 'New Chat' : 'محادثة جديدة'}
              </button>

              {/* Search Input */}
              <div className="relative mb-4">
                <Search className={clsx(
                  "absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4",
                  theme === 'dark' ? "text-white/40" : "text-gray-400"
                )} />
                <input
                  type="text"
                  placeholder={language === 'en' ? 'Search chats...' : 'البحث في المحادثات...'}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className={clsx(
                    "w-full pl-10 pr-4 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 transition-all",
                    theme === 'dark' 
                      ? "bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:ring-white/30 focus:border-white/30" 
                      : "bg-gray-100 border-gray-300 text-gray-900 placeholder:text-gray-500 focus:ring-blue-500 focus:border-blue-500"
                  )}
                />
              </div>

              <div className={clsx(
                "flex-1 overflow-y-auto space-y-2 pr-2 scrollbar-thin",
                theme === 'dark' 
                  ? "bg-gradient-to-b from-blue-900 to-blue-800" 
                  : "bg-gradient-to-b from-white to-gray-100"
              )}>
                {filteredChats.length === 0 && searchQuery.trim() ? (
                  <div className="text-center py-8">
                    <p className={clsx(
                      "text-sm",
                      theme === 'dark' ? "text-white/60" : "text-gray-600"
                    )}>
                      {language === 'en' 
                        ? (filteredChats.length === 0 ? 'No chats found' : 'No conversations yet')
                        : (filteredChats.length === 0 ? 'لم يتم العثور على محادثات' : 'لا توجد محادثات بعد')}
                    </p>
                  </div>
                ) : (
                  filteredChats.map(conv => {
                    // Count ONLY user messages (not assistant responses)
                    const userMessageCount = conv.messages.filter(msg => msg.role === "user").length;
                    
                    return (
                      <div 
                        key={conv.id}
                        onClick={(e) => {
                          e.stopPropagation();
                          loadConversation(conv.id);
                        }}
                        className={clsx(
                          "relative p-3 rounded-lg transition-colors cursor-pointer group border",
                          theme === 'dark' 
                            ? "bg-white/5 hover:bg-white/10 border-white/10" 
                            : "bg-gray-100 hover:bg-gray-200 border-gray-200",
                          currentConversationId === conv.id && (
                            theme === 'dark' 
                              ? "bg-white/20 border-white/30" 
                              : "bg-blue-100 border-blue-300"
                          )
                        )}
                      >
                        {/* Chat info */}
                        <div className="pr-8">
                          <div className="flex items-center gap-2">
                            <p className={clsx(
                              "text-sm font-medium truncate flex-1",
                              theme === 'dark' ? "text-white" : "text-gray-900"
                            )}>{conv.title}</p>
                            {conv.pinned && (
                              <Pin className={clsx(
                                "w-3 h-3 flex-shrink-0",
                                theme === 'dark' ? "text-yellow-400" : "text-yellow-600"
                              )} />
                            )}
                          </div>
                          <p className={clsx(
                            "text-xs mt-1",
                            theme === 'dark' ? "text-white/60" : "text-gray-600"
                          )}>
                            {format(conv.updatedAt, 'HH:mm')}
                            {userMessageCount > 0 && (
                              <>
                                {" • "}{userMessageCount} {language === 'en' 
                                  ? (userMessageCount === 1 ? 'msg' : 'messages') 
                                  : (userMessageCount === 1 ? 'رسالة' : 'رسائل')}
                              </>
                            )}
                          </p>
                        </div>
                        
                        {/* Menu button */}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            console.log('🔵 === MENU BUTTON CLICKED ===');
                            console.log('🔵 Chat ID:', conv.id);
                            console.log('🔵 Current activeMenu:', activeMenu);
                            
                            // Calculate position before opening menu
                            if (!activeMenu || activeMenu !== conv.id) {
                              const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                              console.log('🔵 Button Rect:', rect);
                              const newPosition = { 
                                top: rect.bottom + 8, 
                                right: window.innerWidth - rect.right 
                              };
                              console.log('🔵 Calculated Position:', newPosition);
                              setMenuPosition(newPosition);
                            }
                            
                            const newMenuState = activeMenu === conv.id ? null : conv.id;
                            console.log('🔵 Setting activeMenu to:', newMenuState);
                            setActiveMenu(newMenuState);
                          }}
                          onDoubleClick={(e) => {
                            e.stopPropagation();
                            console.log('🟣 DOUBLE CLICK DETECTED - Forcing menu open');
                            const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                            setMenuPosition({ 
                              top: rect.bottom + 8, 
                              right: window.innerWidth - rect.right 
                            });
                            setActiveMenu(conv.id);
                          }}
                          className={clsx(
                            "absolute top-3 right-3 p-1.5 opacity-0 group-hover:opacity-100 rounded transition-all z-50 cursor-pointer",
                            theme === 'dark' 
                              ? "hover:bg-white/10" 
                              : "hover:bg-gray-300"
                          )}
                          title={language === 'en' ? 'More options' : 'المزيد من الخيارات'}
                          type="button"
                          style={{ cursor: 'pointer' }}
                        >
                          <MoreVertical className={clsx(
                            "w-4 h-4",
                            theme === 'dark' ? "text-white" : "text-gray-700"
                          )} />
                        </button>
                        
                        {/* Dropdown menu */}
                        {activeMenu === conv.id && menuPosition && (
                          <div 
                            className={clsx(
                              "fixed py-1 w-48 rounded-lg shadow-2xl border z-[99999]",
                              theme === 'dark' 
                                ? "bg-gray-900 border-gray-700" 
                                : "bg-white border-gray-200"
                            )}
                            style={{ 
                              position: 'fixed',
                              zIndex: 99999,
                              top: `${menuPosition.top}px`,
                              right: `${menuPosition.right}px`,
                            }}
                            onClick={(e) => {
                              e.stopPropagation();
                              console.log('✅ Dropdown clicked - preventing close');
                            }}
                            onMouseEnter={() => {
                              console.log('🟡 Mouse entered dropdown');
                            }}
                            onMouseLeave={() => {
                              console.log('🟡 Mouse left dropdown');
                            }}
                          >
                            {/* Share */}
                            <button
                              onClick={() => handleShare(conv.id)}
                              className={clsx(
                                "w-full px-4 py-2 text-left text-sm flex items-center gap-2 transition-colors",
                                theme === 'dark' 
                                  ? "hover:bg-white/10 text-white" 
                                  : "hover:bg-gray-100 text-gray-900"
                              )}
                            >
                              <Share2 className="w-4 h-4" />
                              <span>{language === 'en' ? 'Share' : 'مشاركة'}</span>
                            </button>
                            
                            {/* Rename */}
                            <button
                              onClick={() => handleRename(conv.id)}
                              className={clsx(
                                "w-full px-4 py-2 text-left text-sm flex items-center gap-2 transition-colors",
                                theme === 'dark' 
                                  ? "hover:bg-white/10 text-white" 
                                  : "hover:bg-gray-100 text-gray-900"
                              )}
                            >
                              <Edit2 className="w-4 h-4" />
                              <span>{language === 'en' ? 'Rename' : 'إعادة التسمية'}</span>
                            </button>
                            
                            {/* Pin/Unpin */}
                            <button
                              onClick={() => handlePin(conv.id)}
                              className={clsx(
                                "w-full px-4 py-2 text-left text-sm flex items-center gap-2 transition-colors",
                                theme === 'dark' 
                                  ? "hover:bg-white/10 text-white" 
                                  : "hover:bg-gray-100 text-gray-900"
                              )}
                            >
                              <Pin className="w-4 h-4" />
                              <span>{conv.pinned 
                                ? (language === 'en' ? 'Unpin' : 'إلغاء التثبيت') 
                                : (language === 'en' ? 'Pin Chat' : 'تثبيت المحادثة')}</span>
                            </button>
                            
                            {/* Archive */}
                            <button
                              onClick={() => handleArchive(conv.id)}
                              className={clsx(
                                "w-full px-4 py-2 text-left text-sm flex items-center gap-2 transition-colors",
                                theme === 'dark' 
                                  ? "hover:bg-white/10 text-white" 
                                  : "hover:bg-gray-100 text-gray-900"
                              )}
                            >
                              <Archive className="w-4 h-4" />
                              <span>{language === 'en' ? 'Archive' : 'أرشفة'}</span>
                            </button>
                            
                            {/* Divider */}
                            <div className={clsx(
                              "my-1 border-t",
                              theme === 'dark' ? "border-gray-700" : "border-gray-200"
                            )}></div>
                            
                            {/* Delete */}
                            <button
                              onClick={() => handleDelete(conv.id)}
                              className={clsx(
                                "w-full px-4 py-2 text-left text-sm flex items-center gap-2 transition-colors",
                                theme === 'dark' 
                                  ? "hover:bg-red-900/20 text-red-400" 
                                  : "hover:bg-red-100 text-red-600"
                              )}
                            >
                              <Trash2 className="w-4 h-4" />
                              <span>{language === 'en' ? 'Delete' : 'حذف'}</span>
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
              </div>

              {conversations.length > 0 && (
                <button
                  onClick={clearChat}
                  className={clsx(
                    "w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl transition-colors mt-4",
                    theme === 'dark' 
                      ? "bg-red-700 hover:bg-red-600 text-white" 
                      : "bg-red-600 hover:bg-red-700 text-white"
                  )}
                >
                  <Trash2 className="w-4 h-4" />
                  {language === 'en' ? 'Clear All' : 'مسح الكل'}
                </button>
              )}

              {/* Archived Chats Section */}
              {archivedChats.length > 0 && (
                <>
                  <div className={clsx(
                    "mt-6 mb-3 px-1",
                    theme === 'dark' ? "text-white/60" : "text-gray-600"
                  )}>
                    <h3 className={clsx(
                      "text-xs font-semibold uppercase tracking-wider",
                      theme === 'dark' ? "text-white/60" : "text-gray-500"
                    )}>
                      {language === 'en' ? 'Archived Chats' : 'المحادثات المؤرشفة'} ({archivedChats.length})
                    </h3>
                  </div>
                  
                  <div className="space-y-2">
                    {archivedChats.map(archivedChat => {
                      // Count ONLY user messages (not assistant responses)
                      const userMessageCount = archivedChat.messages.filter(msg => msg.role === "user").length;
                      
                      return (
                        <div 
                          key={archivedChat.id}
                          className={clsx(
                            "relative p-3 rounded-lg transition-colors group border",
                            theme === 'dark' 
                              ? "bg-white/5 hover:bg-white/10 border-white/10" 
                              : "bg-gray-50 hover:bg-gray-100 border-gray-200"
                          )}
                        >
                          {/* Chat info */}
                          <div className="pr-8">
                            <div className="flex items-center gap-2">
                              <p className={clsx(
                                "text-sm font-medium truncate flex-1",
                                theme === 'dark' ? "text-white/80" : "text-gray-700"
                              )}>{archivedChat.title}</p>
                              <Archive className={clsx(
                                "w-3 h-3 flex-shrink-0",
                                theme === 'dark' ? "text-white/40" : "text-gray-400"
                              )} />
                            </div>
                            <p className={clsx(
                              "text-xs mt-1",
                              theme === 'dark' ? "text-white/50" : "text-gray-500"
                            )}>
                              {format(archivedChat.updatedAt, 'HH:mm')}
                              {userMessageCount > 0 && (
                                <>
                                  {" • "}{userMessageCount} {language === 'en' 
                                    ? (userMessageCount === 1 ? 'msg' : 'messages') 
                                    : (userMessageCount === 1 ? 'رسالة' : 'رسائل')}
                                </>
                              )}
                            </p>
                          </div>
                          
                          {/* Menu button */}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                              setMenuPosition({ 
                                top: rect.bottom + 8, 
                                right: window.innerWidth - rect.right 
                              });
                              setActiveMenu(activeMenu === `archived-${archivedChat.id}` ? null : `archived-${archivedChat.id}`);
                            }}
                            className={clsx(
                              "absolute top-3 right-3 p-1.5 opacity-0 group-hover:opacity-100 rounded transition-all z-50 cursor-pointer",
                              theme === 'dark' 
                                ? "hover:bg-white/10" 
                                : "hover:bg-gray-200"
                            )}
                            title={language === 'en' ? 'More options' : 'المزيد من الخيارات'}
                            type="button"
                          >
                            <MoreVertical className={clsx(
                              "w-4 h-4",
                              theme === 'dark' ? "text-white" : "text-gray-700"
                            )} />
                          </button>
                          
                          {/* Dropdown menu for archived chat */}
                          {activeMenu === `archived-${archivedChat.id}` && menuPosition && (
                            <div 
                              className={clsx(
                                "fixed py-1 w-48 rounded-lg shadow-2xl border z-[99999]",
                                theme === 'dark' 
                                  ? "bg-gray-900 border-gray-700" 
                                  : "bg-white border-gray-200"
                              )}
                              style={{ 
                                position: 'fixed',
                                zIndex: 99999,
                                top: `${menuPosition.top}px`,
                                right: `${menuPosition.right}px`,
                              }}
                              onClick={(ev) => ev.stopPropagation()}
                            >
                              {/* Unarchive */}
                              <button
                                onClick={() => handleUnarchive(archivedChat.id)}
                                className={clsx(
                                  "w-full px-4 py-2 text-left text-sm flex items-center gap-2 transition-colors",
                                  theme === 'dark' 
                                    ? "hover:bg-white/10 text-white" 
                                    : "hover:bg-gray-100 text-gray-900"
                                )}
                              >
                                <Archive className="w-4 h-4" />
                                <span>{language === 'en' ? 'Unarchive' : 'إلغاء الأرشفة'}</span>
                              </button>
                              
                              {/* Delete Permanently */}
                              <button
                                onClick={() => handleDeleteArchived(archivedChat.id)}
                                className={clsx(
                                  "w-full px-4 py-2 text-left text-sm flex items-center gap-2 transition-colors",
                                  theme === 'dark' 
                                    ? "hover:bg-red-900/20 text-red-400" 
                                    : "hover:bg-red-100 text-red-600"
                                )}
                              >
                                <Trash2 className="w-4 h-4" />
                                <span>{language === 'en' ? 'Delete Permanently' : 'حذف نهائيًا'}</span>
                              </button>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </>
              )}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className={clsx(
          "flex items-center justify-between px-6 py-4 border-b shadow-sm",
          theme === 'dark' 
            ? "bg-gray-800 border-gray-700" 
            : "bg-white border-gray-200"
        )} suppressHydrationWarning>
          <div className="flex items-center gap-4">
            {!sidebarOpen && (
              <button
                onClick={() => setSidebarOpen(true)}
                className={clsx(
                  "p-2 rounded-lg transition-colors",
                  theme === 'dark' 
                    ? "hover:bg-gray-700 text-white" 
                    : "hover:bg-gray-100 text-gray-700"
                )}
              >
                <Menu className="w-6 h-6" />
              </button>
            )}
            
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-800 rounded-full flex items-center justify-center shadow-lg">
                <Building className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className={clsx(
                  "text-xl font-bold",
                  theme === 'dark' ? "text-white" : "text-gray-900"
                )}>
                  {language === 'en' ? 'AI Banking Assistant' : 'المساعد المصرفي الذكي'}
                </h1>
                <p className={clsx(
                  "text-sm",
                  theme === 'dark' ? "text-gray-400" : "text-gray-500"
                )}>
                  {language === 'en' ? 'UAE Bank Customer Support' : 'دعم عملاء البنك الإماراتي'}
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setLanguage(language === 'en' ? 'ar' : 'en')}
              className={clsx(
                "px-4 py-2 rounded-lg transition-colors font-medium flex items-center gap-2",
                theme === 'dark' 
                  ? "bg-blue-900 text-blue-300 hover:bg-blue-800" 
                  : "bg-blue-100 text-blue-700 hover:bg-blue-200"
              )}
            >
              <Languages className="w-4 h-4" />
              {language === 'en' ? 'العربية' : 'English'}
            </button>
            
            <button
              onClick={() => {
                console.log('🔘 Toggle button clicked!');
                console.log('🔘 Current theme:', theme);
                toggleTheme();
              }}
              className={clsx(
                "p-2 rounded-lg transition-colors",
                theme === 'dark' 
                  ? "hover:bg-gray-700" 
                  : "hover:bg-gray-100"
              )}
              title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {theme === 'dark' ? (
                <Sun className="w-6 h-6 text-yellow-500" />
              ) : (
                <Moon className="w-6 h-6 text-gray-700" />
              )}
            </button>
          </div>
        </header>

        {/* Messages Container */}
        <div className={clsx(
          "flex-1 overflow-y-auto p-6 transition-colors duration-300",
          theme === 'dark' 
            ? "bg-gradient-to-b from-gray-900 to-gray-800" 
            : "bg-gradient-to-b from-gray-50 to-white"
        )}>
          {messages.length === 0 ? (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="max-w-4xl mx-auto mt-12"
            >
              <div className="text-center mb-8">
                <h2 className={clsx(
                  "text-3xl font-bold mb-2",
                  theme === 'dark' ? "text-white" : "text-gray-900"
                )}>
                  {language === 'en' 
                    ? 'Welcome to AI Banking Assistant' 
                    : 'مرحباً بك في المساعد المصرفي الذكي'}
                </h2>
                <p className={clsx(
                  "text-lg",
                  theme === 'dark' ? "text-gray-400" : "text-gray-600"
                )}>
                  {language === 'en'
                    ? 'How can I help you today?'
                    : 'كيف يمكنني مساعدتك اليوم؟'}
                </p>
              </div>

              {/* Quick Actions */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-8">
                {quickActions.map((action, index) => (
                  <motion.button
                    key={index}
                    onClick={() => sendMessage(action.query)}
                    whileHover={{ scale: 1.05, y: -5 }}
                    whileTap={{ scale: 0.95 }}
                    className={clsx(
                      "p-4 rounded-xl border-2 hover:shadow-lg transition-all",
                      theme === 'dark' 
                        ? "bg-gray-700 border-gray-600 hover:border-blue-400" 
                        : "bg-white border-gray-200 hover:border-blue-500"
                    )}
                  >
                    <action.icon className={clsx(
                      "w-8 h-8 mx-auto mb-2",
                      theme === 'dark' ? "text-blue-400" : "text-blue-600"
                    )} />
                    <span className={clsx(
                      "text-sm font-medium block text-center",
                      theme === 'dark' ? "text-white" : "text-gray-900"
                    )}>
                      {action.label}
                    </span>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          ) : (
            <div key={currentConversationId || 'empty'} className="max-w-4xl mx-auto space-y-4">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={clsx(
                    "flex gap-3",
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {message.role === 'assistant' && (
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
                      <Bot className="w-6 h-6 text-white" />
                    </div>
                  )}
                  
                  <div className={clsx("max-w-2xl", message.role === 'user' ? 'order-first' : '')}>
                    {message.role === 'assistant' && message.response_type !== 'text' && message.data ? (
                      // Render structured component
                      <StructuredMessage 
                        type={message.response_type!} 
                        data={message.data} 
                        language={language} 
                      />
                    ) : (
                      // Render simple text bubble
                      <motion.div
                        initial={{ scale: 0.9 }}
                        animate={{ scale: 1 }}
                        className={clsx(
                          "px-4 py-3 rounded-2xl shadow-md",
                          message.role === 'user'
                            ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-br-sm'
                            : theme === 'dark'
                              ? 'bg-gray-700 text-white rounded-bl-sm'
                              : 'bg-gray-100 text-gray-900 rounded-bl-sm'
                        )}
                      >
                        {/* Render ALL lines of response - CRITICAL FIX */}
                        <div className="space-y-2">
                          {message.content.split('\n').map((line: string, index: number) => (
                            <p key={index} className="whitespace-pre-wrap leading-relaxed">
                              {line}
                            </p>
                          ))}
                        </div>
                      </motion.div>
                    )}
                    
                    <div className={clsx("flex items-center gap-2 mt-1", message.role === 'user' ? 'justify-end' : '')}>
                      <span className={clsx(
                        "text-xs",
                        theme === 'dark' ? "text-gray-400" : "text-gray-500"
                      )}>
                        {format(message.timestamp, 'HH:mm')}
                      </span>
                      {message.language && (
                        <span className={clsx(
                          "text-xs px-2 py-0.5 rounded-full font-medium",
                          message.language.toLowerCase() === 'arabic'
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                            : 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
                        )}>
                          {message.language}
                        </span>
                      )}
                    </div>
                  </div>

                  {message.role === 'user' && (
                    <div className="w-10 h-10 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0">
                      <User className="w-6 h-6 text-gray-700 dark:text-gray-300" />
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          )}

          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3 justify-start max-w-4xl mx-auto"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-full flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div className="bg-gray-100 dark:bg-gray-700 px-4 py-3 rounded-2xl rounded-bl-sm">
                <div className="flex gap-1">
                  {[0, 1, 2].map((i) => (
                    <motion.div
                      key={i}
                      className={clsx(
                        "w-2 h-2 rounded-full",
                        theme === 'dark' ? "bg-blue-400" : "bg-blue-600"
                      )}
                      animate={{ y: [-5, 0, -5] }}
                      transition={{
                        duration: 0.6,
                        repeat: Infinity,
                        delay: i * 0.15,
                      }}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className={clsx(
          "border-t p-4",
          theme === 'dark' 
            ? "bg-gray-800 border-gray-700" 
            : "bg-white border-gray-200"
        )}>
          <div className="max-w-4xl mx-auto">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                sendMessage(input);
              }}
              className="flex gap-2"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={language === 'en' 
                  ? (isMobile ? 'Ask a question...' : 'Ask about accounts, cards, or loans...') 
                  : (isMobile ? 'اسأل عن شيء...' : 'اسأل عن الحسابات أو البطاقات أو القروض...')}
                disabled={isLoading}
                className={clsx(
                  "flex-1 px-4 py-3 border-2 rounded-xl focus:ring-0 transition-all",
                  isRTL ? 'text-right' : 'text-left',
                  theme === 'dark' 
                    ? "bg-gray-700 border-transparent focus:border-blue-500 focus:bg-gray-600 text-white placeholder-gray-400" 
                    : "bg-gray-100 border-transparent focus:border-blue-500 focus:bg-white text-gray-900 placeholder-gray-500"
                )}
                dir={isRTL ? 'rtl' : 'ltr'}
              />
              
              {/* Dictate Button */}
              <motion.button
                type="button"
                onClick={toggleDictation}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={clsx(
                  "relative px-4 py-3 rounded-xl transition-all flex items-center justify-center shadow-lg",
                  isDictating
                    ? "bg-red-600 hover:bg-red-700 text-white animate-pulse"
                    : theme === 'dark'
                      ? "bg-gray-700 hover:bg-gray-600 text-gray-300"
                      : "bg-gray-200 hover:bg-gray-300 text-gray-700"
                )}
                title={language === 'en' ? 'Dictate (Speech-to-Text)' : 'إملاء (تحويل الصوت إلى نص)'}
              >
                <Mic className="w-5 h-5" />
                {isDictating && (
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-400 rounded-full animate-ping" />
                )}
              </motion.button>
              
              {/* Voice Mode Button */}
              <motion.button
                type="button"
                onClick={openVoiceMode}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={clsx(
                  "px-4 py-3 rounded-xl transition-all flex items-center gap-2 shadow-lg",
                  theme === 'dark'
                    ? "bg-blue-900 hover:bg-blue-800 text-blue-300"
                    : "bg-blue-100 hover:bg-blue-200 text-blue-700"
                )}
                title={language === 'en' ? 'Voice Mode (Hands-free)' : 'وضع الصوت (بدون استخدام اليدين)'}
              >
                <Volume2 className="w-5 h-5" />
                <span className="hidden sm:inline">{language === 'en' ? 'Voice' : 'صوت'}</span>
              </motion.button>
              
              <motion.button
                type="submit"
                disabled={isLoading || !input.trim()}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-500 text-white rounded-xl font-medium transition-all flex items-center gap-2 shadow-lg disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
                <span className="hidden sm:inline">{language === 'en' ? 'Send' : 'إرسال'}</span>
              </motion.button>
            </form>
            
            <p className={clsx(
              "text-xs text-center mt-2",
              theme === 'dark' ? "text-gray-400" : "text-gray-500"
            )}>
              {language === 'en' 
                ? 'AI-powered banking assistant. For emergencies, call 800-BANK.' 
                : 'مساعد مصرفي مدعوم بالذكاء الاصطناعي. للطوارئ، اتصل بـ 800-BANK'}
            </p>
          </div>
        </div>
      </div>

      {/* Voice Mode Overlay */}
      <AnimatePresence>
        {isVoiceModeOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[9999] flex items-center justify-center"
            style={{
              background: 'rgba(4,10,20,0.85)',
              backdropFilter: 'blur(12px)',
            }}
            onClick={closeVoiceMode}
          >
            <div 
              className="flex flex-col items-center gap-8 max-w-2xl w-full px-8"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Animated Orb */}
              <div className="relative">
                {/* Orb container */}
                <div className={clsx(
                  "w-32 h-32 rounded-full relative transition-all duration-500",
                  voiceModeState === 'listening' && "orb-pulsing",
                  voiceModeState === 'processing' && "orb-processing",
                  voiceModeState === 'speaking' && "orb-speaking"
                )}>
                  {/* Core orb */}
                  <div className={clsx(
                    "absolute inset-0 rounded-full transition-all duration-500",
                    voiceModeState === 'idle' && "bg-gray-600 opacity-50",
                    voiceModeState === 'listening' && "bg-blue-500 shadow-[0_0_60px_rgba(59,130,246,0.6)]",
                    voiceModeState === 'processing' && "bg-purple-500 shadow-[0_0_60px_rgba(168,85,247,0.6)]",
                    voiceModeState === 'speaking' && "bg-green-500 shadow-[0_0_60px_rgba(34,197,94,0.6)]"
                  )} />
                  
                  {/* Sound wave rings - listening state */}
                  {voiceModeState === 'listening' && (
                    <>
                      <div className="absolute inset-0 rounded-full border-2 border-blue-400 opacity-30 animate-ping" />
                      <div className="absolute inset-0 rounded-full border-4 border-blue-400 opacity-20 animate-ping animation-delay-200" />
                      <div className="absolute inset-0 rounded-full border-6 border-blue-400 opacity-10 animate-ping animation-delay-400" />
                    </>
                  )}
                  
                  {/* Processing animation */}
                  {voiceModeState === 'processing' && (
                    <div className="absolute inset-0 rounded-full border-4 border-t-white border-r-transparent border-b-purple-300 border-l-transparent animate-spin" />
                  )}
                  
                  {/* Speaking pulse */}
                  {voiceModeState === 'speaking' && (
                    <div className="absolute inset-0 rounded-full bg-green-400 opacity-30 animate-pulse" />
                  )}
                </div>
              </div>
              
              {/* State Label */}
              <div className="text-center">
                <p className="text-2xl font-semibold text-white mb-2">
                  {voiceModeState === 'idle' && (language === 'en' ? 'Tap orb to speak' : 'اضغط للتحدث')}
                  {voiceModeState === 'listening' && (language === 'en' ? 'Listening…' : 'أستمع…')}
                  {voiceModeState === 'processing' && (language === 'en' ? 'Processing…' : 'معالجة…')}
                  {voiceModeState === 'speaking' && (language === 'en' ? 'Speaking…' : 'أتحدث…')}
                </p>
                
                {/* Transcript display */}
                {voiceTranscript && (
                  <p className="text-gray-300 text-sm max-w-md mx-auto mb-4">
                    "{voiceTranscript}"
                  </p>
                )}
                
                {/* Last AI response */}
                {lastAiResponse && (
                  <p className="text-blue-300 text-sm max-w-md mx-auto italic">
                    AI: {lastAiResponse.slice(0, 150)}{lastAiResponse.length > 150 ? '...' : ''}
                  </p>
                )}
              </div>
              
              {/* Control Buttons */}
              <div className="flex gap-4 mt-8">
                {/* Mute Toggle */}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={toggleVoiceMute}
                  className={clsx(
                    "px-6 py-3 rounded-full flex items-center gap-2 font-medium transition-all",
                    voiceMuted
                      ? "bg-red-600 text-white hover:bg-red-700"
                      : theme === 'dark'
                        ? "bg-gray-700 text-white hover:bg-gray-600"
                        : "bg-gray-200 text-gray-900 hover:bg-gray-300"
                  )}
                >
                  <Volume2 className={clsx("w-5 h-5", voiceMuted && "line-through")} />
                  {voiceMuted ? (language === 'en' ? 'Unmute' : 'كتم الصوت') : (language === 'en' ? 'Mute' : 'كتم')}
                </motion.button>
                
                {/* Language Switch */}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={switchVoiceLanguage}
                  className={clsx(
                    "px-6 py-3 rounded-full flex items-center gap-2 font-medium transition-all",
                    theme === 'dark'
                      ? "bg-blue-900 text-blue-300 hover:bg-blue-800"
                      : "bg-blue-100 text-blue-700 hover:bg-blue-200"
                  )}
                >
                  <Globe className="w-5 h-5" />
                  {language === 'en' ? 'العربية' : 'English'}
                </motion.button>
                
                {/* End Call */}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={closeVoiceMode}
                  className="px-6 py-3 rounded-full bg-red-600 hover:bg-red-700 text-white flex items-center gap-2 font-medium transition-all"
                >
                  <PhoneOff className="w-5 h-5" />
                  {language === 'en' ? 'End' : 'إنهاء'}
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
