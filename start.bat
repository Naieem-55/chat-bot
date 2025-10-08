@echo off
cls
echo ====================================
echo RAG Customer Support Chatbot
echo Advanced AI with Query Reformulation
echo ====================================
echo.

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please create a .env file from .env.example and add your ANTHROPIC_API_KEY
    echo.
    echo Run: copy .env.example .env
    echo Then edit .env to add your API key
    pause
    exit /b 1
)

REM Check if vector store exists
if not exist data\vector_store\index.faiss (
    echo [INFO] Vector store not found. Running data ingestion...
    echo.
    python scripts\ingest_data.py
    if errorlevel 1 (
        echo [ERROR] Data ingestion failed!
        pause
        exit /b 1
    )
    echo.
    echo [SUCCESS] Data ingestion completed!
    echo.
)

REM Start the backend server
echo [INFO] Starting backend server on http://localhost:8000
echo.
start "Chatbot Backend" cmd /k python run_server.py

REM Wait a moment for the server to start
timeout /t 5 /nobreak >nul

REM Start the frontend server
echo [INFO] Starting frontend server on http://localhost:3001
echo.
cd frontend
start "Chatbot Frontend" cmd /k python -m http.server 3001

cd ..

echo.
echo ====================================
echo Chatbot is now running!
echo ====================================
echo.
echo Features Enabled:
echo   - Llama 3.3 70B (Best Quality LLM)
echo   - BGE Embeddings (768D Vectors)
echo   - Query Reformulation
echo   - Hallucination Detection
echo   - Real-time Feedback
echo   - Analytics Dashboard
echo.
echo Access Points:
echo   Backend:   http://localhost:8000
echo   Frontend:  http://localhost:3001
echo   API Docs:  http://localhost:8000/docs
echo   Analytics: http://localhost:3001/analytics.html
echo.
echo Open http://localhost:3001 in your browser
echo.
echo Press Ctrl+C in each terminal window to stop the servers
echo ====================================
