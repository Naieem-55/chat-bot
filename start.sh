#!/bin/bash

echo "===================================="
echo "RAG Customer Support Chatbot"
echo "===================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "[ERROR] .env file not found! Try again"
    echo "Please create a .env file from .env.example and add your ANTHROPIC_API_KEY"
    echo ""
    echo "Run: cp .env.example .env"
    echo "Then edit .env to add your API key"
    exit 1
fi

# Check if vector store exists
if [ ! -f data/vector_store/faiss_index.bin ]; then
    echo "[INFO] Vector store not found. Running data ingestion..."
    echo ""
    python scripts/ingest_data.py
    if [ $? -ne 0 ]; then
        echo "[ERROR] Data ingestion failed!"
        exit 1
    fi
    echo ""
    echo "[SUCCESS] Data ingestion completed!"
    echo ""
fi

# Start the backend server in the background
echo "[INFO] Starting backend server on http://localhost:8000"
python run_server.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start the frontend server in the background
echo "[INFO] Starting frontend server on http://localhost:3000"
cd frontend
python -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "===================================="
echo "Chatbot is now running!"
echo "===================================="
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Open http://localhost:3000 in your browser"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "===================================="

# Function to kill both processes on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT

# Wait for background processes
wait
