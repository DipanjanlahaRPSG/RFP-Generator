#!/bin/bash
# Setup and run the RFP Generator backend server

echo "Setting up RFP Generator Backend..."
echo

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo
echo "Installing dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn aiosqlite python-docx openai python-dotenv pydantic

echo
echo "Checking for .env file..."
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please create a .env file with your OPENAI_API_KEY"
    echo
    echo "Example .env content:"
    echo "OPENAI_API_KEY=your_key_here"
    echo "OPENAI_MODEL=gpt-4o"
    echo
    read -p "Press enter to continue..."
fi

echo
echo "Starting server..."
echo "Server will be available at http://localhost:8000"
echo "API documentation at http://localhost:8000/docs"
echo
python server.py
