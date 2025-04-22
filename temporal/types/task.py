from dataclasses import dataclass
from enum import Enum
from typing import Optional
from temporalio.common import RetryPolicy

from notifications.types.email import EmailParams


class TaskType(Enum):
    EMAIL = "email"
    REPORT = "report"


@dataclass
class TaskData:
    task_execution_id: int
    name: str
    task_type: TaskType
    order: int
    retry_policy: Optional[RetryPolicy] = None
    email_config: Optional[EmailParams] = None


@dataclass
class TaskResult:
    task_execution_id: int
    status: str
    result: Optional[dict] = None
    error_message: Optional[str] = None