from dataclasses import dataclass
from typing import Optional


@dataclass
class UpdateTaskExecutionParams:
    task_execution_id: int
    status: str
    error_message: Optional[str] = None
