#!/usr/bin/env python
"""
Script de vérification de l'installation du framework Gen-Tests-Self-Healing
"""
import sys
import subprocess
from pathlib import Path

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_command(command, description):
    """Check if a command is available"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ {description}")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description}")
            if result.stderr:
                print(f"   Erreur: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description}")
        print(f"   Erreur: {str(e)}")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists"""
    path = Path(filepath)
    if path.exists():
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} (NOT FOUND)")
        return False

def check_directory_structure(base_path, structure, indent=0):
    """Check directory structure recursively"""
    all_ok = True
    for name, content in structure.items():
        path = base_path / name
        prefix = "  " * indent + "├── "
        if isinstance(content, dict):
            # It's a directory
            if path.exists() and path.is_dir():
                print(f"{prefix}✅ {name}/")
                all_ok &= check_directory_structure(path, content, indent + 1)
            else:
                print(f"{prefix}❌ {name}/ (MISSING)")
                all_ok = False
        else:
            # It's a file
            if path.exists() and path.is_file():
                print(f"{prefix}✅ {name}")
            else:
                print(f"{prefix}❌ {name} (MISSING)")
                all_ok = False
    return all_ok

def main():
    """Main verification function"""
    print("\n" + "🔍" * 30)
    print("  Vérification de l'installation GenTestsSH")
    print("🔍" * 30)

    results = []

    # Check Python version
    print_section("1. Environnement Python")
    python_version = sys.version.split()[0]
    print(f"✅ Python version: {python_version}")
    results.append(True)

    # Check framework installation
    print_section("2. Framework Gen-Tests-Self-Healing")
    framework_installed = check_command(
        "pip show gen-tests-self-healing",
        "Framework installé"
    )
    results.append(framework_installed)

    # Check CLI availability
    print_section("3. CLI auto-heal")
    cli_available = check_command(
        "auto-heal --version",
        "Commande auto-heal disponible"
    )
    results.append(cli_available)

    # Check Playwright
    print_section("4. Playwright")
    playwright_installed = check_command(
        "playwright --version",
        "Playwright installé"
    )
    results.append(playwright_installed)

    # Check pytest
    print_section("5. Pytest")
    pytest_installed = check_command(
        "pytest --version",
        "Pytest installé"
    )
    results.append(pytest_installed)

    # Check project structure
    print_section("6. Structure de project-sample-1")
    base_path = Path(__file__).parent / "sources" / "src" / "project-sample-1"

    structure = {
        "src": {
            "index.html": None,
            "dashboard.html": None,
        },
        "tests": {
            "playwright": {
                "test_project_sample_1.py": None,
            }
        },
        "docs": {
            "TESTING.md": None,
        },
        "requirements.txt": None,
        "pytest.ini": None,
        ".gitignore": None,
        "README.md": None,
    }

    if base_path.exists():
        print(f"project-sample-1/")
        structure_ok = check_directory_structure(base_path, structure, 0)
        results.append(structure_ok)
    else:
        print(f"❌ project-sample-1 not found at {base_path}")
        results.append(False)

    # Check framework structure
    print_section("7. Structure du Framework")
    framework_path = Path(__file__).parent / "sources" / "gen-tests-self-healing"

    framework_structure = {
        "framework": {
            "cli.py": None,
            "core": {
                "config.py": None,
                "logger.py": None,
                "test_runner.py": None,
                "patch_manager.py": None,
            },
            "llm": {
                "llm_analyzer.py": None,
            },
        },
        "setup.py": None,
        "README.md": None,
    }

    if framework_path.exists():
        print(f"gen-tests-self-healing/")
        framework_ok = check_directory_structure(framework_path, framework_structure, 0)
        results.append(framework_ok)
    else:
        print(f"❌ Framework not found at {framework_path}")
        results.append(False)

    # Summary
    print_section("RÉSUMÉ")
    total = len(results)
    passed = sum(results)

    print(f"\nTests réussis: {passed}/{total}")

    if all(results):
        print("\n✅ ✅ ✅  TOUT EST OK!  ✅ ✅ ✅")
        print("\nVous pouvez maintenant:")
        print("  1. Créer un nouveau projet: auto-heal create-project mon-projet")
        print("  2. Tester project-sample-1: auto-heal test-project sources/src/project-sample-1")
        print("  3. Vérifier la config: auto-heal config-check")
        return 0
    else:
        print("\n⚠️  QUELQUES PROBLÈMES DÉTECTÉS")
        print("\nPour résoudre:")
        if not framework_installed or not cli_available:
            print("  1. Installer le framework:")
            print("     cd sources/gen-tests-self-healing")
            print("     pip install -e .")
        if not playwright_installed:
            print("  2. Installer Playwright:")
            print("     playwright install")
        if not pytest_installed:
            print("  3. Installer pytest:")
            print("     pip install pytest pytest-playwright")
        return 1

if __name__ == "__main__":
    sys.exit(main())

