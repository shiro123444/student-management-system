"""
Progress tracking service for long-running tasks
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import uuid

logger = logging.getLogger(__name__)

class ProgressService:
    """Service for tracking progress of asynchronous tasks"""
    
    def __init__(self):
        # In-memory storage for demo purposes
        # In production, would use Redis or database
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.cleanup_interval = 3600  # 1 hour
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_old_tasks())
    
    async def start_task(
        self,
        task_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start tracking a new task"""
        task_id = str(uuid.uuid4())
        
        self.tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "status": "pending",
            "progress": 0,
            "message": "Task started",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "metadata": metadata or {},
            "result": None,
            "error": None
        }
        
        logger.info(f"Started task {task_id} of type {task_type}")
        return task_id
    
    async def update_task_progress(
        self,
        task_id: str,
        progress: int,
        message: Optional[str] = None
    ) -> bool:
        """Update task progress"""
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found for progress update")
            return False
        
        task = self.tasks[task_id]
        task["progress"] = max(0, min(100, progress))
        task["status"] = "processing"
        task["updated_at"] = datetime.utcnow()
        
        if message:
            task["message"] = message
        
        logger.debug(f"Task {task_id} progress: {progress}% - {message}")
        return True
    
    async def complete_task(
        self,
        task_id: str,
        result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Mark task as completed"""
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found for completion")
            return False
        
        task = self.tasks[task_id]
        task["status"] = "completed"
        task["progress"] = 100
        task["message"] = "Task completed successfully"
        task["updated_at"] = datetime.utcnow()
        task["result"] = result
        
        logger.info(f"Task {task_id} completed successfully")
        return True
    
    async def fail_task(
        self,
        task_id: str,
        error: str
    ) -> bool:
        """Mark task as failed"""
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found for failure")
            return False
        
        task = self.tasks[task_id]
        task["status"] = "failed"
        task["message"] = f"Task failed: {error}"
        task["updated_at"] = datetime.utcnow()
        task["error"] = error
        
        logger.error(f"Task {task_id} failed: {error}")
        return True
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a task"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id].copy()
        
        # Calculate elapsed time
        elapsed = datetime.utcnow() - task["created_at"]
        task["elapsed_seconds"] = int(elapsed.total_seconds())
        
        # Estimate completion time for processing tasks
        if task["status"] == "processing" and task["progress"] > 0:
            estimated_total = elapsed.total_seconds() * (100 / task["progress"])
            remaining = estimated_total - elapsed.total_seconds()
            task["estimated_completion_seconds"] = max(0, int(remaining))
        
        return task
    
    async def list_tasks(
        self,
        task_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List tasks with optional filtering"""
        tasks = []
        
        for task in self.tasks.values():
            # Apply filters
            if task_type and task["type"] != task_type:
                continue
            if status and task["status"] != status:
                continue
            
            # Add elapsed time
            elapsed = datetime.utcnow() - task["created_at"]
            task_copy = task.copy()
            task_copy["elapsed_seconds"] = int(elapsed.total_seconds())
            
            tasks.append(task_copy)
        
        # Sort by creation time (newest first)
        tasks.sort(key=lambda x: x["created_at"], reverse=True)
        
        return tasks[:limit]
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task from tracking"""
        if task_id not in self.tasks:
            return False
        
        del self.tasks[task_id]
        logger.info(f"Task {task_id} deleted from tracking")
        return True
    
    async def get_task_statistics(self) -> Dict[str, Any]:
        """Get statistics about tasks"""
        if not self.tasks:
            return {
                "total_tasks": 0,
                "by_status": {},
                "by_type": {},
                "average_completion_time": 0
            }
        
        # Count by status
        status_counts = {}
        type_counts = {}
        completion_times = []
        
        for task in self.tasks.values():
            # Count by status
            status = task["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by type
            task_type = task["type"]
            type_counts[task_type] = type_counts.get(task_type, 0) + 1
            
            # Calculate completion time for completed tasks
            if status == "completed":
                elapsed = task["updated_at"] - task["created_at"]
                completion_times.append(elapsed.total_seconds())
        
        # Calculate average completion time
        avg_completion = 0
        if completion_times:
            avg_completion = sum(completion_times) / len(completion_times)
        
        return {
            "total_tasks": len(self.tasks),
            "by_status": status_counts,
            "by_type": type_counts,
            "average_completion_time_seconds": avg_completion,
            "oldest_task_age_seconds": self._get_oldest_task_age(),
            "newest_task_age_seconds": self._get_newest_task_age()
        }
    
    def _get_oldest_task_age(self) -> int:
        """Get age of oldest task in seconds"""
        if not self.tasks:
            return 0
        
        oldest = min(task["created_at"] for task in self.tasks.values())
        return int((datetime.utcnow() - oldest).total_seconds())
    
    def _get_newest_task_age(self) -> int:
        """Get age of newest task in seconds"""
        if not self.tasks:
            return 0
        
        newest = max(task["created_at"] for task in self.tasks.values())
        return int((datetime.utcnow() - newest).total_seconds())
    
    async def _cleanup_old_tasks(self):
        """Background task to clean up old completed/failed tasks"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                cutoff_time = datetime.utcnow() - timedelta(hours=24)  # Keep for 24 hours
                tasks_to_delete = []
                
                for task_id, task in self.tasks.items():
                    if (task["status"] in ["completed", "failed"] and 
                        task["updated_at"] < cutoff_time):
                        tasks_to_delete.append(task_id)
                
                for task_id in tasks_to_delete:
                    del self.tasks[task_id]
                
                if tasks_to_delete:
                    logger.info(f"Cleaned up {len(tasks_to_delete)} old tasks")
                    
            except Exception as e:
                logger.error(f"Error in task cleanup: {e}")
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        if task["status"] not in ["pending", "processing"]:
            return False  # Can't cancel completed/failed tasks
        
        task["status"] = "cancelled"
        task["message"] = "Task cancelled by user"
        task["updated_at"] = datetime.utcnow()
        
        logger.info(f"Task {task_id} cancelled")
        return True
    
    async def retry_task(self, task_id: str) -> Optional[str]:
        """Retry a failed task (creates a new task)"""
        if task_id not in self.tasks:
            return None
        
        original_task = self.tasks[task_id]
        
        if original_task["status"] != "failed":
            return None  # Can only retry failed tasks
        
        # Create new task with same metadata
        new_task_id = await self.start_task(
            task_type=original_task["type"],
            metadata={
                **original_task["metadata"],
                "retry_of": task_id
            }
        )
        
        logger.info(f"Created retry task {new_task_id} for failed task {task_id}")
        return new_task_id