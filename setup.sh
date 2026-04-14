#!/usr/bin/env bash
# GUADRAILS RAG WITH ENDEE - Quick Setup Script
# This script automates the setup process

set -e

echo "
╔════════════════════════════════════════════════════════╗
║  ⚔️  GUADRAILS RAG WITH ENDEE - Setup Script            ║
║  Privacy-First Offline AI Document Assistant v2.0.0   ║
╚════════════════════════════════════════════════════════╝
"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Prerequisites Check${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}❌ Python 3.9+ not found${NC}"
    echo "   Download from: https://python.org"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found$(python3 --version)${NC}"

# Check pip
if ! command -v pip &> /dev/null; then
    echo -e "${YELLOW}❌ pip not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip found${NC}"

echo ""
echo -e "${BLUE}📦 Installing Dependencies${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

echo ""
echo -e "${BLUE}⚙️  Setup Configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env created${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Edit .env if you need custom configuration:${NC}"
    echo "   - Ollama host/model"
    echo "   - Endee database host"
    echo "   - Server port and host"
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

echo ""
echo -e "${BLUE}🚀 Next Steps${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  Start Ollama (if not already running):"
echo "   ollama service start    # macOS/Linux"
echo "   # or download and run from: https://ollama.com"
echo ""
echo "2️⃣  Start Endee Vector Database:"
echo "   cd ../endee"
echo "   ./run.sh"
echo ""
echo "3️⃣  Start GUADRAILS RAG:"
echo "   python app.py"
echo ""
echo "4️⃣  Open in browser:"
echo "   http://localhost:8000"
echo ""
echo -e "${GREEN}✨ Setup complete!${NC}"
