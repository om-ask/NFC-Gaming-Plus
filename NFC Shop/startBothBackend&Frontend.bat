@echo off
REM Start the backend
echo Starting the backend...
cd backend
start cmd /k "python main.py"
if %errorlevel% neq 0 (
    echo Failed to start the backend.
    pause
)

REM Start the frontend
echo Starting the frontend...
cd ../frontend/ShoppingCartReact
start cmd /k "npm run dev"
if %errorlevel% neq 0 (
    echo Failed to start the frontend.
    pause
)

REM Return to the root folder
cd ..
echo Both backend and frontend are running.
pause

