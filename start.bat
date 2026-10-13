@echo off
title QuestFlow Launcher
echo ===================================================
echo Starting QuestFlow (Backend + Frontend)
echo ===================================================

echo Starting Flask Backend on Port 5000...
start "QuestFlow Backend (Flask Port 5000)" cmd /k "cd /d %~dp0questflow-backend && "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" app.py"

echo Starting Node.js Frontend on Port 3000...
start "QuestFlow Frontend (Node Port 3000)" cmd /k "cd /d %~dp0questflow-frontend && node server.js"

echo Waiting 2 seconds for servers to initialize...
timeout /t 2 /nobreak >nul

echo Opening browser at http://localhost:3000...
start http://localhost:3000

echo Done! Both servers are running.
