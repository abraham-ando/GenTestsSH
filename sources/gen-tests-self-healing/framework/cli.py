"""
CLI for Gen-Tests-Self-Healing Framework
"""
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import json

from framework.core.config import config
from framework.core.logger import get_logger
from framework.core.patch_manager import PatchManager

logger = get_logger(__name__)
console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Gen-Tests-Self-Healing Framework CLI

    A framework for self-healing test automation with Playwright and LLM integration.
    """
    pass


@cli.command()
@click.argument('test_file', type=click.Path(exists=True))
@click.option('--max-retries', '-r', default=3, help='Maximum healing attempts')
@click.option('--headless/--headed', default=True, help='Run browser in headless mode')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def run(test_file: str, max_retries: int, headless: bool, debug: bool):
    """Run tests with auto-heal capability"""

    console.print(Panel.fit(
        "[bold cyan]Gen-Tests-Self-Healing Framework[/bold cyan]\n"
        f"Running tests from: {test_file}",
        border_style="cyan"
    ))

    # Update config
    config.playwright.headless = headless
    config.auto_heal.max_retries = max_retries

    if debug:
        logger.level("DEBUG")

    # Run tests
    try:
        console.print("\n[yellow]Starting test execution...[/yellow]")

        # Configure OpenTelemetry
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource

        resource = Resource.create({"service.name": "auto-heal-cli"})
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317"))
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)

        # Run pytest
        import pytest
        exit_code = pytest.main([test_file, "-v", "--tb=short"])

        if exit_code == 0:
            console.print("\n[green]✓ All tests passed![/green]")
        else:
            console.print("\n[red]✗ Some tests failed[/red]")

        sys.exit(exit_code)

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--headless/--headed', default=True, help='Run browser in headless mode')
def test_project(project_path: str, headless: bool):
    """Run all tests for a specific project"""
    
    project_dir = Path(project_path).resolve()
    test_dir = project_dir / "tests"
    
    if not test_dir.exists():
        console.print(f"[red]✗ No tests directory found in {project_dir}[/red]")
        sys.exit(1)
    
    console.print(Panel.fit(
        f"[bold cyan]Testing Project: {project_dir.name}[/bold cyan]\n"
        f"Test directory: {test_dir}",
        border_style="cyan"
    ))
    
    # Update config
    config.playwright.headless = headless
    
    # Run pytest on the project's test directory
    try:
        import pytest
        exit_code = pytest.main([str(test_dir), "-v", "--tb=short"])
        
        if exit_code == 0:
            console.print(f"\n[green]SUCCESS: All tests passed for {project_dir.name}![/green]")
        else:
            console.print(f"\n[red]FAILED: Some tests failed for {project_dir.name}[/red]")
        
        sys.exit(exit_code)
        
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--show-backups', is_flag=True, help='Show backup files')
def status(show_backups: bool):
    """Show status of patches and backups"""

    console.print(Panel.fit(
        "[bold cyan]Auto-Heal Framework Status[/bold cyan]",
        border_style="cyan"
    ))

    # Show patches
    patch_dir = config.auto_heal.patch_dir
    patches = list(patch_dir.glob("*.json"))

    if patches:
        table = Table(title="Recent Patches", show_header=True)
        table.add_column("Timestamp", style="cyan")
        table.add_column("Test File", style="yellow")
        table.add_column("Confidence", style="green")

        for patch_file in sorted(patches, reverse=True)[:10]:
            with open(patch_file, 'r') as f:
                data = json.load(f)
                table.add_row(
                    data.get("timestamp", "Unknown")[:19],
                    Path(data.get("test_file", "Unknown")).name,
                    f"{data.get('confidence', 0):.2f}"
                )

        console.print(table)
    else:
        console.print("\n[yellow]No patches found[/yellow]")

    # Show backups if requested
    if show_backups:
        backup_dir = config.auto_heal.backup_dir
        backups = list(backup_dir.glob("*.py"))

        if backups:
            console.print(f"\n[cyan]Backups:[/cyan] {len(backups)} files in {backup_dir}")
        else:
            console.print("\n[yellow]No backups found[/yellow]")


@cli.command()
@click.argument('backup_file', type=click.Path(exists=True))
@click.argument('target_file', type=click.Path())
def restore(backup_file: str, target_file: str):
    """Restore a test file from backup"""

    manager = PatchManager()
    success = manager.restore_backup(Path(backup_file), Path(target_file))

    if success:
        console.print(f"[green]✓ Restored {target_file} from backup[/green]")
    else:
        console.print(f"[red]✗ Failed to restore backup[/red]")
        sys.exit(1)


@cli.command()
def config_check():
    """Check configuration and dependencies"""

    console.print(Panel.fit(
        "[bold cyan]Configuration Check[/bold cyan]",
        border_style="cyan"
    ))

    # Check LLM configuration
    table = Table(show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_column("Status", style="green")

    # LLM Config
    table.add_row(
        "LLM Provider",
        config.llm.provider,
        "✓" if config.llm.provider in ["openai", "anthropic"] else "✗"
    )

    if config.llm.provider == "openai":
        has_key = bool(config.llm.openai_api_key)
        table.add_row(
            "OpenAI API Key",
            "***" + config.llm.openai_api_key[-4:] if has_key else "Not set",
            "✓" if has_key else "✗"
        )

        # Check for LM Studio
        if config.llm.openai_base_url:
            table.add_row(
                "OpenAI Base URL",
                config.llm.openai_base_url,
                "✓ (LM Studio mode)"
            )
            table.add_row(
                "Model",
                config.llm.openai_model,
                "✓"
            )
    elif config.llm.provider == "anthropic":
        has_key = bool(config.llm.anthropic_api_key)
        table.add_row(
            "Anthropic API Key",
            "***" + config.llm.anthropic_api_key[-4:] if has_key else "Not set",
            "✓" if has_key else "✗"
        )

    # Auto-Heal Config
    table.add_row("Auto-Commit", str(config.auto_heal.auto_commit), "✓")
    table.add_row("Auto-PR", str(config.auto_heal.auto_pr), "✓")
    table.add_row("Confidence Threshold", str(config.auto_heal.confidence_threshold), "✓")
    table.add_row("Max Retries", str(config.auto_heal.max_retries), "✓")

    console.print(table)

    # Check Playwright
    console.print("\n[cyan]Checking Playwright installation...[/cyan]")
    try:
        from playwright.sync_api import sync_playwright
        console.print("[green]✓ Playwright is installed[/green]")
    except ImportError:
        console.print("[red]✗ Playwright is not installed. Run: playwright install[/red]")

    # Check pytest
    console.print("\n[cyan]Checking pytest installation...[/cyan]")
    try:
        import pytest
        console.print(f"[green]✓ pytest {pytest.__version__} is installed[/green]")
    except ImportError:
        console.print("[red]✗ pytest is not installed[/red]")


@cli.command()
@click.option('--port', default=8080, help='Port to run the UI on')
def ui(port: int):
    """Start the Agent Dev UI"""
    from framework.ui.dev_ui import start_dev_ui
    try:
        start_dev_ui(port)
    except Exception as e:
        console.print(f"[red]Failed to start UI: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('project_name')
@click.option('--path', default='sources/src', help='Base path for projects')
def create_project(project_name: str, path: str):
    """Create a new autonomous project structure"""
    
    base_path = Path(path)
    project_path = base_path / project_name
    
    if project_path.exists():
        console.print(f"[red]✗ Project {project_name} already exists at {project_path}[/red]")
        sys.exit(1)
    
    console.print(f"[cyan]Creating project structure for {project_name}...[/cyan]")
    
    # Create project directories
    directories = [
        project_path,
        project_path / "src",
        project_path / "tests",
        project_path / "tests" / "playwright",
        project_path / "docs",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        console.print(f"  [green]+[/green] Created {directory.relative_to(base_path)}")
    
    # Create project files
    files_content = {
        "README.md": f"""# {project_name}

## Description

This is an autonomous project using the Gen-Tests-Self-Healing framework.

## Structure

```
{project_name}/
├── src/                    # Source files (HTML, CSS, JS, etc.)
├── tests/                  # Test files
│   └── playwright/         # Playwright tests
├── docs/                   # Documentation
├── requirements.txt        # Project dependencies
├── pytest.ini             # Pytest configuration
└── README.md              # This file
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with auto-heal
auto-heal test-project .

# Run specific test
pytest tests/playwright/test_example.py -v
```

## Development

Add your HTML/web files in `src/` and your Playwright tests in `tests/playwright/`.
""",
        "requirements.txt": """# Gen-Tests-Self-Healing Framework
gen-tests-self-healing>=1.0.0

# Testing
pytest>=8.0.0
pytest-playwright>=0.4.0
pytest-asyncio>=0.23.0
playwright>=1.40.0
""",
        "pytest.ini": f"""[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
asyncio_mode = auto
""",
        ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# Playwright
test-results/
playwright-report/
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/
traces/
screenshots/

# Auto-heal
patches/
backups/
""",
        "tests/playwright/test_example.py": """\"\"\"
Example Playwright test for {project_name}
\"\"\"
import pytest
from playwright.sync_api import Page, expect


def test_example(page: Page):
    \"\"\"Example test - replace with your actual tests\"\"\"
    # Navigate to your page
    page.goto("file://" + str(Path(__file__).parent.parent.parent / "src" / "index.html"))
    
    # Add your test assertions here
    expect(page).to_have_title(/{project_name}/i)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
    }
    
    for file_path, content in files_content.items():
        full_path = project_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        console.print(f"  [green]+[/green] Created {full_path.relative_to(base_path)}")
    
    console.print(f"\n[green]SUCCESS: Project {project_name} created successfully![/green]")
    console.print(f"\n[cyan]Next steps:[/cyan]")
    console.print(f"  1. cd {project_path}")
    console.print(f"  2. Add your web files to src/")
    console.print(f"  3. Write your tests in tests/playwright/")
    console.print(f"  4. Run: auto-heal test-project .")


if __name__ == '__main__':
    cli()

