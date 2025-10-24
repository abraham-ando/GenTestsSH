"""
Utility components
"""
__all__ = []
"""
Gen Tests Self-Healing Framework
Auto-healing test automation framework with Playwright and LLM
"""
__version__ = "1.0.0"
__author__ = "Auto-Heal Framework"

# Make framework components easily importable
from .framework.core.config import config
from .framework.core.logger import get_logger
from .framework.core.test_runner import AutoHealTestRunner
from .framework.core.patch_manager import PatchManager
from .framework.llm.llm_analyzer import LLMAnalyzer

__all__ = [
    "config",
    "get_logger",
    "AutoHealTestRunner",
    "PatchManager",
    "LLMAnalyzer",
]

