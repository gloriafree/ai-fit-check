#!/bin/bash

# AI Fit Check Backend Server Startup Script
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting AI Fit Check Backend...${NC}\n"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Using .env.example${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}Created .env from .env.example${NC}"
        echo -e "${YELLOW}Please update .env with your configuration${NC}\n"
    fi
fi

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo -e "${GREEN}Loaded .env configuration${NC}\n"
fi

# Check for Python virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip first (avoid build issues on Python 3.13+)
echo -e "${GREEN}Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1

# Install/upgrade dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -r requirements.txt

# Create data directories
mkdir -p data/persons data/wardrobe

# Check if config exists
if [ ! -f "../configs/config.yaml" ]; then
    echo -e "${RED}ERROR: configs/config.yaml not found!${NC}"
    echo "Please ensure the config file exists in ../configs/config.yaml"
    exit 1
fi

echo -e "${GREEN}Starting FastAPI server...${NC}"
echo -e "${GREEN}Server will be available at: http://localhost:8000${NC}"
echo -e "${GREEN}API Documentation: http://localhost:8000/docs${NC}\n"

# Run the server
python main.py
