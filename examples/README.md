# Projets Exemples

Ce dossier contient les applications web à tester.

## 📁 Structure

```
src/
├── project-sample-1/          # Application de connexion
│   ├── index.html            # Page de connexion
│   └── dashboard.html        # Dashboard
├── project-sample-2/          # (À ajouter)
└── README.md
```

## 🌐 project-sample-1

Application de connexion simple avec :
- Formulaire de connexion
- Validation HTML5
- Messages d'erreur
- Dashboard protégé
- Accessibilité WCAG 2.2 + RGAA 4

### Credentials de test
- **Username**: admin
- **Password**: password123

### Pages
1. **index.html** - Page de connexion
2. **dashboard.html** - Dashboard après connexion

### Ouvrir localement
```bash
# Ouvrir dans le navigateur
start sources/src/project-sample-1/index.html

# Ou utiliser un serveur local
cd sources/src/project-sample-1
python -m http.server 8000
# Puis ouvrir http://localhost:8000
```

## 🧪 Tests Associés

Les tests pour ces projets sont dans `sources/tests/playwright/`

Exemple :
- `test_project_sample_1.py` - Tests pour project-sample-1

## ➕ Ajouter un Nouveau Projet

1. Créer un dossier `project-sample-X/`
2. Ajouter vos fichiers HTML/CSS/JS
3. Créer `test_project_sample_X.py` dans `tests/playwright/`
4. Utiliser le framework Auto-Heal pour les tests

## 📝 Exemple de Structure HTML

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Mon Projet</title>
</head>
<body>
    <!-- Utiliser des sélecteurs stables -->
    <button id="submit" data-testid="submit-btn">
        Soumettre
    </button>
</body>
</html>
```

### Bonnes Pratiques

✅ **À FAIRE**:
- Utiliser `data-testid` pour les tests
- Ajouter des attributs ARIA
- Labels appropriés sur les inputs
- IDs uniques et descriptifs

❌ **À ÉVITER**:
- Sélecteurs basés sur les styles CSS
- Sélecteurs trop génériques
- Éléments sans labels
- Structures trop complexes

