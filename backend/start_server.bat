@echo off
REM Setup and run the RFP Generator backend server

echo Setting up RFP Generator Backend...
echo.

REM Check if venv exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install --upgrade pip
pip install fastapi uvicorn aiosqlite python-docx openai python-dotenv pydantic

echo.
echo Checking for .env file...
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create a .env file with your OPENAI_API_KEY
    echo.
    echo Example .env content:
    echo OPENAI_API_KEY=your_key_here
    echo OPENAI_MODEL=gpt-4o
    echo.
    pause
)

echo.
echo Starting server...
echo Server will be available at http://localhost:8000
echo API documentation at http://localhost:8000/docs
echo.
python server.py
