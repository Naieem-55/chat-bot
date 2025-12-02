@echo off
cls
echo ====================================
echo RAG Chatbot - Clean Start
echo ====================================
echo.

REM Kill any existing servers
echo [1/4] Killing existing servers...
taskkill /F /IM python.exe 2>nul >nul
timeout /t 2 /nobreak >nul
echo    Done!
echo.

REM Check vector store
echo [2/4] Checking vector store...
if not exist data\vector_store\index.faiss (
    echo    Vector store not found! Run: py scripts\ingest_data.py
    pause
    exit /b 1
)
echo    Found vector store!
echo.

REM Start backend
echo [3/4] Starting backend on http://localhost:8002
start "Backend API" cmd /k "py -m uvicorn src.api.main:app --host 0.0.0.0 --port 8002 --reload"
timeout /t 5 /nobreak >nul
echo    Backend started!
echo.

REM Start frontend
echo [4/4] Starting frontend on http://localhost:3001
cd frontend
start "Frontend Server" cmd /k "py -m http.server 3001"
cd ..
timeout /t 2 /nobreak >nul
echo    Frontend started!
echo.

echo ====================================
echo All servers running!
echo ====================================
echo.
echo Access Points:
echo    Main Chat:     http://localhost:3001/
echo    Documents:     http://localhost:3001/documents.html
echo    Analytics:     http://localhost:3001/analytics.html
echo    API Backend:   http://localhost:8002
echo    API Docs:      http://localhost:8002/docs
echo.
echo To stop: Close the Backend and Frontend terminal windows
echo ====================================
pause
