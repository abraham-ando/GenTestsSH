from typing import Dict, Any
from .app import celery_app
from ...application.services.orchestrator import AgentOrchestrator
from ..config.config import config
import logging

# Configure logger separately for backend or reuse framework logger if compatible
logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="heal_test_task")
def heal_test_task(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Celery task to run the self-healing process
    """
    logger.info(f"Task {self.request.id} started. Healing test: {context.get('test_name', 'unknown')}")
    
    # Initialize Orchestrator
    # Note: Orchestrator might need different initialization in backend context
    # ideally it should be stateless or use a singleton pattern if thread-safe
    orchestrator = AgentOrchestrator()
    
    # Run the heal process (synchronously within the worker, but async from API perspective)
    # Ensure tracing is active (if relying on env vars it should be auto-picked up)
    import os
    os.environ["OTEL_SERVICE_NAME"] = "auto-heal-worker"
    
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        result = loop.run_until_complete(orchestrator.heal_test(context))
        logger.info(f"Task {self.request.id} completed. Result: {result.get('confidence', 0)}")
        return result
    except Exception as e:
        logger.error(f"Task {self.request.id} failed: {e}")
        return {"error": str(e), "confidence": 0.0}
