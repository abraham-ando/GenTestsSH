from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ...infrastructure.celery.app import celery_app
from ...infrastructure.celery.tasks import heal_test_task
from ...infrastructure.config.config import config

app = FastAPI(title="GenTestsSH Backend", version="1.0.0")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev simplicity. In dynamic setup, can be specific.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealRequest(BaseModel):
    context: Dict[str, Any]

class TaskResponse(BaseModel):
    task_id: str
    status: str

# Root redirects to health or removed to avoid collision

@app.post("/heal", response_model=TaskResponse)
async def trigger_heal(request: HealRequest):
    """
    Trigger a self-healing task
    """
    task = heal_test_task.delay(request.context)
    return {"task_id": task.id, "status": "PENDING"}

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status and result of a task
    """
    task_result = celery_app.AsyncResult(task_id)
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
    return response

@app.get("/health")
async def health_check():
    return {"status": "ok", "redis": config.REDIS_URL}

# Dev UI Integration
try:
    from agent_framework.devui import DevServer
    from ...application.services.workflow import self_healing_workflow
    
    # Initialize DevServer
    dev_server = DevServer()
    # Register entities (call the factory function)
    dev_server.register_entities([self_healing_workflow()])
    
    dev_ui_app = dev_server.create_app()
    
    # Log routes for debugging
    print("Dev UI Routes:")
    for route in dev_ui_app.routes:
        print(f"  {getattr(route, 'path', '???')} -> {getattr(route, 'name', '???')}")

    
    # Mount the Dev UI API at /v1 if that's what's missing
    app.mount("/", dev_ui_app) 

    # Redis bridge for real-time events
    import asyncio
    import redis.asyncio as async_redis
    import json

    async def redis_event_bridge():
        """Listen to Redis and emit events to Dev UI"""
        logger = logging.getLogger("api.redis_bridge")
        logger.info(f"Starting Redis bridge on {config.REDIS_URL}...")
        try:
            r = async_redis.from_url(config.REDIS_URL, decode_responses=True)
            pubsub = r.pubsub()
            await pubsub.subscribe("agent-events")
            
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        if data.get("type") == "executor_event":
                            # Map to DevServer event structure
                            # DevServer.emit_external_event expects a dict that looks like a workflow event
                            dev_server.emit_external_event({
                                "executor_id": data["executor_id"],
                                "event_type": "ExecutorInvokedEvent" if data["state"] == "running" else "ExecutorCompletedEvent",
                                "data": data.get("output") or data.get("error") or "",
                                "timestamp": data["timestamp"]
                            })
                    except Exception as e:
                        logger.error(f"Error processing Redis event: {e}")
        except Exception as e:
            logger.error(f"Redis bridge connection error: {e}")
            await asyncio.sleep(5)  # Retry delay
            asyncio.create_task(redis_event_bridge())

    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(redis_event_bridge())

except ImportError as e:
    print(f"Failed to import DevServer: {e}")
    # Fallback or just ignore if not installed
    pass
except Exception as e:
    print(f"Failed to mount Dev UI: {e}")
