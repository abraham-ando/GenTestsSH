#!/usr/bin/env python
"""
Script d'exécution automatique de toutes les prochaines étapes
"""
import subprocess
import sys
import time
from pathlib import Path

def run_command(command, description, timeout=300):
    """Execute a command and return the result"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    print(f"Commande: {command}\n")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=r"C:\Users\zele.abraham.ando\PycharmProjects\GenTestsSH"
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        if result.returncode == 0:
            print(f"✅ {description} - RÉUSSI")
            return True
        else:
            print(f"❌ {description} - ÉCHOUÉ (code: {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️ {description} - TIMEOUT (dépassé {timeout}s)")
        return False
    except Exception as e:
        print(f"❌ {description} - ERREUR: {str(e)}")
        return False

def main():
    print("\n" + "🚀" * 30)
    print("  EXÉCUTION AUTOMATIQUE DES PROCHAINES ÉTAPES")
    print("🚀" * 30 + "\n")
    
    base_path = Path(r"/")
    results = {}
    
    # Étape 1: Installation du Framework
    print("\n📦 ÉTAPE 1/5: Installation du Framework")
    results['framework'] = run_command(
        "cd sources/gen-tests-self-healing && pip install -e .",
        "Installation du framework",
        timeout=180
    )
    
    if not results['framework']:
        print("\n⚠️ L'installation du framework a échoué. Arrêt du script.")
        return 1
    
    # Étape 2: Installation de Playwright
    print("\n📦 ÉTAPE 2/5: Installation de Playwright")
    results['playwright'] = run_command(
        "playwright install",
        "Installation des navigateurs Playwright",
        timeout=600  # 10 minutes
    )
    
    # Étape 3: Vérification
    print("\n🔍 ÉTAPE 3/5: Vérification de l'installation")
    
    # Vérifier que le package est installé
    print("\nVérification du package gen-tests-self-healing...")
    check_pkg = run_command(
        "pip show gen-tests-self-healing",
        "Vérification du package installé",
        timeout=10
    )

    if not check_pkg:
        print("⚠️ Le package n'est pas installé. Tentative de vérification alternative...")
        results['version'] = False
        results['config'] = False
    else:
        # Vérifier la version avec Python direct (plus fiable)
        print("\nVérification de la commande auto-heal...")
        results['version'] = run_command(
            'python -c "from framework.cli import cli; print(\'CLI importé avec succès\')"',
            "Vérification de l'import du CLI",
            timeout=10
        )

        # Essayer la commande auto-heal si disponible
        if results['version']:
            run_command(
                "auto-heal --version",
                "Test de la commande auto-heal (optionnel)",
                timeout=10
            )

        # Vérifier la configuration
        results['config'] = run_command(
            "python -c \"from framework.core.config import config; print('Config OK')\"",
            "Vérification de la configuration",
            timeout=10
        )

    # Étape 4: Test de project-sample-1
    print("\n🧪 ÉTAPE 4/5: Test de project-sample-1")
    results['test_sample'] = run_command(
        "auto-heal test-project sources/src/project-sample-1",
        "Test du projet sample-1",
        timeout=120
    )
    
    # Étape 5: Créer un projet test
    print("\n🆕 ÉTAPE 5/5: Création d'un projet de validation")
    results['create_project'] = run_command(
        "auto-heal create-project test-validation",
        "Création d'un projet de test",
        timeout=30
    )
    
    # Vérifier que le projet a été créé
    test_project_path = base_path / "sources" / "src" / "test-validation"
    if test_project_path.exists():
        print(f"✅ Projet test-validation créé avec succès: {test_project_path}")
        results['verify_project'] = True
    else:
        print(f"❌ Projet test-validation non trouvé: {test_project_path}")
        results['verify_project'] = False
    
    # Résumé final
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES RÉSULTATS")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n✅ Étapes réussies: {passed}/{total}\n")
    
    for step, success in results.items():
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"  {step.ljust(20)} : {status}")
    
    # Conclusion
    print("\n" + "="*60)
    if all(results.values()):
        print("🎉 TOUTES LES ÉTAPES ONT RÉUSSI!")
        print("="*60)
        print("\n✅ Installation complète terminée avec succès!")
        print("\nVous pouvez maintenant:")
        print("  • Créer des projets: auto-heal create-project <nom>")
        print("  • Tester des projets: auto-heal test-project <chemin>")
        print("  • Vérifier le statut: auto-heal status")
        return 0
    else:
        print("⚠️ CERTAINES ÉTAPES ONT ÉCHOUÉ")
        print("="*60)
        print("\nConsultez les erreurs ci-dessus pour plus de détails.")
        print("\nPour réessayer manuellement:")
        print("  1. Ouvrez QUICK_INSTALL.md")
        print("  2. Suivez les étapes une par une")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        print(f"\n\nScript terminé avec le code: {exit_code}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Script interrompu par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

