# FAQ - Frequently Asked Questions

## Installation & Setup

### Q: Quelle version de Python est requise ?
**A:** Python 3.10 ou supérieur est requis.

### Q: Puis-je utiliser un autre LLM que OpenAI ?
**A:** Oui ! Le framework supporte OpenAI et Anthropic Claude. Vous pouvez également étendre `LLMAnalyzer` pour supporter d'autres providers.

### Q: Dois-je payer pour l'API OpenAI/Anthropic ?
**A:** Oui, vous avez besoin d'une clé API valide avec des crédits. Les coûts sont généralement faibles (quelques centimes par test).

### Q: Le framework fonctionne-t-il sans clé API ?
**A:** Non, une clé API est nécessaire pour l'analyse LLM. Cependant, vous pouvez utiliser les tests Playwright classiques sans auto-heal.

## Configuration

### Q: Comment changer le seuil de confiance ?
**A:** Dans `.env`, modifiez `CONFIDENCE_THRESHOLD=0.7` (valeurs entre 0.0 et 1.0).

### Q: Puis-je désactiver les commits automatiques ?
**A:** Oui, définissez `AUTO_COMMIT=false` dans `.env`.

### Q: Comment changer le nombre de tentatives ?
**A:** Modifiez `MAX_RETRIES=3` dans `.env` ou passez `max_retries` à `run_test_with_healing()`.

## Utilisation

### Q: Comment tester mon propre site web ?
**A:** Modifiez le `BASE_URL` dans vos tests :
```python
BASE_URL = "https://mon-site.com"
```

### Q: Les tests fonctionnent-ils en mode headless ?
**A:** Oui, par défaut. Changez `HEADLESS=false` pour voir le navigateur.

### Q: Puis-je utiliser Firefox ou Safari ?
**A:** Oui, modifiez `test_runner.py` :
```python
self.browser = await self.playwright.firefox.launch()
# ou
self.browser = await self.playwright.webkit.launch()
```

### Q: Comment visualiser les traces Playwright ?
**A:** Utilisez la commande :
```bash
playwright show-trace traces/trace_<timestamp>.zip
```

## Dépannage

### Q: "Module 'openai' not found"
**A:** Installez les dépendances :
```bash
pip install -r requirements.txt
```

### Q: "Playwright not installed"
**A:** Installez les navigateurs :
```bash
playwright install chromium
```

### Q: Les tests échouent avec "No API key"
**A:** Vérifiez que `.env` contient votre clé API et que le fichier est bien à la racine du projet.

### Q: Le patch n'est pas appliqué
**A:** Vérifiez :
- La confiance est au-dessus du seuil (`CONFIDENCE_THRESHOLD`)
- Le fichier de test existe et est accessible en écriture
- Les permissions du système de fichiers

### Q: Git commit échoue
**A:** Assurez-vous que :
- Git est initialisé (`git init`)
- Le fichier n'est pas déjà staged avec des conflits
- Vous avez configuré git user.name et user.email

## Performance

### Q: Les tests sont lents
**A:** 
- Utilisez `HEADLESS=true`
- Réduisez `SLOW_MO=0`
- Augmentez les timeouts si nécessaire
- Utilisez des sélecteurs plus spécifiques

### Q: L'analyse LLM prend du temps
**A:** 
- C'est normal (1-3 secondes par analyse)
- Utilisez `gpt-4o-mini` au lieu de `gpt-4` pour plus de rapidité
- Considérez un cache local pour les analyses répétitives

### Q: Trop de traces/screenshots occupent de l'espace
**A:** Nettoyez régulièrement :
```bash
# Windows
del /q traces\*.zip
del /q screenshots\*.png

# Linux/Mac
rm -f traces/*.zip
rm -f screenshots/*.png
```

## Sécurité

### Q: Ma clé API est-elle sécurisée ?
**A:** 
- Ne committez JAMAIS `.env` dans Git
- Utilisez des secrets dans CI/CD
- Limitez les permissions de la clé API
- Rotez régulièrement les clés

### Q: Les patches peuvent-ils introduire des bugs ?
**A:** 
- Oui, c'est pourquoi il y a un seuil de confiance
- Les backups sont créés automatiquement
- Revoyez les patches manuellement si confiance < 0.8
- Testez toujours après un patch

## Intégration CI/CD

### Q: Comment utiliser dans GitHub Actions ?
**A:** Le workflow est déjà fourni dans `.github/workflows/tests.yml`. Ajoutez votre clé API dans les secrets GitHub.

### Q: Puis-je utiliser avec GitLab CI ?
**A:** Oui, adaptez le workflow GitHub Actions pour GitLab CI :
```yaml
test:
  image: mcr.microsoft.com/playwright/python:v1.40.0
  script:
    - pip install -r requirements.txt
    - pytest sources/tests/playwright/main.py -v
```

### Q: Comment gérer les secrets en CI ?
**A:** Utilisez les secrets de votre plateforme CI :
- GitHub: Repository Settings > Secrets
- GitLab: Settings > CI/CD > Variables
- Azure: Pipelines > Library > Variable groups

## Avancé

### Q: Puis-je personnaliser le prompt LLM ?
**A:** Oui, modifiez `_build_prompt()` dans `llm_analyzer.py`.

### Q: Comment ajouter des métriques personnalisées ?
**A:** Étendez `PatchManager` pour logger des métriques supplémentaires dans les fichiers JSON de patch.

### Q: Puis-je utiliser plusieurs LLM providers simultanément ?
**A:** Oui, créez plusieurs instances de `LLMAnalyzer` avec des configurations différentes et comparez les résultats.

### Q: Comment débugger un patch qui ne fonctionne pas ?
**A:** 
1. Vérifiez les logs dans `logs/auto-heal.log`
2. Inspectez le JSON de patch dans `patches/`
3. Examinez les traces Playwright
4. Restaurez le backup et testez manuellement

## Support

### Q: Où puis-je obtenir de l'aide ?
**A:** 
- GitHub Issues pour les bugs
- Discussions pour les questions
- Documentation dans les fichiers MD

### Q: Comment contribuer au projet ?
**A:** Lisez `CONTRIBUTING.md` et ouvrez une Pull Request !

### Q: Le projet est-il maintenu ?
**A:** Oui, consultez `CHANGELOG.md` pour les mises à jour.

