import sys
from os.path import dirname, abspath
import logging

# Ensure project root is in path
project_root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(project_root)

from apps.backend.agents.workflow import workflow
from agent_framework.devui import serve
from apps.backend.logger import get_logger

logger = get_logger(__name__)

def start():
    """Start the Dev UI server"""
    logger.info("Starting Dev UI Server...")
    try:
        serve(
            entities=[workflow],
            port=8080,
            ui_enabled=True,
            tracing_enabled=True,
            mode="developer",
            auto_open=True
        )
    except Exception as e:
        logger.error(f"Failed to start Dev UI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start()
