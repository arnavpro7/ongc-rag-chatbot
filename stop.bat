@echo off
echo Stopping the chatbot services...
docker compose down
echo.
echo Stopped. Your data and downloaded model are still saved.
echo Run start.bat anytime to start it again.
pause
