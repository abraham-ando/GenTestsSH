# 📁 Structure Complète du Projet

```
GenTestsSH/
│
├── 📄 README.md                          # Documentation originale du concept
├── 📄 PROJECT_README.md                  # Documentation complète du framework ⭐
├── 📄 QUICK_START.md                     # Guide de démarrage rapide
├── 📄 ADVANCED_EXAMPLES.md               # Exemples d'utilisation avancée
├── 📄 FAQ.md                             # Questions fréquentes
├── 📄 CONTRIBUTING.md                    # Guide de contribution
├── 📄 CHANGELOG.md                       # Historique des versions
├── 📄 LICENSE                            # Licence MIT
│
├── 📄 requirements.txt                   # Dépendances Python
├── 📄 setup.py                           # Installation du package
├── 📄 pytest.ini                         # Configuration pytest
├── 📄 .env.example                       # Exemple de configuration
├── 📄 .gitignore                         # Fichiers à ignorer
│
├── 📁 .github/
│   ├── 📁 workflows/
│   │   └── 📄 tests.yml                 # CI/CD GitHub Actions
│   └── 📁 instructions/                  # Instructions Copilot
│       ├── a11y.instructions.md
│       ├── beastmode.instructions.md
│       ├── follow-up-question.instructions.md
│       └── performance-optimization.instructions.md
│
├── 📁 sources/
│   ├── 📁 src/
│   │   ├── 📄 README.md
│   │   └── 📁 project-sample-1/          # Application web exemple
│   │       ├── 📄 index.html            # Page de connexion
│   │       └── 📄 dashboard.html        # Dashboard
│   │
│   └── 📁 tests/
│       └── 📁 playwright/                # Framework Auto-Heal ⭐
│           ├── 📄 __init__.py           # Package initialization
│           ├── 📄 config.py             # Configuration (Pydantic)
│           ├── 📄 logger.py             # Logging (loguru + structlog)
│           ├── 📄 llm_analyzer.py       # Analyse LLM (OpenAI/Anthropic)
│           ├── 📄 patch_manager.py      # Gestion des patches + Git
│           ├── 📄 test_runner.py        # Runner avec auto-heal
│           ├── 📄 main.py               # Suite de tests Playwright
│           ├── 📄 cli.py                # Interface CLI (Click)
│           └── 📄 README.md
│
└── 📁 .venv/                             # Environnement virtuel (ignoré)

📁 Dossiers créés automatiquement:
├── logs/                                 # Logs d'exécution
├── traces/                               # Traces Playwright (.zip)
├── screenshots/                          # Screenshots d'échecs
├── patches/                              # Métadonnées des patches (.json)
└── backups/                              # Backups des fichiers modifiés
```

## 🎯 Composants Principaux

### 1. **config.py** - Configuration
- Modèles Pydantic pour type safety
- Charge les variables d'environnement
- Crée les dossiers nécessaires
- Configuration Playwright, LLM, Auto-Heal

### 2. **logger.py** - Logging
- Loguru pour logs colorés en console
- Structlog pour logs JSON structurés
- Rotation automatique des logs
- Niveaux de log configurables

### 3. **llm_analyzer.py** - Analyse LLM
- Support OpenAI (GPT-4o-mini, GPT-4)
- Support Anthropic (Claude 3)
- Analyse intelligente des échecs
- Génération de patches Python
- Scoring de confiance

### 4. **patch_manager.py** - Gestion des Patches
- Création automatique de backups
- Application intelligente des patches
- Intégration Git (commit automatique)
- Sauvegarde des métadonnées
- Restauration de backups

### 5. **test_runner.py** - Runner Auto-Heal
- Exécution de tests Playwright
- Capture d'erreurs détaillée
- Tracing et screenshots automatiques
- Retry logic avec healing
- Support async/await

### 6. **main.py** - Tests
- Suite de tests Playwright
- Tests de connexion
- Tests de dashboard
- Tests d'accessibilité
- Intégration auto-heal

### 7. **cli.py** - Interface CLI
- Commande `run` pour exécuter les tests
- Commande `status` pour voir les patches
- Commande `restore` pour restaurer des backups
- Commande `config-check` pour valider la config
- Commande `init` pour initialiser un projet
- Interface Rich colorée

## 📦 Pages HTML Exemples

### index.html - Page de Connexion
- Formulaire avec validation HTML5
- Design moderne et responsive
- Accessibilité WCAG 2.2 complète
- Simulation d'authentification
- Messages d'erreur

### dashboard.html - Dashboard
- Interface utilisateur simple
- Cards pour différentes sections
- Bouton de déconnexion
- Design cohérent

## 🚀 Flux d'Exécution

```
1. Lancer test
   ↓
2. Test échoue (ex: selector #submit introuvable)
   ↓
3. Capture contexte:
   - Erreur + message
   - DOM snapshot
   - Screenshot
   - Trace Playwright
   ↓
4. Envoi au LLM
   ↓
5. LLM analyse et génère:
   - Nouveau sélecteur (ex: button:has-text("Se connecter"))
   - Patch Python
   - Confiance: 0.92
   ↓
6. Vérification confiance > seuil (0.7)
   ↓
7. Backup du fichier original
   ↓
8. Application du patch
   ↓
9. Commit Git (si AUTO_COMMIT=true)
   ↓
10. Re-exécution du test
   ↓
11. ✅ Test réussi !
```

## 🔧 Technologies Utilisées

- **Python 3.10+**: Langage principal
- **Playwright**: Automatisation navigateur
- **OpenAI/Anthropic**: LLM pour analyse
- **Pytest**: Framework de test
- **Click**: Interface CLI
- **Rich**: Affichage console coloré
- **Loguru/Structlog**: Logging avancé
- **Pydantic**: Validation de données
- **GitPython**: Intégration Git
- **dotenv**: Variables d'environnement

## 📊 Métriques et Monitoring

Le framework collecte:
- Nombre de tests exécutés
- Taux de réussite des auto-heals
- Confiance moyenne des patches
- Temps d'exécution
- Nombre de retries
- Historique des modifications

## ✅ Checklist de Vérification

- [x] Configuration complète
- [x] Pages HTML exemples
- [x] Framework auto-heal complet
- [x] Tests Playwright
- [x] Interface CLI
- [x] Logging avancé
- [x] Intégration Git
- [x] Documentation complète
- [x] CI/CD GitHub Actions
- [x] Accessibilité WCAG 2.2
- [x] Exemples avancés
- [x] FAQ
- [x] Guide de contribution

## 🎓 Pour Aller Plus Loin

1. **Personnalisation du LLM**: Modifiez `_build_prompt()` dans `llm_analyzer.py`
2. **Nouveaux providers**: Étendez la classe `LLMAnalyzer`
3. **Métriques custom**: Ajoutez des champs dans les JSON de patch
4. **Dashboard web**: Créez une interface Streamlit pour visualiser les métriques
5. **Tests parallèles**: Utilisez `asyncio.gather()` pour la parallélisation

## 🏆 Prêt à Utiliser !

Le projet est maintenant **100% fonctionnel** et prêt pour:
- Développement local
- Tests automatisés
- Intégration CI/CD
- Production

