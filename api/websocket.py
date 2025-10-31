from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from utils.logger import get_logger
from services.websocket_service import websocket_service
from services.task_service import task_service
from core.orchestrator import AgentOrchestrator
from agents.base_agent import Agent
from tools.weather_tool import WeatherTool
from tools.time_tool import TimeTool
import asyncio

logger = get_logger(__name__)

router = APIRouter()

# Initialize agents and orchestrator
# TODO: Move this to a dedicated initialization module or dependency injection
weather_agent = Agent(
    Name="Weather Agent",
    Description="Provides weather information for a given location",
    Tools=[WeatherTool()],
    Model="gpt-4o-mini"
)

time_agent = Agent(
    Name="Time Agent",
    Description="Provides the current time for a given city",
    Tools=[TimeTool()],
    Model="gpt-4o-mini"
)

orchestrator = AgentOrchestrator([weather_agent, time_agent])


class TaskRequest(BaseModel):
    prompt: str
    metadata: Dict[str, Any] = {}


@router.post("/api/tasks")
async def create_task(request: TaskRequest):
    """Create a new agent task"""
    try:
        task_id = await task_service.create_task(request.prompt)
        
        logger.info(f"Task created: {task_id}")
        
        return {
            "task_id": task_id,
            "status": "created",
            "message": "Task created successfully. Connect via WebSocket to receive updates."
        }
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for real-time task updates"""
    await websocket_service.connect_websocket(task_id, websocket)
    
    try:
        # Send initial connection confirmation
        await websocket_service.send_message(task_id, {
            "type": "connection.established",
            "task_id": task_id,
            "message": "Connected to task stream"
        })
        
        # Get task metadata
        task_metadata = task_service.task_metadata.get(task_id)
        if not task_metadata:
            await websocket_service.send_error(task_id, "Task not found")
            await websocket_service.disconnect_websocket(task_id)
            return
        
        prompt = task_metadata.get("prompt")
        
        # Send starting message
        await websocket_service.send_progress(
            task_id, 
            10, 
            "Analyzing your request...",
            step_number=1,
            total_steps=5
        )
        
        # Execute the agent task
        async def run_agent_task():
            try:
                # Send progress update
                await websocket_service.send_progress(
                    task_id,
                    30,
                    "Routing to appropriate agent...",
                    step_number=2,
                    total_steps=5
                )
                
                # Run orchestrator (note: orchestrator needs async support)
                # For now, we'll run it in a thread pool since it's synchronous
                import concurrent.futures
                loop = asyncio.get_event_loop()
                
                await websocket_service.send_progress(
                    task_id,
                    60,
                    "Agent processing your request...",
                    step_number=3,
                    total_steps=5
                )
                
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    result = await loop.run_in_executor(
                        pool,
                        orchestrator.orchestrate_task,
                        prompt
                    )
                
                await websocket_service.send_progress(
                    task_id,
                    90,
                    "Finalizing response...",
                    step_number=4,
                    total_steps=5
                )
                
                # Send completion message
                await websocket_service.send_message(task_id, {
                    "type": "task.complete",
                    "result": result,
                    "status": "completed"
                })
                
                # Mark task as complete
                task_service.complete_task(task_id, result)
                
                await websocket_service.send_progress(
                    task_id,
                    100,
                    "Complete!",
                    step_number=5,
                    total_steps=5
                )
                
            except asyncio.CancelledError:
                logger.info(f"Task {task_id} was cancelled")
                await websocket_service.send_message(task_id, {
                    "type": "task.cancelled",
                    "message": "Task was cancelled by user"
                })
                raise
            except Exception as e:
                logger.error(f"Error in task {task_id}: {e}", exc_info=True)
                await websocket_service.send_error(
                    task_id, 
                    str(e),
                    context="agent_execution"
                )
                task_service.cancel_task(task_id)
        
        # Create and register the task
        task = asyncio.create_task(run_agent_task())
        task_service.register_task(task_id, task)
        
        # Keep connection alive and listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received message from client: {data}")
                
                # Handle client messages (e.g., cancel request)
                if data == "cancel":
                    logger.info(f"Client requested cancellation of task {task_id}")
                    task_service.cancel_task(task_id)
                    break
                    
            except WebSocketDisconnect:
                logger.info(f"Client disconnected from task {task_id}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {e}", exc_info=True)
        
    finally:
        # Cleanup
        await websocket_service.disconnect_websocket(task_id)
        logger.info(f"WebSocket connection closed for task {task_id}")


@router.get("/api/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get the status of a task"""
    status = task_service.get_task_status(task_id)
    
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    metadata = task_service.task_metadata.get(task_id, {})
    
    return {
        "task_id": task_id,
        "status": status,
        "metadata": metadata
    }


@router.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "lilli-agent-system",
        "active_tasks": len(task_service.active_tasks),
        "active_connections": len(websocket_service.active_connections)
    }

