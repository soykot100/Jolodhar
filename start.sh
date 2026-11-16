#!/bin/bash
# JOLODHAR - Start Script for Linux/macOS/VS Code Terminal
# Team Aphelion - NASA Space Apps Challenge
# Usage: ./start.sh

cd "$(dirname "$0")"

echo "=========================================="
echo "  JOLODHAR - Smart IoT-ML Drain Monitoring"
echo "  Team Aphelion - NASA Space Apps"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "Install: https://www.python.org/downloads/"
    exit 1
fi

# Step 1: Create venv if not exists
if [ ! -d "venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create venv"
        exit 1
    fi
fi

# Step 2: Activate venv
echo "[2/4] Activating virtual environment..."
source venv/bin/activate

# Step 3: Install dependencies
echo "[3/4] Installing dependencies (this may take a few minutes on first run)..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

# Step 4: Train model if not exists
if [ ! -f "ml/model.pkl" ]; then
    echo "[4/4] Training ML model (first run only)..."
    python ml/train_model.py
else
    echo "[4/4] ML model already trained."
fi

echo ""
echo "=========================================="
echo "  Starting JOLODHAR Server"
echo "=========================================="
echo "Public:  http://localhost:5000/public"
echo "Login:   http://localhost:5000/login"
echo "         (admin / jolodhar2025)"
echo "=========================================="
echo "Press Ctrl+C to stop."
echo ""

python app.py
