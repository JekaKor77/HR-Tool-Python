#!/bin/bash
# Startup script for HR CV Analysis System

echo "Starting HR CV Analysis System..."
echo "================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please run: python setup.py"
    exit 1
fi

# Check if OpenAI API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  Please edit .env file and add your OpenAI API key"
    echo "   Get your API key from: https://platform.openai.com/api-keys"
    exit 1
fi

echo "✅ Starting Flask application..."
echo "🌐 Open your browser to: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the Flask application
python app.py
