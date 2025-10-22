# Exemples d'utilisation avancée

## 1. Test avec Retry personnalisé

```python
from test_runner import AutoHealTestRunner
from playwright.async_api import Page

async def main():
    runner = AutoHealTestRunner()
    await runner.setup()
    
    async def test_complex_interaction(page: Page):
        await page.goto("https://example.com")
        await page.click(".dynamic-button")
        await page.fill("input[name='search']", "test")
        await page.press("input[name='search']", "Enter")
        await page.wait_for_selector(".results")
    
    # Personnaliser le nombre de tentatives
    result = await runner.run_test_with_healing(
        test_complex_interaction, 
        max_retries=5
    )
    
    await runner.teardown()
```

## 2. Analyse manuelle d'échec

```python
from llm_analyzer import LLMAnalyzer

analyzer = LLMAnalyzer()

context = {
    "error": "TimeoutError",
    "message": "Waiting for selector '#submit' failed",
    "url": "https://example.com/login",
    "dom_snapshot": "<html>...</html>",
    "selector": "#submit"
}

patch_info = await analyzer.analyze_failure(context)
print(f"Nouveau sélecteur: {patch_info['selector']}")
print(f"Confiance: {patch_info['confidence']}")
```

## 3. Gestion manuelle des patches

```python
from patch_manager import PatchManager
from pathlib import Path

manager = PatchManager()

# Créer un backup
backup = manager.create_backup(Path("test_login.py"))

# Appliquer un patch
success = manager.apply_patch(
    test_file=Path("test_login.py"),
    line_number=42,
    original_code='await page.click("#submit")',
    patch_code='await page.get_by_role("button", name="Submit").click()',
    patch_info={
        "selector": 'role=button[name="Submit"]',
        "confidence": 0.95,
        "explanation": "Using role-based selector for better stability"
    }
)

# Commit si succès
if success:
    manager.commit_changes(Path("test_login.py"), patch_info)
```

## 4. Configuration programmatique

```python
from config import config

# Modifier la configuration au runtime
config.playwright.headless = False
config.playwright.slow_mo = 100
config.auto_heal.confidence_threshold = 0.8
config.auto_heal.max_retries = 5
config.llm.provider = "anthropic"
```

## 5. Logging personnalisé

```python
from logger import get_logger, get_struct_logger

# Logger standard
logger = get_logger("my_tests")
logger.info("Test started")
logger.error("Test failed", error="Details")

# Logger structuré (JSON)
struct_logger = get_struct_logger("my_tests")
struct_logger.info("test.started", test_name="login", user="admin")
```

## 6. Test avec contexte personnalisé

```python
async def test_with_custom_context():
    runner = AutoHealTestRunner()
    await runner.setup()
    
    # Configurer le contexte du navigateur
    context = await runner.browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Custom User Agent",
        locale="fr-FR",
        timezone_id="Europe/Paris"
    )
    
    page = await context.new_page()
    
    # Votre test ici
    await page.goto("https://example.com")
    
    await page.close()
    await context.close()
    await runner.teardown()
```

## 7. Intégration avec pytest fixtures

```python
import pytest
from test_runner import AutoHealTestRunner

@pytest.fixture(scope="module")
async def auto_heal_runner():
    runner = AutoHealTestRunner()
    await runner.setup()
    yield runner
    await runner.teardown()

@pytest.fixture
async def authenticated_page(auto_heal_runner):
    """Page déjà authentifiée"""
    async def setup_page(page):
        await page.goto("https://example.com/login")
        await page.fill("#username", "admin")
        await page.fill("#password", "password")
        await page.click("#submit")
        return page
    
    page = await auto_heal_runner.context.new_page()
    await setup_page(page)
    yield page
    await page.close()

@pytest.mark.asyncio
async def test_dashboard(auto_heal_runner, authenticated_page):
    async def test_func(page):
        await page.goto("https://example.com/dashboard")
        # Tests...
    
    result = await auto_heal_runner.run_test_with_healing(
        lambda p: test_func(authenticated_page)
    )
    assert result["status"] == "passed"
```

## 8. Monitoring et métriques

```python
import json
from pathlib import Path
from datetime import datetime, timedelta

def analyze_patches(days=7):
    """Analyse des patches des derniers jours"""
    patch_dir = Path("patches")
    cutoff = datetime.now() - timedelta(days=days)
    
    stats = {
        "total": 0,
        "high_confidence": 0,
        "low_confidence": 0,
        "avg_confidence": 0
    }
    
    confidences = []
    
    for patch_file in patch_dir.glob("*.json"):
        with open(patch_file) as f:
            data = json.load(f)
            patch_time = datetime.fromisoformat(data["timestamp"])
            
            if patch_time > cutoff:
                stats["total"] += 1
                confidence = data.get("confidence", 0)
                confidences.append(confidence)
                
                if confidence >= 0.8:
                    stats["high_confidence"] += 1
                else:
                    stats["low_confidence"] += 1
    
    if confidences:
        stats["avg_confidence"] = sum(confidences) / len(confidences)
    
    return stats

# Utilisation
stats = analyze_patches(days=7)
print(f"Patches créés: {stats['total']}")
print(f"Confiance moyenne: {stats['avg_confidence']:.2f}")
```

## 9. Test de régression avec snapshots

```python
import json
from pathlib import Path

async def test_with_snapshot(runner):
    """Test avec snapshot du DOM"""
    async def test_func(page):
        await page.goto("https://example.com")
        
        # Capturer un snapshot
        dom = await page.content()
        snapshot_file = Path("snapshots/page_snapshot.html")
        snapshot_file.parent.mkdir(exist_ok=True)
        snapshot_file.write_text(dom, encoding="utf-8")
        
        # Comparer avec snapshot précédent si existe
        if snapshot_file.exists():
            previous = snapshot_file.read_text(encoding="utf-8")
            if previous != dom:
                print("⚠️ DOM a changé depuis le dernier snapshot")
    
    await runner.run_test_with_healing(test_func)
```

## 10. Parallélisation des tests

```python
import asyncio
from test_runner import AutoHealTestRunner

async def run_parallel_tests():
    """Exécuter plusieurs tests en parallèle"""
    
    async def test_1(runner):
        async def func(page):
            await page.goto("https://example.com/page1")
        return await runner.run_test_with_healing(func)
    
    async def test_2(runner):
        async def func(page):
            await page.goto("https://example.com/page2")
        return await runner.run_test_with_healing(func)
    
    # Créer plusieurs runners
    runners = [AutoHealTestRunner() for _ in range(2)]
    
    # Setup
    await asyncio.gather(*[r.setup() for r in runners])
    
    # Exécuter en parallèle
    results = await asyncio.gather(
        test_1(runners[0]),
        test_2(runners[1])
    )
    
    # Teardown
    await asyncio.gather(*[r.teardown() for r in runners])
    
    return results

# Utilisation
results = asyncio.run(run_parallel_tests())
```
"""
Initialize the Playwright test package
"""
__version__ = "1.0.0"
__author__ = "Auto-Heal Framework"

from .config import config
from .logger import get_logger
from .test_runner import AutoHealTestRunner
from .llm_analyzer import LLMAnalyzer
from .patch_manager import PatchManager

__all__ = [
    "config",
    "get_logger",
    "AutoHealTestRunner",
    "LLMAnalyzer",
    "PatchManager"
]

