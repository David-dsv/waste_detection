# 🚀 Comment Lancer le Backend

## ✅ Port 5001 est maintenant libre!

### Méthode Simple (Recommandé)

Depuis le dossier `backend`, exécutez:

```bash
source venv/bin/activate
python app.py
```

Vous devriez voir:

```
🤖 Initialisation YOLOv8n...
📥 Chargement du modèle YOLOv8n...
✅ Modèle YOLOv8n chargé avec succès!
✅ YOLOv8 chargé avec succès (détection active)

🚀 Urban Waste Detection API démarrée
📍 http://localhost:5001
🔧 Debug mode: True
🧠 Gemini AI: activé

 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5001
```

---

## 🔥 Puis Lancez le Frontend

Dans un **nouveau terminal**:

```bash
cd frontend
npm install    # première fois seulement
npm start
```

→ Ouvre http://localhost:3000

---

## 🧪 Testez le Système

### Test 1: Health Check
```bash
curl http://localhost:5001/api/health | jq .
```

Devrait retourner:
```json
{
  "status": "ok",
  "database": "healthy",
  "model_loaded": false,
  "gemini_enabled": true
}
```

### Test 2: Upload Image
```bash
curl -X POST http://localhost:5001/api/detect \
  -F "image=@test_bottle.jpg" \
  | jq .
```

### Test 3: Avec Script Python
```bash
python test_detection.py
```

---

## ⚠️ Si le Port est Encore Occupé

Tuez le processus:
```bash
lsof -ti:5001 | xargs kill -9
```

Ou changez de port dans `backend/.env`:
```bash
PORT=5002
```

---

## 📊 Ce qui Fonctionne

✅ Backend Flask sur port 5001
✅ YOLOv8 nano (~3MB) chargé automatiquement
✅ Gemini 2.0 Flash activé
✅ 40+ classes de déchets détectables
✅ Base de données SQLite
✅ Annotation automatique des images

---

## 🎯 Workflow Complet

```
1. User uploads image
        ↓
2. YOLOv8 détecte objets (bottle, cup, laptop, etc.)
        ↓
3. Gemini analyse et génère recommandations
        ↓
4. Frontend affiche résultats + analyse IA
```

---

**Vous êtes prêt! Lancez `python app.py` dans le dossier backend!** 🚀
