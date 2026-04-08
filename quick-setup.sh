#!/bin/bash

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "=================================="
echo "   Intranet Guardia — Setup"
echo "=================================="
echo ""

# ─── Docker ───────────────────────────────────────────────
echo -e "${YELLOW}[1/5] Vérification de Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker n'est pas installé.${NC}"
    echo ""
    echo "Installe Docker Desktop depuis :"
    echo "  macOS   → https://docs.docker.com/desktop/install/mac-install/"
    echo "  Linux   → https://docs.docker.com/engine/install/"
    echo ""
    exit 1
fi
echo -e "${GREEN}✓ Docker $(docker --version | cut -d' ' -f3 | tr -d ',')${NC}"

# ─── Docker Compose ───────────────────────────────────────
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Docker Compose n'est pas disponible.${NC}"
    echo "Mets à jour Docker Desktop."
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose disponible${NC}"

# ─── Python ───────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[2/5] Vérification de Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 n'est pas installé.${NC}"
    echo ""
    echo "Installe Python 3.13 :"
    echo "  macOS  → brew install python@3.13"
    echo "  Linux  → sudo apt install python3.13 python3.13-venv"
    echo ""
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# ─── Environnement virtuel ────────────────────────────────
echo ""
echo -e "${YELLOW}[3/5] Création de l'environnement virtuel...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Environnement virtuel créé${NC}"
else
    echo -e "${GREEN}✓ Environnement virtuel déjà existant${NC}"
fi

source venv/bin/activate

# ─── Dépendances Python ───────────────────────────────────
echo ""
echo -e "${YELLOW}[4/5] Installation des dépendances Python...${NC}"
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dépendances installées${NC}"

# ─── Variables d'environnement ────────────────────────────
echo ""
echo -e "${YELLOW}[5/5] Configuration des variables d'environnement...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Fichier .env créé depuis .env.example${NC}"
else
    echo -e "${GREEN}✓ Fichier .env déjà existant${NC}"
fi

# ─── Résumé ───────────────────────────────────────────────
echo ""
echo "=================================="
echo -e "${GREEN}   Setup terminé !${NC}"
echo "=================================="
echo ""
echo "Lance l'application avec :"
echo ""
echo "  docker compose up -d"
echo ""
echo "Puis ouvre http://localhost:5000"
echo ""
echo "Pour activer l'environnement virtuel :"
echo "  source venv/bin/activate"
echo ""