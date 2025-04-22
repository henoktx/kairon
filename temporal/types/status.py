from enum import Enum


class Status(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"