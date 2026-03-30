@echo off
echo ========================================
echo AI Customer Support Chatbot Setup
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo [!] .env file not found!
    echo [*] Copying .env.example to .env
    copy .env.example .env
    echo.
    echo [!] IMPORTANT: Edit .env and add your GOOGLE_API_KEY
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo [*] Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo [*] Installing Python dependencies...
pip install -r requirements.txt
echo.

REM Initialize vector store
echo [*] Initializing vector store with FAQ documents...
python initialize_vectorstore.py
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the chatbot:
echo   Backend:  uvicorn backend.main:app --reload
echo   Frontend: streamlit run frontend\streamlit_app.py
echo.
pause
