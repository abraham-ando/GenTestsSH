# 🎯 COMMANDES À UTILISER - GenTestsSH Multi-Projets

## ✅ L'installation est terminée!

Voici les commandes principales que vous pouvez maintenant utiliser:

---

## 📋 COMMANDES CLI PRINCIPALES

### 1. Créer un Nouveau Projet

```bash
auto-heal create-project mon-nouveau-projet
```

Cette commande crée automatiquement:
- `sources/src/mon-nouveau-projet/`
- Structure complète (src/, tests/, docs/)
- Fichiers de configuration (requirements.txt, pytest.ini, etc.)

### 2. Tester un Projet

```bash
# Tester project-sample-1
auto-heal test-project sources\src\project-sample-1

# Tester votre projet
auto-heal test-project sources\src\mon-nouveau-projet
```

### 3. Vérifier la Configuration

```bash
auto-heal config-check
```

Affiche:
- Configuration LLM (OpenAI, Anthropic, LM Studio)
- Configuration auto-heal
- État de Playwright et pytest

### 4. Voir le Statut

```bash
auto-heal status
```

Affiche:
- Patches récents
- Backups disponibles
- Statistiques

### 5. Exécuter un Test Spécifique

```bash
auto-heal run sources\src\mon-projet\tests\playwright\test_example.py
```

---

## 🏗️ WORKFLOW DE DÉVELOPPEMENT

### Créer et Développer un Nouveau Projet

```bash
# 1. Créer le projet
auto-heal create-project mon-app

# 2. Aller dans le projet
cd sources\src\mon-app

# 3. Ajouter vos fichiers HTML/CSS/JS dans src/
# (Ouvrez sources/src/mon-app/src/ et ajoutez vos fichiers)

# 4. Écrire vos tests dans tests/playwright/
# (Créez des fichiers test_*.py)

# 5. Installer les dépendances du projet
pip install -r requirements.txt

# 6. Lancer les tests
pytest tests\ -v

# Ou avec auto-heal
cd ..\..\..\
auto-heal test-project sources\src\mon-app
```

---

## 🧪 TESTER PLUSIEURS PROJETS

```bash
# Tester tous les projets un par un
auto-heal test-project sources\src\project-sample-1
auto-heal test-project sources\src\mon-projet-1
auto-heal test-project sources\src\mon-projet-2
```

---

## 📊 STRUCTURE D'UN PROJET

Chaque projet créé aura cette structure:

```
mon-projet/
├── src/                    # Vos fichiers sources
│   └── index.html         # (Ajoutez vos fichiers ici)
├── tests/                  # Vos tests
│   └── playwright/
│       └── test_example.py
├── docs/                   # Documentation
├── requirements.txt        # Dépendances
├── pytest.ini             # Config pytest
├── .gitignore             # Fichiers à ignorer
└── README.md              # Documentation
```

---

## 🔧 CONFIGURATION LLM

Si vous voulez utiliser l'auto-healing avec LLM:

### Option 1: LM Studio (Recommandé pour développement local)

Créez/modifiez le fichier `.env` à la racine:

```env
# LM Studio Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=lm-studio
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_MODEL=local-model

# Auto-Heal Configuration
AUTO_HEAL_ENABLED=true
AUTO_COMMIT=false
AUTO_PR=false
CONFIDENCE_THRESHOLD=0.7
MAX_HEALING_RETRIES=3
```

### Option 2: OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-votre-clé-ici
OPENAI_MODEL=gpt-4

AUTO_HEAL_ENABLED=true
AUTO_COMMIT=false
AUTO_PR=false
```

### Option 3: Anthropic

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=votre-clé-ici
ANTHROPIC_MODEL=claude-3-opus-20240229

AUTO_HEAL_ENABLED=true
AUTO_COMMIT=false
AUTO_PR=false
```

---

## 📖 EXEMPLE DE TEST

Créez un fichier `tests/playwright/test_mon_feature.py`:

```python
"""
Tests pour mon projet
"""
import pytest
from pathlib import Path
from playwright.async_api import Page, expect

try:
    from framework.core.test_runner import AutoHealTestRunner
except ImportError:
    import sys
    framework_path = Path(__file__).parent.parent.parent.parent.parent / "gen-tests-self-healing"
    sys.path.insert(0, str(framework_path))
    from framework.core.test_runner import AutoHealTestRunner

BASE_URL = "file://" + str(Path(__file__).parent.parent.parent / "src")

@pytest.fixture
async def runner():
    runner = AutoHealTestRunner()
    await runner.setup()
    yield runner
    await runner.teardown()

async def test_ma_page(runner: AutoHealTestRunner):
    """Test de ma page principale"""
    async def test_func(page: Page):
        await page.goto(f"{BASE_URL}/index.html")
        await expect(page).to_have_title(/Mon Titre/)
        await expect(page.locator("h1")).to_be_visible()
    
    result = await runner.run_test_with_healing(test_func)
    assert result["status"] == "passed"
```

---

## 🚨 COMMANDES DE DÉPANNAGE

### Réinstaller le Framework

```bash
cd sources\gen-tests-self-healing
pip uninstall gen-tests-self-healing -y
pip install -e .
```

### Réinstaller Playwright

```bash
playwright install --force
```

### Vérifier l'Installation

```bash
python verify_installation.py
```

### Nettoyer les Caches

```bash
# Nettoyer les caches Python
rmdir /s /q __pycache__
rmdir /s /q .pytest_cache

# Nettoyer les résultats de tests
rmdir /s /q test-results
rmdir /s /q playwright-report
```

---

## 📚 DOCUMENTATION DISPONIBLE

- **Installation**: `QUICK_INSTALL.md`
- **Multi-Projets**: `docs\MULTI_PROJECT_STRUCTURE.md`
- **Vérification**: `docs\INSTALLATION_VERIFICATION.md`
- **Structure**: `NETTOYAGE_COMPLETE.md`
- **Récapitulatif**: `RESTRUCTURATION_FINALE.md`

---

## 🎯 COMMANDES RAPIDES

```bash
# Créer un projet
auto-heal create-project <nom>

# Tester un projet
auto-heal test-project <chemin>

# Vérifier la config
auto-heal config-check

# Voir le statut
auto-heal status

# Liste des projets
dir sources\src\
```

---

## 🎉 VOUS ÊTES PRÊT!

Tout est maintenant installé et configuré. Vous pouvez:

1. ✅ Créer de nouveaux projets avec `auto-heal create-project`
2. ✅ Tester vos projets avec `auto-heal test-project`
3. ✅ Chaque projet est autonome et indépendant
4. ✅ Le framework est partagé par tous les projets

**Bon développement! 🚀**

