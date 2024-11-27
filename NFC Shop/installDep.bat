@echo off
echo Checking dependencies...

REM Navigate to the backend folder and check Python dependencies
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install backend dependencies. Exiting...
    pause
    exit /b 1
)

REM Navigate to the frontend folder and check Node.js dependencies
cd ../frontend/ShoppingCartReact
echo Installing frontend dependencies...
npm install
if %errorlevel% neq 0 (
    echo Failed to install frontend dependencies. Exiting...
    pause
    exit /b 1
)