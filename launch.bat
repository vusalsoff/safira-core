@echo off
echo ========================================================
echo SAFIRA v2.0 - Hybrid Logical Knowledge Engine
echo ========================================================

echo [1] Checking Ollama local LLM...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Ollama is running.
) else (
    echo Starting Ollama in background...
    start /B ollama serve
)

echo.
echo [2] Starting SAFIRA FastAPI Backend (Port 8000)...
start cmd /k ".\venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000"

echo.
echo [3] Starting SAFIRA Frontend (Port 5173)...
cd safira-frontend
start cmd /k "npm run dev"

echo.
echo ========================================================
echo SYSTEM READY
echo Frontend: http://localhost:5173/
echo Backend API: http://localhost:8000/docs
echo ========================================================
pause
