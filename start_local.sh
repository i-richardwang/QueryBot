#!/bin/bash

# QueryBot Local Development Startup Script
# This script helps you start the QueryBot application locally

set -e

echo "🚀 QueryBot Local Development Startup"
echo "===================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from env.example..."
    cp env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
    echo "📝 Edit .env file and run this script again."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Check if MySQL is running
echo "🔍 Checking MySQL connection..."
if ! mysql -h localhost -P 3306 -e "SELECT 1;" 2>/dev/null; then
    echo "❌ MySQL is not running or not accessible."
    echo "   Please ensure MySQL service is running on localhost:3306"
    exit 1
fi

# Check if Milvus is running
echo "🔍 Checking Milvus connection..."
if ! curl -s http://localhost:19530/health &> /dev/null; then
    echo "❌ Milvus is not running or not accessible."
    echo "   Please ensure Milvus service is running on localhost:19530"
    exit 1
fi

echo "✅ All dependencies are ready!"

# Ask user what to start
echo ""
echo "What would you like to start?"
echo "1) API Server only"
echo "2) Frontend only"
echo "3) Both API Server and Frontend"
echo "4) Setup demo data first"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Starting API Server..."
        uv run uvicorn backend.sql_assistant.api:app --host 0.0.0.0 --port 8000 --reload
        ;;
    2)
        echo "🚀 Starting Frontend..."
        cd frontend && uv run streamlit run app.py
        ;;
    3)
        echo "🚀 Starting both API Server and Frontend..."
        echo "API Server will start in background, Frontend in foreground"
        uv run uvicorn backend.sql_assistant.api:app --host 0.0.0.0 --port 8000 --reload &
        sleep 3
        cd frontend && uv run streamlit run app.py
        ;;
    4)
        echo "🔧 Setting up demo data..."
        uv run python tools/setup_demo_environment.py
        echo "✅ Demo data setup complete!"
        echo "Now you can start the services by running this script again."
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again and choose 1-4."
        exit 1
        ;;
esac
