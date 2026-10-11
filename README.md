# 🏦 Banking AI Customer Support Chatbot

A production-ready, intelligent banking customer support chatbot with advanced RAG (Retrieval-Augmented Generation), intent detection, tool integration, and bilingual support (English & Arabic).

## 🌟 Key Features

### Core Capabilities
- ✅ **Intent Detection** - Automatically identifies user intent (13+ banking intents)
- ✅ **Tool System** - Executable banking tools for common tasks
- ✅ **RAG Knowledge Base** - FAQ-based responses with vector search
- ✅ **Hybrid Responses** - Combines FAQ + General Knowledge intelligently
- ✅ **Hallucination Prevention** - Guardrails to avoid incorrect information
- ✅ **Escalation System** - Routes complex queries to human support
- ✅ **Conversation Memory** - Remembers context across multiple turns
- ✅ **Bilingual Support** - English and Arabic language detection
- ✅ **Analytics Dashboard** - Real-time insights and metrics

### Technical Highlights
- **Intent-Aware Routing** - Classifies queries before responding
- **Confidence Scoring** - Knows when it's uncertain
- **Multi-Modal Responses** - Tools, FAQs, or general knowledge
- **Response Time Tracking** - Performance monitoring built-in
- **Failed Query Analysis** - Identifies knowledge gaps

## 📋 Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Features Guide](#features-guide)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## 🏗️ Architecture

```
User Interface (Next.js Chat UI)
         ↓
FastAPI Backend
         ↓
Intent Detection Layer → Tool System
         ↓
RAG Pipeline
    ├─ Language Detection
    ├─ Vector Search (FAISS)
    ├─ Embedding Service (Sentence Transformers)
    └─ LLM (Groq)
         ↓
Analytics Tracker
```

### Components

1. **Intent Detector** (`backend/intent_detection.py`)
   - Rule-based intent classification
   - 13 banking-specific intents
   - Escalation keyword detection

2. **Tool System** (`backend/tools.py`)
   - Executable banking functions
   - Structured responses for common tasks
   - 6 built-in tools

3. **RAG Pipeline** (`backend/rag_pipeline.py`)
   - Enhanced with intent integration
   - Hallucination detection
   - Confidence-based routing


## 📦 Installation

### Prerequisites
- Python 3.10+
- Groq API key (free tier available at https://console.groq.com)
- Node.js 20+ and npm (for Next.js frontend)
- Git (for cloning)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd "AI Customer Support Chatbot (Arabic + English)"
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy example environment file
copy .env.example .env  # Windows
cp .env.example .env  # Linux/Mac

# Edit .env and add your Groq API key
GROQ_API_KEY=your_groq_api_key_here
```

### Step 5: Initialize Vector Database
```bash
python initialize_vectorstore.py
```

### Step 6: Install Frontend Dependencies (Next.js Chat UI)
The frontend chat interface is built with Next.js and requires Node.js dependencies to be installed.

**For Windows:**
```bash
# Navigate to the frontend chat-ui directory
cd frontend\chat-ui

# Install all required dependencies
npm install
```

**For Linux/Mac:**
```bash
# Navigate to the frontend chat-ui directory
cd frontend/chat-ui

# Install all required dependencies
npm install
```

**What gets installed:**
- Next.js 16.1.7 framework
- React 19.2.3
- TypeScript support
- Tailwind CSS for styling
- Additional UI libraries (framer-motion, lucide-react, axios, etc.)

**Important Notes:**
- Make sure you're in the `frontend/chat-ui` directory, NOT just the `frontend` directory
- The installation may take 1-2 minutes depending on your internet connection
- If you see warnings about vulnerabilities, they are non-critical dev dependencies
- After installation, you can verify by checking the `node_modules` folder exists

## 🚀 Quick Start

### Start Backend Server
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will start on: `http://localhost:8000`

### Start Next.js Chat Interface
**First-Time Setup:**
Before running the frontend for the first time, ensure dependencies are installed:
```bash
cd frontend/chat-ui
npm install  # Only needed once
```

**Start Development Server:**
```bash
cd frontend/chat-ui
npm run dev
```

Chat interface will open at: `http://localhost:3000`

**Troubleshooting Frontend Issues:**

If you get `'next' is not recognized` error:
```bash
# Make sure you're in the correct directory
cd frontend/chat-ui

# Reinstall dependencies if needed
npm install

# Then start the server
npm run dev
```

If you get `Missing script: "dev"` error:
- Verify you're in `frontend/chat-ui` directory (not just `frontend`)
- Check that `package.json` exists in the current directory
- Run `npm install` to ensure all dependencies are installed

## 🔌 API Endpoints

### Chat Endpoints

#### POST /chat
Main chat endpoint with intent detection and analytics.

**Request:**
```json
{
  "message": "How do I open a bank account?",
  "conversation_id": "optional-uuid"
}
```

**Response:**
```json
{
  "answer": "You can open an account online...",
  "language": "English",
  "confidence": 0.92,
  "conversation_id": "uuid-here",
  "fallback": false,
  "intent": "account_opening"
}
```

#### POST /intent/detect
Detect intent from a message.

**Request:**
```json
{
  "message": "I lost my debit card"
}
```

**Response:**
```json
{
  "intent": "card_block",
  "intent_description": "Card Blocking Request",
  "confidence": 0.85,
  "matched_keywords": ["lost card"],
  "needs_escalation": false
}
```


### Utility Endpoints

#### GET /health
Health check endpoint.

#### GET /conversations/count
Get number of active conversations.

#### POST /chat/reset/{conversation_id}
Reset conversation history.

#### DELETE /chat/{conversation_id}
Delete entire conversation.

## 🎯 Features Guide

### Supported Intents

| Intent | Description | Example Queries |
|--------|-------------|----------------|
| `account_opening` | Opening new accounts | "How to open account?", "I want new account" |
| `card_block` | Blocking lost/stolen cards | "Lost my card", "Card stolen" |
| `balance_check` | Checking account balance | "Check balance", "How much money?" |
| `loan_information` | Loan products info | "Personal loan rates", "Home loan eligibility" |
| `online_banking` | Digital banking support | "Forgot password", "Login issue" |
| `atm_services` | ATM-related queries | "ATM withdrawal limit", "Cash deposit" |
| `money_transfer` | Transfer services | "Send money abroad", "Wire transfer" |
| `credit_card` | Credit card services | "Apply credit card", "Credit limit" |
| `pin_reset` | PIN reset assistance | "Forgot PIN", "Change PIN" |
| `fraud_report` | Fraud reporting | "Unauthorized transaction", "Scam" |
| `working_hours` | Branch timing info | "When are you open?", "Bank hours" |
| `account_balance` | Account balance inquiry | "My balance", "Account funds" |
| `general_banking_question` | General inquiries | "What services do you offer?" |

### Built-in Tools

1. **block_card** - Immediate card blocking instructions
2. **check_balance** - Balance checking methods
3. **loan_information** - Loan product details
4. **open_account_steps** - Account opening guide
5. **reset_pin_guide** - PIN reset instructions
6. **transfer_money_guide** - Money transfer process

### Response Modes

The chatbot uses different response strategies:

1. **FAQ Mode** (High confidence ≥ 0.5)
   - Uses retrieved FAQ content
   - Highest accuracy
   - Source documents included

2. **Tool Mode** (Specific intents detected)
   - Executes banking tools
   - Structured step-by-step guidance
   - Confidence: 0.85

3. **General Knowledge Mode** (Low confidence)
   - Uses LLM general knowledge
   - Banking context maintained
   - Marked as fallback

4. **Escalation Mode** (Complex queries)
   - Routes to human support
   - Provides contact information
   - Confidence: 1.0

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional - Backend Configuration
LOG_LEVEL=INFO
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
SIMILARITY_THRESHOLD=0.5
VECTOR_DB_PATH=./vector_db
LLM_MODEL=openai/gpt-oss-20b

# Optional - Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Tuning Parameters

**Similarity Threshold** (`SIMILARITY_THRESHOLD`)
- Range: 0.0 to 1.0
- Default: 0.5
- Higher = more strict FAQ matching
- Lower = more general knowledge usage

**Chunk Size** (`CHUNK_SIZE`)
- Default: 1000 characters
- Larger chunks = more context but slower
- Smaller chunks = faster but less context

**Chunk Overlap** (`CHUNK_OVERLAP`)
- Default: 200 characters
- Ensures continuity between chunks



## 🐳 Deployment

### Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t banking-chatbot .

# Run container
docker run -p 8000:8000 -p 3000:3000 -e GROQ_API_KEY=your_key banking-chatbot
```

### Production Checklist

- [ ] Set strong API keys
- [ ] Configure CORS origins
- [ ] Enable HTTPS
- [ ] Set up logging
- [ ] Configure backup for vector DB
- [ ] Monitor rate limits
- [ ] Set up error alerting
- [ ] Regular FAQ updates

### Scaling Considerations

**Horizontal Scaling:**
- Use Redis for conversation memory
- Load balance multiple backend instances
- Shared vector database storage

**Performance Optimization:**
- Enable response caching
- Use CDN for static assets
- Implement request queuing
- Monitor memory usage

## 🔧 Troubleshooting

### Common Issues

**Issue: "No vector index found"**
```bash
# Solution: Initialize vector store
python initialize_vectorstore.py
```

**Issue: "Groq API key not found"**
```bash
# Solution: Check .env file
echo $GROQ_API_KEY  # Should show your key
# Verify API key is valid at https://console.groq.com
```

**Issue: "Module not found errors"**
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Issue: "Low confidence responses"**
- Add more FAQ entries
- Adjust `SIMILARITY_THRESHOLD` lower
- Review failed queries in analytics

**Issue: "Hallucinated responses"**
- Increase `SIMILARITY_THRESHOLD`
- Add more specific FAQ content
- Review hallucination detection logic

### Debugging Mode

Enable verbose logging:

```bash
# In .env file
LOG_LEVEL=DEBUG
```

View detailed logs:

```bash
# Backend logs
tail -f logs/backend.log

# Conversation logs
cat logs/conversation_logs.json
```

### Getting Help

1. Check existing issues in repository
2. Review analytics dashboard for patterns
3. Enable DEBUG logging
4. Test with `/intent/detect` endpoint

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests if applicable
4. Submit pull request

## 📧 Support

### Getting Help
For questions or issues:
- Check documentation above
- 📧 **Email**: vishwanathamrish@gmail.com


---

**Built with ❤️ using FastAPI, LangChain, Groq LLM, FAISS, and Next.js 16**

*Production-ready Banking AI Customer Support Chatbot*

---

## 🔗 Additional Resources

- **Groq Console**: https://console.groq.com
- **Groq Documentation**: https://console.groq.com/docs
- **Next.js Documentation**: https://nextjs.org/docs
- **FAISS**: https://faiss.ai
- **LangChain**: https://python.langchain.com
