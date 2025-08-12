#!/bin/bash

# DRAir - Flight Search Application Startup Script
echo "🚀 Starting DRAir Flight Search Application..."

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Setting up environment...${NC}"

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
source .venv/bin/activate

# Start FastAPI backend in background
echo -e "${GREEN}🌐 Starting FastAPI backend on http://127.0.0.1:8000...${NC}"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
FASTAPI_PID=$!

# Wait a moment for FastAPI to start
sleep 3

# Start Streamlit frontend
echo -e "${GREEN}🎨 Starting Streamlit frontend on http://127.0.0.1:8501...${NC}"
streamlit run streamlit_app.py --server.port 8501 --server.address 127.0.0.1 &
STREAMLIT_PID=$!

echo -e "${BLUE}✅ DRAir Flight Search is now running!${NC}"
echo -e "${YELLOW}📖 Access the application at:${NC}"
echo -e "   🌐 FastAPI Backend:  http://127.0.0.1:8000"
echo -e "   🌐 API Documentation: http://127.0.0.1:8000/docs"
echo -e "   🎨 Streamlit Frontend: http://127.0.0.1:8501"
echo ""
echo -e "${YELLOW}🛑 To stop the application, press Ctrl+C${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down DRAir Flight Search...${NC}"
    kill $FASTAPI_PID 2>/dev/null
    kill $STREAMLIT_PID 2>/dev/null
    echo -e "${GREEN}✅ Application stopped successfully!${NC}"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for background processes
wait
