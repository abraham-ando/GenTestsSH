@echo off
REM Script de verification et installation pour GenTestsSH

echo ========================================
echo Installation du Framework Gen-Tests-Self-Healing
echo ========================================
echo.

cd /d "%~dp0sources\gen-tests-self-healing"

echo [1/5] Installation du framework...
pip install -e .
if errorlevel 1 (
    echo ERREUR: Installation du framework echouee
    pause
    exit /b 1
)
echo Framework installe avec succes!
echo.

echo [2/5] Installation des navigateurs Playwright...
playwright install
if errorlevel 1 (
    echo ERREUR: Installation de Playwright echouee
    pause
    exit /b 1
)
echo Playwright installe avec succes!
echo.

echo [3/5] Verification de l'installation...
auto-heal --version
if errorlevel 1 (
    echo ERREUR: Commande auto-heal non trouvee
    echo Veuillez redemarrer votre terminal
    pause
    exit /b 1
)
echo.

echo [4/5] Verification de la configuration...
auto-heal config-check
echo.

echo [5/5] Test de project-sample-1...
cd /d "%~dp0"
auto-heal test-project sources/src/project-sample-1
echo.

echo ========================================
echo Installation et verification terminees!
echo ========================================
echo.
echo Commandes disponibles:
echo   - auto-heal create-project ^<nom^>
echo   - auto-heal test-project ^<chemin^>
echo   - auto-heal config-check
echo   - auto-heal status
echo.

pause

