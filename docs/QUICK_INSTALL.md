# 🚀 Guide d'Installation Rapide - GenTestsSH

## Étape 1: Installation du Framework

Ouvrez un terminal et exécutez les commandes suivantes **une par une**:

```bash
# Naviguer vers le dossier du framework
cd C:\Users\zele.abraham.ando\PycharmProjects\GenTestsSH\sources\gen-tests-self-healing

# Installer le framework
pip install -e .
```

**Attendez que l'installation se termine** (cela peut prendre 1-2 minutes).

## Étape 2: Installation de Playwright

```bash
# Installer les navigateurs Playwright
playwright install
```

**Attendez que l'installation se termine** (cela peut prendre 5-10 minutes).

## Étape 3: Vérification

```bash
# Retourner à la racine
cd C:\Users\zele.abraham.ando\PycharmProjects\GenTestsSH

# Vérifier que auto-heal fonctionne
auto-heal --version

# Vérifier la configuration
auto-heal config-check
```

## Étape 4: Test de project-sample-1

```bash
# Tester le projet exemple
auto-heal test-project sources\src\project-sample-1
```

## Étape 5: Créer votre premier projet

```bash
# Créer un nouveau projet
auto-heal create-project mon-premier-projet

# Vérifier que le projet a été créé
dir sources\src\mon-premier-projet
```

## 📋 Résolution de Problèmes

### Si "auto-heal: command not found"
1. Vérifiez que l'installation du framework a réussi:
   ```bash
   pip show gen-tests-self-healing
   ```
2. Si le package n'est pas trouvé, réinstallez:
   ```bash
   cd sources\gen-tests-self-healing
   pip install -e .
   ```
3. Redémarrez votre terminal

### Si "No module named 'framework'"
Le framework n'est pas installé correctement. Réinstallez:
```bash
cd sources\gen-tests-self-healing
pip uninstall gen-tests-self-healing -y
pip install -e .
```

### Si les tests ne fonctionnent pas
1. Vérifiez que Playwright est installé:
   ```bash
   playwright --version
   ```
2. Si non installé:
   ```bash
   playwright install
   ```
   
## 🎯 Commandes Principales

```bash
# Créer un projet
auto-heal create-project <nom>

# Tester un projet
auto-heal test-project <chemin>

# Vérifier la config
auto-heal config-check

# Voir le statut
auto-heal status

# Exécuter un test
auto-heal run <test-file>
```

---

**Bon développement! 🚀**

