#!/bin/bash

# Urban Waste Detection - Quick Start Script
# Ce script démarre le backend et le frontend

echo "🚀 Démarrage Urban Waste Detection System"
echo "=========================================="

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier si on est dans le bon dossier
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Erreur: Exécutez ce script depuis la racine du projet"
    exit 1
fi

# 1. Démarrer le Backend
echo ""
echo -e "${YELLOW}📡 Démarrage Backend (Flask API)...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment non trouvé. Exécutez d'abord: cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activer venv et démarrer backend en arrière-plan
source venv/bin/activate
python app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend démarré (PID: $BACKEND_PID)${NC}"
echo "   📍 API: http://localhost:5001"
echo "   📋 Logs: backend.log"

cd ..

# 2. Démarrer le Frontend
echo ""
echo -e "${YELLOW}🎨 Démarrage Frontend (React)...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances npm..."
    npm install
fi

echo -e "${GREEN}✅ Frontend en cours de démarrage...${NC}"
echo "   📍 App: http://localhost:3000"
echo ""

# Démarrer frontend (en premier plan)
npm start

# Cleanup quand on quitte
trap "kill $BACKEND_PID 2>/dev/null" EXIT
