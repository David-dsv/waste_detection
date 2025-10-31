# Guide de Contribution

Merci de votre intérêt pour Urban Waste Detection! 🎉

## Comment Contribuer

### Types de Contributions Bienvenues

1. **🐛 Rapports de Bugs**
   - Utiliser le template d'issue GitHub
   - Inclure étapes de reproduction
   - Fournir logs/screenshots

2. **✨ Nouvelles Fonctionnalités**
   - Discuter d'abord dans une issue
   - Fork le repo
   - Créer une branche feature
   - Soumettre une PR

3. **📝 Documentation**
   - Corriger typos
   - Améliorer clarté
   - Ajouter exemples

4. **🧪 Tests**
   - Augmenter couverture
   - Ajouter tests edge cases

## Process de Contribution

### 1. Setup Environnement

```bash
# Fork et clone
git clone https://github.com/VOTRE-USERNAME/urban-waste-detection.git
cd urban-waste-detection

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Installer dépendances
pip install -r backend/requirements.txt
cd frontend && npm install
```

### 2. Créer une Branche

```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
# ou
git checkout -b fix/correction-bug
```

### 3. Développer

- **Code style**: PEP 8 (Python), Prettier (JavaScript)
- **Commits**: Messages clairs et descriptifs
- **Tests**: Ajouter tests pour nouvelles fonctionnalités

### 4. Tests

```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm test
```

### 5. Pull Request

1. Push votre branche
2. Ouvrir PR vers `main`
3. Remplir template PR
4. Attendre review

## Guidelines de Code

### Python (Backend)

```python
# Bon exemple
def detect_waste(image_path: str) -> List[Dict]:
    """
    Détecte les déchets dans une image.

    Args:
        image_path: Chemin vers l'image

    Returns:
        Liste de détections avec bounding boxes
    """
    # Implementation...
    pass
```

**Standards:**
- Docstrings pour toutes les fonctions
- Type hints
- Formatage Black: `black .`
- Linting Flake8: `flake8 .`

### JavaScript/React (Frontend)

```javascript
// Bon exemple
/**
 * Composant pour upload d'images.
 *
 * @param {Function} onDetectionComplete - Callback après détection
 */
const ImageUpload = ({ onDetectionComplete }) => {
  // Implementation...
};

export default ImageUpload;
```

**Standards:**
- JSDoc pour composants
- Prettier: `npm run format`
- ESLint: `npm run lint`

## Domaines Nécessitant Aide

### High Priority
- [ ] Intégration capteurs IoT réels (MQTT)
- [ ] App mobile React Native
- [ ] Tests E2E (Cypress/Playwright)
- [ ] Documentation API (Swagger/OpenAPI)

### Medium Priority
- [ ] Traductions i18n (FR, EN, ES)
- [ ] Dark mode frontend
- [ ] Export rapports PDF
- [ ] Amélioration performances modèle

### Good First Issues
- [ ] Améliorer messages d'erreur
- [ ] Ajouter exemples dataset
- [ ] Créer tutoriels vidéo
- [ ] Refactoring code

## Code de Conduite

### Notre Engagement

Environnement inclusif, respectueux et professionnel.

### Comportements Attendus
✅ Langage inclusif et respectueux
✅ Feedback constructif
✅ Focus sur le bien du projet
✅ Empathie envers les autres

### Comportements Inacceptables
❌ Harcèlement
❌ Discrimination
❌ Trolling
❌ Attaques personnelles

### Application

Violations rapportées à: [votre-email@example.com]

Mesures: Warning → Suspension temporaire → Ban permanent

## Questions?

- **Issues GitHub**: Pour bugs et features
- **Discussions**: Pour questions générales
- **Email**: [votre-email@example.com]
- **Discord**: [lien serveur] (optionnel)

## Remerciements

Merci à tous les contributeurs! 🙏

Liste complète: [CONTRIBUTORS.md](CONTRIBUTORS.md)

---

**Ready to contribute? Let's make cities cleaner together!** 🌍
