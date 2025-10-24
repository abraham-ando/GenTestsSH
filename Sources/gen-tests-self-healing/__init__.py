"""
Gen-Tests-Self-Healing Framework
A self-healing test automation framework with Playwright and LLM integration
"""

__version__ = "1.0.0"

from framework.core.test_runner import AutoHealTestRunner
from framework.core.config import config
from framework.core.logger import get_logger

__all__ = [
    "AutoHealTestRunner",
    "config",
    "get_logger",
]

