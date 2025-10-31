# Urban Waste Detection System 🗑️

Système intelligent de détection des déchets urbains utilisant l'IA (YOLO11) pour identifier et classifier automatiquement différents types de déchets dans les images et vidéos.

## 🎯 Fonctionnalités

- **Détection en temps réel** : Analyse d'images et de vidéos pour détecter les déchets
- **Classification intelligente** : 6 catégories de déchets (Plastique, Verre, Métal, Papier, Cigarettes, Autres)
- **Analyse IA avancée** : Intégration de Gemini AI pour des analyses contextuelles
- **Dashboard interactif** : Visualisation des statistiques et des tendances
- **API REST** : Interface complète pour l'intégration
- **Modèle personnalisé** : Entraîné sur le dataset TACO (Trash Annotations in Context)

## 🏗️ Architecture

```
AI_PROJECT/
├── urban-waste-detection/
│   ├── backend/           # API Flask + YOLO
│   │   ├── app.py
│   │   ├── models/        # Modèles de données
│   │   ├── routes/        # Endpoints API
│   │   └── services/      # Services de détection
│   │
│   └── frontend/          # Interface Next.js
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   └── services/
│       └── public/
│
└── yolo_taco_workspace/   # Entraînement des modèles
    ├── train_yolo11.py
    └── taco_yolo_data/
```

## 🚀 Installation

### Prérequis

- Python 3.8+
- Node.js 18+
- pip et npm

### Backend (Flask + YOLO)

```bash
cd urban-waste-detection/backend

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API

# Lancer le serveur
python app.py
```

Le backend sera disponible sur `http://localhost:5001`

### Frontend (Next.js)

```bash
cd urban-waste-detection/frontend

# Installer les dépendances
npm install

# Configurer les variables d'environnement
cp .env.example .env.local

# Lancer en mode développement
npm run dev
```

Le frontend sera disponible sur `http://localhost:3000`

## 🤖 Modèle YOLO11

Le projet utilise YOLO11 (dernière version) entraîné sur le dataset TACO pour une détection précise des déchets urbains.

### Classes détectées

| Classe | Description |
|--------|-------------|
| Cigarette | Mégots de cigarettes |
| Glass | Verre (bouteilles, verres) |
| Metal | Métaux (canettes, conserves) |
| Other | Autres déchets |
| Paper | Papier et carton |
| Plastic | Plastique (bouteilles, sacs, emballages) |

### Entraîner un nouveau modèle

```bash
cd yolo_taco_workspace

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer ultralytics
pip install ultralytics torch torchvision

# Lancer l'entraînement
python train_yolo11.py
```

## 📡 API Endpoints

### Détection

- `POST /api/detect` - Analyser une image
- `POST /api/detect/batch` - Analyser plusieurs images
- `POST /api/detect/video` - Analyser une vidéo

### Statistiques

- `GET /api/statistics/overview` - Vue d'ensemble
- `GET /api/statistics/by-class` - Par catégorie
- `GET /api/statistics/daily` - Tendances journalières

### Détections

- `GET /api/detections` - Liste des détections
- `GET /api/detections/:id` - Détail d'une détection
- `DELETE /api/detections/:id` - Supprimer une détection

## 🔧 Configuration

### Variables d'environnement (Backend)

```env
FLASK_ENV=development
PORT=5001
DATABASE_URL=sqlite:///waste_detection.db
CONFIDENCE_THRESHOLD=0.5
USE_GEMINI=true
GEMINI_API_KEY=votre_clé_api
```

### Variables d'environnement (Frontend)

```env
NEXT_PUBLIC_API_URL=http://localhost:5001
```

## 📊 Dataset TACO

Le modèle est entraîné sur [TACO dataset](http://tacodataset.org/) - Trash Annotations in Context, qui contient des milliers d'images annotées de déchets dans des contextes réels.

## 🛠️ Technologies utilisées

**Backend:**
- Flask (API REST)
- Ultralytics YOLO11 (Détection d'objets)
- Google Gemini AI (Analyse contextuelle)
- SQLAlchemy (ORM)
- SQLite (Base de données)

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Recharts (Visualisations)

**IA & ML:**
- YOLO11 (Détection)
- PyTorch (Framework ML)
- OpenCV (Traitement d'images)

## 📈 Performance

- **Temps de détection** : ~50-100ms par image
- **Précision (mAP50)** : ~85-90% sur TACO test set
- **Support GPU** : CUDA, MPS (Apple Silicon), CPU

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT.

## 👥 Auteurs

- **Équipe Urban Waste Detection**

## 🙏 Remerciements

- Dataset TACO pour les données d'entraînement
- Ultralytics pour YOLO11
- Google pour Gemini AI
- La communauté open source

## 📞 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.

---

Made with ❤️ for a cleaner planet 🌍
