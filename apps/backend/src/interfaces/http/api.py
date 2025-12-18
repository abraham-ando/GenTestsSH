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
    # Actually, the Dev UI frontend usually expects the API at root of its base URL.
    # If the dev_ui_app itself prefixes everything with /v1, then we mount at /.
    # If it DOES NOT, we might need a different mount point.
    app.mount("/", dev_ui_app) 

except ImportError as e:
    print(f"Failed to import DevServer: {e}")
    # Fallback or just ignore if not installed
    pass
except Exception as e:
    print(f"Failed to mount Dev UI: {e}")
