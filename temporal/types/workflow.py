from dataclasses import dataclass
from typing import List, Optional

from .task import TaskData, TaskResult


@dataclass
class WorkflowInput:
    execution_id: int
    workflow_name: str
    tasks: List[TaskData]
    delay_seconds: int = 0


@dataclass
class WorkflowResult:
    execution_id: int
    status: str
    task_results: List[TaskResult]
    error_message: Optional[str] = None
