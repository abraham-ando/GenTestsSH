# Framework Auto-Healing pour Playwright

Framework Python pour l'auto-correction des tests Playwright avec LLM (LM Studio / OpenAI / Anthropic).

## 🎯 Architecture

```
gen-tests-self-healing/
├── framework/              # Code du framework
│   ├── core/              # Composants principaux
│   │   ├── config.py      # Configuration
│   │   ├── logger.py      # Logging
│   │   ├── patch_manager.py   # Gestion des patches
│   │   └── test_runner.py     # Runner avec auto-heal
│   ├── llm/               # Intégration LLM
│   │   └── llm_analyzer.py    # Analyse et génération
│   └── utils/             # Utilitaires
└── README.md
```

## 📦 Installation

```bash
pip install -e .
```

## 🚀 Utilisation

### Importer le framework

```python
from gen_tests_self_healing.framework.core import AutoHealTestRunner, config
from gen_tests_self_healing.framework.llm import LLMAnalyzer

# Configurer
config.llm.openai_base_url = "http://localhost:1234/v1"
config.llm.openai_model = "openai/gpt-oss-20b"

# Utiliser
runner = AutoHealTestRunner()
await runner.setup()
result = await runner.run_test_with_healing(test_func)
await runner.teardown()
```

### Configuration via .env

```env
# LM Studio (Local)
OPENAI_API_KEY=lm-studio
OPENAI_MODEL=openai/gpt-oss-20b
OPENAI_BASE_URL=http://localhost:1234/v1

# Options
LLM_PROVIDER=openai
AUTO_COMMIT=true
CONFIDENCE_THRESHOLD=0.7
MAX_RETRIES=3
```

## 🔧 Composants

### AutoHealTestRunner
Runner principal avec capacité d'auto-correction.

### LLMAnalyzer
Analyse les échecs de tests et génère des patches via LLM.

### PatchManager
Gère les backups, l'application des patches et l'intégration Git.

### Config
Configuration centralisée avec Pydantic.

## 📚 Documentation

Voir le README principal du projet pour la documentation complète.

## 🤝 Contribution

Ce framework fait partie du projet GenTestsSH.

