"""
Initialize the Playwright test package
"""
__version__ = "1.0.0"
__author__ = "Auto-Heal Framework"

from .config import config
from .logger import get_logger

__all__ = [
    "config",
    "get_logger"
]

