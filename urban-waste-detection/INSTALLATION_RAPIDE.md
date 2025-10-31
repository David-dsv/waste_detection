# 🚀 INSTALLATION RAPIDE - Avec Gemini 2.0 Flash

## ✅ Votre configuration est PRÊTE!

J'ai configuré votre projet avec:
- ✅ Gemini 2.0 Flash (clé API déjà configurée)
- ✅ RF-DETR pour détection d'objets
- ✅ Backend Flask + Frontend React
- ✅ Fichiers `.env` et `.gitignore` créés

---

## 📋 ÉTAPES D'INSTALLATION (15 minutes)

### Étape 1: Vérifier les prérequis
```bash
python3 --version  # Doit être 3.9+
node --version     # Doit être 16+
git --version
```

### Étape 2: Aller dans le projet
```bash
cd /Users/vuong/Desktop/AI_PROJECT/urban-waste-detection
```

### Étape 3: Installer les dépendances BACKEND
```bash
cd backend

# Créer environnement virtuel
python3 -m venv venv

# Activer environnement
source venv/bin/activate  # Sur macOS/Linux
# ou sur Windows: venv\Scripts\activate

# Installer dépendances (inclut Gemini)
pip install --upgrade pip
pip install -r requirements.txt

# Créer la base de données
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Créer dossier uploads
mkdir -p uploads
```

### Étape 4: Installer les dépendances FRONTEND
```bash
# Ouvrir un NOUVEAU terminal
cd /Users/vuong/Desktop/AI_PROJECT/urban-waste-detection/frontend

# Installer dépendances npm
npm install
```

### Étape 5: TESTER - Lancer le backend
```bash
# Terminal 1 (backend)
cd /Users/vuong/Desktop/AI_PROJECT/urban-waste-detection/backend
source venv/bin/activate
python app.py
```

Vous devriez voir:
```
✅ Gemini Analyzer initialisé avec modèle: gemini-2.0-flash-exp
🚀 Urban Waste Detection API démarrée
📍 http://localhost:5000
```

### Étape 6: TESTER - Lancer le frontend
```bash
# Terminal 2 (frontend)
cd /Users/vuong/Desktop/AI_PROJECT/urban-waste-detection/frontend
npm start
```

Le navigateur s'ouvrira sur: http://localhost:3000

---

## 🧪 TESTER L'ANALYSE GEMINI

### Test 1: Via l'interface web
1. Ouvrir http://localhost:3000
2. Aller sur l'onglet "Détection"
3. Uploader une image de déchets (ou prendre une photo)
4. Cliquer "Détecter les déchets"
5. **Regarder la réponse JSON dans la console** → Vous verrez `ai_analysis` avec:
   - `summary`: Résumé en français
   - `severity`: faible/moyenne/élevée/critique
   - `recommendations`: Actions recommandées
   - `environmental_risks`: Risques environnementaux
   - `health_risks`: Risques sanitaires

### Test 2: Via API directe
```bash
# Tester l'API
curl -X POST http://localhost:5000/api/detect \
  -F "image=@/path/to/your/waste_image.jpg" \
  -F "gps_lat=48.8566" \
  -F "gps_lon=2.3522"
```

---

## 🔧 CONFIGURATION ACTUELLE

Votre fichier `backend/.env` contient:
```bash
# Gemini 2.0 Flash (DÉJÀ CONFIGURÉ)
GEMINI_API_KEY=AIzaSyDCGhv0uIVNpMLW42uuMCVtIivkg_lOK68
GEMINI_MODEL=gemini-2.0-flash-exp
USE_GEMINI=true

# Base de données locale
DATABASE_URL=sqlite:///waste_detection.db

# Flask
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production-xyz123
```

---

## 📝 CE QUE FAIT GEMINI

Quand vous uploadez une image de déchets, le système:

1. **RF-DETR** détecte les objets (bouteilles, sacs, etc.)
2. **Gemini 2.0 Flash** analyse les détections et génère:
   - 📊 Résumé de la situation
   - ⚠️ Niveau de sévérité (faible → critique)
   - 🎯 Recommandations d'action prioritaires
   - 🌍 Risques environnementaux
   - 🏥 Risques sanitaires
   - ⏰ Urgence d'intervention (0-10)
   - 🚛 Type d'équipe nécessaire

**Exemple de réponse Gemini:**
```json
{
  "summary": "Accumulation importante de 15 bouteilles plastiques et 8 sacs dans une zone résidentielle. Risque modéré de pollution.",
  "severity": "moyenne",
  "severity_score": 6,
  "environmental_risks": [
    "Pollution micro-plastiques",
    "Obstruction canalisations"
  ],
  "health_risks": [
    "Prolifération insectes",
    "Contamination eaux pluviales"
  ],
  "recommendations": [
    {
      "action": "Collecte rapide dans les 48h",
      "priority": "haute",
      "reason": "Éviter accumulation supplémentaire"
    },
    {
      "action": "Installer poubelles additionnelles",
      "priority": "moyenne",
      "reason": "Zone sous-équipée"
    }
  ],
  "urgency_score": 6,
  "intervention_type": "manuel",
  "estimated_time": "1-2 heures"
}
```

---

## 🎨 AFFICHER L'ANALYSE DANS LE FRONTEND

Le frontend reçoit déjà `ai_analysis` dans la réponse. Pour l'afficher:

**Option 1: Dans la console**
Ouvrir DevTools (F12) et voir la réponse complète

**Option 2: Afficher dans l'UI** (à implémenter)
Modifier `frontend/src/components/ImageUpload.jsx` ligne ~150:

```javascript
// Après ligne result && (
{result.ai_analysis && (
  <Box sx={{ mt: 2, p: 2, bgcolor: 'info.light', borderRadius: 2 }}>
    <Typography variant="h6">🧠 Analyse IA</Typography>
    <Typography><strong>Résumé:</strong> {result.ai_analysis.summary}</Typography>
    <Typography><strong>Sévérité:</strong> {result.ai_analysis.severity}</Typography>
    <Typography><strong>Score:</strong> {result.ai_analysis.severity_score}/10</Typography>

    <Typography variant="subtitle2" sx={{ mt: 2 }}>Recommandations:</Typography>
    {result.ai_analysis.recommendations?.map((rec, i) => (
      <Typography key={i}>• {rec.action} ({rec.priority})</Typography>
    ))}
  </Box>
)}
```

---

## 🆘 PROBLÈMES COURANTS

### Problème: "google-generativeai not installed"
```bash
cd backend
source venv/bin/activate
pip install google-generativeai
```

### Problème: "GEMINI_API_KEY not found"
Vérifier que `backend/.env` existe et contient la clé

### Problème: Port 5000 déjà utilisé
```bash
# Dans backend/.env, changer:
PORT=5001

# Puis dans frontend/.env.local:
REACT_APP_API_URL=http://localhost:5001/api
```

### Problème: Gemini répond en anglais
Modifier `backend/services/gemini_analyzer.py` ligne 51:
```python
# Ajouter au début du prompt:
"IMPORTANT: Réponds TOUJOURS en français."
```

---

## 🚀 PROCHAINES ÉTAPES

### Maintenant:
1. ✅ Tester l'installation
2. ✅ Uploader une image de déchets
3. ✅ Vérifier l'analyse Gemini dans la console

### Cette semaine:
1. Afficher l'analyse IA dans l'interface
2. Télécharger dataset TACO (optionnel)
3. Publier sur GitHub

### Plus tard:
1. Entraîner RF-DETR sur TACO
2. Déployer sur Vercel + Heroku
3. Créer portfolio LinkedIn

---

## 📚 FICHIERS IMPORTANTS

- `backend/.env` → Configuration (DÉJÀ PRÊT)
- `backend/services/gemini_analyzer.py` → Code Gemini
- `backend/routes/detection.py` → Intégration Gemini (ligne 124-141)
- `frontend/src/components/ImageUpload.jsx` → Upload image

---

## 💡 TIPS

**Gemini 2.0 Flash est:**
- ✅ Gratuit (quota généreux)
- ✅ Très rapide (<1s)
- ✅ Multimodal (texte + images si besoin)
- ✅ Excellent en français

**Pour tester différents prompts:**
Modifier `backend/services/gemini_analyzer.py` ligne 51 (fonction `analyze_detections`)

---

## 🎉 FÉLICITATIONS!

Vous avez maintenant:
- ✅ Détection objets (RF-DETR)
- ✅ Analyse IA (Gemini 2.0 Flash)
- ✅ Backend + Frontend fonctionnels
- ✅ Configuration prête

**COMMENCEZ PAR L'ÉTAPE 1 CI-DESSUS!** 🚀

Questions? Lisez `QUICKSTART.md` ou `GUIDE_COMPLET.md`
