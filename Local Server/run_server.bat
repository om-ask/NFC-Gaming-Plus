@echo off
REM Install requirements
echo Installing requirements
pip install -r requirements.txt

REM Start the broker
echo Starting the broker...
start cmd /k "python broker.py"
if %errorlevel% neq 0 (
    echo Failed to start the backend.
    pause
)

REM Start the server
echo Starting the server...
start cmd /k "python main.py"
if %errorlevel% neq 0 (
    echo Failed to start the frontend.
    pause
)

REM Return to the root folder
cd ..
echo Both backend and frontend are running.
pause
