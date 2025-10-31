#!/bin/bash

###############################################################################
# Urban Waste Detection - Installation automatique
# Ce script configure l'environnement complet du projet
###############################################################################

set -e  # Arrêter en cas d'erreur

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗑️  URBAN WASTE DETECTION SYSTEM - Setup Automatique"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonctions utilitaires
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Vérifier prérequis
check_prerequisites() {
    echo "🔍 Vérification des prérequis..."
    echo ""

    # Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
        print_success "Python $PYTHON_VERSION installé"
    else
        print_error "Python 3.9+ requis. Installez Python: https://python.org"
        exit 1
    fi

    # Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION installé"
    else
        print_error "Node.js 16+ requis. Installez Node: https://nodejs.org"
        exit 1
    fi

    # npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm $NPM_VERSION installé"
    else
        print_error "npm requis (installé avec Node.js)"
        exit 1
    fi

    # Git
    if command -v git &> /dev/null; then
        print_success "Git installé"
    else
        print_error "Git requis. Installez Git: https://git-scm.com"
        exit 1
    fi

    echo ""
}

# Setup Backend
setup_backend() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 Configuration Backend (Flask + ML)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    cd backend

    # Environnement virtuel
    print_info "Création de l'environnement virtuel Python..."
    python3 -m venv venv
    print_success "Environnement virtuel créé"

    # Activation
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    print_success "Environnement virtuel activé"

    # Dépendances
    print_info "Installation des dépendances Python (peut prendre 5-10min)..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt
    print_success "Dépendances Python installées"

    # Configuration
    if [ ! -f .env ]; then
        print_info "Création du fichier .env..."
        cp .env.example .env
        print_success "Fichier .env créé (à configurer manuellement)"
    else
        print_info "Fichier .env déjà existant"
    fi

    # Base de données
    print_info "Initialisation de la base de données..."
    python -c "from app import app, db; app.app_context().push(); db.create_all()" || true
    print_success "Base de données initialisée"

    # Dossier uploads
    mkdir -p uploads
    print_success "Dossier uploads créé"

    cd ..
    echo ""
}

# Setup Frontend
setup_frontend() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎨 Configuration Frontend (React)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    cd frontend

    # Configuration
    if [ ! -f .env.local ]; then
        print_info "Création du fichier .env.local..."
        cp .env.example .env.local
        print_success "Fichier .env.local créé"
    else
        print_info "Fichier .env.local déjà existant"
    fi

    # Dépendances
    print_info "Installation des dépendances npm (peut prendre 5min)..."
    npm install
    print_success "Dépendances npm installées"

    cd ..
    echo ""
}

# Setup ML Training
setup_ml() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🧠 Configuration ML Training (optionnel)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    read -p "Voulez-vous installer les dépendances ML pour entraînement? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd ml-training

        print_info "Installation des dépendances ML..."
        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            source ../backend/venv/Scripts/activate
        else
            source ../backend/venv/bin/activate
        fi
        pip install -r requirements.txt
        print_success "Dépendances ML installées"

        # Créer dossiers
        mkdir -p data/taco_raw
        mkdir -p data/taco_processed
        mkdir -p outputs
        print_success "Dossiers ML créés"

        cd ..
    else
        print_info "Installation ML skippée (vous pouvez l'installer plus tard)"
    fi

    echo ""
}

# Vérifier installation
verify_installation() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔍 Vérification de l'installation"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    ERRORS=0

    # Backend
    if [ -d "backend/venv" ]; then
        print_success "Backend: Environnement virtuel OK"
    else
        print_error "Backend: Environnement virtuel manquant"
        ERRORS=$((ERRORS + 1))
    fi

    if [ -f "backend/.env" ]; then
        print_success "Backend: Configuration OK"
    else
        print_error "Backend: Fichier .env manquant"
        ERRORS=$((ERRORS + 1))
    fi

    # Frontend
    if [ -d "frontend/node_modules" ]; then
        print_success "Frontend: node_modules OK"
    else
        print_error "Frontend: node_modules manquant"
        ERRORS=$((ERRORS + 1))
    fi

    if [ -f "frontend/.env.local" ]; then
        print_success "Frontend: Configuration OK"
    else
        print_error "Frontend: Fichier .env.local manquant"
        ERRORS=$((ERRORS + 1))
    fi

    echo ""

    if [ $ERRORS -eq 0 ]; then
        print_success "Installation complète avec succès! ✨"
    else
        print_error "$ERRORS erreur(s) détectée(s). Vérifiez les logs ci-dessus."
    fi

    echo ""
}

# Instructions démarrage
print_instructions() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🚀 Prochaines Étapes"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1️⃣  CONFIGURATION"
    echo "   Éditez les fichiers de configuration:"
    echo "   - backend/.env (clés API, base de données)"
    echo "   - frontend/.env.local (URL backend)"
    echo ""
    echo "2️⃣  LANCER LE BACKEND"
    echo "   cd backend"
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "   venv\\Scripts\\activate"
    else
        echo "   source venv/bin/activate"
    fi
    echo "   python app.py"
    echo "   → http://localhost:5000"
    echo ""
    echo "3️⃣  LANCER LE FRONTEND (nouveau terminal)"
    echo "   cd frontend"
    echo "   npm start"
    echo "   → http://localhost:3000"
    echo ""
    echo "4️⃣  OU UTILISER DOCKER (alternative)"
    echo "   docker-compose up -d"
    echo "   → Tous les services démarrés automatiquement"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📚 DOCUMENTATION"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "   README.md          - Documentation complète"
    echo "   QUICKSTART.md      - Guide rapide"
    echo "   docs/DEPLOYMENT.md - Déploiement production"
    echo "   CONTRIBUTING.md    - Guide contribution"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "💬 SUPPORT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "   GitHub Issues: https://github.com/votre-username/urban-waste-detection/issues"
    echo "   Email: votre-email@example.com"
    echo ""
    print_success "Bon développement! 🌍🗑️✨"
    echo ""
}

# Menu principal
main() {
    check_prerequisites
    setup_backend
    setup_frontend
    setup_ml
    verify_installation
    print_instructions
}

# Exécuter
main
