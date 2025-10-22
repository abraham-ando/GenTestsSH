"""
CLI for Playwright Auto-Heal Framework
"""
import asyncio
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from test_runner import AutoHealTestRunner
from logger import get_logger

logger = get_logger(__name__)
console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Playwright Auto-Heal Framework CLI

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
        "[bold cyan]Playwright Auto-Heal Framework[/bold cyan]\n"
        f"Running tests from: {test_file}",
        border_style="cyan"
    ))

    # Update config
    from config import config
    config.playwright.headless = headless
    config.auto_heal.max_retries = max_retries

    if debug:
        logger.level("DEBUG")

    # Run tests
    try:
        # Import and run the test file
        console.print("\n[yellow]Starting test execution...[/yellow]")

        # For now, run pytest
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
@click.option('--show-backups', is_flag=True, help='Show backup files')
def status(show_backups: bool):
    """Show status of patches and backups"""

    from config import config

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

        import json
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

    from patch_manager import PatchManager

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

    from config import config

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
        import playwright
        try:
            version = playwright.__version__
        except AttributeError:
            version = "installed"
        console.print(f"[green]✓ Playwright {version}[/green]")
    except ImportError:
        console.print("[red]✗ Playwright not installed[/red]")


@cli.command()
def init():
    """Initialize a new auto-heal project"""

    console.print(Panel.fit(
        "[bold cyan]Initialize Auto-Heal Project[/bold cyan]",
        border_style="cyan"
    ))

    # Create .env file
    env_file = Path(".env")
    if not env_file.exists():
        import shutil
        example_path = Path(__file__).parent.parent.parent.parent / ".env.example"
        if example_path.exists():
            shutil.copy(example_path, env_file)
            console.print("[green]✓ Created .env file[/green]")
        else:
            console.print("[yellow]⚠ .env.example not found[/yellow]")
    else:
        console.print("[yellow]⚠ .env file already exists[/yellow]")

    # Create directories
    from config import config
    config._create_directories()
    console.print("[green]✓ Created necessary directories[/green]")

    # Initialize git if not exists
    try:
        import git
        git.Repo(search_parent_directories=True)
        console.print("[green]✓ Git repository found[/green]")
    except git.InvalidGitRepositoryError:
        if click.confirm("Initialize Git repository?"):
            git.Repo.init()
            console.print("[green]✓ Git repository initialized[/green]")
    except ImportError:
        console.print("[yellow]⚠ GitPython not installed[/yellow]")

    console.print("\n[bold green]✓ Project initialized![/bold green]")
    console.print("\nNext steps:")
    console.print("1. Edit .env file with your API keys")
    console.print("2. Run: python sources\\tests\\playwright\\cli.py config-check")
    console.print("3. Run: python sources\\tests\\playwright\\cli.py run tests/test_file.py")


if __name__ == "__main__":
    cli()

