# Quick Start Guide - Urban Waste Detection

Guide de démarrage rapide pour tester le projet en 15 minutes.

## Option 1: Docker (Recommandé)

### Prérequis
- Docker Desktop installé
- 8GB RAM minimum

### Étapes (5 minutes)

```bash
# 1. Cloner le projet
git clone https://github.com/votre-username/urban-waste-detection.git
cd urban-waste-detection

# 2. Copier fichiers de configuration
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 3. Lancer tous les services
docker-compose up -d

# 4. Vérifier que tout fonctionne
# Backend API: http://localhost:5000
# Frontend: http://localhost:3000
# Database: localhost:5432
```

**C'est tout!** L'application est accessible à http://localhost:3000

### Arrêter les services
```bash
docker-compose down
```

---

## Option 2: Installation Manuelle

### Prérequis
- Python 3.9+
- Node.js 16+
- PostgreSQL (optionnel, SQLite par défaut)

### Backend (10 minutes)

```bash
# 1. Aller dans le dossier backend
cd backend

# 2. Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env
# Éditer .env si nécessaire

# 5. Initialiser la base de données
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# 6. Lancer le serveur
python app.py
```

Backend accessible à: http://localhost:5000

### Frontend (5 minutes)

Dans un nouveau terminal:

```bash
# 1. Aller dans le dossier frontend
cd frontend

# 2. Installer dépendances
npm install

# 3. Configuration
cp .env.example .env.local

# 4. Lancer l'application
npm start
```

Frontend accessible à: http://localhost:3000

---

## Tester l'Application

### 1. Upload d'Image

1. Ouvrir http://localhost:3000
2. Onglet "Détection"
3. Glisser-déposer une image de déchets
   - Ou utiliser une image de test: `tests/sample_images/waste1.jpg`
4. Cliquer "Détecter les déchets"

### 2. Voir les Résultats

- **Détections**: Objets détectés avec bounding boxes
- **Carte**: Onglet "Carte" pour visualisation géographique
- **Dashboard**: Onglet "Dashboard" pour statistiques

### 3. Tester l'API Directement

```bash
# Health check
curl http://localhost:5000/api/health

# Upload image
curl -X POST http://localhost:5000/api/detect \
  -F "image=@path/to/image.jpg" \
  -F "gps_lat=48.8566" \
  -F "gps_lon=2.3522"

# Récupérer statistiques
curl http://localhost:5000/api/statistics/overview
```

---

## Entraîner le Modèle (Avancé)

### Télécharger le Dataset TACO

```bash
cd ml-training

# Installer dépendances ML
pip install -r requirements.txt

# Télécharger et préparer TACO
python prepare_data.py
```

Durée: ~15 minutes (téléchargement + traitement)

### Fine-tuner RF-DETR

**Option A: Notebook Colab (Recommandé - GPU gratuit)**

1. Ouvrir: `ml-training/notebooks/train_colab.ipynb`
2. Upload vers Google Colab
3. Exécuter toutes les cellules
4. Télécharger le modèle entraîné

Durée: ~2-3 heures sur GPU Tesla T4

**Option B: Local (nécessite GPU)**

```bash
cd ml-training

# Lancer entraînement
python train_rfdetr.py \
  --config ./data/taco_processed/dataset.yaml \
  --epochs 50 \
  --batch-size 16 \
  --wandb  # Optionnel: logging Weights & Biases
```

Durée: ~5-8 heures sur GPU moderne

### Utiliser le Modèle Entraîné

```bash
# Copier le modèle vers le backend
cp ml-training/outputs/best_model.pth backend/models/

# Ou export ONNX (plus rapide en inférence)
cd ml-training
python export_onnx.py --checkpoint outputs/best_model.pth

# Mettre à jour backend/.env
MODEL_PATH=./models/best_model.onnx
MODEL_TYPE=onnx
```

---

## Troubleshooting

### Problème: Port déjà utilisé

```bash
# Changer port backend (backend/.env)
PORT=5001

# Changer port frontend (frontend/.env.local)
PORT=3001
```

### Problème: Erreur de dépendances

```bash
# Backend
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Frontend
rm -rf node_modules package-lock.json
npm install
```

### Problème: Modèle introuvable

Le backend démarre sans modèle chargé (mode API only).

Pour utiliser la détection:
1. Télécharger un modèle pré-entraîné (voir Releases GitHub)
2. Ou entraîner votre propre modèle (voir section ci-dessus)
3. Placer dans `backend/models/`
4. Mettre à jour `MODEL_PATH` dans `.env`

### Problème: Base de données

```bash
# Réinitialiser DB SQLite
rm backend/waste_detection.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Ou utiliser PostgreSQL
# 1. Installer PostgreSQL
# 2. Créer DB: createdb waste_detection
# 3. Mettre à jour DATABASE_URL dans .env
```

---

## Prochaines Étapes

### Pour Développeurs

1. **Lire la documentation complète**: [docs/](docs/)
2. **Contribuer**: [CONTRIBUTING.md](CONTRIBUTING.md)
3. **Tests**: `pytest backend/tests/` et `npm test` (frontend)

### Pour Chercheurs ML

1. **Dataset**: [ml-training/data/](ml-training/data/)
2. **Notebooks**: [ml-training/notebooks/](ml-training/notebooks/)
3. **Évaluation**: `python ml-training/evaluate.py`

### Pour Déploiement Production

1. **Guide complet**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
2. **Docker**: `docker-compose -f docker-compose.prod.yml up`
3. **Cloud**: Heroku, AWS, GCP (instructions détaillées dans DEPLOYMENT.md)

---

## Ressources Additionnelles

- **Documentation API**: http://localhost:5000/api (après lancement)
- **Dataset TACO**: http://tacodataset.org/
- **RF-DETR Paper**: https://arxiv.org/abs/2304.08069
- **Issues GitHub**: Pour bugs et questions

---

## Support

- **GitHub Issues**: https://github.com/votre-username/urban-waste-detection/issues
- **Discussions**: https://github.com/votre-username/urban-waste-detection/discussions
- **Email**: votre-email@example.com

---

**Enjoy building cleaner cities with AI!** 🌍🗑️✨
