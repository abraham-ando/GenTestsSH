# GenTestsSH - Framework de Tests Auto-Réparants

Framework d'automatisation de tests avec capacités d'auto-réparation, propulsé par Playwright et intégration LLM.

## Resumer

Résumé détaillé de l'architecture et du fonctionnement :

1. Vue d'ensemble
   Ce projet est un framework de tests "Self-Healing" (auto-réparants) pour applications web, construit sur Playwright (Python). Sa particularité est d'utiliser l'IA (LLMs comme OpenAI, Claude, ou LM Studio local) pour détecter quand un test échoue à cause d'un sélecteur CSS obsolète et proposer/appliquer automatiquement une correction.

2. Structure du Projet
   Le projet est organisé de manière modulaire :

sources/gen-tests-self-healing/ (Le Cœur)
C'est le framework lui-même, packagé comme une bibliothèque Python.
Contient la logique d'analyse (llm_analyzer.py), le gestionnaire de patchs (patch_manager.py), et le runner de tests spécialisé (test_runner.py).
Expose une CLI auto-heal.
sources/src/ (Les Projets)
C'est ici que vivent vos projets de tests concrets.
Actuellement contient un exemple : project-sample-1 (avec sans doute des tests d'exemple sur une page de login/dashboard).
docs/ (Documentation)
Documentation très complète : Installation, Démarrage rapide, Architecture multi-projets, Setup LM Studio, etc.
scripts/
Scripts utilitaires pour la maintenance ou le setup. 3. Workflow de "Self-Healing"
Le processus décrit dans la documentation est le suivant :

Exécution : Le test Playwright se lance normalement.
Échec : Si une action (ex: click) échoue, le framework intercepte l'erreur.
Analyse : Il capture le DOM, le screenshot et l'erreur, et envoie le tout au LLM.
Réparation : Le LLM suggère un nouveau sélecteur (plus robuste, ex: data-testid ou un rôle ARIA).
Patch : Le framework modifie votre fichier de test .py automatiquement pour remplacer le sélecteur cassé par le nouveau.
Validation : Le test est relancé pour vérifier que ça passe. 4. État Actuel & Points Forts
Documentation solide : Les fichiers QUICK_START.md et Files dans docs/ sont clairs et bien structurés.
Agnostique au LLM : Compatible avec des modèles locaux (LM Studio) pour la confidentialité ou des modèles puissants (GPT-4/Claude) pour la performance.
Sécurité : Système de backup avant patch et possibilité de review manuelle (confiance threshold).
C'est une base très solide pour construire des suites de tests maintenables.

## 📚 Documentation

- **[Installation Rapide](docs/QUICK_INSTALL.md)** - Guide d'installation pas à pas
- **[Commandes Disponibles](docs/COMMANDES_UTILISABLES.md)** - Toutes les commandes CLI
- **[Guide Multi-Projets](docs/MULTI_PROJECT_STRUCTURE.md)** - Architecture et structure
- **[Configuration LM Studio](docs/LM_STUDIO_SETUP.md)** - Configuration LLM
- **[FAQ](FAQ.md)** - Questions fréquentes
- **[Index Complet](docs/INDEX.md)** - Toute la documentation

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
