import time
from typing import Dict, Any, Optional

class TaskStore:
    def __init__(self, ttl_seconds: int = 1800):
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds

    def add_task(self, task_id: str, data: Dict[str, Any]):
        data["created_at"] = time.time()
        self._tasks[task_id] = data
        self._cleanup()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        self._cleanup()
        return self._tasks.get(task_id)

    def remove_task(self, task_id: str):
        if task_id in self._tasks:
            del self._tasks[task_id]

    def _cleanup(self):
        now = time.time()
        expired = [tid for tid, d in self._tasks.items() if now - d.get("created_at", 0) > self._ttl]
        for tid in expired:
            del self._tasks[tid]

# Global singleton
task_store = TaskStore()
