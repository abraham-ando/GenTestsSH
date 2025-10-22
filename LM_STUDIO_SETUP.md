# Guide de Configuration LM Studio

## 🎯 Configuration Complète pour Utiliser LM Studio

Votre projet est maintenant configuré pour utiliser **LM Studio** avec le modèle **openai/gpt-oss-20b** en local !

---

## ✅ Étape 1: Vérifier LM Studio

### Lancer LM Studio
1. Ouvrez **LM Studio**
2. Assurez-vous que le modèle `openai/gpt-oss-20b` est bien téléchargé
3. Chargez le modèle dans LM Studio

### Activer le Serveur Local
1. Dans LM Studio, allez dans l'onglet **"Local Server"** ou **"Developer"**
2. Cliquez sur **"Start Server"**
3. Vérifiez que le serveur démarre sur `http://localhost:1234`
4. Le modèle devrait être prêt à recevoir des requêtes

---

## ✅ Étape 2: Configuration du Projet (DÉJÀ FAIT ✓)

Votre fichier `.env` a été automatiquement mis à jour avec :

```env
# LM Studio Configuration (Local Model)
OPENAI_API_KEY=lm-studio
OPENAI_MODEL=openai/gpt-oss-20b
OPENAI_BASE_URL=http://localhost:1234/v1

# LLM Provider
LLM_PROVIDER=openai
```

**Points importants :**
- ✅ `OPENAI_API_KEY=lm-studio` : Clé factice (LM Studio n'en a pas besoin)
- ✅ `OPENAI_MODEL=openai/gpt-oss-20b` : Votre modèle local
- ✅ `OPENAI_BASE_URL=http://localhost:1234/v1` : URL du serveur LM Studio
- ✅ `LLM_PROVIDER=openai` : Utilise l'API compatible OpenAI

---

## ✅ Étape 3: Modifications du Code (DÉJÀ FAIT ✓)

J'ai mis à jour automatiquement :

### 1. `config.py`
- Ajout du champ `openai_base_url` pour supporter LM Studio

### 2. `llm_analyzer.py`
- Détection automatique de LM Studio via `OPENAI_BASE_URL`
- Configuration de `openai.api_base` pour pointer vers votre serveur local
- Logs informatifs pour confirmer l'utilisation de LM Studio

---

## 🚀 Étape 4: Tester la Configuration

### Test 1: Vérifier la configuration
```bash
python sources\tests\playwright\cli.py config-check
```

Vous devriez voir :
```
✓ LM Studio mode detected - using local model
✓ Model configured: openai/gpt-oss-20b
✓ Using custom OpenAI base URL: http://localhost:1234/v1
```

### Test 2: Lancer un test simple
```bash
python sources\tests\playwright\test_runner.py
```

### Test 3: Lancer la suite complète
```bash
pytest sources\tests\playwright\main.py -v
```

---

## 🔍 Vérification du Serveur LM Studio

### Test manuel de l'API
Ouvrez PowerShell et exécutez :

```powershell
# Test de santé du serveur
curl http://localhost:1234/v1/models

# Devrait retourner quelque chose comme :
# {"data": [{"id": "openai/gpt-oss-20b", ...}]}
```

Ou avec Python :
```python
import requests
response = requests.get("http://localhost:1234/v1/models")
print(response.json())
```

---

## ⚙️ Paramètres LM Studio Recommandés

Dans LM Studio, pour le modèle GPT-OSS-20B :

### Paramètres de Génération
- **Temperature**: 0.0 - 0.2 (pour des réponses déterministes)
- **Max Tokens**: 1000 - 2000
- **Top P**: 0.9
- **Context Length**: 4096 ou plus

### Paramètres Serveur
- **Port**: 1234 (par défaut)
- **CORS**: Activé si nécessaire
- **API Key**: Pas nécessaire pour local

---

## 🎯 Avantages de LM Studio

✅ **Gratuit** - Pas de frais API  
✅ **Privé** - Données restent en local  
✅ **Rapide** - Pas de latence réseau  
✅ **Offline** - Fonctionne sans Internet  
✅ **Illimité** - Pas de limite de requêtes  

---

## 🐛 Dépannage

### Erreur: "Connection refused"
**Solution**: Vérifiez que le serveur LM Studio est démarré
```bash
# Dans LM Studio: Start Server
```

### Erreur: "Model not found"
**Solution**: Vérifiez que le nom du modèle dans `.env` correspond exactement à celui dans LM Studio
```env
OPENAI_MODEL=openai/gpt-oss-20b  # Doit correspondre exactement
```

### Erreur: "Timeout"
**Solution**: Le modèle 20B peut être lent. Augmentez le timeout :
```env
TIMEOUT=60000  # 60 secondes au lieu de 30
```

### Port différent de 1234
**Solution**: Si LM Studio utilise un autre port, mettez à jour :
```env
OPENAI_BASE_URL=http://localhost:VOTRE_PORT/v1
```

---

## 📊 Comparaison des Performances

| Critère | LM Studio (Local) | OpenAI API |
|---------|-------------------|------------|
| Coût | Gratuit ✅ | ~$0.001/requête |
| Vitesse | 2-5s (selon GPU) | 1-2s |
| Confidentialité | 100% privé ✅ | Cloud |
| Disponibilité | Offline ✅ | Internet requis |
| Qualité | Bon (20B params) | Excellent (GPT-4) |

---

## 🔄 Basculer entre LM Studio et OpenAI

### Pour utiliser LM Studio (actuel)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=lm-studio
OPENAI_MODEL=openai/gpt-oss-20b
OPENAI_BASE_URL=http://localhost:1234/v1
```

### Pour revenir à OpenAI API
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-votre-vraie-cle-api
OPENAI_MODEL=gpt-4o-mini
# OPENAI_BASE_URL=  # Commenter ou laisser vide
```

### Pour utiliser Anthropic Claude
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=votre-cle-anthropic
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

---

## ✅ Checklist de Configuration

- [x] LM Studio installé
- [x] Modèle `openai/gpt-oss-20b` téléchargé
- [ ] **Serveur LM Studio démarré** ⚠️ (À FAIRE MAINTENANT)
- [x] Fichier `.env` configuré
- [x] Code mis à jour pour supporter LM Studio
- [ ] Test de connexion réussi
- [ ] Premier test auto-heal exécuté

---

## 🚀 Prochaine Étape

**MAINTENANT:** Lancez le serveur LM Studio et testez !

```bash
# 1. Dans LM Studio: Start Server (port 1234)

# 2. Vérifiez la configuration
python sources\tests\playwright\cli.py config-check

# 3. Lancez un test
python sources\tests\playwright\test_runner.py
```

---

**Vous êtes prêt !** Le framework utilisera maintenant votre modèle local GPT-OSS-20B au lieu de l'API OpenAI. 🎉

---

**Note**: Si vous avez des questions ou rencontrez des problèmes, consultez la section Dépannage ci-dessus.

