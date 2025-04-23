from dataclasses import dataclass
from enum import Enum
from typing import Optional

from notifications.types.email import EmailParams
from reports.types.report import ReportParams


class TaskType(Enum):
    EMAIL = "email"
    REPORT = "report"


@dataclass
class TaskData:
    task_execution_id: int
    name: str
    task_type: str
    order: int
    initial_interval: int
    maximum_attempts: int
    backoff_coefficient: float
    email_config: Optional[EmailParams] = None
    report_config: Optional[ReportParams] = None


@dataclass
class TaskResult:
    task_execution_id: int
    status: str
    error_message: Optional[str] = None
