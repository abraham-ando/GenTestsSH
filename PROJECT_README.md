# Playwright Auto-Heal Framework

Un framework de tests automatisés avec capacité d'auto-correction utilisant Playwright, Python et LLM (GPT-4 / Claude).

## 🎯 Objectif

Créer des tests Playwright capables de se réparer automatiquement lorsque les sélecteurs deviennent obsolètes, en utilisant l'IA pour analyser les échecs et générer des patches intelligents.

## 🚀 Installation

### Prérequis

- Python 3.10 ou supérieur
- Git
- Clé API OpenAI ou Anthropic

### Installation des dépendances

```bash
# Cloner le repository
git clone <your-repo-url>
cd GenTestsSH

# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Installer les navigateurs Playwright
playwright install chromium
```

### Configuration

1. Copier le fichier `.env.example` vers `.env`:
```bash
copy .env.example .env
```

2. Éditer `.env` et ajouter vos clés API:
```env
OPENAI_API_KEY=sk-votre-cle-ici
LLM_PROVIDER=openai
AUTO_COMMIT=true
CONFIDENCE_THRESHOLD=0.7
```

## 📁 Structure du Projet

```
GenTestsSH/
├── sources/
│   ├── src/
│   │   └── project-sample-1/        # Exemple d'application web
│   │       ├── index.html           # Page de connexion
│   │       └── dashboard.html       # Dashboard
│   └── tests/
│       └── playwright/
│           ├── config.py            # Configuration
│           ├── logger.py            # Logging
│           ├── llm_analyzer.py      # Analyse LLM
│           ├── patch_manager.py     # Gestion des patches
│           ├── test_runner.py       # Runner avec auto-heal
│           ├── main.py              # Tests principaux
│           └── cli.py               # Interface CLI
├── .env.example                     # Exemple de configuration
├── requirements.txt                 # Dépendances Python
├── pytest.ini                       # Configuration pytest
└── README.md
```

## 🎮 Utilisation

### Exécuter les tests

```bash
# Via pytest
pytest sources/tests/playwright/main.py -v

# Via le CLI
python sources/tests/playwright/cli.py run sources/tests/playwright/main.py

# Avec options
python sources/tests/playwright/cli.py run sources/tests/playwright/main.py --max-retries 5 --headed
```

### Commandes CLI

```bash
# Vérifier la configuration
python sources/tests/playwright/cli.py config-check

# Voir le statut des patches
python sources/tests/playwright/cli.py status

# Restaurer un backup
python sources/tests/playwright/cli.py restore backups/main_20241022_120000.py sources/tests/playwright/main.py

# Initialiser un nouveau projet
python sources/tests/playwright/cli.py init
```

## 🔧 Fonctionnement

### 1. Détection d'échec

Lorsqu'un test échoue, le framework capture:
- Type d'erreur et message
- URL de la page
- Snapshot du DOM
- Sélecteur qui a échoué
- Fichier et ligne de code
- Screenshot et trace Playwright

### 2. Analyse LLM

Le contexte est envoyé à un LLM qui:
- Analyse pourquoi le sélecteur a échoué
- Propose un sélecteur alternatif plus robuste
- Génère un patch Python minimal
- Évalue sa confiance (0.0 - 1.0)

### 3. Application du patch

Si la confiance dépasse le seuil configuré:
- Backup du fichier original
- Application du patch
- Commit Git automatique (optionnel)
- Re-exécution du test

### 4. Validation

Le test est relancé automatiquement avec le nouveau sélecteur.

## 📊 Exemple de Patch

**Original (échoué):**
```python
await page.click("#submit")
```

**Après auto-heal:**
```python
await page.get_by_role("button", name="Se connecter").click()
```

## 🎯 Bonnes Pratiques

### Sélecteurs robustes

Le LLM privilégie dans l'ordre:
1. `data-testid` attributes
2. ARIA roles et labels
3. Texte visible
4. Classes sémantiques
5. IDs (en dernier recours)

### Accessibilité (WCAG 2.2 + RGAA 4)

Les tests vérifient:
- Labels appropriés
- Attributs ARIA
- Navigation clavier
- Contraste des couleurs
- Structure sémantique

### Performance

- Cache des résultats LLM
- Traces compressées
- Logs structurés
- Backups automatiques

## 🔍 Monitoring

### Logs

Les logs sont disponibles dans:
```
logs/auto-heal.log
```

### Traces Playwright

Les traces sont sauvegardées dans:
```
traces/trace_<timestamp>.zip
```

Visualiser avec:
```bash
playwright show-trace traces/trace_<timestamp>.zip
```

### Patches

Historique des patches dans:
```
patches/patch_<timestamp>.json
```

## 🧪 Tests Disponibles

### TestLoginPage
- `test_login_success`: Connexion réussie
- `test_login_failure`: Connexion échouée
- `test_form_validation`: Validation HTML5

### TestDashboard
- `test_dashboard_loads`: Chargement du dashboard
- `test_logout_button`: Déconnexion

## 🛡️ Sécurité

- Les clés API ne sont jamais committées
- Les backups sont créés avant chaque modification
- Option de revue manuelle pour faible confiance
- Isolation des tests dans des contextes séparés

## 🔄 CI/CD

Le workflow GitHub Actions:
- Exécute les tests sur Python 3.10, 3.11, 3.12
- Upload des traces et screenshots en cas d'échec
- Sauvegarde des patches générés
- Linting avec Black, Flake8, MyPy

## 📈 Métriques

Le framework track:
- Taux de succès des auto-heals
- Confiance moyenne des patches
- Temps de healing
- Nombre de retries nécessaires

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing`)
3. Commit (`git commit -m '[Auto-Heal] Add feature'`)
4. Push (`git push origin feature/amazing`)
5. Ouvrir une Pull Request

## 📝 License

MIT

## 🙏 Remerciements

- [Playwright](https://playwright.dev/)
- [OpenAI](https://openai.com/)
- [Anthropic](https://anthropic.com/)

## 📞 Support

Pour questions et support:
- Issues GitHub
- Documentation: Voir fichiers MD

---

**Powered by Playwright + Python + LLM** 🚀

