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
        """Create backup of test file before patching"""
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
        """Apply patch to test file"""
        try:
            backup_path = self.create_backup(test_file)

            with open(test_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if line_number > 0 and line_number <= len(lines):
                if self._normalize_code(lines[line_number - 1]) == self._normalize_code(original_code):
                    lines[line_number - 1] = patch_code if patch_code.endswith('\n') else patch_code + '\n'
                    logger.info(f"Exact match found at line {line_number}")
                else:
                    found = False
                    for i, line in enumerate(lines):
                        if self._normalize_code(line) == self._normalize_code(original_code):
                            lines[i] = patch_code if patch_code.endswith('\n') else patch_code + '\n'
                            logger.info(f"Fuzzy match found at line {i + 1}")
                            found = True
                            break

                    if not found:
                        logger.error(f"Could not find matching line in {test_file}")
                        return False
            else:
                logger.error(f"Invalid line number: {line_number}")
                return False

            with open(test_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            self._save_patch_metadata(test_file, patch_info, backup_path)
            logger.success(f"Patch applied to {test_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to apply patch: {e}")
            return False

    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison"""
        return ' '.join(code.split())

    def _save_patch_metadata(self, test_file: Path, patch_info: Dict[str, Any], backup_path: Path):
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

        import json
        metadata_file = self.patch_dir / f"patch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Patch metadata saved: {metadata_file}")

    def commit_changes(self, test_file: Path, patch_info: Dict[str, Any]) -> bool:
        """Commit changes to Git"""
        if not config.auto_heal.auto_commit:
            logger.info("Auto-commit disabled")
            return False

        if not self.repo:
            logger.warning("No Git repository available")
            return False

        try:
            self.repo.index.add([str(test_file)])
            commit_msg = self._create_commit_message(test_file, patch_info)
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

    def restore_backup(self, backup_path: Path, original_path: Path) -> bool:
        """Restore file from backup"""
        try:
            shutil.copy2(backup_path, original_path)
            logger.success(f"Restored {original_path} from backup")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False

