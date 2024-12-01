@echo off
REM Install requirements
echo Installing requirements
pip install -r requirements.txt

REM Start the registration process
echo Starting the registration system...
start cmd /k "python mainOLD.py"
if %errorlevel% neq 0 (
    echo Failed to start the backend.
    pause
)

echo Registration System is running
pause
