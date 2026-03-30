#!/bin/bash

echo "========================================"
echo "AI Customer Support Chatbot Setup"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "[!] .env file not found!"
    echo "[*] Copying .env.example to .env"
    cp .env.example .env
    echo ""
    echo "[!] IMPORTANT: Edit .env and add your GOOGLE_API_KEY"
    echo ""
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "[*] Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "[*] Installing Python dependencies..."
pip install -r requirements.txt
echo ""

# Initialize vector store
echo "[*] Initializing vector store with FAQ documents..."
python initialize_vectorstore.py
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To start the chatbot:"
echo "  Backend:  uvicorn backend.main:app --reload"
echo "  Frontend: streamlit run frontend/streamlit_app.py"
echo ""
