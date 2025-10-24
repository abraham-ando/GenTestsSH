# GenTestsSH - Framework de Tests Auto-Réparants

Framework d'automatisation de tests avec capacités d'auto-réparation, propulsé par Playwright et intégration LLM.

## 🚀 Démarrage Rapide

```bash
# 1. Installer le framework
cd sources/gen-tests-self-healing
pip install -e .
playwright install

# 2. Créer votre premier projet
auto-heal create-project mon-projet

# 3. Tester votre projet
auto-heal test-project sources/src/mon-projet
```

## 📚 Documentation

- **[Installation Rapide](docs/QUICK_INSTALL.md)** - Guide d'installation pas à pas
- **[Commandes Disponibles](docs/COMMANDES_UTILISABLES.md)** - Toutes les commandes CLI
- **[Guide Multi-Projets](docs/MULTI_PROJECT_STRUCTURE.md)** - Architecture et structure
- **[Configuration LM Studio](docs/LM_STUDIO_SETUP.md)** - Configuration LLM
- **[FAQ](FAQ.md)** - Questions fréquentes
- **[Index Complet](docs/INDEX.md)** - Toute la documentation

## 🎯 Commandes Principales

```bash
auto-heal create-project <nom>      # Créer un nouveau projet
auto-heal test-project <chemin>     # Tester un projet
auto-heal config-check              # Vérifier la configuration
auto-heal status                    # Voir le statut
auto-heal --help                    # Aide complète
```

## 📁 Structure du Projet

```
GenTestsSH/
├── sources/
│   ├── gen-tests-self-healing/    # Framework (partagé)
│   └── src/                       # Vos projets (autonomes)
│       ├── project-sample-1/
│       └── [vos-projets]/
├── docs/                          # Documentation
└── README.md                      # Ce fichier
```

## ✨ Fonctionnalités

- ✅ Tests Playwright avec auto-réparation
- ✅ Intégration LLM (OpenAI, Anthropic, LM Studio)
- ✅ Architecture multi-projets autonomes
- ✅ CLI puissant et intuitif
- ✅ Génération automatique de patches
- ✅ Gestion des backups et historique

## 🔧 Configuration

Le framework supporte plusieurs providers LLM:

- **LM Studio** (recommandé pour développement local)
- **OpenAI** (GPT-4, GPT-3.5)
- **Anthropic** (Claude)

Voir [LM_STUDIO_SETUP.md](docs/LM_STUDIO_SETUP.md) pour la configuration.

## 📖 Plus d'Informations

Consultez la [documentation complète](docs/INDEX.md) pour plus de détails.

## 📝 Licence

MIT License - voir [LICENSE](LICENSE)

