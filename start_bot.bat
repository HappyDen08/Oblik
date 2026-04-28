@echo off
echo Starting Project Rita Bot...

:: Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install/Update dependencies
echo Checking dependencies...
pip install -r requirements.txt

:: Run the bot
echo Running bot...
python main.py bot

pause
