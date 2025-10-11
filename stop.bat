@echo off
echo ====================================
echo Stopping RAG Chatbot Servers
echo ====================================
echo.

echo Killing all Python/Uvicorn servers...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Backend*" 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Frontend*" 2>nul

echo.
echo Killing servers on port 8000...
FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') DO (
    echo   Killing PID: %%P
    taskkill /F /PID %%P 2>nul
)

echo.
echo Killing servers on port 8001...
FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') DO (
    echo   Killing PID: %%P
    taskkill /F /PID %%P 2>nul
)

echo.
echo Killing servers on port 8002...
FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr ":8002" ^| findstr "LISTENING"') DO (
    echo   Killing PID: %%P
    taskkill /F /PID %%P 2>nul
)

echo.
echo Killing servers on port 3001...
FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr ":3001" ^| findstr "LISTENING"') DO (
    echo   Killing PID: %%P
    taskkill /F /PID %%P 2>nul
)

timeout /t 2 /nobreak >nul

echo.
echo ✅ All servers stopped!
echo.
pause
