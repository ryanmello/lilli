import asyncio
from typing import Any, Dict, Callable, Coroutine, Optional
import uuid
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

class TaskService():
    def __init__(self):
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_metadata: Dict[str, Dict[str, Any]] = {}

    async def create_task(self, prompt: str, coro: Optional[Coroutine] = None) -> str:
        """Create a new task with optional coroutine to execute"""
        task_id = str(uuid.uuid4())
        
        # Store metadata
        self.task_metadata[task_id] = {
            "prompt": prompt,
            "status": "running",
            "created_at": datetime.now().isoformat()
        }
        
        # If a coroutine is provided, create and store the actual asyncio task
        if coro:
            self.active_tasks[task_id] = asyncio.create_task(coro)
        
        logger.info(f"Created AI analysis task {task_id}")
        logger.info(f"User prompt: {prompt[:100]}...")
        return task_id
    
    def register_task(self, task_id: str, task: asyncio.Task):
        """Register an existing asyncio task (if task creation happens elsewhere)"""
        self.active_tasks[task_id] = task
        logger.info(f"Registered asyncio task for {task_id}")
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel and cleanup a task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if isinstance(task, asyncio.Task) and not task.done():
                task.cancel()
                logger.info(f"Cancelled analysis task {task_id}")
            del self.active_tasks[task_id]
            # Cleanup metadata too
            self.task_metadata.pop(task_id, None)
            return True
        return False
    
    def complete_task(self, task_id: str, result: Any = None):
        """Mark a task as completed and clean up active task"""
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
        
        # Update metadata status
        if task_id in self.task_metadata:
            self.task_metadata[task_id]["status"] = "completed"
            self.task_metadata[task_id]["completed_at"] = datetime.now().isoformat()
            if result:
                self.task_metadata[task_id]["result"] = result
        
        logger.info(f"Completed task {task_id}")
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get the current status of a task"""
        return self.task_metadata.get(task_id, {}).get("status")
    
task_service = TaskService()
