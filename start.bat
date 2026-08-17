@echo off
echo ============================================
echo   Local LLM Chatbot - Automatic Setup
echo ============================================
echo.

echo [1/4] Checking Docker is running...
docker info >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Docker Desktop is not running.
    echo Please open Docker Desktop first, wait for it to say "Engine running", then double-click this file again.
    pause
    exit /b 1
)
echo Docker is running. Good.
echo.

echo [2/4] Setting up configuration file...
if not exist .env (
    copy .env.example .env >nul
    echo Created .env file.
) else (
    echo .env already exists, skipping.
)
echo.

echo [3/4] Starting the chatbot services (this may take a few minutes the first time)...
docker compose up -d
if errorlevel 1 (
    echo.
    echo ERROR: Something went wrong starting the services. Scroll up to see the error message.
    pause
    exit /b 1
)
echo.

echo [4/4] Downloading the AI model (this can take 5-15 minutes depending on your internet)...
docker exec -it ollama ollama pull llama3.2:3b
echo.

echo ============================================
echo   All done!
echo   Open your browser and go to: http://localhost:3000
echo ============================================
echo.
pause
