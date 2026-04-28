@echo off
echo Starting Project Rita API...

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Checking dependencies...
pip install -r requirements.txt

echo Running API...
python main.py api

pause
