import asyncio
import httpx
from typing import Dict, Any, Optional
from .logger import get_logger

logger = get_logger(__name__)

class BackendClient:
    """Client for interacting with GenTestsSH Backend"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=60.0)

    async def trigger_heal(self, context: Dict[str, Any]) -> str:
        """
        Trigger healing process
        
        Returns:
            task_id (str)
        """
        try:
            # Clean context to be JSON serializable
            # Remove binary data if any or large strings if necessary
            # For now sending as is
            response = await self.client.post("/heal", json={"context": context})
            response.raise_for_status()
            data = response.json()
            return data["task_id"]
        except httpx.HTTPError as e:
            logger.error(f"Failed to trigger heal: {e}")
            raise

    async def poll_task(self, task_id: str, interval: float = 2.0, timeout: float = 120.0) -> Optional[Dict[str, Any]]:
        """
        Poll task status until completion
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            try:
                response = await self.client.get(f"/tasks/{task_id}")
                response.raise_for_status()
                data = response.json()
                status = data.get("status")
                
                if status == "SUCCESS":
                    return data.get("result")
                elif status == "FAILURE":
                    logger.error(f"Task failed on backend")
                    return None
                elif status == "REVOKED":
                    logger.error("Task revoked")
                    return None
                
                # Still PENDING or STARTED
                logger.debug(f"Task {task_id} status: {status}. Waiting...")
                await asyncio.sleep(interval)
                
            except httpx.HTTPError as e:
                logger.error(f"Failed to poll task: {e}")
                # Don't break immediately on transient network errors? 
                # For now let's wait more
                await asyncio.sleep(interval)

        logger.error(f"Polling timeout for task {task_id}")
        return None

    async def close(self):
        await self.client.aclose()
