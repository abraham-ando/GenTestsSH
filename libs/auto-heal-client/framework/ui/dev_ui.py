"""
Dev UI Server for GenTestsSH
"""
import asyncio
from agent_framework.devui import serve
from ..agents.agents import AgentFactory
from ..core.logger import get_logger

logger = get_logger(__name__)

def start_dev_ui(port: int = 8080):
    """
    Start the Dev UI server
    """
    logger.info(f"Starting Dev UI on port {port}...")
    
    # Import and create the workflow
    from ..agents.workflow import workflow
    
    # Start server with workflow
    # Note: Hot reload is not supported for dynamically created entities
    # Tracing disabled as OTLP collector is not running
    try:
        serve(
            entities=[workflow],
            port=port,
            ui_enabled=True,
            tracing_enabled=True,  # Enabled to visualize agent execution
            mode="developer",
            auto_open=True
        )
    except Exception as e:
        logger.error(f"Failed to start Dev UI: {e}")
        raise
