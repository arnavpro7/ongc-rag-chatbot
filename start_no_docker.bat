@echo off
echo ============================================
echo   Local LLM Chatbot - No-Docker Setup
echo ============================================
echo.

echo [1/4] Checking Ollama is installed...
where ollama >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Ollama is not installed or not found.
    echo Please install it first from https://ollama.com/download
    echo Then close this window and double-click start_no_docker.bat again.
    pause
    exit /b 1
)
echo Ollama found. Good.
echo.

echo [2/4] Checking Python 3.12 is installed...
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python 3.12 was not found.
    echo Please install it from https://www.python.org/downloads/release/python-31210/
    echo Download the "Windows installer (64-bit)" and run it.
    echo Then close this window and double-click start_no_docker.bat again.
    pause
    exit /b 1
)
echo Python 3.12 found. Good.
echo.

echo [3/4] Installing Open WebUI using Python 3.12 (only happens once, may take a few minutes)...
py -3.12 -m pip install open-webui --quiet
if errorlevel 1 (
    echo.
    echo ERROR: Open WebUI failed to install. Scroll up to see the error.
    pause
    exit /b 1
)
echo.

echo [4/4] Downloading the AI model (5-15 minutes depending on your internet)...
ollama pull llama3.2:3b
echo.

echo ============================================
echo   Setup complete. Starting the chatbot now...
echo   Once it says the server is running, open your browser to:
echo   http://localhost:3000
echo   Keep this window open while you use the chatbot.
echo ============================================
echo.
py -3.12 -m open_webui serve --port 3000
pause
