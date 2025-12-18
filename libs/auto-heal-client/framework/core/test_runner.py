"""
Test Runner with Auto-Heal capabilities
"""
import asyncio
import traceback
import inspect
from typing import Optional, Dict, Any
from pathlib import Path
from playwright.async_api import async_playwright, Page, Error as PlaywrightError

from .config import config
from .logger import get_logger
from .client import BackendClient
from .patch_manager import PatchManager

logger = get_logger(__name__)


class AutoHealTestRunner:
    """Test runner with automatic healing capabilities"""

    def __init__(self):
        self.client = BackendClient()
        self.patch_manager = PatchManager()
        self.playwright = None
        self.browser = None
        self.context = None

    async def setup(self):
        """Setup Playwright browser"""
        logger.info("Setting up Playwright...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=config.playwright.headless,
            slow_mo=config.playwright.slow_mo
        )
        self.context = await self.browser.new_context()

        # Enable tracing
        await self.context.tracing.start(screenshots=True, snapshots=True, sources=True)
        logger.info("Playwright setup complete")

    async def teardown(self):
        """Teardown Playwright browser"""
        if self.context:
            # Save trace
            trace_path = config.playwright.trace_dir / f"trace_{asyncio.get_event_loop().time()}.zip"
            await self.context.tracing.stop(path=str(trace_path))
            logger.info(f"Trace saved: {trace_path}")

        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()

        if self.client:
            await self.client.close()

        logger.info("Playwright teardown complete")

    async def run_test_with_healing(
        self,
        test_func,
        max_retries: int = None
    ) -> Dict[str, Any]:
        """
        Run test with automatic healing on failure

        Args:
            test_func: Test function to run
            max_retries: Maximum number of healing attempts

        Returns:
            Dictionary with test results
        """
        if max_retries is None:
            max_retries = config.auto_heal.max_retries

        retry_count = 0
        last_error = None

        while retry_count <= max_retries:
            try:
                page = await self.context.new_page()

                # Run the test
                if asyncio.iscoroutinefunction(test_func):
                    await test_func(page)
                else:
                    test_func(page)

                logger.success(f"Test '{test_func.__name__}' passed")
                await page.close()

                return {
                    "status": "passed",
                    "retries": retry_count,
                    "test_name": test_func.__name__
                }

            except Exception as e:
                last_error = e
                logger.error(f"Test '{test_func.__name__}' failed: {e}")

                if retry_count >= max_retries:
                    logger.error(f"Max retries ({max_retries}) reached. Giving up.")
                    break

                # Capture failure context
                context = await self._capture_failure_context(page, e, test_func)

                # Take screenshot
                screenshot_path = config.playwright.screenshot_dir / f"failure_{test_func.__name__}_{retry_count}.png"
                await page.screenshot(path=str(screenshot_path))
                context["screenshot"] = str(screenshot_path)

                await page.close()

                # Analyze and attempt to heal
                healed = await self._attempt_heal(context)

                if not healed:
                    logger.error("Healing failed. Stopping retries.")
                    break

                retry_count += 1
                logger.info(f"Retry {retry_count}/{max_retries}")

        return {
            "status": "failed",
            "retries": retry_count,
            "test_name": test_func.__name__,
            "error": str(last_error)
        }

    async def _capture_failure_context(
        self,
        page: Page,
        error: Exception,
        test_func
    ) -> Dict[str, Any]:
        """Capture context when test fails"""
        try:
            # Get DOM snapshot
            dom_snapshot = await page.content()

            # Get test file and line number
            test_file, line_number, original_code = self._get_test_location(test_func, error)

            # Extract failed selector from error message
            selector = self._extract_selector_from_error(str(error))

            context = {
                "error": type(error).__name__,
                "message": str(error),
                "url": page.url,
                "dom_snapshot": dom_snapshot,
                "test_file": str(test_file),
                "line_number": line_number,
                "original_code": original_code,
                "selector": selector,
                "stack_trace": traceback.format_exc()
            }

            logger.debug(f"Captured failure context: {context['error']}")
            return context

        except Exception as e:
            logger.error(f"Failed to capture context: {e}")
            return {
                "error": type(error).__name__,
                "message": str(error),
                "capture_error": str(e)
            }

    def _get_test_location(self, test_func, error) -> tuple:
        """Get test file path, line number, and original code"""
        try:
            # Get source file
            source_file = Path(inspect.getfile(test_func))

            # Get line number from traceback
            tb = traceback.extract_tb(error.__traceback__)
            for frame in reversed(tb):
                if frame.filename == str(source_file):
                    line_number = frame.lineno

                    # Read the line
                    with open(source_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if 0 <= line_number - 1 < len(lines):
                            original_code = lines[line_number - 1].strip()
                            return source_file, line_number, original_code

            # Fallback
            return source_file, 1, ""

        except Exception as e:
            logger.error(f"Failed to get test location: {e}")
            return Path("unknown"), 0, ""

    def _extract_selector_from_error(self, error_message: str) -> str:
        """Extract selector from error message"""
        # Common patterns in Playwright errors
        patterns = [
            r'locator\([\'"]([^\'"]+)[\'"]\)',
            r'selector [\'"]([^\'"]+)[\'"]',
            r'waiting for selector [\'"]([^\'"]+)[\'"]',
        ]

        for pattern in patterns:
            import re
            match = re.search(pattern, error_message)
            if match:
                return match.group(1)

        return "unknown"

    async def _attempt_heal(self, context: Dict[str, Any]) -> bool:
        """
        Attempt to heal the failing test

        Args:
            context: Failure context

        Returns:
            True if healing successful, False otherwise
        """
        logger.info("Attempting to heal test via Backend API...")

        try:
            # 1. Trigger healing task
            task_id = await self.client.trigger_heal(context)
            logger.info(f"Healing task triggered. Task ID: {task_id}")

            # 2. Poll for result
            patch_info = await self.client.poll_task(task_id)

            if not patch_info:
                logger.error("Healing task failed or timed out.")
                return False

            # Check confidence
            confidence = patch_info.get("confidence", 0.0)
            if confidence < config.auto_heal.confidence_threshold:
                logger.warning(f"Confidence ({confidence:.2f}) below threshold ({config.auto_heal.confidence_threshold})")
                logger.info("Manual review recommended")
                return False

        except Exception as e:
            logger.error(f"Error during healing process: {e}")
            return False

        # Apply patch
        test_file = Path(context.get("test_file", ""))
        if not test_file.exists():
            logger.error(f"Test file not found: {test_file}")
            return False

        success = self.patch_manager.apply_patch(
            test_file=test_file,
            line_number=context.get("line_number", 0),
            original_code=context.get("original_code", ""),
            patch_code=patch_info.get("patch_code", ""),
            patch_info=patch_info
        )

        if not success:
            logger.error("Failed to apply patch")
            return False

        # Commit changes if enabled
        if config.auto_heal.auto_commit:
            self.patch_manager.commit_changes(test_file, patch_info)

        logger.success(f"Test healed with confidence {confidence:.2f}")
        return True


async def run_test_example():
    """Example of running a test with auto-heal"""
    runner = AutoHealTestRunner()

    try:
        await runner.setup()

        # Define a test function
        async def test_login(page: Page):
            await page.goto("file://" + str(Path(__file__).parent.parent.parent / "src" / "project-sample-1" / "index.html"))
            await page.fill("#username", "admin")
            await page.fill("#password", "password123")
            await page.click("#submit")  # This might fail if selector changes
            await page.wait_for_url("**/dashboard.html", timeout=5000)

        # Run test with healing
        result = await runner.run_test_with_healing(test_login)
        logger.info(f"Test result: {result}")

    finally:
        await runner.teardown()


if __name__ == "__main__":
    asyncio.run(run_test_example())
"""
Patch Manager - Handles creation and application of test patches
"""
import shutil
import re
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import git
from git.exc import GitCommandError

from .config import config
from .logger import get_logger

logger = get_logger(__name__)


class PatchManager:
    """Manages test patches and Git integration"""

    def __init__(self):
        self.patch_dir = config.auto_heal.patch_dir
        self.backup_dir = config.auto_heal.backup_dir
        self.repo = self._init_repo()

    def _init_repo(self) -> Optional[git.Repo]:
        """Initialize Git repository"""
        try:
            repo = git.Repo(search_parent_directories=True)
            logger.info(f"Git repo found at: {repo.working_dir}")
            return repo
        except git.InvalidGitRepositoryError:
            logger.warning("Not a git repository. Auto-commit disabled.")
            return None

    def create_backup(self, file_path: Path) -> Path:
        """
        Create backup of test file before patching

        Args:
            file_path: Path to the file to backup

        Returns:
            Path to the backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(file_path, backup_path)
        logger.info(f"Backup created: {backup_path}")

        return backup_path

    def apply_patch(
        self,
        test_file: Path,
        line_number: int,
        original_code: str,
        patch_code: str,
        patch_info: Dict[str, Any]
    ) -> bool:
        """
        Apply patch to test file

        Args:
            test_file: Path to the test file
            line_number: Line number where the error occurred
            original_code: Original code that failed
            patch_code: New code to apply
            patch_info: Full patch information from LLM

        Returns:
            True if patch applied successfully, False otherwise
        """
        try:
            # Create backup
            backup_path = self.create_backup(test_file)

            # Read file content
            with open(test_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Find and replace the failing line
            if line_number > 0 and line_number <= len(lines):
                # Try exact match first
                # Try exact match first
                if self._normalize_code(lines[line_number - 1]) == self._normalize_code(original_code):
                    indentation = self._get_indentation(lines[line_number - 1])
                    patch_code = patch_code.strip()
                    lines[line_number - 1] = f"{indentation}{patch_code}\n"
                    logger.info(f"Exact match found at line {line_number}")
                else:
                    # Try fuzzy match
                    found = False
                    for i, line in enumerate(lines):
                        if self._normalize_code(line) == self._normalize_code(original_code):
                            indentation = self._get_indentation(lines[i])
                            patch_code = patch_code.strip()
                            lines[i] = f"{indentation}{patch_code}\n"
                            logger.info(f"Fuzzy match found at line {i + 1}")
                            found = True
                            break

                    if not found:
                        logger.error(f"Could not find matching line in {test_file}")
                        return False
            else:
                logger.error(f"Invalid line number: {line_number}")
                return False

            # Write patched content
            with open(test_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            # Save patch metadata
            self._save_patch_metadata(test_file, patch_info, backup_path)

            logger.success(f"Patch applied to {test_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to apply patch: {e}")
            return False

    def _get_indentation(self, line: str) -> str:
        """Get indentation (leading whitespace) from line"""
        return line[:len(line) - len(line.lstrip())]

    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison (remove extra whitespace)"""
        return ' '.join(code.split())

    def _save_patch_metadata(
        self,
        test_file: Path,
        patch_info: Dict[str, Any],
        backup_path: Path
    ):
        """Save patch metadata for tracking"""
        timestamp = datetime.now().isoformat()
        metadata = {
            "timestamp": timestamp,
            "test_file": str(test_file),
            "backup_file": str(backup_path),
            "selector": patch_info.get("selector"),
            "selector_method": patch_info.get("selector_method"),
            "confidence": patch_info.get("confidence"),
            "explanation": patch_info.get("explanation"),
            "patch_code": patch_info.get("patch_code")
        }

        # Save as JSON
        import json
        metadata_file = self.patch_dir / f"patch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Patch metadata saved: {metadata_file}")

    def commit_changes(self, test_file: Path, patch_info: Dict[str, Any]) -> bool:
        """
        Commit changes to Git

        Args:
            test_file: Path to the modified test file
            patch_info: Patch information

        Returns:
            True if committed successfully, False otherwise
        """
        if not config.auto_heal.auto_commit:
            logger.info("Auto-commit disabled")
            return False

        if not self.repo:
            logger.warning("No Git repository available")
            return False

        try:
            # Stage the file
            self.repo.index.add([str(test_file)])

            # Create commit message
            commit_msg = self._create_commit_message(test_file, patch_info)

            # Commit
            self.repo.index.commit(commit_msg)
            logger.success(f"Changes committed: {commit_msg[:50]}...")

            return True

        except GitCommandError as e:
            logger.error(f"Git commit failed: {e}")
            return False

    def _create_commit_message(self, test_file: Path, patch_info: Dict[str, Any]) -> str:
        """Create descriptive commit message"""
        selector = patch_info.get("selector", "unknown")
        confidence = patch_info.get("confidence", 0.0)
        explanation = patch_info.get("explanation", "No explanation")

        return f"""[Auto-Heal] Fix selector in {test_file.name}

Selector: {selector}
Confidence: {confidence:.2f}
Method: {patch_info.get('selector_method', 'unknown')}

Explanation:
{explanation}

Auto-generated by Playwright Auto-Heal Framework
"""

    def create_pull_request(self, test_file: Path, patch_info: Dict[str, Any]) -> bool:
        """
        Create pull request for the patch (GitHub integration)

        Args:
            test_file: Path to the modified test file
            patch_info: Patch information

        Returns:
            True if PR created successfully, False otherwise
        """
        if not config.auto_heal.auto_pr:
            logger.info("Auto-PR disabled")
            return False

        # TODO: Implement GitHub API integration
        logger.warning("Pull request creation not yet implemented")
        return False

    def restore_backup(self, backup_path: Path, original_path: Path) -> bool:
        """
        Restore file from backup

        Args:
            backup_path: Path to the backup file
            original_path: Path to restore to

        Returns:
            True if restored successfully, False otherwise
        """
        try:
            shutil.copy2(backup_path, original_path)
            logger.success(f"Restored {original_path} from backup")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False

