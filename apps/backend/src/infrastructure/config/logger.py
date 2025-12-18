import sys
from loguru import logger as loguru_logger

def get_logger(name: str):
    """
    Get a configured logger instance
    """
    # Configure loguru if not already configured
    # In a real app we might want more complex config
    return loguru_logger.bind(name=name)
